from rw import *
from omega import *
from clustering import *
from adj_rand import *
from tabulate import tabulate
import tabulate as T
from sklearn.linear_model import LogisticRegression
from graph_transforms import *

from sklearn.metrics import f1_score
from itertools import *


del(T.LATEX_ESCAPE_RULES[u'$'])
del(T.LATEX_ESCAPE_RULES[u'\\'])
#del(T.LATEX_ESCAPE_RULES[u'_'])
del(T.LATEX_ESCAPE_RULES[u'}'])
del(T.LATEX_ESCAPE_RULES[u'{'])


def plot_graph_stats(graphs,method,label='',folder='',splitter=':',which=1,use_saved_irt=True):
    '''For each graph, apply method, and plot the number return by method corresponding to the value for tau_animal (asim) and tau (sim).
    If method is a string and not a function call, attend to load from file the parameter named by method in folder.
    
    If use_saved_irt, get the irt level that has been precalculated for that graph; otherwise, run a random walk and calculate the IRT level de novo.
    '''
    if type(method) is str:
        stats = get_graph_stats_from_file(graphs,method,folder,splitter,which)
    else:
        stats = get_graph_stats(graphs, method)
        
    if not use_saved_irt:
        irts = get_irt_class(graphs)
        
    sim_all = []
    asim_all = []
    v = []
    color = []
    for k in graphs:
        parts = k.split('_')
        
        asim = float(parts[-1][1:])
        sim = float(parts[-2])             

        sim_all.append(sim)
        asim_all.append(asim)
        v.append(stats[k])
        
        
        if use_saved_irt:
            irt_level = get_saved_irts(k)[k]
        else:
            irt_level = irts[k]
        
        color.append('black' if irt_level == 2 else 'yellow' if irt_level == 1 else 'white')                 

    plot_scatter(asim,sim,v,'animal sim','non-animal sim',label,color=color)    

def get_irt_class(graphs):
    '''For each graph in graphs, run a random walk and determine the IRT level it meets. See has_irt_pattern in rw.py.'''
    new= {}
    for n in graphs:
        if random_walk_possible(graphs[n]):
            #print n
            graph = graphs[n]
            
            graph = get_cluster(graph,'animal:N')#,graph)
            
            #print( n, get_walk_length(n))
            
            a,b,cat,title,f_p,f_c = random_walk_trial(graph,n,True,get_walk_length(n),False)
            #plot_irt(a,b,cat,title)
            #print a        
            b_f,b_s = irt_self_longterm_avg(b,cat,multi=True)
            #print has_irt_pattern(b,b_f,b_s)
            new[n] = 2 if has_irt_pattern(b,b_f,b_s) else 1 if has_irt_pattern(b,b_f,b_s,weak=True) else 0    
    return new


def get_graph_stats(graphs,method):
    '''For each graph in graphs, apply and store some transform specified by function call method.'''
    new = {}
    for k in graphs:
        if random_walk_possible(graphs[k]):
            graph = get_cluster(graphs[k],'animal:N')
            new[k] = method( graph )
    return new


def get_graph_stats_from_file(graphs,stat,folder,splitter=':',which=1):
    '''For each graph in graphs, search files for statistic stat and return its value.
    Folder specifies where to look.'''
    new = {}
    
    for n in graphs:
        
        if folder == 'omg/':
            fname = folder + n +'.txt'
        elif folder == 'swc_latest/':
            fname = folder + n + '.graphml.txt'
            
        try:
            with open(fname) as f:
                lines = f.readlines()
                occurence = 1
                for line in lines:
                    if stat in line:
                        if occurence == which:
                            # N.B.: splitter should be ' ' for swness
                            number = line.split(splitter)[1].strip()
                            new[n] = float( number.split(' ')[0] )
                            break
                        else:
                            occurence += 1
        except IOError as e:
            print e
    
    return new


def parse_dicts(d):
    '''Make a nested dictionary with 3 levels: base name, tau, tau_animal for the graphs in d.'''
    new = {}
    
    names = ['learner','gold','BEAGLE','learner_af_24']
    
    for k in d:
        parts = k.split('_')
        
        asim = float(parts[-1][1:])
        sim = float(parts[-2])        
        name = max([x for x in names if x in k], key=len)
        
        if name not in new: new[name] = {} 
        if sim not in new[name]: new[name][sim] = {} 
        if sim not in new[name][sim]: new[name][sim][asim] = {} 
        
        new[name][sim][asim] = d[k]
        
    return new


