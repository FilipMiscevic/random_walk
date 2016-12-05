from rw import *
from sklearn.metrics import adjusted_rand_score as adj_rand

                
def test_avg_adj_rand(d):
    '''Determine the adjusted rand index for a clustering. d is a list of lists representing the clustering, and the number represents their ground truth. Because adj rand is a symmetric value, the reverse could be true and the measure would be the same (i.e., the clusters could be the ground truth clusters and the number the putative clusters).'''
    g = 0
    clusters = []
    ground_truth = []
    for c in d:
        clusters += [g for cc in c]
        ground_truth += c
        g += 1
    
    #one = adj_rand(clusters, ground_truth)
    #two = np.mean( [ adj_rand([0 for i in c],c) for c in d ] )
    '''
    print d
    print '----------------'
    print ground_truth
    print clusters
    '''
    #if one != two:
    #    print 'WARNING: Adj rand index differs'
    #    print one, two
    return adj_rand(clusters, ground_truth)

def test_get_cluster_cat_labels(graph,clusters):
    all_cluster_labels = []
    for cluster in clusters:

        labels= []

        cluster_categories = {}
        names = []
        #if len(cluster) == 1: #uncomment this to discount singletonss
            #continue
        for vid in cluster:
            name = graph.vs[vid]['label']

            names.append(name)
            for s in A_NAME[name]:
                if cluster_categories.get(s) == None:
                    cluster_categories[s] = 1
                else:
                    cluster_categories[s] += 1

        #cluster label is most frequently occurring category in the cluster
        cluster_category = max([(value, key) for key, value in cluster_categories.items()])[1]

        #print cluster_category

        for vid in cluster:
            name = graph.vs[vid]['label']

            #print '    ' + name

            if cluster_category in A_NAME[name]:
                labels.append( ALL_CATEG_NAMES.index(cluster_category) )#A_NUM[ cluster_category+':N' ] )
            else:
                #just get the first category the remaining animal belongs to for now
                labels.append(list(A_NUM[name])[0])

        all_cluster_labels.append(labels)

    return all_cluster_labels