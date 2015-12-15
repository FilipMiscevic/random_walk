import os,sys
p = os.path.abspath('../')
# next line adds the directory to a path which "imports" searches for files.
# Alternatively, this path could be added to PYTHONPATH.
sys.path.append(p) 
os.chdir('../')

#import core.learn as learn
#import core.learnconfig as config
#import core.plot as plot
from core.input import *
from core.wmmapping import *
import core.evaluate as evaluate
import pickle
from core.wgraph import *

from animals import *

if __name__ == "__main__":
    LEX = read_gold_lexicon('data/all_catf_norm_prob_lexicon_cs.all',8500)
    
    words_raw = LEX.words()
    words = [ word.split(':')[0] for word in words_raw]
    
    
    
    count = 0
    shared_words = []
    non_shared = []
    total_words = 0
    words_w_pos = []
    
    with open('animals.txt') as words_to_check:
        for word in words_to_check:
            word = word.lower().strip()
            #print word
            total_words +=1
            if word in words:
                count += 1
                shared_words.append(word)
                #words_w_pos.append(words_raw[words.index(word)])
            else:
                non_shared.append(word)
    words_w_pos = [w +':N' for w in shared_words]
    #print count
    #print total_words
    #print shared_words
    #print words_w_pos
    #print non_shared
    
    
    learner = pickle.load( open( "./core/learner.obj", "rb" ) )
    '''
    
    animal = learner._learned_lexicon.meaning('animal:N')
    #self._learned_lexicon.meaning(word)
    for w in words_w_pos:
        print(w)
        print(evaluate.calculate_similarity(8500, learner._learned_lexicon.meaning(w), animal, 'COS'))'''    
    
    color_list = known_colors.keys() 
    
    shared_categ = {'bat:N': 12, 'bull:N': 10, 'cub:N': 14, 'frog:N': 20, 'tiger:N': 10, 'devil:N': 3, 'moth:N': 13, 'insect:N': 13, 'dog:N': 15, 'dolphin:N': 20, 'turkey:N': 9, 'wasp:N': 13, 'lion:N': 10, 'rooster:N': 9, 'chick:N': 9, 'cat:N': 15, 'kiwi:N': 5, 'ram:N': 9, 'deer:N': 14, 'tick:N': 13, 'duck:N': 5, 'flea:N': 13, 'gorilla:N': 16, 'elephant:N': 0, 'fish:N': 20, 'clam:N': 20, 'pig:N': 9, 'goat:N': 9, 'owl:N': 5, 'seal:N': 20, 'giraffe:N': 0, 'snake:N': 18, 'cricket:N': 13, 'mosquito:N': 13, 'horse:N': 9, 'bug:N': 13, 'sheep:N': 9, 'dinosaur:N': 18, 'monkey:N': 16, 'ant:N': 13, 'rat:N': 19, 'reindeer:N': 8, 'toad:N': 20, 'squirrel:N': 19, 'reptile:N': 18, 'caterpillar:N': 13, 'donkey:N': 9, 'pony:N': 9, 'salmon:N': 11, 'cow:N': 9, 'trout:N': 11, 'ray:N': 20, 'quail:N': 5, 'moose:N': 14, 'snail:N': 20, 'jack:N': 11, 'sponge:N': 20, 'kitten:N': 15, 'swallow:N': 5, 'tuna:N': 11, 'cattle:N': 6, 'chicken:N': 9, 'crane:N': 10, 'turtle:N': 20, 'robin:N': 5, 'human:N': 16, 'shark:N': 20, 'lamb:N': 9, 'worm:N': 13, 'alligator:N': 20, 'penguin:N': 20, 'leopard:N': 10, 'swift:N': 5, 'bear:N': 14, 'butterfly:N': 13, 'sparrow:N': 5, 'fawn:N': 8, 'swan:N': 5, 'chipmunk:N': 19, 'fly:N': 13, 'calf:N': 9, 'wolf:N': 14, 'hare:N': 17, 'bird:N': 5, 'camel:N': 4, 'parrot:N': 15, 'pigeon:N': 5, 'crocodile:N': 18, 'spider:N': 9, 'rabbit:N': 17, 'mouse:N': 19, 'mole:N': 19, 'crow:N': 5, 'seagull:N': 5, 'steer:N': 6, 'eagle:N': 5, 'kangaroo:N': 3, 'bee:N': 13, 'tortoise:N': 18, 'whale:N': 20, 'kid:N': 9, 'dragon:N': 18, 'goose:N': 20, 'puppy:N': 15, 'crab:N': 20, 'lobster:N': 20, 'beetle:N': 13, 'dove:N': 5, 'kite:N': 5, 'porcupine:N': 19, 'grasshopper:N': 13, 'fox:N': 14, 'beaver:N': 20, 'lizard:N': 18, 'hen:N': 9, 'bunny:N': 17}
    
    '''g = WordsGraph(20,0.6,'hub-categories-prob-random',0,0.00001,20,0,1,'map')
    final = g.create_final_graph(words_w_pos,learner._learned_lexicon,8500,'COS') 
    
    plot(final,'final_animals_0.6_clusters.svg',bbox=(1024,1024),vertex_color=[color_list[x] for x in final.clusters().membership],layout=final.layout('kk'))
    
    
    
    plot(final,'final_animals_0.6_troyercateg.svg',bbox=(1024,1024),vertex_color=['white' if l not in shared_categ else known_colors.keys()[shared_categ[l]+15] for l in final.vs['label']]
,layout=final.layout('kk'))
    
    corpus = g.create_final_graph(words_w_pos,learner._gold_lexicon,8500,'COS')
    
    plot(corpus,'corpus_animals_0.6_clusters.svg',bbox=(1024,1024),vertex_color=[color_list[x] for x in corpus.clusters().membership],layout=corpus.layout('kk'))
    plot(corpus,'corpus_animals_0.6_troyercateg.svg',bbox=(1024,1024),vertex_color=['white' if l not in shared_categ else known_colors.keys()[shared_categ[l]+15] for l in corpus.vs['label']]
    ,layout=corpus.layout('kk'))  
    '''
    words_w_pos.append('animal:N')
    words_w_pos.append('organism:N')
    
    nouns = [i for i in learner._learned_lexicon.words() if i[-2:]==':N']
    
    g = WordsGraph(20,0.6,'hub-categories-prob-random',0,0.00001,20,0,1,'map')
    #final = g.create_final_graph(words_w_pos,learner._learned_lexicon,8500,'COS')
    '''
    gold = g.create_final_graph(words_w_pos,learner._gold_lexicon,8500,'COS')#,words_to_compare=learner._learned_lexicon.words())
    
    plot(gold,'gold_animals_0.6_clusters_animal.svg',bbox=(1024,1024),vertex_color=[color_list[x] for x in gold.clusters().membership],layout=gold.layout('fr',weights=rescale(gold.es['distance'],out_range=(0.1,0))),edge_width=rescale([1-i for i in gold.es['distance']],out_range=(0.5,3)))
    
    plot(gold,'gold_animals_0.6_troyercateg_animal.svg',bbox=(1024,1024),vertex_color=['white' if l not in shared_categ else known_colors.keys()[shared_categ[l]+15] for l in gold.vs['label']]
   ,layout=gold.layout('fr',weights=rescale(gold.es['distance'],out_range=(0.1,0))),edge_width=rescale([1-i for i in gold.es['distance']],out_range=(0.5,3)))    
    
    learned = g.create_final_graph(words_w_pos,learner._learned_lexicon,8500,'COS')
    
    plot(learned,'learned_animals_0.6_clusters_animal.svg',bbox=(1024,1024),vertex_color=[color_list[x] for x in learned.clusters().membership],layout=learned.layout('fr',weights=rescale(learned.es['distance'],out_range=(0.1,0))),edge_width=rescale([1-i for i in learned.es['distance']],out_range=(0.5,3)))
    
    plot(learned,'learned_animals_0.6_troyercateg_animal.svg',bbox=(1024,1024),vertex_color=['white' if l not in shared_categ else known_colors.keys()[shared_categ[l]+15] for l in learned.vs['label']]
    ,layout=learned.layout('fr',weights=rescale(learned.es['distance'],out_range=(0.1,0))),edge_width=rescale([1-i for i in learned.es['distance']],out_range=(0.5,3)))
    
    ###compare with all nouns
    gold_compare_nouns = g.create_final_graph(words_w_pos,learner._gold_lexicon,8500,'COS',words_to_compare=nouns)
    
    plot(gold_compare_nouns,'gold_compare_nouns_animals_0.6_clusters_animal.svg',bbox=(1024,1024),vertex_color=[color_list[x] for x in gold_compare_nouns.clusters().membership],layout=gold_compare_nouns.layout('fr',weights=rescale(gold_compare_nouns.es['distance'],out_range=(0.1,0))),edge_width=rescale([1-i for i in gold_compare_nouns.es['distance']],out_range=(0.5,3)))
    
    plot(gold_compare_nouns,'gold_compare_nouns_animals_0.6_troyercateg_animal.svg',bbox=(1024,1024),vertex_color=['white' if l not in shared_categ else known_colors.keys()[shared_categ[l]+15] for l in gold_compare_nouns.vs['label']]
   ,layout=gold_compare_nouns.layout('fr',weights=rescale(gold_compare_nouns.es['distance'],out_range=(0.1,0))),edge_width=rescale([1-i for i in gold_compare_nouns.es['distance']],out_range=(0.5,3)))    
    '''
    learned_compare_nouns = g.create_final_graph(words_w_pos,learner._learned_lexicon,8500,'COS',words_to_compare=nouns)
    
    plot(learned_compare_nouns,'learned_compare_nouns_animals_0.6_clusters_animal.svg',bbox=(4096,4096),vertex_color=[color_list[x] for x in learned_compare_nouns.clusters().membership],layout=learned_compare_nouns.layout('fr',weights=rescale(learned_compare_nouns.es['distance'],out_range=(0.1,0))),edge_width=rescale([1-i for i in learned_compare_nouns.es['distance']],out_range=(0.5,3)))
    
    plot(learned_compare_nouns,'learned_compare_nouns_animals_0.6_troyercateg_animal.svg',bbox=(4096,4096),vertex_color=['white' if l not in shared_categ else known_colors.keys()[shared_categ[l]+15] for l in learned_compare_nouns.vs['label']]
    ,layout=learned_compare_nouns.layout('fr',weights=rescale(learned_compare_nouns.es['distance'],out_range=(0.1,0))),edge_width=rescale([1-i for i in learned_compare_nouns.es['distance']],out_range=(0.5,3)))    
    
    '''
    gold_nouns = g.create_final_graph(nouns,learner._gold_lexicon,8500,'COS')
    
    plot(gold_nouns,'gold_nouns_0.6_clusters.svg',bbox=(1024,1024),vertex_color=[color_list[x] for x in gold_nouns.clusters().membership],layout=gold.layout('fr',weights=rescale(gold.es['distance'],out_range=(0.1,0))),edge_width=rescale([1-i for i in gold.es['distance']],out_range=(0.5,3)))
    
    plot(gold_nouns,'gold_nouns_0.6_troyercateg.svg',bbox=(1024,1024),vertex_color=['white' if l not in shared_categ else known_colors.keys()[shared_categ[l]+15] for l in gold_nouns.vs['label']]
    ,layout=gold.layout('fr',weights=rescale(gold.es['distance'],out_range=(0.1,0))),edge_width=rescale([1-i for i in gold.es['distance']],out_range=(0.5,3)))    
    
    learned_nouns = g.create_final_graph(nouns,learner._learned_lexicon,8500,'COS')
    
    plot(learned_nouns,'learned_nouns_0.6_clusters.svg',bbox=(1024,1024),vertex_color=[color_list[x] for x in learned_nouns.clusters().membership],layout=gold.layout('fr',weights=rescale(gold.es['distance'],out_range=(0.1,0))),edge_width=rescale([1-i for i in gold.es['distance']],out_range=(0.5,3)))
    
    plot(learned_nouns,'learned_nouns_0.6_troyercateg.svg',bbox=(1024,1024),vertex_color=['white' if l not in shared_categ else known_colors.keys()[shared_categ[l]+15] for l in learned_nouns.vs['label']]
    ,layout=gold.layout('fr',weights=rescale(gold.es['distance'],out_range=(0.1,0))),edge_width=rescale([1-i for i in gold.es['distance']],out_range=(0.5,3)))  
    
    
    
    g = WordsGraph(20,0.7,'hub-categories-prob-random',0,0.00001,20,0,1,'map')
    #final = g.create_final_graph(words_w_pos,learner._learned_lexicon,8500,'COS')
    final = g.create_final_graph(words_w_pos,learner._learned_lexicon,8500,'COS')#,words_to_compare=learner._learned_lexicon.words())
    
    plot(final,'final_animals_0.7_clusters_animal.svg',bbox=(1024,1024),vertex_color=[color_list[x] for x in final.clusters().membership],layout=final.layout('kk'))
    
    plot(final,'final_animals_0.7_troyercateg_animal.svg',bbox=(1024,1024),vertex_color=['white' if l not in shared_categ else known_colors.keys()[shared_categ[l]+15] for l in final.vs['label']]
    ,layout=final.layout('kk'))  '''  
    '''
    plot(final,'final_animals_0.7_clusters.svg',bbox=(1024,1024),vertex_color=[color_list[x] for x in final.clusters().membership],layout=final.layout('kk'))
    
    
    plot(final,'final_animals_0.7_troyercateg.svg',bbox=(1024,1024),vertex_color=['white' if l not in shared_categ else known_colors.keys()[shared_categ[l]+15] for l in final.vs['label']]
,layout=final.layout('kk'))
    
    corpus = g.create_final_graph(words_w_pos,learner._gold_lexicon,8500,'COS')
    
    plot(corpus,'corpus_animals_0.7.svg',bbox=(1024,1024),vertex_color=[color_list[x] for x in corpus.clusters().membership],layout=corpus.layout('kk'))
    plot(corpus,'corpus_animals_0.7_troyercateg.svg',bbox=(1024,1024),vertex_color=['white' if l not in shared_categ else known_colors.keys()[shared_categ[l]+15] for l in corpus.vs['label']]
    ,layout=corpus.layout('kk'))    '''  


    
    '''for n in final.vs['label']:
        if n in ANIMAL_CATEG_NUM_POS:
            if TEST == None:
                TEST = []
            else:
                TEST.append(n)    
    
    for n in final.vs['label']:
        if n in ANIMAL_CATEG_NUM_POS:
            if TEST2 == None:
                TEST2 = {}
            else:
                TEST2[n]=ANIMAL_CATEG_NUM_POS[n]'''
    