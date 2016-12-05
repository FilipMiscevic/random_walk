from rw import *
from clustering import *

#from the brain connectivity toolkit, https://github.com/aestrivex/bctpy/blob/master/bct/algorithms/reference.py, as referenced in The Ubiquity of Small Networks, Telesford et al.
def latmio_und_connected(R, itr, D=None):
    '''
    This function "latticizes" an undirected network, while preserving the
    degree distribution. The function does not preserve the strength
    distribution in weighted networks. The function also ensures that the
    randomized network maintains connectedness, the ability for every node
    to reach every other node in the network. The input network for this
    function must be connected.
    Parameters
    ----------
    R : NxN np.ndarray
        undirected binary/weighted connection matrix
    itr : int
        rewiring parameter. Each edge is rewired approximately itr times.
    D : np.ndarray | None
        distance-to-diagonal matrix. Defaults to the actual distance matrix
        if not specified.
    Returns
    -------
    Rlatt : NxN np.ndarray
        latticized network in original node ordering
    Rrp : NxN np.ndarray
        latticized network in node ordering used for latticization
    ind_rp : Nx1 np.ndarray
        node ordering used for latticization
    eff : int
        number of actual rewirings carried out
    '''
    if not np.all(R == R.T):
        raise BCTParamError("Input must be undirected")

    #if number_of_components(R) > 1:
     #   raise BCTParamError("Input is not connected")

    n = len(R)

    ind_rp = np.random.permutation(n)  # randomly reorder matrix
    R = R.copy()
    R = R[np.ix_(ind_rp, ind_rp)]

    if D is None:
        D = np.zeros((n, n))
        un = np.mod(range(1, n), n)
        um = np.mod(range(n - 1, 0, -1), n)
        u = np.append((0,), np.where(un < um, un, um))

        for v in range(int(np.ceil(n / 2))):
            D[n - v - 1, :] = np.append(u[v + 1:], u[:v + 1])
            D[v, :] = D[n - v - 1, :][::-1]

    i, j = np.where(np.tril(R))
    k = len(i)
    itr *= k

    # maximal number of rewiring attempts per iteration
    max_attempts = np.round(n * k / (n * (n - 1) / 2))

    # actual number of successful rewirings
    eff = 0

    for it in range(itr):
        att = 0
        while att <= max_attempts:
            rewire = True
            while True:
                e1 = np.random.randint(k)
                e2 = np.random.randint(k)
                while e1 == e2:
                    e2 = np.random.randint(k)
                a = i[e1]
                b = j[e1]
                c = i[e2]
                d = j[e2]

                if a != c and a != d and b != c and b != d:
                    break

            if np.random.random() > .5:
                i.setflags(write=True)
                j.setflags(write=True)
                i[e2] = d
                j[e2] = c  # flip edge c-d with 50% probability
                c = i[e2]
                d = j[e2]  # to explore all potential rewirings

            # rewiring condition
            if not (R[a, d] or R[c, b]):
                # lattice condition
                if (D[a, b] * R[a, b] + D[c, d] * R[c, d] >= D[a, d] * R[a, b] + D[c, b] * R[c, d]):
                    # connectedness condition
                    if not (R[a, c] or R[b, d]):
                        P = R[(a, d), :].copy()
                        P[0, b] = 0
                        P[1, c] = 0
                        PN = P.copy()
                        PN[:, d] = 1
                        PN[:, a] = 1
                        while True:
                            P[0, :] = np.any(R[P[0, :] != 0, :], axis=0)
                            P[1, :] = np.any(R[P[1, :] != 0, :], axis=0)
                            P *= np.logical_not(PN)
                            if not np.all(np.any(P, axis=1)):
                                rewire = False
                                break
                            elif np.any(P[:, (b, c)]):
                                break
                            PN += P
                    # end connectedness testing

                    if rewire:  # reassign edges
                        R[a, d] = R[a, b]
                        R[a, b] = 0
                        R[d, a] = R[b, a]
                        R[b, a] = 0
                        R[c, b] = R[c, d]
                        R[c, d] = 0
                        R[b, c] = R[d, c]
                        R[d, c] = 0

                        j.setflags(write=True)
                        j[e1] = d
                        j[e2] = b
                        eff += 1
                        break
            att += 1

    Rlatt = R[np.ix_(ind_rp[::-1], ind_rp[::-1])]
    return Rlatt, R, ind_rp, eff

