import os,sys
p = os.path.abspath('../')
# next line adds the directory to a path which "imports" searches for files.
# Alternatively, this path could be added to PYTHONPATH.
sys.path.append(p) 
os.chdir('../')

from numpy.random import seed,choice
import random
from core.graph_tool_igraph import *
from itertools import groupby
from animals import *
import pylab,scipy,numpy
from generate_animal_graphs import *

##functions adapted from https://github.com/AusterweilLab/randomwalk
def random_walk(g,start=None,seed=None,weighted=False,stop=None,restart=0):
    #seed(seed)
    
    if type(start) == str:
        try:
            start = g.vs.find(label=start).index
        except Exception as e:
            #pass
    #if start is None:
            start=random.choice(range(g.vcount()))
        
    assert type(start) == int

    walk=[]
    unused_nodes=set(range(g.vcount()))    
    unused_nodes.remove(start)
    s = start
    count = 0
    while len(unused_nodes) > 0:
        _p=start
        if weighted==False:
            start=choice(g.neighbors(start)) # follow random edge
        else:
            neighboring_edges = [g.get_eid(start,n) for n in g.neighbors(start)]
            distances = g.es[neighboring_edges]['distance']
            weights = [1-i for i in distances]
            total = sum(weights)
            normalized_weights = [w/total for w in weights]
            
            start=choice(g.neighbors(start),p=normalized_weights)
            
        walk.append((_p,start))
        if start in unused_nodes:
            unused_nodes.remove(start)
            #if restart:
                #if numpy.random.binomial(1,0.05):
                    #start = s           
        if restart:
            if numpy.random.binomial(1,restart):
                start = s 
        if stop:
            if count >= stop:
                break

        
        count +=1
        
            
    return walk

# generates fake IRTs from # of steps in a random walk, using gamma distribution
def stepsToIRT(irts, beta=1, seed=None):
    np.random.seed(seed)
    new_irts=[]
    for irtlist in irts:
        newlist=[np.random.gamma(irt, beta) for irt in irtlist]
        new_irts.append(newlist)
    return new_irts

# first hitting times for each node
def firstHits(walk):
    firsthit=[]
    path=path_from_walk(walk)
    for i in observed_walk(walk):
        firsthit.append(path.index(i))
    return zip(observed_walk(walk),firsthit)

# Unique nodes in random walk preserving order
# (aka fake participant data)
# http://www.peterbe.com/plog/uniqifiers-benchmark
def observed_walk(walk):
    seen = {}
    result = []
    for item in path_from_walk(walk):
        if item in seen: continue
        seen[item] = 1
        result.append(item)
    return result

# flat list from tuple walk
def path_from_walk(walk):
    path=list(zip(*walk)[0]) # first element from each tuple
    path.append(walk[-1][1]) # second element from last tuple
    return path

# return simulated data on graph g
# if usr_irts==1, return irts (as steps)
def genX(g,s=None,use_irts=0,seed=None,weighted=False,stop=None,restart=0):
    rwalk=random_walk(g,s,seed,weighted,stop,restart)
    Xs=observed_walk(rwalk)
    
    if use_irts==0: 
        return Xs
    else:
        fh=list(zip(*firstHits(rwalk))[1])
        irts=[fh[i]-fh[i-1] for i in range(1,len(fh))]
        return Xs, irts
    
def get_cluster(g,vertex):
    '''Return a subgraph containing the cluster to which vertex v belongs.'''
    vertex = g.vs.find(label=vertex).index if type(vertex)==str else vertex
    
    vertices = [l for l in g.clusters() if vertex in l]
    
    return g.subgraph(vertices[0])

def in_same_cluster(g,v,w):
    '''Determine whether two vertices in a graph belong to the same cluster.'''
    v = g.vs.find(label=v).index if type(v)==str else v    
    w = g.vs.find(label=w).index if type(w)==str else w

    v_clust = [l for l in g.clusters() if v in l]
    
    w_in_v_clust = [m for m in v_clust if w in m]
    
    return bool(w_in_v_clust)