def get_models_named(names=None,like=None,a_filter=True):
    '''Get graphs from file. If names is a list of names, get those specified graphs. If like is a string, get all graphs that have that as a substring in their names. a_filter specifies whether to filter out non-animal words.'''
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
            g = Graph()
            
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


def get_saved_irts(like):
    if 'animals_learner_af_0' in like.lower():
        return {'animals_learner_af_0.6_A0.5': 0, 'animals_learner_af_0.6_A0.4': 0, 'animals_learner_af_0.6_A0.7': 0, 'animals_learner_af_0.85_A0.4': 0, 'animals_learner_af_0.5_A0.85': 0, 'animals_learner_af_0.8_A0.6': 0, 'animals_learner_af_0.8_A0.5': 2, 'animals_learner_af_0.8_A0.4': 2, 'animals_learner_af_0.6_A0.85': 0, 'animals_learner_af_0.85_A0.7': 0, 'animals_learner_af_0.85_A0.6': 0, 'animals_learner_af_0.85_A0.5': 2, 'animals_learner_af_0.6_A0.6': 0, 'animals_learner_af_0.6_A0.8': 0, 'animals_learner_af_0.7_A0.85': 0, 'animals_learner_af_0.8_A0.7': 2, 'animals_learner_af_0.4_A0.4': 0, 'animals_learner_af_0.7_A0.8': 0, 'animals_learner_af_0.5_A0.8': 0, 'animals_learner_af_0.5_A0.4': 0, 'animals_learner_af_0.5_A0.5': 0, 'animals_learner_af_0.5_A0.6': 0, 'animals_learner_af_0.5_A0.7': 0, 'animals_learner_af_0.7_A0.6': 0, 'animals_learner_af_0.7_A0.7': 0, 'animals_learner_af_0.7_A0.4': 1, 'animals_learner_af_0.7_A0.5': 1}
    elif 'animals_learner_af_2' in like.lower():
        return {'animals_learner_af_24000_24000_0.6_A0.85': 0, 'animals_learner_af_24000_24000_0.7_A0.6': 0, 'animals_learner_af_24000_24000_0.7_A0.7': 0, 'animals_learner_af_24000_24000_0.7_A0.5': 1, 'animals_learner_af_24000_24000_0.7_A0.8': 0, 'animals_learner_af_24000_0.4_A0.5': 0, 'animals_learner_af_24000_24000_0.5_A0.85': 0, 'animals_learner_af_24000_0.85_A0.4': 2, 'animals_learner_af_24000_0.4_A0.8': 0, 'animals_learner_af_24000_24000_0.6_A0.7': 0, 'animals_learner_af_24000_24000_0.6_A0.6': 0, 'animals_learner_af_24000_0.6_A0.8': 0, 'animals_learner_af_24000_0.6_A0.6': 0, 'animals_learner_af_24000_0.6_A0.7': 0, 'animals_learner_af_24000_0.6_A0.4': 0, 'animals_learner_af_24000_0.6_A0.5': 0, 'animals_learner_af_24000_0.4_A0.4': 0, 'animals_learner_af_24000_24000_0.6_A0.8': 0, 'animals_learner_af_24000_0.4_A0.6': 0, 'animals_learner_af_24000_0.4_A0.7': 0, 'animals_learner_af_24000_0.7_A0.5': 0, 'animals_learner_af_24000_24000_0.8_A0.7': 2, 'animals_learner_af_24000_24000_0.8_A0.6': 0, 'animals_learner_af_24000_24000_0.8_A0.5': 0, 'animals_learner_af_24000_0.7_A0.4': 1, 'animals_learner_af_24000_24000_0.85_A0.7': 0, 'animals_learner_af_24000_24000_0.85_A0.6': 0, 'animals_learner_af_24000_24000_0.85_A0.5': 0, 'animals_learner_af_24000_0.7_A0.85': 0, 'animals_learner_af_24000_0.7_A0.7': 0, 'animals_learner_af_24000_24000_0.6_A0.5': 0, 'animals_learner_af_24000_0.6_A0.85': 0, 'animals_learner_af_24000_0.7_A0.6': 0, 'animals_learner_af_24000_0.7_A0.8': 0, 'animals_learner_af_24000_0.8_A0.4': 0, 'animals_learner_af_24000_0.8_A0.5': 0, 'animals_learner_af_24000_0.8_A0.6': 0, 'animals_learner_af_24000_0.8_A0.7': 2, 'animals_learner_af_24000_0.4_A0.85': 0, 'animals_learner_af_24000_0.85_A0.6': 0, 'animals_learner_af_24000_0.85_A0.7': 0, 'animals_learner_af_24000_24000_0.7_A0.85': 0, 'animals_learner_af_24000_0.85_A0.5': 0, 'animals_learner_af_24000_0.5_A0.7': 0, 'animals_learner_af_24000_0.5_A0.6': 0, 'animals_learner_af_24000_0.5_A0.5': 0, 'animals_learner_af_24000_0.5_A0.4': 0, 'animals_learner_af_24000_24000_0.5_A0.8': 0, 'animals_learner_af_24000_24000_0.5_A0.5': 0, 'animals_learner_af_24000_24000_0.5_A0.6': 0, 'animals_learner_af_24000_24000_0.5_A0.7': 0, 'animals_learner_af_24000_0.5_A0.8': 0, 'animals_learner_af_24000_0.5_A0.85': 0}

    elif 'gold_af' in like.lower():
        return {'gold_af_HILLS_SHARED_0.75_A0.45': 0, 'gold_af_HILLS_SHARED_LEARNED_0.8_0.97_A0.4': 0, 'gold_af_HILLS_SHARED_0.96_A0.4': 0, 'gold_af_HILLS_SHARED_0.55_A0.65': 0, 'gold_af_HILLS_SHARED_LEARNED_0.8_0.7_A0.4': 0, 'gold_af_HILLS_SHARED_0.6_A0.45': 0, 'gold_af_HILLS_SHARED_0.55_A0.75': 0, 'gold_af_HILLS_SHARED_LEARNED_0.8_0.96_A0.4': 0, 'gold_af_HILLS_SHARED_0.7_A0.75': 0, 'gold_af_HILLS_SHARED_LEARNED_0.8_0.99_A0.4': 0, 'gold_af_HILLS_SHARED_0.85_A0.55': 2, 'gold_af_HILLS_SHARED_0.75_A0.55': 0, 'gold_af_HILLS_SHARED_0.99_A0.4': 0, 'gold_af_HILLS_SHARED_0.6_A0.55': 0, 'gold_af_HILLS_SHARED_LEARNED_0.8_0.95_A0.4': 0, 'gold_af_HILLS_SHARED_0.65_A0.5': 0, 'gold_af_HILLS_SHARED_0.65_A0.4': 0, 'gold_af_HILLS_SHARED_0.65_A0.7': 0, 'gold_af_HILLS_SHARED_0.65_A0.6': 0, 'gold_af_HILLS_SHARED_0.55_A0.6': 0, 'gold_af_HILLS_SHARED_0.55_A0.7': 0, 'gold_af_HILLS_SHARED_0.55_A0.4': 0, 'gold_af_HILLS_SHARED_0.55_A0.5': 0, 'gold_af_HILLS_SHARED_0.8_A0.65': 0, 'gold_af_HILLS_SHARED_0.7_A0.65': 0, 'gold_af_HILLS_SHARED_0.85_A0.45': 2, 'gold_af_HILLS_SHARED_0.65_A0.65': 0, 'gold_af_HILLS_SHARED_0.8_A0.75': 0, 'gold_af_HILLS_SHARED_0.6_A0.65': 0, 'gold_af_HILLS_SHARED_0.999_A0.4': 0, 'gold_af_HILLS_SHARED_0.7_A0.55': 0, 'gold_af_HILLS_SHARED_0.85_A0.75': 0, 'gold_af_HILLS_SHARED_0.97_A0.4': 0, 'gold_af_HILLS_SHARED_0.82_A0.65': 2, 'gold_af_HILLS_SHARED_0.7_A0.7': 0, 'gold_af_HILLS_SHARED_0.8_A0.45': 0, 'gold_af_HILLS_SHARED_0.6_A0.75': 0, 'gold_af_HILLS_SHARED_LEARNED_0.8_0.8_A0.4': 1, 'gold_af_HILLS_SHARED_LEARNED_0.8_0.999_A0.4': 0, 'gold_af_HILLS_SHARED_0.85_A0.65': 0, 'gold_af_HILLS_SHARED_0.6_A0.5': 0, 'gold_af_HILLS_SHARED_0.6_A0.4': 0, 'gold_af_HILLS_SHARED_0.6_A0.7': 0, 'gold_af_HILLS_SHARED_0.6_A0.6': 0, 'gold_af_HILLS_SHARED_0.7_A0.45': 0, 'gold_af_HILLS_SHARED_0.9_A0.55': 0, 'gold_af_HILLS_SHARED_0.95_A0.6': 0, 'gold_af_HILLS_SHARED_0.95_A0.7': 0, 'gold_af_HILLS_SHARED_0.9_A0.6': 0, 'gold_af_HILLS_SHARED_0.95_A0.5': 0, 'gold_af_HILLS_SHARED_0.8_A0.6': 0, 'gold_af_HILLS_SHARED_LEARNED_0.8_0.85_A0.4': 0, 'gold_af_HILLS_SHARED_0.8_A0.55': 1, 'gold_af_HILLS_SHARED_LEARNED_0.8_0.98_A0.4': 0, 'gold_af_HILLS_SHARED_LEARNED_0.8_0.9_A0.4': 1, 'gold_af_HILLS_SHARED_0.65_A0.55': 0, 'gold_af_HILLS_SHARED_0.85_A0.7': 2, 'gold_af_HILLS_SHARED_0.85_A0.6': 2, 'gold_af_HILLS_SHARED_0.85_A0.5': 2, 'gold_af_HILLS_SHARED_0.85_A0.4': 2, 'gold_af_HILLS_SHARED_LEARNED_0.8_0.88_A0.4': 0, 'gold_af_HILLS_SHARED_0.95_A0.45': 0, 'gold_af_HILLS_SHARED_LEARNED_0.8_0.55_A0.4': 0, 'gold_af_HILLS_SHARED_0.9_A0.45': 0, 'gold_af_HILLS_SHARED_0.95_A0.55': 0, 'gold_af_HILLS_SHARED_0.9_A0.4': 1, 'gold_af_HILLS_SHARED_0.65_A0.75': 0, 'gold_af_HILLS_SHARED_0.9_A0.5': 0, 'gold_af_HILLS_SHARED_0.8_A0.7': 0, 'gold_af_HILLS_SHARED_0.95_A0.4': 0, 'gold_af_HILLS_SHARED_0.8_A0.5': 1, 'gold_af_HILLS_SHARED_0.8_A0.4': 1, 'gold_af_HILLS_SHARED_0.9_A0.7': 0, 'gold_af_HILLS_SHARED_0.98_A0.4': 0, 'gold_af_HILLS_SHARED_0.75_A0.65': 0, 'gold_af_HILLS_SHARED_0.65_A0.45': 0, 'gold_af_HILLS_SHARED_0.95_A0.65': 0, 'gold_af_HILLS_SHARED_0.9_A0.75': 0, 'gold_af_HILLS_SHARED_0.55_A0.45': 0, 'gold_af_HILLS_SHARED_0.75_A0.4': 0, 'gold_af_HILLS_SHARED_0.75_A0.5': 0, 'gold_af_HILLS_SHARED_0.75_A0.6': 0, 'gold_af_HILLS_SHARED_0.75_A0.7': 1, 'gold_af_HILLS_SHARED_0.7_A0.6': 0, 'gold_af_HILLS_SHARED_0.88_A0.4': 2, 'gold_af_HILLS_SHARED_0.7_A0.4': 0, 'gold_af_HILLS_SHARED_0.7_A0.5': 0, 'gold_af_HILLS_SHARED_LEARNED_0.8_0.6_A0.4': 0, 'gold_af_HILLS_SHARED_0.75_A0.75': 0, 'gold_af_HILLS_SHARED_0.55_A0.55': 0, 'gold_af_HILLS_SHARED_0.9_A0.65': 1, 'gold_af_HILLS_SHARED_0.95_A0.75': 0}
    elif 'beagle_h' in like.lower():
        return {'BEAGLE_HILLS_SHARED_0.75_A0.5': 0, 'BEAGLE_HILLS_SHARED_0.75_A0.4': 0, 'BEAGLE_HILLS_SHARED_0.4_A0.55': 0, 'BEAGLE_HILLS_SHARED_0.8_A0.45': 0, 'BEAGLE_HILLS_SHARED_0.5_A0.6': 0, 'BEAGLE_HILLS_SHARED_0.5_A0.5': 0, 'BEAGLE_HILLS_SHARED_0.5_A0.4': 1, 'BEAGLE_HILLS_SHARED_0.35_A0.55': 0, 'BEAGLE_HILLS_SHARED_0.65_A0.35': 0, 'BEAGLE_HILLS_SHARED_0.45_A0.45': 0, 'BEAGLE_HILLS_SHARED_0.45_A0.5': 0, 'BEAGLE_HILLS_SHARED_0.7_A0.5': 0, 'BEAGLE_HILLS_SHARED_0.55_A0.35': 0, 'BEAGLE_HILLS_SHARED_0.6_A0.55': 0, 'BEAGLE_HILLS_SHARED_0.75_A0.6': 0, 'BEAGLE_HILLS_SHARED_0.4_A0.35': 0, 'BEAGLE_HILLS_SHARED_0.6_A0.35': 0, 'BEAGLE_HILLS_SHARED_0.3_A0.5': 0, 'BEAGLE_HILLS_SHARED_0.3_A0.4': 0, 'BEAGLE_HILLS_SHARED_0.35_A0.35': 0, 'BEAGLE_HILLS_SHARED_0.3_A0.6': 0, 'BEAGLE_HILLS_SHARED_0.55_A0.45': 0, 'BEAGLE_HILLS_SHARED_0.4_A0.6': 0, 'BEAGLE_HILLS_SHARED_0.3_A0.55': 0, 'BEAGLE_HILLS_SHARED_0.65_A0.4': 0, 'BEAGLE_HILLS_SHARED_0.65_A0.5': 0, 'BEAGLE_HILLS_SHARED_0.65_A0.6': 0, 'BEAGLE_HILLS_SHARED_0.55_A0.6': 0, 'BEAGLE_HILLS_SHARED_0.55_A0.5': 0, 'BEAGLE_HILLS_SHARED_0.55_A0.4': 0, 'BEAGLE_HILLS_SHARED_0.55_A0.55': 0, 'BEAGLE_HILLS_SHARED_0.3_A0.35': 0, 'BEAGLE_HILLS_SHARED_0.65_A0.55': 0, 'BEAGLE_HILLS_SHARED_0.35_A0.5': 0, 'BEAGLE_HILLS_SHARED_0.35_A0.4': 0, 'BEAGLE_HILLS_SHARED_0.35_A0.6': 0, 'BEAGLE_HILLS_SHARED_0.4_A0.45': 0, 'BEAGLE_HILLS_SHARED_0.8_A0.35': 0, 'BEAGLE_HILLS_SHARED_0.8_A0.55': 0, 'BEAGLE_HILLS_SHARED_0.7_A0.4': 0, 'BEAGLE_HILLS_SHARED_0.35_A0.45': 0, 'BEAGLE_HILLS_SHARED_0.6_A0.6': 0, 'BEAGLE_HILLS_SHARED_0.6_A0.4': 0, 'BEAGLE_HILLS_SHARED_0.45_A0.35': 0, 'BEAGLE_HILLS_SHARED_0.65_A0.45': 0, 'BEAGLE_HILLS_SHARED_0.45_A0.6': 0, 'BEAGLE_HILLS_SHARED_0.45_A0.4': 0, 'BEAGLE_HILLS_SHARED_0.5_A0.45': 0, 'BEAGLE_HILLS_SHARED_0.6_A0.5': 0, 'BEAGLE_HILLS_SHARED_0.75_A0.35': 0, 'BEAGLE_HILLS_SHARED_0.6_A0.45': 0, 'BEAGLE_HILLS_SHARED_0.4_A0.5': 0, 'BEAGLE_HILLS_SHARED_0.4_A0.4': 0, 'BEAGLE_HILLS_SHARED_0.7_A0.35': 0, 'BEAGLE_HILLS_SHARED_0.5_A0.55': 1, 'BEAGLE_HILLS_SHARED_0.7_A0.6': 0, 'BEAGLE_HILLS_SHARED_0.75_A0.55': 0, 'BEAGLE_HILLS_SHARED_0.3_A0.45': 0, 'BEAGLE_HILLS_SHARED_0.5_A0.35': 1, 'BEAGLE_HILLS_SHARED_0.45_A0.55': 0, 'BEAGLE_HILLS_SHARED_0.8_A0.4': 0, 'BEAGLE_HILLS_SHARED_0.8_A0.5': 0, 'BEAGLE_HILLS_SHARED_0.8_A0.6': 0, 'BEAGLE_HILLS_SHARED_0.7_A0.45': 0, 'BEAGLE_HILLS_SHARED_0.7_A0.55': 0, 'BEAGLE_HILLS_SHARED_0.75_A0.45': 0}