def randmio_und_connected(R, itr):
    '''
    This function randomizes an undirected network, while preserving the
    degree distribution. The function does not preserve the strength
    distribution in weighted networks. The function also ensures that the
    randomized network maintains connectedness, the ability for every node
    to reach every other node in the network. The input network for this
    function must be connected.
    NOTE the changes to the BCT matlab function of the same name 
    made in the Jan 2016 release 
    have not been propagated to this function because of substantially
    decreased time efficiency in the implementation. Expect these changes
    to be merged eventually.
    Parameters
    ----------
    W : NxN np.ndarray
        undirected binary/weighted connection matrix
    itr : int
        rewiring parameter. Each edge is rewired approximately itr times.
    Returns
    -------
    R : NxN np.ndarray
        randomized network
    eff : int
        number of actual rewirings carried out
    '''
    if not np.all(R == R.T):
        raise BCTParamError("Input must be undirected")

    #if number_of_components(R) > 1:
     #   raise BCTParamError("Input is not connected")

    R = R.copy()
    n = len(R)
    i, j = np.where(np.tril(R))
    k = len(i)
    itr *= k

    # maximum number of rewiring attempts per iteration
    max_attempts = np.round(n * k / (n * (n - 1)))
    # actual number of successful rewirings
    eff = 0

    for it in range(int(itr)):
        att = 0
        while att <= max_attempts:  # while not rewired
            rewire = True
            while True:
                e1 = np.random.randint(k)
                e2 = np.random.randint(k)
                while e1 == e2:
                    e2 = np.random.randint(k)
                a = i[e1]
                b = j[e1]
                c = i[e2]
                d = j[e2]

                if a != c and a != d and b != c and b != d:
                    break  # all 4 vertices must be different

            if np.random.random() > .5:

                i.setflags(write=True)
                j.setflags(write=True)
                i[e2] = d
                j[e2] = c  # flip edge c-d with 50% probability
                c = i[e2]
                d = j[e2]  # to explore all potential rewirings

            # rewiring condition
            if not (R[a, d] or R[c, b]):
                # connectedness condition
                if not (R[a, c] or R[b, d]):
                    P = R[(a, d), :].copy()
                    P[0, b] = 0
                    P[1, c] = 0
                    PN = P.copy()
                    PN[:, d] = 1
                    PN[:, a] = 1
                    while True:
                        P[0, :] = np.any(R[P[0, :] != 0, :], axis=0)
                        P[1, :] = np.any(R[P[1, :] != 0, :], axis=0)
                        P *= np.logical_not(PN)
                        if not np.all(np.any(P, axis=1)):
                            rewire = False
                            break
                        elif np.any(P[:, (b, c)]):
                            break
                        PN += P
                # end connectedness testing

                if rewire:
                    R[a, d] = R[a, b]
                    R[a, b] = 0
                    R[d, a] = R[b, a]
                    R[b, a] = 0
                    R[c, b] = R[c, d]
                    R[c, d] = 0
                    R[b, c] = R[d, c]
                    R[d, c] = 0

                    j.setflags(write=True)
                    j[e1] = d
                    j[e2] = b  # reassign edge indices
                    eff += 1
                    break
            att += 1

    return R, eff

def wrap_bct(g, func, **args):
    g = get_cluster(g,'animal:N')
    
    d = g.get_adjacency(attribute='distance')
    #d = np.matrix(d.data)    
    d = np.array(d.data)
    
    l = func(d, **args)
    
    f = Graph.Weighted_Adjacency( l[0].tolist() , mode='undirected', attr='distance',loops=False )
    
    f.vs['label']=g.vs['label']
    f.es['similarity'] = [1-x for x in f.es['distance']]
    
    return f

#def local_cc_undirected(g):
#    return 2*mean([c /(float(c)*(c-1)) if c > 1 else 0 for c in g.vs.outdegree()])

def rewire_randomize(g, itr, times = 1):
    g = get_cluster(g,'animal:N')
    
    d = g.get_adjacency(attribute='distance')
    #d = np.matrix(d.data)    
    d = np.array(d.data)
    
    #l = wrap_bct(g, latmio_und_connected, itr=itr) 
    l = randmio_und_connected(d,itr)    
    
    f = Graph.Weighted_Adjacency( l[0].tolist() , mode='undirected', attr='distance',loops=False )
    
    f.vs['label']=g.vs['label']
    f.es['similarity'] = [1-x for x in f.es['distance']]
    
    return f
    

def rewire_latticize(g,itr):
    g = get_cluster(g,'animal:N')
    
    d = g.get_adjacency(attribute='distance')
    #d = np.matrix(d.data)    
    d = np.array(d.data)
    
    #l = wrap_bct(g, latmio_und_connected, itr=itr) 
    l = latmio_und_connected(d,itr)    
    
    f = Graph.Weighted_Adjacency( l[0].tolist() , mode='undirected', attr='distance',loops=False )
    
    f.vs['label']=g.vs['label']
    f.es['similarity'] = [1-x for x in f.es['distance']]
    
    return f

def rewire_latticize_telesford(g,times = 0):
    g = get_cluster(g,'animal:N')
    
    d = g.get_adjacency(attribute='distance')
    #d = np.matrix(d.data)    
    d = np.array(d.data)
    
    #l = wrap_bct(g, latmio_und_connected, itr=itr) 
    q,  _x,_y,_z = latmio_und_connected(d,5)    
    
    l_best = Graph.Weighted_Adjacency( q.tolist() , mode='undirected', attr='distance',loops=False )
    q_best = q
    l_best_cc = np.mean( l_best.transitivity_local_undirected(mode='zero') )
    print str(l_best_cc) + '*'
    
    act_times = 0
    while act_times < times:
        
        q,  _x,_y,_z = latmio_und_connected(q_best,5) #doesn't work when only 1 itr
        
        l = Graph.Weighted_Adjacency( q.tolist() , mode='undirected', attr='distance',loops=False )
            
        l_cc = np.mean( l.transitivity_local_undirected(mode='zero') )
        print l_cc
        if l_cc >= l_best_cc:
            print '*'
            
            l_best = l
            q_best = q
            l_best_cc = l_cc            
        
        act_times += 1
        #print act_times
        
    #l_best.vs['label']=g.vs['label']
    #l_best.es['similarity'] = [1-x for x in l_best.es['distance']]
    
    return l_best
    