def gen_random_walk(g,weighted=True, log_file='',itr=1,name='',stop=None,restart=0):

    start = 'bird:N'    
    
    g = get_cluster(g,start)
    
    a,b = genX(g,s=start,use_irts=1,weighted=weighted,stop=stop,restart=restart)
    
    a_names = g.vs[a]['label']
    #a_categories = [SHARED_HILLS_POS_CATEG_NUM.get(i,-1) for i in g.vs[a]['label']]
    #a_cat_changed = [1 if a_categories[i-1] != a_categories[i] else 0 for i in range(1,len(a_categories))]
    
    
    ##calculate whether category changes as per Abbott et al.
    j = 0
    cat=[]
    #cat_names=[]
    for i,n in enumerate(a_names):
        if (n == start and i == 0) or i==0:
            cat.append(j)
            #cat_names.append(None)           
        else:
            ##!!!change this back
            s = A_NAME.get(n)
            t = A_NAME.get(a_names[i-1])
            if s == None or t == None:
                if n == 'animal:N' or a_names[i-1] == 'animal:N':
                    cat.append(j)
                    continue
                cat.append(None)
                continue
            intsct = t.intersection(s)
            if len(intsct) == 0:
                j+=1
                cat.append(j)
                #cat_names.append
            else:
                cat.append(j)
    
    #append to logfile
    if log_file:
        with open(log_file + '.txt','a') as f:
            lines = 'Weighted: ' + str(weighted),'Name: ' + name, 'Path: ' + str(a_names), 'Categ: ' + str(cat)
            #print '\n'.join(lines)+'\n\n'
            #print b
            f.write('\n'.join(lines)+'\n\n')
            
    return b,cat,a

def precision_recall(graph):
    try:
        graph = graph.copy()
        graph.remove_vertex(graph.vs.find(label='animal:N'))
    except Exception as e:
        pass
    
    precision = {}
    recall = {}
    
    for cluster in graph.clusters():
        fp = float(0)
        fn = float(0)
        tp = float(0)
        cluster_categories = {}
        names = []
        for vid in cluster:
            name = graph.vs[vid]['label']
            names.append(name)
            for s in SHARED_NAME[name]:
                if cluster_categories.get(s) == None:
                    cluster_categories[s] = 1
                else:
                    cluster_categories[s] += 1
        
        #cluster label is most frequently occurring category in the cluster
        cluster_category = max([(value, key) for key, value in cluster_categories.items()])[1]
        
        for vid in cluster:
            name = graph.vs[vid]['label']
 
            if cluster_category in SHARED_NAME[name]:
                tp += 1
            else:
                fp += 1
        
        for animal in [key for key, value in SHARED_NAME.items() if cluster_category in value]:
            if animal not in names:
                fn += 1
                
        #print tp,fp,fn
                
        precision[cluster_category] = float(tp/(tp+fp))
        recall[cluster_category] = float(tp/(tp+fn))    

    return precision,recall
                
