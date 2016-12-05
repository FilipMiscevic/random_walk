from rw import *

def precision_recall_animal_delete(g,title='',n='precision_recall'):
    try:
        graph = get_cluster(g.copy(),'animal:N')
        graph.remove_vertex(graph.vs.find(label='animal:N'))

    except Exception as e:
        print "WARNING: vertex 'animal:N' not found"

    return precision_recall(graph,graph.clusters(), title,n)

def precision_recall(graph,clusters,title='',n='precision_recall'):
    '''Calculate precision and recall scores for the connected components in graph g.'''


    precision = {}
    recall = {}
    tpfpfn = {}
    c=  {}

    for cluster in clusters:
        fp = float(0)
        fn = float(0)
        tp = float(0)
        cluster_categories = {}
        #if len(cluster) == 1: #uncomment this to discount singletonss
            #continue
        for vid in cluster:
            name = graph.vs[vid]['label']

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
                tp += 1
            else:
                fp += 1

        cluster_names = [graph.vs[b]['label'] for b in cluster ]
        for animal in [key for key, value in A_NAME.items() if cluster_category in value and key in graph.vs['label']]:
            if animal not in cluster_names:
                fn += 1

        #print tp,fp,fn

        tpfpfn[cluster_category] = (tp,fp,fn)

        c[cluster_category] = cluster_names

        precision[cluster_category] = float(tp/(tp+fp))
        recall[cluster_category] = float(tp/(tp+fn))    

    with open(n+'.txt','a') as f:
        f.write('---------------------------------\nName: {}\n'.format(title))
        f.write('Precision: \n')
        for key,value in precision.items():
            f.write('        {}: {} ({} of {} learned words in cluster)\n'.format(key,value,tpfpfn[key][0],tpfpfn[key][0]+tpfpfn[key][2]))
        f.write('\nRecall: \n')
        for key,value in recall.items():
            f.write('        {}: {} ({} of {} learned words in cluster)\n'.format(key,value,tpfpfn[key][0],tpfpfn[key][0]+tpfpfn[key][2]))        

    return precision,recall,c

def precision_recall_old(g,title='',n='precision_recall'):
    '''Calculate precision and recall scores for the connected components in graph g.'''
    try:
        graph = get_cluster(g.copy(),'animal:N')
        graph.remove_vertex(graph.vs.find(label='animal:N'))

    except Exception as e:
        print "WARNING: vertex 'animal:N' not found"

    precision = {}
    recall = {}
    tpfpfn = {}
    c=  {}

    for cluster in graph.clusters():
        fp = float(0)
        fn = float(0)
        tp = float(0)
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
                tp += 1
            else:
                fp += 1

        cluster_names = [graph.vs[b]['label'] for b in cluster ]
        for animal in [key for key, value in A_NAME.items() if cluster_category in value and key in graph.vs['label']]:
            if animal not in cluster_names:
                fn += 1

        #print tp,fp,fn

        tpfpfn[cluster_category] = (tp,fp,fn)

        c[cluster_category] = cluster_names

        precision[cluster_category] = float(tp/(tp+fp))
        recall[cluster_category] = float(tp/(tp+fn))    

    with open(n+'.txt','a') as f:
        f.write('---------------------------------\nName: {}\n'.format(title))
        f.write('Precision: \n')
        for key,value in precision.items():
            f.write('        {}: {} ({} of {} learned words in cluster)\n'.format(key,value,tpfpfn[key][0],tpfpfn[key][0]+tpfpfn[key][2]))
        f.write('\nRecall: \n')
        for key,value in recall.items():
            f.write('        {}: {} ({} of {} learned words in cluster)\n'.format(key,value,tpfpfn[key][0],tpfpfn[key][0]+tpfpfn[key][2]))        

    return precision,recall,c


def precision_recall_with_singletons(graph,clusters,title='',n='precision_recall_singletons'):
    '''EXPERIMENTAL --
    Calculate precision and recall scores including singletons as their own cluster.'''

    precision = []#{}
    recall = []#{}
    tpfpfn = []#{}
    c=  []#{}
    c_names = []

    for cluster in clusters:
        fp = float(0)
        fn = float(0)
        tp = float(0)
        cluster_categories = {}
        names = []
        #if len(cluster) == 1: #uncomment this to discount singletons
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
                tp += 1
            else:
                fp += 1

        cluster_names = [graph.vs[b]['label'] for b in cluster ]
        for animal in [key for key, value in A_NAME.items() if cluster_category in value and key in graph.vs['label']]:
            if animal not in cluster_names:
                fn += 1

        #print tp,fp,fn
        c.append(cluster_category)
        tpfpfn.append( (tp,fp,fn) )

        #tpfpfn[cluster_category] = (tp,fp,fn)

        c_names.append(cluster_names)
        precision.append(float(tp/(tp+fp)))
        recall.append(float(tp/(tp+fn)))

        #precision[cluster_category] = float(tp/(tp+fp))
        #recall[cluster_category] = float(tp/(tp+fn)) 
    '''
    print c
    print c_names
    print precision
    print recall
    print tpfpfn
        '''
    with open(n+'.txt','a') as f:
        f.write('---------------------------------\nName: {}\n'.format(title))
        f.write('Precision: \n')
        key=-1
        for name,value in zip(c,precision):
            key+=1
            f.write('        {}: {} ({} of {} learned words in cluster)\n'.format(name,value,tpfpfn[key][0],tpfpfn[key][0]+tpfpfn[key][2]))
        f.write('\nRecall: \n')
        key=-1
        for name,value in zip(c,recall):
            key+=1
            f.write('        {}: {} ({} of {} learned words in cluster)\n'.format(name,value,tpfpfn[key][0],tpfpfn[key][0]+tpfpfn[key][2]))        

    return precision,recall,c#,c_names

def calculate_fscore(p,r,c,weighted=True): #takes lists
    '''Calculate the f-score given precision and recall.
    '''

    if type(p) == dict:

        items = p.keys()


        avg_p = np.average([p[k] for k in items], weights=[len(c[k]) for k in items] if weighted else None)
        avg_r = np.average([r[k] for k in items], weights=[len(c[k]) for k in items] if weighted else None)
    else:
        avg_p = np.average(p, weights = [len(q) for q in c] if weighted else None)
        avg_r = np.average(r, weights = [len(q) for q in c] if weighted else None)

    #print 'avgp:' + str(avg_p)
    #print 'avgr:' + str(avg_r)

    #calculate harmonic mean of precision and recall
    return 2*( (avg_p*avg_r) / (avg_p + float(avg_r)) )

def order_by_fscore(graphs,weighted=True):
    '''Calculate f-score for graphs and print in non-increasing order of f-score.'''
    f = {}

    for name,graph in graphs.items():
        p,r,c = precision_recall(graph,title=name,n='precision_recall')
        items = p.keys()        

        if len(items) ==0:
            continue



        f[name] = calculate_fscore(p, r, c, weighted)

    f = sorted( ((v,k) for k,v in f.iteritems()), reverse=True)

    for v,k in f:
        print "%s: %f" % (k,v)

    return f


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