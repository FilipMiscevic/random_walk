from core.input import *
from core.wmmapping import *
import core.evaluate as evaluate
import pickle
from core.wgraph import *

from animals import *

def plot_graph(graph,n,show_pos=True):
    if show_pos == False:
        labels = [i[:-2] for i in graph.vs['label']]
    else:
        labels=graph.vs['label']

    layout = graph.layout('fr',weights=rescale(graph.es['distance'],out_range=(0.1,0)))
    edge_width=rescale([1-i for i in graph.es['distance']],out_range=(0.5,1.5))
    
    #plot(graph,name+'_clusters.svg',bbox=(2048,2048),vertex_color=[color_list[x] for x in graph.clusters().membership],layout=layout,edge_width=edge_width)
    
    plot(graph,n+'_hillscateg.svg',bbox=(1500,1500),vertex_labels=labels,vertex_color=['white' if l not in ANIMAL_CATEG_NUM_POS else known_colors.keys()[ANIMAL_CATEG_NUM_POS[l]+15] for l in graph.vs['label']]
    ,layout=layout,edge_width=edge_width)
    
def learned_words(ll,words,sim):
    return [i for i in words if ll.acquisition_score(i) >= sim]
    #return [i for i in words if evaluate.calculate_similarity(8500,learner._learned_lexicon.meaning(i),GOLD.meaning(i),'COS') >= sim]
    
def get_animal_sim(graph,l1,l2):
    return evaluate.calculate_similarity(8500,l1.meaning(word),l2.meaning('animal:N'),'COS')

def get_beagle(similarity): 
    graph = Graph.Read_Adjacency('dataancosim.txt',attribute='similarity',mode='undirected')
    
    names=None
    with open('datamatrixlabels.txt','r') as f:
        names = f.readlines()
    names = [name.strip('\n')+":N" for name in names]
    
    graph.vs['label']=names
    
    graph.es.select(similarity = 1.0).delete()
    graph.es.select(similarity_lt = similarity).delete()
    
    graph.es['distance']= [1-graph.es[i]['similarity'] for i in range(0,graph.ecount())]
    graph.es['weight']= graph.es['distance']
    assert graph.is_weighted() == True
    
    names_shared = set(names).intersection(A_NAME)
    global sub
    sub = graph.subgraph(graph.vs(label_in=names_shared))

    sub.add_vertices(1)
    sub.vs[-1:]['label'] ='animal:N'
    a = sub.vcount() - 1
    b = sub.vs.find(label='bird:N').index
    sub.add_edges([(a,b)])
    sub.es[-1:]['distance']=0.99
    
    return sub

def generate_graphs(sim_thresholds,word_groups,lexicons,
    plot_graphs = True,
    show_pos = True,
    write_graphs = True,
    connect_to_animal = True,
    animal_sim = 0.4,
    overwrite = False):
    
    all_graphs = {}
    
    for sim in sim_thresholds:
        
        g = WordsGraph(20,sim,'hub-categories-prob-random',0,0.00001,20,0,1,'map')
        #print 'this part loaded'
        
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
                if write_graphs: write_graphxl(graph,fpath)                
    return all_graphs

def write_graphxl(graph,fpath):
    gg = graph.copy()
    #needed to fix bug when importing to graph_tool
    gg.vs['acqscore']=0
    gg.write_graphml(open(fpath,'wb'))    

if __name__ == "__main__":
    if 'learner' not in globals():
        print("Loading learner...")     
        execfile('create_learner2.py')
        #learner = pickle.load( open( "./learner_comp.obj", "rb" ) )
    print("Learner in memory.")
    
    color_list = known_colors.keys() 
    
    #other words to compare
    #NOUNS = [i for i in learner._learned_lexicon.words() if i[-2:]==':N']
    #GOLD_ANIMALS_SIM_0_0_SHARED = [i for i in SHARED_HILLS_POS_CATEG_NUM if evaluate.calculate_similarity(8500,GOLD.meaning(i),GOLD.meaning('animal:N'),'COS')>0.0] #577
    
    #TEST_FOOD = [i for i in GOLD.words() if 'food#2' in GOLD.meaning(i).seen_features() or 'food#1' in GOLD.meaning(i).seen_features()]

    sim_thresholds = [0.55,0.6,0.7,0.8,0.85,0.88,0.9,0.95,0.96,0.97,0.98,0.99,0.999]
    
    lexicons = {'all_dev_utt_learner_af':learner._learned_lexicon,'gold_af':GOLD}
    
    word_groups = {'HILLS_SHARED':SHARED_HILLS_POS_CATEG_NUM.keys() + ['animal:N'],'HILLS_SHARED_LEARNED_0.8':learned_words(learner,SHARED_HILLS_POS_CATEG_NUM,0.8) + ['animal:N']}
    #{'ALL_GOLD_ANIMALS':GOLD_ANIMALS_POS + ['animal:N'],
    #{'HILLS_SHARED':SHARED_HILLS_POS_CATEG_NUM.keys() + ['animal:N'],
    
    
    print("Generating graphs...")
    
    all_graphs = generate_graphs(sim_thresholds,word_groups,lexicons,
        plot_graphs = True,
        show_pos = True,
        write_graphs = True,
        connect_to_animal = True,
        animal_sim = 0.4,
        overwrite = False)