def create_irt_graph(b,cat,multi=False):
    '''get patch entry pos'''
    orders = []
    
    n = []
    p = []
    irts= []
    
    if multi==True:
        #assert len(b)==len(cat)
        size = len(cat)
        
        
        for q,w in enumerate(cat):
            
            neg_order = []
            pos_order = []
            
            for j,k in enumerate(w):
                
                #if k==cat[j]:
                    #k==cat[j]
                if k >= w[len(w)-1]:
                    to_next=0
                else:
                    next_cat = w.index(k+1)             
                    to_next = next_cat - j
                
                neg_order.append(-to_next)
                
                same_cat = w.index(k)
                
                to_same = j - same_cat + 1
                
                pos_order.append(to_same)
                
            n.append(neg_order)
            p.append(pos_order)
            #orders += [n,p]
            #irts += b[q]
    else:      
    
        neg_order = []
        pos_order = []
        
        for j,k in enumerate(cat):
            if k >= cat[len(cat)-1]:
                to_next=0
            else:
                next_cat = cat.index(k+1)             
                to_next = next_cat - j
            
            neg_order.append(-to_next)
            
            same_cat = cat.index(k)
            
            to_same = j - same_cat + 1
            
            pos_order.append(to_same)
            
        order = [neg_order,pos_order]
        
    binned = {}
    binned_counts = {}
    binned_final = {}
    binned_sem = {}

    orders = [n,p]
    #print orders
    
    for g in orders:
        for s,order in enumerate(g):
            for j,k in enumerate(order):
                
                if binned.get(k,None):
                    binned[k] += b[s][j-1]
                    binned_counts[k] += 1
                    binned_sem[k].append(b[s][j-1])
                else:
                    binned[k] = b[s][j-1] if not j==0 else 0
                    binned_counts[k] = 1
                    binned_sem[k] = []
            
    for key in binned:
        binned_final[key] = float(binned[key]) / float(binned_counts[key])
        binned_sem[key] = scipy.stats.sem(binned_sem[key])
       
    return binned_final,binned_sem

def irt_self_longterm_avg(b,cat,multi=False):
    '''get patch entry pos'''
    orders = []
    
    n = []
    p = []
    irts= []
    
    if multi==True:
        #assert len(b)==len(cat)
        size = len(cat)
        
        
        for q,w in enumerate(cat):
            
            neg_order = []
            pos_order = []
            
            for j,k in enumerate(w):
                
                #if k==cat[j]:
                    #k==cat[j]
                if k >= w[len(w)-1]:
                    to_next=0
                else:
                    next_cat = w.index(k+1)             
                    to_next = next_cat - j
                
                neg_order.append(-to_next)
                
                same_cat = w.index(k)
                
                to_same = j - same_cat + 1
                
                pos_order.append(to_same)
                
            n.append(neg_order)
            p.append(pos_order)
            #orders += [n,p]
            #irts += b[q]
    else:      
    
        neg_order = []
        pos_order = []
        
        for j,k in enumerate(cat):
            if k >= cat[len(cat)-1]:
                to_next=0
            else:
                next_cat = cat.index(k+1)             
                to_next = next_cat - j
            
            neg_order.append(-to_next)
            
            same_cat = cat.index(k)
            
            to_same = j - same_cat + 1
            
            pos_order.append(to_same)
            
        order = [neg_order,pos_order]
        
    binned = {}
    binned_counts = {}
    binned_final = {}
    binned_sem = {}

    orders = [n,p]
    
    for g in orders:
        for s,order in enumerate(g):
            ind_mean = mean(b[s])
            #print ind_mean
            for j,k in enumerate(order):
                
                if binned.get(k,None):
                    #
                    binned[k] += b[s][j-1] / ind_mean
                    binned_counts[k] += 1
                    #
                    binned_sem[k].append(b[s][j-1] / ind_mean)
                else:
                    binned[k] = b[s][j-1] / ind_mean if not j==0 else 0
                    binned_counts[k] = 1
                    binned_sem[k] = []
            
    for key in binned:
        binned_final[key] = float(binned[key]) / float(binned_counts[key])
        binned_sem[key] = scipy.stats.sem(binned_sem[key])

    return binned_final,binned_sem

def calc_small_worldness(graph,filename="graphstats"):
    #avg_c, median_sp = self.calc_graph_stats(graph, filename)
    #graph = get_cluster(graph,'animal:N')

    global rand_graph
    rand_graph = Graph.Erdos_Renyi(graph.vcount(),m=graph.ecount())
    rand_graph.es['distance']=graph.es['distance']
    #rand_graph.vs[
    #rejection_count = random_rewire(rand_graph, "erdos")
    #print "rejection count", rejection_count
    
    
    ##graph_paths = graph.shortest_paths_dijkstra()
    ##rand_paths = rand_graph.shortest_path_dikkstra()
    avg_c = graph.transitivity_avglocal_undirected()
    rand_avg_c = rand_graph.transitivity_avglocal_undirected()
    
    avg_sp = graph.average_path_length()
    rand_avg_sp = rand_graph.average_path_length()

    #rand_avg_c, rand_median_sp = self.calc_graph_stats(rand_graph, filename)

    stat_file = open(filename + ".txt", 'a')
    stat_file.write("small-worldness %.3f" % ((avg_c / rand_avg_c)/(float(avg_sp)/rand_avg_sp)) + "\n\n")
    stat_file.close()
    