if __name__ == "__main__":
    m = ['gold_af_HILLS_SHARED_0','BEAGLE_H','animals_learner_af_0','animals_learner_af_2']
    latex = []
    tables = []
    #m = ['gold_af_HILLS_SHARED_0']
    
    #irtss = []
            
    for n in m:
        
        graphs = get_models(like=n)
        
        #irts = get_irt_class(graphs)
        #irtss.append(irts)
        irts = get_saved_irts(n)
        '''
        L = get_graph_stats_from_file(graphs,'l','omg/')
        Lambda = get_graph_stats_from_file(graphs,'lratio','omg/')
        CC = get_graph_stats_from_file(graphs,'c','omg/')
        gamma = get_graph_stats_from_file(graphs,'cratio','omg/')
        omega = get_graph_stats_from_file(graphs,'omega','omg/')
        '''
        L2 = get_graph_stats_from_file(graphs,'l','omg/')
        CC2 = get_graph_stats_from_file(graphs,'c','omg/')        
        omega = get_graph_stats_from_file(graphs,'omega','omg/')
        gamma_lat = get_graph_stats_from_file(graphs,'cratio','omg/')
        
        
        L = get_graph_stats_from_file(graphs,'avg distance in LCC','swc_latest/')
        CC = get_graph_stats_from_file(graphs,'avg local clustering coefficient','swc_latest/')        
        L_rand = get_graph_stats_from_file(graphs,'avg distance in LCC','swc_latest/',which=2)
        CC_rand = get_graph_stats_from_file(graphs,'avg local clustering coefficient','swc_latest/',which=2)        
        
        gamma = {k:0 if CC_rand[k] == 0 else CC[k]/CC_rand[k] for k in CC}
        Lambda = {k:0 if L_rand[k] == 0 else L[k]/L_rand[k] for k in L}

        sparsity = get_graph_stats_from_file(graphs,'sparsity','swc_latest/')
        sigma = get_graph_stats_from_file(graphs,'small-worldness','swc_latest/',' ')        
                
        rand_idx = get_graph_stats(graphs,get_hdbscan_adj_rand_idx)
        w_fscore = get_graph_stats(graphs,get_hdbscan_fscore)
        fscore = get_graph_stats(graphs,get_hdbscan_fscore_unweighted)
        w_fscore_n = get_graph_stats(graphs,get_hdbscan_fscore_all)
        fscore_n = get_graph_stats(graphs,get_hdbscan_fscore_unweighted_all)        
        
        V = get_graph_stats_from_file(graphs,'number of nodes in LLC','swc_latest/')
        E = get_graph_stats_from_file(graphs,'number of edges in LLC','swc_latest/')
        
        #print tabulate(
        headers = ["Name",
                   "$\|V\|$",
                   "$\|E\|$",
                   "L",
                   #"PL2", ##different for some reason
                   '$\lambda$',
                   "CC",
                   #'CC2',
                   '$\gamma$',
                   #r"$\gamma_{lat}$",
                   "Sparsity",
                   r"$\sigma$",
                   #r"$\omega$",
                   "Adj Rand",
                   "Wgt F-score (unique)",
                   "F-score (unique)",
                   "Wgt F-score",                   
                   "F-score",                   
                   'Clusters (HDBSCAN)',
                   'Clusters (del animal)',
                   'S',
                   'IRT']
        
        table = []
        order = graphs.keys()
        order.sort()
        for k in order:
            
            #graphs[k] = get_cluster(graphs[k],'animal:N')
            
            irt = irts.get(k,None)
            colored_name = k
            if (irt == None) or get_cluster(graphs[k],'animal:N').vcount() <= 30:
                colored_name = '\\rowcolor{gray}' + colored_name
            elif irt == 2:
                colored_name = '\\rowcolor{green}' + colored_name
            elif irt == 1:
                colored_name = '\\rowcolor{yellow}' + colored_name

            
            a,s = clusters_animals(graphs[k])
            try:
                hdbscan_clusters = np.max(fit_hdbscan(graphs[k]).labels_) + 1
            except Exception:
                hdbscan_clusters = -1
                
            row = [colored_name,
                   V.get(k, ''),
                   #get_cluster(graphs[k],'animal:N').vcount(),
                   E.get(k, ''),
                   #get_cluster(graphs[k],'animal:N').ecount(),
                   L.get(k,''),
                   #L2.get(k,''), ### comparison
                   Lambda.get(k,''),
                   CC.get(k,''),
                   #CC2.get(k,''), ## comparison
                   gamma.get(k,''),
                   #gamma_lat.get(k,''),
                   sparsity.get(k, ''),
                   sigma.get(k, 0), #does this make sense??
                   #omega.get(k,''),
                   str(rand_idx.get(k,''))[:4],
                   str(w_fscore.get(k,''))[:4],
                   str(fscore.get(k,''))[:4],
                   str(w_fscore_n.get(k,''))[:4],
                   str(fscore_n.get(k,''))[:4],                   
                   str(hdbscan_clusters),
                   str(a),
                   str(s),
                   #str(single_a.get(k,'')),
                   irt]
            
            table.append(row)
            tables.append(row)
            
        latex.append( '\\noindent\\adjustbox{max width=\\textwidth,max height=\\textheight,keepaspectratio}{'+ tabulate(table,headers=headers,tablefmt='latex') +'}' )
        
    print '\n'.join(latex)
    
    h = np.array(tables)
    
    header = headers[1:-1]
    h_names = h[ np.float32(h[:,1]) > 30]
    names = h_names[:,0]
    
    #h_names = h_names[ [True if 'gold' in name else False  for name in names],: ]
    h = np.float32(h_names[:,1:])
    
    l = LogisticRegression()
    l.fit(h[:,:-1], binarize(h[:,-1]))
    
    f = l.coef_.copy()

    irt2 = l.predict(h[:,:-1])
    print '\n'.join([str(dd) for dd in zip(irt2.tolist(),h[:,-1])])
    print '\n'.join([str(['%.3f' % qq for qq in dd]) for dd in f.tolist()])
    print l.score(h[:,:-1], binarize(h[:,-1]))
    
    all_rows = [i for i in xrange(len(header))]
    
    #tests = [[i] for i in xrange(len(headers)-1)]
    
    
    tests = list(combinations(all_rows,1))
    [tests.extend(list(combinations(all_rows,qq))) for qq in xrange(2,len(header))]
    
    
    for rows in tests:
        c = LogisticRegression()
        #rows = [2,3,4,5,6,7,8,9,10]
        right = binarize(h[:,-1])
        c.fit(h[:,rows],right)
        irt3 = c.predict(h[:,rows])
        #print '\n'.join([str(dd) for dd in zip(irt3.tolist(),h[:,-1])])
        #if 1.0 * np.count_nonzero(irt3[right > 0]) / np.count_nonzero(right) >= 0.78:
        if c.score(h[:,rows],right) > 0.93 or [header[j] for j in rows] == ['$\\|E\\|$', 'L', '$\\gamma$', 'Clusters (del animal)', 'S']:

            print [header[j] for j in rows]
            
            #for fdjh in zip(names[np.where(np.logical_xor(right,irt3))], right[np.where(np.logical_xor(right,irt3))]):
             #   print fdjh
            print c.coef_
            print 'classification accuracy: ' + str(c.score(h[:,rows],right))
            print 'true positives:          ' + str(1.0 * np.count_nonzero(irt3[right > 0]) / np.count_nonzero(right))
            print 'fscore:                  ' + str(f1_score(right, irt3))