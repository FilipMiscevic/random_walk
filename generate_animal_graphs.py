from core.input import *
from core.wmmapping import *
import core.evaluate as evaluate
import pickle
from core.wgraph import *
import igraph
import re

from animals import *

def plot_graph(graph,n,show_pos=True,vertex_colors='default'):
    '''Graph,Str,Bool -> None
    Save graph as an .SVG with filename n.
    '''
    if show_pos == False:
        labels = [i[:-2] for i in graph.vs['label']]
    else:
        labels=graph.vs['label']

    layout = graph.layout('fr',weights=rescale(graph.es['distance'],out_range=(0.1,0)))
    edge_width=rescale([1-i for i in graph.es['distance']],out_range=(0.5,1.5))
    
    #plot(graph,name+'_clusters.svg',bbox=(2048,2048),vertex_color=[color_list[x] for x in graph.clusters().membership],layout=layout,edge_width=edge_width)
    v_colors = None
    
    if vertex_colors == None:
        pass
    elif vertex_colors == 'default':
        v_colors = ['white' if l not in ANIMAL_CATEG_NUM_POS else known_colors.keys()[ANIMAL_CATEG_NUM_POS[l]+15] for l in graph.vs['label']]
    else:
        v_colors = ['white' if qq == -1 else known_colors.keys()[qq+25] for qq in vertex_colors]
    
    igraph.plot(graph,n+'_hillscateg.svg',bbox=(1500,1500),vertex_labels=labels,vertex_color=v_colors
    ,layout=layout,edge_width=edge_width)
    
def learned_words(l,words,sim):
    '''Lexicon,List,Float -> List
    Return a list of words from 'words' from a learned lexicon if its acquisition score is >= 'sim'.
    '''
    return [i for i in words if l.acquisition_score(i) >= sim]
    #return [i for i in words if evaluate.calculate_similarity(8500,learner._learned_lexicon.meaning(i),GOLD.meaning(i),'COS') >= sim]

def get_beagle(similarity,asim=None,fname='animals_cosines.txt',labels='animals_labels.txt'):
    '''Float -> Graph
    Generate and return a graph from the BEAGLE adjacency matrix with edges filtered to have a distance of 1-similarity.
    '''
    if asim==None:
        asim = similarity
        
    graph = Graph.Read_Adjacency(fname,attribute='similarity',mode='undirected')
    
    names=None
    with open(labels,'r') as f:
        names = f.readlines()
    names = [name.strip()+":N" for name in names]
    
    graph.vs['label']=names
    
    graph.es.select(similarity = 1.0).delete()
    
   
    a = graph.vs.find(label='animal:N').index
    
    e = graph.es.select(similarity_lt = asim)    
    ae = e.select(_target = a) 
    ae.delete()     
    
    e2 = graph.es.select(similarity_lt = similarity)        
    nae = e2.select(_target_ne = a)
    nae.delete()   
    
    graph.es.select(similarity_lt = similarity).delete()
    
    graph.es['distance']= [1-graph.es[i]['similarity'] for i in range(0,graph.ecount())]
    graph.es['weight']= graph.es['distance']
    #assert graph.is_weighted() == True
    
    names_shared = set(names).intersection(A_NAME.keys() + ['animal:N'])
    sub = graph.subgraph(graph.vs(label_in=names_shared))
    
    return sub

def generate_graphs(sim_thresholds,word_groups,lexicons,
    plot_graphs = True,
    show_pos = True,
    write_graphs = True,
    connect_to_animal = True,
    animal_sim = 0.4,
    overwrite = False):
    '''List,List,List -> List'''
    
    all_graphs = {}
    
    for sim in sim_thresholds:
        
        g = WordsGraph(20,sim,'hub-categories-prob-random',0,0.00001,20,0,1,'map')
        
        for w in word_groups:
            for _l in lexicons:
                
                name = '_'.join([_l,w,str(sim)])
                
                if connect_to_animal:
                    name = ''.join([name,'_A',str(animal_sim)])
                
                fpath = "graphs/" + name + '.graphml'
                
                if not overwrite:
                    if os.path.isfile(fpath):
                        print(name + " exists, skipping")
                        continue
                    
                print(name)
                
                graph = g.create_final_graph(word_groups[w],lexicons[_l],8500,'COS')

                #connect to word animal for learned data
                if connect_to_animal:
                    for word in word_groups[w]:
                        #don't connect animal to itself
                        if word == 'animal:N':
                            continue
                        
                        a_sim = evaluate.calculate_similarity(8500,lexicons[_l].meaning(word),lexicons[_l].meaning('animal:N'),'COS')
                        #learner.acquisition_score(word)
                        if a_sim >= animal_sim:
                            e = graph.add_edge(graph.vs.find(label='animal:N').index,graph.vs.find(label=word).index)
                            graph.edge_properties['distance'][e] = 1-a_sim
                
                all_graphs[name] = graph
                if plot_graphs: plot_graph(graph,name,show_pos)
                if write_graphs: write_graphml(graph,fpath)                
    return all_graphs