def calc_small_worldness_orig(self, graph, filename):
    avg_c, median_sp = self.calc_graph_stats(graph, filename)

    rand_graph = Graph(graph)
    rejection_count = random_rewire(rand_graph, "erdos")
    print "rejection count", rejection_count
    rand_avg_c, rand_median_sp = self.calc_graph_stats(rand_graph, filename)

    stat_file = open(filename + ".txt", 'a')
    stat_file.write("small-worldness %.3f" % ((avg_c / rand_avg_c)/(float(median_sp)/rand_median_sp)) + "\n\n")
    stat_file.close()

def calc_graph_stats_orig(self, graph, filename):
    """ calc graph stats """

    """Average Local Clustering Coefficient"""
    #local_clust_co = local_clustering(graph)
    #avg_local_clust = vertex_average(graph, local_clust_co)
    avg_local_clust = graph.transitivity_avglocal_undirected()

    """Average Degree (sparsity)"""
    #avg_total_degree = vertex_average(graph, "total")
    avg_total_degree = graph.knn()

    nodes_num = graph.num_vertices()
    edges_num = graph.num_edges()

    """ Largest Component of the Graph"""
    #lc_labels = label_largest_component(graph)

    #lc_graph = Graph(graph)
    #lc_graph.set_vertex_filter(lc_labels)
    #lc_graph.purge_vertices()
    lc_graph = graph.clusters(mode='weak').giant()

    """Average Shortest Path in LCC"""
    #lc_distances = lc_graph.edge_properties["distance"]
    lc_distances = lc_graph.es["distance"]
    
    #dist = shortest_distance(lc_graph)#, weights=lc_distances) #TODO
    dist = lc_graph.shortest_paths_dijkstra()
    dist_list = []
    for v in lc_graph.vertices():
        #dist_list += list(dist[v].a)
        dist_list += list(dist[v.index])


    """ Median Shortest Path """
    #distances = graph.edge_properties["distance"] #TODO
    distances = graph.es['distance']
    #gdist = shortest_distance(graph)#, weights=distances)
    gdist = graph.shortest_paths_dijkstra()
    
    graph_dists = []
    counter = 0
    for v in graph.vertices():
        #for othv in gdist[v].a:
        for othv in gdist[v.index]:
            if othv != 0.0: # not to include the distance to the node
                graph_dists.append(othv)
            else:
                counter +=1
  #  print "num v", graph.num_vertices(), counter
    median_sp = np.median(graph_dists)
  #  print "median", median_sp#, graph_dists


    stat_file = open(filename + ".txt", 'a')
    stat_file.write("number of nodes:"+ str(nodes_num) + "\nnumber of edges:" + str(edges_num) + "\n")
    stat_file.write("avg total degree:" + "%.2f +/- %.2f" % avg_total_degree  + "\n")
    stat_file.write("sparsity:" + "%.2f" % (avg_total_degree[0] / float(nodes_num))  + "\n")

    stat_file.write("number of nodes in LLC:"+  str(lc_graph.num_vertices()) + "\nnumber of edges in LLC:" + str(lc_graph.num_edges()) + "\n")
    stat_file.write("connectedness:" + "%.2f" % (lc_graph.num_vertices()/float(nodes_num)) + "\n")
    stat_file.write("avg distance in LCC:" + "%.2f +/- %.2f" % (np.mean(dist_list), np.std(dist_list)) + "\n\n")

    stat_file.write("avg local clustering coefficient:" + "%.2f +/- %.2f" % avg_local_clust + "\n")
    stat_file.write("median distnace in graph:" + "%.2f" % median_sp + "\n\n")
    
    stat_file.close()

    return avg_local_clust[0], median_sp

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
    
    return graph.subgraph(graph.vs(label_in=names_shared))

