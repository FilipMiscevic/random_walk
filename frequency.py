from rw import *

def adjacency_names(graph,name='',n='graph_names'):
    spaces = 12
    
    with open(n+'.txt','a') as f:
        if name:
            f.write('Name: {}\n'.format(name))
            
        for i in range(0,graph.vcount()):
            node_name = graph.vs['label'][i]
            
            for q,neighbor in enumerate(graph.neighbors(i)):
                if q == 0:
                    f.write(node_name + ' '*(spaces-len(node_name)) + graph.vs['label'][neighbor])
                    f.write('\n')
                    
                else:
                    f.write(' '*spaces + graph.vs[neighbor]['label'] + '\n')
            f.write('\n')

def count_occurences(g,corpus):
    freq = {}
    
    #regex=[]
    
    for i in range(0,g.ecount()):
        s = g.es[i].source
        t = g.es[i].target
        k = [g.vs['label'][s],g.vs['label'][t]]
        k.sort()
        #because tuples are hashable while lists are not
        k = tuple(k)
        
        freq[k] = 0
        
    with open(corpus, 'rb') as f:
        for line in f:
            for key in freq.keys():
                if key[0] in line and key[1] in line:
                    freq[key] += 1
            
    return freq

            
def compare_features(gold,learner,n='features.csv'):
    with open(n, 'ab') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                                quotechar="\"", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Word','Gold Features','Score','Learned Features','Score','COS sim'])    
        
        for word in SHARED_HILLS_POS_CATEG_NAMED:
            lf = learner._learned_lexicon.meaning(word).sorted_features()
            gf = gold.meaning(word).sorted_features()
            sim = learner.acquisition_score(word)
            for i in range(0,len(gf)):
                gf_f =[gf[i][1],gf[i][0]] if i < len(gf) else ['','']
                lf_f = [lf[i][1],lf[i][0]] if i < len(lf) else ['','']
                writer.writerow([word if i==0 else '']+gf_f+lf_f+[sim if i==0 else ''])  
                
            writer.writerow([''])
            
def comparative_adjacency_csv(graph,gold_graph,counts,name='',n='graph_names.csv'):
    with open(n, 'ab') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                                quotechar="\"", quoting=csv.QUOTE_MINIMAL)
        
        writer.writerow(['Node','Name','Dist',name,'Name','Dist','Freq'])
        for i in range(0,gold_graph.vcount()):
            node_name = gold_graph.vs['label'][i]
            
            gg_nb = gold_graph.neighbors(i)
            
            if node_name not in graph.vs['label']:
                for n,d in enumerate(gg_nb):
                    if n == 0:
                        writer.writerow([node_name, gold_graph.vs['label'][d] ])
                    else:
                        writer.writerow(['', gold_graph.vs['label'][d] ])
            else:
                g_nb = graph.neighbors(graph.vs.find(label=node_name).index)
                
                size = max(len(g_nb),len(gg_nb))
                
                for s in range(0,size):
                    
                    
                    g=[]
                    if s < len(g_nb):
                        g = [graph.vs['label'][g_nb[s]],graph.es['distance'][graph.get_eid(g_nb[s],graph.vs.find(label=node_name).index)], counts[
                            tuple(sorted(
                                [graph.vs['label'][g_nb[s]],node_name]
                             )) ] ]   
                        
                    #gg=[]
                    if s < len(gg_nb):
                        gg = [gold_graph.vs['label'][gg_nb[s]],gold_graph.es['distance'][gold_graph.get_eid(gg_nb[s],gold_graph.vs.find(label=node_name).index)], '']
                    else:
                        gg = ['','','']
                        
                        
                        
                    
                    if s == 0:
                        writer.writerow([node_name]+gg+g)
                    else:
                        writer.writerow(['']+gg+g)
                
            '''
            
            if node_name in graph.vs['label']:
            
                if len(gold_graph.neighbors(i)) < len(graph.neighbors(graph.vs.find(label=node_name).index)):
                    g=graph
                else:
                    g=gold_graph
                for q in range(0,len(g.neighbors(i))):
                    
                    count = 0
                    m2 = []

                    if gold_graph.vs[g.neighbors(i)[q]]['label'] in graph.vs['label'] and q < len(graph.neighbors(graph.vs.find(label=node_name).index)):
                       
                        for line in open('data/animals.dev'):
                            if re.findall(r'E: (?=.*{})(?=.*{})'.format(node_name,graph.vs['label'][graph.neighbors(graph.vs.find(label=node_name).index)[q]]),line) != []:
                                if count == 0:
                                    print re.findall(r'E: (?=.*{})(?=.*{})'.format(node_name,graph.vs['label'][graph.neighbors(graph.vs.find(label=node_name).index)[q]]),line)
                                    print r'E: (?=.*{})(?=.*{})'.format(node_name,graph.vs['label'][graph.neighbors(graph.vs.find(label=node_name).index)[q]])
                                count +=1
                        m2 = [graph.vs['label'][graph.neighbors(graph.vs.find(label=node_name).index)[q]],graph.es['distance'][graph.get_eid(i,graph.neighbors(graph.vs.find(label=node_name).index)[q])], count]
                        
                    m1 = [gold_graph.vs['label'][gold_graph.neighbors(i)[q]],gold_graph.es['distance'][gold_graph.get_eid(i,gold_graph.neighbors(i)[q])] ] if q < len(gold_graph.neighbors(i)) else ['','']
                    
                    
                    if q == 0:
                        writer.writerow([node_name] + m1 + m2 )
                    else:
                        writer.writerow([''] + m1 + m2 )
            else:

                for qq,d in enumerate(gold_graph.neighbors(i)):
                    
                    if qq == 0:
                        writer.writerow([node_name, gold_graph.vs['label'][d] ])
                        #writer.writerow([''])                 
                        #f.write('\n')
                        
                    else:
                        writer.writerow(['', gold_graph.vs['label'][d] ])

        writer.writerow([''])    '''             