def filter_edges(graph,sim,animal_edges='exclude'):
    '''Graph,Float,Str -> Graph
    Remove edges from a graph if the distance is 1-sim. Do this for edges connected to the node animal, all edges besides these, or all edges in the graph.
    '''
    graph = graph.copy()
    
    if animal_edges == 'include':
        #graph.es.select(distance_gt = 1-sim).delete() 
        graph.es.select(similarity_gt = 1-sim).delete()             
    elif animal_edges == 'only':
        a = graph.vs.find(label='animal:N').index
        s1 = graph.es.select(_target = a) 
        s2 = s1.select(distance_gt = 1-sim)
        s2.delete()     
    else:
        a = graph.vs.find(label='animal:N').index
        s1 = graph.es.select(distance_gt = 1-sim)
        #s2 = s1.select(_source_ne = a)
        s3 = s1.select(_target_ne = a)
        s3.delete()
    
    return graph

def write_graphml(graph,fpath):
    '''Graph,Str -> None
    Save the Graph at the specified file path (fpath) in GraphML format.
    '''
    g = graph.copy()
    #needed to fix bug when importing to graph_tool
    g.vs['acqscore']=0
    g.write_graphml(open(fpath,'wb'))    
    
def get_model(name,a_filter=True):
    '''Str -> Graph
    Return a Graph with graphml filename 'name' in the directory graphs/, if it exists; return None otherwise.'''
    try:
        return get_models([name],a_filter).items()[0][1]
    except IndexError as e:
        return None
    
def convert_hfp(p):
    lines = []
    with open(p, 'rb') as f:
        for l in f:
            if '>0x' in l:
                ll = re.findall(r"<.*?>",l)
                val = re.findall(r"0x.*?[\^<]",l)[0][:-1]
                lines.append(ll[0]+str(float.fromhex(val))+ll[1])
            else:
                lines.append(l)
    with open(p,'wb') as f:
        f.writelines(lines)
                
    
def get_models(names=None,like=None,a_filter=True):
    files = os.listdir('graphs/') 
    file_names = None
    models = {}    

    if names == None:
        if like == None:
            file_names = files
            names = [name[:-8] for name in file_names]
        else:
            file_names = [f for f in files if like in f]
            names = [name[:-8] for name in file_names]            
    else:
        file_names = [name + '.graphml' for name in names]
    
    for i,n in enumerate(file_names):
        if n in files:
            g = igraph.Graph()
            
            #needed when reading graph_tool generated graphml
            convert_hfp('graphs/'+n)
            
            g2 = g.Read_GraphML(open('graphs/'+n))# directed=False)
            g2.simplify(combine_edges='max')
            if a_filter:
                models[names[i]] = g2.subgraph(g2.vs(label_in=A_NAME.keys()+['animal:N']))
            else:
                models[names[i]] = g2
        else:
            print("WARNING: graphs/{} not found.\n".format(n))
            
    return models
    
