import os,sys
p = os.path.abspath('../')
# next line adds the directory to a path which "imports" searches for files.
# Alternatively, this path could be added to PYTHONPATH.
sys.path.append(p) 
os.chdir('../')

from core.input import *
from core.wmmapping import *
import core.evaluate as evaluate
import pickle
from core.wgraph import *

from animals import *

def plot_graph(graph,show_pos=True):
    if show_pos == False:
        labels = [i[:-2] for i in graph.vs['label']]
    else:
        labels=graph.vs['label']                    

    layout = graph.layout('fr',weights=rescale(graph.es['distance'],out_range=(0.1,0)))
    edge_width=rescale([1-i for i in graph.es['distance']],out_range=(0.5,1.5))
    
    #plot(graph,name+'_clusters.svg',bbox=(2048,2048),vertex_color=[color_list[x] for x in graph.clusters().membership],layout=layout,edge_width=edge_width)
    
    plot(graph,name+'_hillscateg.svg',bbox=(1500,1500),vertex_labels=labels,vertex_color=['white' if l not in ANIMAL_CATEG_NUM_POS else known_colors.keys()[ANIMAL_CATEG_NUM_POS[l]+15] for l in graph.vs['label']]
    ,layout=layout,edge_width=edge_width)
    
def learned_words(words,sim):
    return [i for i in words if learner.acquisition_score(i) >= sim]
    #return [i for i in words if evaluate.calculate_similarity(8500,learner._learned_lexicon.meaning(i),GOLD.meaning(i),'COS') >= sim]

if __name__ == "__main__":
    if 'learner' not in globals():
        print("Loading learner...")        
        learner = pickle.load( open( "./learner_comp.obj", "rb" ) )
    print("Learner in memory.")
    
    color_list = known_colors.keys() 
    
    #other words to compare
    #NOUNS = [i for i in learner._learned_lexicon.words() if i[-2:]==':N']
    #GOLD_ANIMALS_SIM_0_6_POS = [i for i in GOLD.words() if evaluate.calculate_similarity(8500,GOLD.meaning(i),GOLD.meaning('animal:N'),'COS')>0.6] #577
    
    #TEST_FOOD = [i for i in GOLD.words() if 'food#2' in GOLD.meaning(i).seen_features() or 'food#1' in GOLD.meaning(i).seen_features()]

    sim_thresholds = [0.97,0.98]#[0.55,0.6,0.7,0.8,0.85,0.88,0.9,0.95]#,0.9,0.95,0.96,0.97,0.98,0.99,0.999]
    
    lexicons = {'all_dev_utt_learner':learner._learned_lexicon}#,'gold':GOLD}
    
    word_groups = {'HILLS_SHARED_LEARNED_0.7':learned_words(SHARED_HILLS_POS_CATEG_NUM,0.7) + ['animal:N'],
                   'HILLS_SHARED_LEARNED_0.8':learned_words(SHARED_HILLS_POS_CATEG_NUM,0.8) + ['animal:N'],
                   'HILLS_SHARED_LEARNED_0.9':learned_words(SHARED_HILLS_POS_CATEG_NUM,0.9) + ['animal:N']}#,                   'GOLD_ANIMALS_SIM_06':GOLD_ANIMALS_SIM_0_6_POS}
    #{'ALL_GOLD_ANIMALS':GOLD_ANIMALS_POS + ['animal:N'],
    #{'HILLS_SHARED':SHARED_HILLS_POS_CATEG_NUM.keys() + ['animal:N'],
    
    plot_graphs = True
    show_pos= True
    connect_to_animal = True
    animal_sim = 0.4
    
    all_graphs = {}
    
    print("Generating graphs...")
    
    for sim in sim_thresholds:
        
        g = WordsGraph(20,sim,'hub-categories-prob-random',0,0.00001,20,0,1,'map')
        
        for w in word_groups:
            for _l in lexicons:
                graph = g.create_final_graph(word_groups[w],lexicons[_l],8500,'COS')
                name = '_'.join([_l,w,str(sim)])
                print(name)
                all_graphs[name]=graph
                
                if connect_to_animal:
                    for word in word_groups[w]:
                        a_sim = evaluate.calculate_similarity(8500,lexicons[_l].meaning(word),lexicons[_l].meaning('animal:N'),'COS')
                        if a_sim >= animal_sim:
                            e = graph.add_edge(graph.vs.find(label='animal:N').index,graph.vs.find(label=word).index)
                            graph.edge_properties['distance'][e] = 1-a_sim
                
                
                if plot_graphs == True: plot_graph(graph,show_pos)