def mean_no_zero(a):
    '''List -> float
       float -> float
    Return the average of a list of numbers, excluding None values. If a is a number, return a.
    '''
    if type(a) is float or type(a) is int:
        return a
    return np.mean([[j for j in i if j != None and j != 0] for i in a if i != None and i != 0])


def calculate_omega(g,name='graph',itr_r=600,itr_l=600,save_graph=True):
    '''Omega is an alternative measure of small-worldness as introduced in "The Ubiquity of Small-world Networks (Telesford et al.)".
    
    c is the average local clustering coefficient (transitivity).
    l is the characteristic path length.
    
    No subscript refers to original graph. Subscript rand refers to a random graph that preserves the original degree distribution. Subscript latt refers to a lattice network.
    
    omega = l_rand / l - c / c_latt
    '''
        
    ###measurements from original graph
    l = np.mean( g.shortest_paths_dijkstra() ) #exclude path lengths of 0 because this trivially refers to the path to the source node itself?
    c = np.mean( g.transitivity_local_undirected(mode='zero') )
    
    ###random network, preserving degree distribution
    rand = rewire_randomize(g,itr=itr_r,times=1)    
    #rand.rewire(n=1000,mode='simple')
    l_rand = np.mean( rand.shortest_paths_dijkstra() )
    c_rand = np.mean( rand.transitivity_local_undirected(mode='zero') )
    if save_graph:
        fname = str(itr_r)+'_'+name
        write_graphml(rand,'rand/'+fname+'.graphml')
        plot_graph(rand,'rand_'+fname)
    
    ###lattice network
    latt = rewire_latticize(g,itr=itr_l)
    #latt = rewire_latticize_telesford(g,times = itr_l)
    l_latt = np.mean( latt.shortest_paths_dijkstra() )
    c_latt = np.mean( latt.transitivity_local_undirected(mode='zero') )
    if save_graph:
        fname = str(itr_l)+'_'+name
        write_graphml(latt,'lattice/'+fname+'.graphml')
        plot_graph(latt,'latt_'+fname)    
    
    ###write to file
    with open('omg/'+name+'.txt','wb') as f:
        lines= [
    "l_rand: %.2f" % l_rand,
    #print "c_rand: %.2f" % c_rand
    
     "     l: %.2f" % l
    , "lratio: %.2f" % float(l_rand/l)
    , ''
    , "     c: %.2f" % c
    , "c_latt: %.2f" % c_latt
    , "cratio: %.2f" % float(c/c_latt)
    , ''
    , " omega: %.2f" % float(l_rand / l - c / c_latt) 
    ]
        f.write('\n'.join(lines))

    
    return l_rand / l - c / c_latt


if __name__ == "__main__":  
    names = ['gold_af_HILLS_SHARED_0.8_A0.4','BEAGLE_HILLS_SHARED_0.5_A0.4']
    names = ['gold_af_HILLS_SHARED','animals_learner','BEAGLE_HILLS_SHARED']
    
    #plot_omega_irt('animals_learner_af')
    
    
    #itr = 5
    for name in names:
        #g = get_model(name)
        #g = get_cluster(g,'animal:N')
        #print ''
        #print name
        #print '----------------'
        #calculate_omega(g)
        generate_omg_curve(name)
        #generate_adj_rand_curve(name)
        plt.show()

    '''
    for name in names:
        X = []
        Y = []        
        g = get_model(name)
        g = get_cluster(g,'animal:N')   
        
        #print ''
        #print name
        #print '----------------'        
        
        for itr in np.arange(0,1000,50):
            X.append(itr)
            #print ' itr: ' + str(itr)
            Y.append( calculate_omega( g,itr_l=itr,itr_r = 200 ) )
            
        plot_scatter(X,Y,0,x_lab='itr',y_lab='cc',title=name,color=['blue' for i in range(0,len(X))] )
        plt.show()
    '''
    '''
    g = get_cluster(g,'animal:N')

    d = g.get_adjacency(attribute='distance')
    #d = np.matrix(d.data)    
    d = np.array(d.data)
    
    l = latmio_und_connected(d,1)
    
    #f = g.copy()
    #f.es['distance'] = l[0].tolist()
    f = g.Weighted_Adjacency( l[0].tolist() , mode='undirected', attr='distance',loops=False )
    
    '''
    
    #f = rewire_latticize(g,itr)
    
    #plot_graph(f,name+"_latticized")
    