def generate_graphs_from_file(sim_thresholds,word_groups,lexicons,
    plot_graphs = True,
    show_pos = True,
    write_graphs = True,
    connect_to_animal = True,
    animal_sims = [''],
    overwrite = False):

    all_graphs = {}
    
    min_g = None
    
    for animal_sim in sorted(animal_sims):
        
        for sim in sorted(sim_thresholds):
            
            g = WordsGraph(20,sim,'hub-categories-prob-random',0,0.00001,20,0,1,'map')

            for w in word_groups:
                for _l in lexicons:
                
                    name = '_'.join([_l,w,str(sim)])
                    
                    if connect_to_animal:
                        name = ''.join([name,'_A',str(animal_sim)])
                    
                    fpath = "graphs/" + name + '.graphml'
                                        
                    if not overwrite:
                        if os.path.isfile(fpath):
                            print(name + " exists, skipping")
                            #continue
                    print name
                    if sim == min(sim_thresholds) and animal_sim == min(animal_sims):
                        min_sim = min(min(sim_thresholds),min(animal_sims))
                        if _l == "BEAGLE":
                            graph = get_beagle(min_sim)
                        else:
                            graph = get_models([name]).items()[0][1]
                        #print graph
                        min_g = graph
                    else: 
                        graph = filter_edges(min_g, sim, animal_edges='exclude')
                        graph = filter_edges(graph,animal_sim, animal_edges='only')
                    
                    all_graphs[name] = graph
                    if plot_graphs: plot_graph(graph,name,show_pos)
                    if write_graphs: write_graphml(graph,fpath)                
    return all_graphs    

def load_learner_lex(fname):
    return pickle.load(open(fname,'rb'))

    
def get_cluster(g,vertex):
    '''Return a subgraph containing the connected component to which vertex v belongs.'''
    try:
        vertex = g.vs.find(label=vertex).index if type(vertex)==str else vertex
        vertices = [l for l in g.clusters() if vertex in l]
        return g.subgraph(vertices[0])
    except Exception as e:
        print('WARNING: node {} not found'.format(vertex))


def in_same_cluster(g,v,w):
    '''Determine whether two vertices in a graph belong to the same connected component.'''
    v = g.vs.find(label=v).index if type(v)==str else v    
    w = g.vs.find(label=w).index if type(w)==str else w

    v_clust = [l for l in g.clusters() if v in l]
    
    w_in_v_clust = [m for m in v_clust if w in m]
    
    return bool(w_in_v_clust)

def get_beagle_shared(sim,other_graph=get_model('all_dev_utt_learner_af_HILLS_SHARED_0.78_A0.5')):
    '''Get the BEAGLE network containing the intersection of words learned by BEAGLE and by other_graph.
    '''
    beagle = get_beagle(sim)
    
    names_shared = set(beagle.vs['label']).intersection(other_graph.vs['label'])
    beagle_sub = beagle.subgraph(beagle.vs(label_in=names_shared))  
    #assert beagle_sub.vcount() <= other_graph.vcount()
    return beagle_sub

if __name__ == "__main__":
    if 'LEX' not in globals():
        print("Loading learner lexicon...")    
        LEX = load_learner_lex('learn_af_lexicon.lex')
        #execfile('create_learner2.py')
        #learner = pickle.load( open( "./learner_comp.obj", "rb" ) )
    print("Learner lexicon in memory.")
    
    color_list = known_colors.keys() 
    
    #other words to compare
    #NOUNS = [i for i in learner._learned_lexicon.words() if i[-2:]==':N']
    #GOLD_ANIMALS_SIM_0_0_SHARED = [i for i in SHARED_HILLS_POS_CATEG_NUM if evaluate.calculate_similarity(8500,GOLD.meaning(i),GOLD.meaning('animal:N'),'COS')>0.0] #577
    
    #TEST_FOOD = [i for i in GOLD.words() if 'food#2' in GOLD.meaning(i).seen_features() or 'food#1' in GOLD.meaning(i).seen_features()]

    sim_thresholds = [0.5]
    #LEX = load_learner_lex()
    lexicons = {'all_dev_utt_learner_af':LEX}#,'gold_af':GOLD}
    
    word_groups = {'HILLS_SHARED':SHARED_HILLS_POS_CATEG_NUM.keys() + ['animal:N']}#{'learned_nouns':ALL_NOUNS_08}#{'HILLS_SHARED':SHARED_HILLS_POS_CATEG_NUM.keys() + ['animal:N'],'HILLS_SHARED_LEARNED_0.8':learned_words(learner,SHARED_HILLS_POS_CATEG_NUM,0.8) + ['animal:N']}
    #{'ALL_GOLD_ANIMALS':GOLD_ANIMALS_POS + ['animal:N'],
    #{'HILLS_SHARED':SHARED_HILLS_POS_CATEG_NUM.keys() + ['animal:N'],
    
    
    print("Generating graphs...")
    
    all_graphs = generate_graphs(sim_thresholds,word_groups,lexicons,
        plot_graphs = True,
        show_pos = True,
        write_graphs = True,
        connect_to_animal = False,
        animal_sim = 0.5,
        overwrite = False)