def adjacency_names(graph,name='',n='graph_names.txt'):
    spaces = 12
    
    with open(n,'a') as f:
        if name:
            f.write('Name: {}\n'.format(name))
            
        for i in range(0,graph.vcount()):
            node_name = graph.vs['label'][i]
            
            for q,neighbor in enumerate(graph.neighbors(i)):
                if q == 0:
                    f.write(node_name + ' '*(spaces-len(node_name)) + graph.vs['label'][neighbor] + '\n')
                    
                else:
                    f.write(' '*spaces + graph.vs[neighbor]['label'] + '\n')
            f.write('\n')
            
def write_summary(title,b):
    with open(title+'.txt','a') as l:
        l.write('\n----------------------------------\n')
        l.write('SUMMARY STATISTICS:')
        l.write('\n----------------------------------\n')   
        l.write('Avg words: {}\n'.format(mean([mean(len(z)) for z in b])))
        l.write('Avg patch switches: {}\n'.format(mean([z[-1:][0] for z in b])))
        l.write('Avg itms/patch: {}\n'.format(mean([mean([len(list(group)) for key, group in groupby(z)]) for z in b])))    
            
if __name__ == "__main__":
    #if not 'all_graphs' in globals():
        #execfile('generate_animal_graphs.py')    
    #for graph in all_graphs:
        #gen_random_walks(graph,True,'adul_rw_weighted_add_animal_0.5')
    
    if 'g' not in globals():
        g = Graph.Read_Pickle(fname='gHS0.999.igr')        
        
    models = {'BEAGLE_0.1':get_beagle(0.1),'gold':g}
    weight_opts = {'wrw':True,'rw':False}
    restarts =  {'restart':0.05,'':0}
    walk_lengths = [30]
    #g2= all_graphs['all_dev_utt_learner_HILLS_SHARED_0.88']
    
    b=[]
    cat=[]
    a=[]
    
    for m in models:
        for weight_opt in weight_opts:
            for rstrt in restarts:
                for walk_length in walk_lengths:
            
                    for i in range(0,282):
                        title = "_".join([m,str(weight_opt),'282',str(walk_length),'restart '+str(restarts[rstrt]) if rstrt else ''])
                        
                        b_i,c_i,a_i = gen_random_walk(g=models[m],weighted=weight_opts[weight_opt],log_file=title,stop=walk_length,restart=restarts[rstrt],name=title)
                        
                        b.append(b_i)
                        #b.append(b_i) #needed since we generate two orders, pos and neg        
                        cat.append(c_i)
                        a.append(a_i)
                        
                    binned_final,binned_sem = irt_self_longterm_avg(b,cat,multi=True)
                    
                    r = [-3,-2,-1,1,2,3,4]
                    
                    x = range(0,7)
                    y = scipy.array([binned_final[i] for i in r])
                    yerr=[binned_sem[i] for i in r]
                    f = pylab.figure()
                    ax = f.add_axes([0.1, 0.1, 0.8, 0.8])
                    ax.bar(x, y, align='center')
                    ax.set_xticks(x)
                    ax.set_xticklabels(r)
                    ax.set_xlabel('Patch Entry Position')
                    ax.set_ylabel('Average IRT/Long-term Average IRT')
                    ax.set_title(title+' avg-words:'+str(mean([mean(len(z)) for z in a])))
                    pylab.plot([-1,7],[1,1])        
                    ax.errorbar(x, y, yerr=yerr, fmt='o')
                    write_summary(title,b)
                    
                f.show()   
        