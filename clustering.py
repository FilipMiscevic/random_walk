from adj_rand import *
from precision_recall import *
import hdbscan as h
import rw
import numpy as np


def fit_hdbscan(g,min_cluster_size=2):
    #name = 'learner_af_0.85_24000_A0.4'
    #name = 'all_dev_utt_learner_af_HILLS_SHARED_0.8_A0.4'
    
    #name = 'BEAGLE_HILLS_SHARED_0.5_A0.4'
    
    #g = get_model(name)
    g = rw.get_cluster(g,'animal:N')
    #g.remove_vertex(g.vs.find(label='animal:N'))    
    
    d = g.shortest_paths_dijkstra(weights='distance')
    d = np.array(d)
    
    '''
    ##first way of 
    d = g.get_adjacency(attribute='distance')
    d = np.matrix(d.data)
    d[d == 0] = 1 #non-connected nodes have a distance of 1 #try something that is larger than longest path
    ##try using minimum paths
    np.fill_diagonal(d,0)
    
    names = None
    
    #assert (d.transpose() == d).all()

    '''
    ##also try using

        
    c = h.HDBSCAN(metric='precomputed', min_cluster_size=min_cluster_size, gen_min_span_tree=True)
    c.fit_predict(d)    
    return c

def get_hdbscan_clusters(g,c):
    clusters = {}
        
    for vid,cid in enumerate(c.labels_):
        
        if g.vs[vid]['label'] == 'animal:N':
            continue
        
        if clusters.get(cid,None) is None:
            clusters[cid] = [vid]
        else:
            clusters[cid].append(vid)
            
    #uncategorized nodes
    qq = clusters.pop(-1,None)    
    
    return clusters.values() + [[q] for q in qq] #comment to exclude singletons

def get_hdbscan_fscore_unweighted(g):
    return get_hdbscan_fscore(g,weighted=False)

def get_hdbscan_fscore(g,weighted=True):
    
    c = fit_hdbscan(g)
    
    clusters = get_hdbscan_clusters(g,c)
    
     
    p,r,c = precision_recall(g,
                             clusters
                             )
    
    return calculate_fscore(p,r,c,weighted)    

### these versions will include multiple categories multiple times ###
def get_hdbscan_fscore_unweighted_all(g):
    return get_hdbscan_fscore(g,weighted=False)

def get_hdbscan_fscore_all(g,weighted=True):
    
    c = fit_hdbscan(g)
    
    clusters = get_hdbscan_clusters(g,c)
    
     
    p,r,c = precision_recall_with_singletons(g,
                             clusters
                             )
    
    return calculate_fscore(p,r,c,weighted)    

def get_hdbscan_adj_rand_idx(g,weighted=False):
    
    c = fit_hdbscan(g)
        
    clusters = get_hdbscan_clusters(g,c)    
    
    cat_clusters = test_get_cluster_cat_labels(g,clusters)
    
    return test_avg_adj_rand(cat_clusters)


if __name__ == "__main__":
    names = ['gold_af_HILLS_SHARED']
    names +=['animals_learner','BEAGLE_HILLS_SHARED']
    names +=['all_dev_utt_learner']
    
    #plot_omega_irt('animals_learner_af')
    
    
    #itr = 5
    for name in names:
        generate_adj_rand_curve(name)
        plt.show()    
    '''
    name = 'learner_af_0.85_24000_A0.4'
    name = 'all_dev_utt_learner_af_HILLS_SHARED_0.8_A0.4'
    
    #name = 'BEAGLE_HILLS_SHARED_0.5_A0.4'
    
    g = get_model(name)
    g = get_cluster(g,'animal:N')
    #g.remove_vertex(g.vs.find(label='animal:N'))    
    
    d = g.shortest_paths_dijkstra(weights='distance')
    d = np.array(d)
    
    
    ##first way of 
    #d = g.get_adjacency(attribute='distance')
    #d = np.matrix(d.data)
    #d[d == 0] = 1 #non-connected nodes have a distance of 1 #try something that is larger than longest path
    ##try using minimum paths
    #np.fill_diagonal(d,0)
    
    #names = None
    
    #assert (d.transpose() == d).all()

    ##also try using

        
    c = h.HDBSCAN(metric='precomputed', min_cluster_size=2, gen_min_span_tree=True)
    c.fit_predict(d)
    
    
    #organize into clusters
    clusters = {}
    
    for vid,cid in enumerate(c.labels_):
        
        if g.vs[vid]['label'] == 'animal:N':
            continue
        
        if clusters.get(cid,None) is None:
            clusters[cid] = [vid]
        else:
            clusters[cid].append(vid)
            
    #uncategorized nodes
    qq = clusters.pop(-1,None)
    name = 'BEAGLE_HILLS_SHARED_0.5_A0.4'
    
    g = get_model(name)
    
    print get_hdbscan_adj_rand_idx(g)
    
    c = fit_hdbscan(g)
    
    clusters = get_hdbscan_clusters(g,c)
    
    
    #plot_graph(g,name+"_clustered",vertex_colors=c.labels_)
    
    p,r,d = precision_recall(g,
                             clusters
                             )
    
    print p, r, d
    
    print calculate_fscore(p,r,d)
    '''
    