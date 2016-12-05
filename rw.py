from animals import *
from generate_animal_graphs import *
from numpy.random import seed,choice
import random
#from core.graph_tool_igraph import *
from igraph import *
from itertools import groupby
import itertools
import pylab,scipy
import csv,re
import os
from mpl_toolkits.mplot3d import Axes3D,proj3d
from matplotlib import cm,markers
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from matplotlib._png import read_png
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from clustering import *
from plotting import *

#suppress figure generation until plt.show() called
plt.ioff()

#number of iterations of random walks to average per experiment
ITR = 282


def mean(a):
    '''List -> float
       float -> float
    Return the average of a list of numbers, excluding None values. If a is a number, return a.
    '''
    if type(a) is float or type(a) is int:
        return a
    return np.mean([i for i in a if i != None])


def a_len(a):
    '''List -> int
    Return the length of a list excluding None values.
    '''
    return len([i for i in a if i != None])


####################
### RANDOM WALKS ###
####################

def random_walk_possible(g):
    '''For a given graph g, determine if a random walk starting at 'animal:N' is possible.
    Criteria: 'animal:N' exists and has neighbors.
    '''
    start = 'animal:N'
    
    g = get_cluster(g,start)
    if g == None:
        return False
        #return a,b,cat,title, full_paths,full_cats
    elif len(g.neighbors(g.vs.find(label=start).index)) == 0:
        return False
    
    return True
    

def random_walk_trial(g,m,weight_opt,walk_length,restart=None):
    '''Wrapper function to conduct a random walk as many times as ITR.'''
    #if animal not in network or connected to anything, skip
    '''
    start = 'animal:N'
    
    g = g.get_cluster(start)
    if g == None:
        return None
        #return a,b,cat,title, full_paths,full_cats
    elif len(g.neighbors(g.vs.find(label=start).index)) == 0:
        return None
        #return a,b,cat,title, full_paths,full_cats
    '''
    
    #print "test " + str(g)
    b=[]
    cat=[]
    a=[]    
    
    full_cats = []
    full_paths = []
    
    title = "_".join([m,str(weight_opt),str(ITR),str(walk_length),'restart '+str(restart) if restart else ''])

    for i in range(0,ITR):
        
        b_i,c_i,a_i,f_p,c_f = gen_random_walk(g=g,weighted=weight_opt,log_file=title,stop=walk_length,restart=restart,name=title)
        
        b.append(b_i)
        cat.append(c_i)
        a.append(a_i)
        
        full_cats.append(c_f)
        full_paths.append(f_p)
        
    #log the trial
    #write_summary(title,a,cat,walk_length)
    #precision_recall(g,title)
        
    return a,b,cat,title, full_paths,full_cats


def get_walk_length(name):
    '''Str -> int
    Return the walk length for a particular graph.
    '''
    name=name.lower()
    if 'gold_af' in name:
        return 50
    elif 'learner_af' in name:
        return 95
    elif 'beagle_shared' in name:
        return 45
    elif 'beagle' in name:
        return 70

def gen_random_walk(g,weighted=True, log_file='',itr=1,name='',stop=None,restart=0):
    '''Perform a single random walk and determine the categories of each word.'''

    start = 'animal:N'    
    
    g = get_cluster(g,start)
    
    a,rwalk,b = genX(g,s=start,use_irts=1,weighted=weighted,stop=stop,restart=restart)
    
    a_names = g.vs[a]['label']
    #a_categories = [SHARED_HILLS_POS_CATEG_NUM.get(i,-1) for i in g.vs[a]['label']]
    #a_cat_changed = [1 if a_categories[i-1] != a_categories[i] else 0 for i in range(1,len(a_categories))]
    
    
    ##calculate whether category changes as per Abbott et al.
    cat = get_fluid_cat_switches(a_names,start)
                
                
    full_path = [g.vs['label'][rwalk[0][0]]] +  [g.vs['label'][z[1]] for z in rwalk]
    
    cat_full = get_fluid_cat_switches(full_path,start)
    
    ##LOG
    '''
    #append to logfile
    if log_file:
        with open(log_file + '.txt','a') as f:
            lines = 'Walk #:' + 'Weighted: ' + str(weighted),'Full Path: [' + ', '.join(full_path) + ']\n'+'IRTS:'+str(b)+'\nWords: ' + str(a_names), 'Categ: ' + str(cat)
            #print '\n'.join(lines)+'\n\n'
            #print b
            f.write('\n'.join(lines)+'\n\n')
    '''
            
    #cats_altered = [c for i,c in zip(full_path,cat_full) if i
            
    return b,cat,a,full_path,cat_full


def random_walk_am(g,start=None,seed=None,weighted=False,stop=None,restart=0):
    '''Perform a random walk on adjacency matrix g.'''
    #seed(seed)
       
    #if type(start) == str:
    #    try:
    #        start = g.vs.find(label=start).index
    #    except Exception as e:
    #        start=random.choice(range(g.vcount()))
        
    assert type(start) == int

    walk=[]
    unused_nodes=set(range(len(g)))
    unused_nodes.remove(start)
    s = start
    count = 0
    while len(unused_nodes) > 0:
        _p=start            
        neighbors = [i for i,jj in enumerate(g[start,:]) if jj != 0]
        if weighted==False:
            start=choice(neighbors) # follow random edge
        else:
            weights = g[start,neighbors]
            #distances = g.es[neighboring_edges]['distance']
            #weights = [1-i for i in distances]
            total = np.sum(weights)
            normalized_weights = np.divide(weights,total)
            
            start=choice(neighbors,p=normalized_weights)
            
        walk.append((_p,start))
        if start in unused_nodes:
            unused_nodes.remove(start)
            
        if restart:
            if np.random.binomial(1,restart):
                start = s 
        if stop:
            if count >= stop:
                break

        count +=1
    return walk
    
def random_walk(g,start=None,seed=None,weighted=False,stop=None,restart=0):
    '''Perform a random walk on graph g.'''
    #seed(seed)
       
    if type(start) == str:
        try:
            start = g.vs.find(label=start).index
        except Exception as e:
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
            
        if restart:
            if np.random.binomial(1,restart):
                start = s 
        if stop:
            if count >= stop:
                break

        count +=1
    return walk

## Random walk methods modified from https://github.com/AusterweilLab/randomwalk

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
        return Xs,rwalk
    else:
        fh=list(zip(*firstHits(rwalk))[1])
        irts=[fh[i]-fh[i-1] for i in range(1,len(fh))]
        return Xs,rwalk,irts


#####################################
### DETERMINING CATEGORY SWITCHES ###
#####################################


def get_fluid_cat_switches(a_names,start):
    ##calculate whether category changes as per Abbott et al.: i.e., category switch only when next word has no categories in common with previous word.
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
                if n == 'animal:N' or a_names[i-1] == 'animal:N': #or n == 'billy_goat:N' or a_names[i-1] == 'billy_goat:N':
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
    return cat

######################
### CALCULATE IRTs ###
######################

def create_irt_graph(b,cat,multi=False):
    '''Determine the IRT for patch entry positions normalized to the average long-term IRT within one trial.'''
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


def irt_self_longterm_avg(b,cat,multi=True):
    '''Determine IRTs for each patch entry positions using fluid categories normalized to the long-term average IRT accross all trials in the experiment.'''
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
            
            for j,kk in enumerate(w):
                
                if kk >= max(w):
                    to_next=0
                elif kk == None:
                    continue
                    #print 'Error: list index'
                else:
                    next_cat = w.index(kk+1)             
                    to_next = next_cat - j
                
                neg_order.append(-to_next)
                
                same_cat = w.index(kk)
                
                to_same = j - same_cat + 1
                
                pos_order.append(to_same)
                
            n.append(neg_order)
            p.append(pos_order)

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
                        
def write_summary(title,a,c,itr):
    with open(title+'_summary.txt','a') as l:
        l.write('\n----------------------------------\n')
        l.write('SUMMARY STATISTICS:')
        l.write('\n----------------------------------\n')   
        avg_words = [mean(a_len(z)) for z in c]
        avg_patch_switch = [q[-1:][0] for q in c]
        avg_itm_ptch = [mean([len(list(group)) for key, group in groupby(m)]) for m in c]
        l.write('Avg words: {0:.3f} (SD {1:.3f})\n'.format(mean(avg_words),scipy.stats.tstd(avg_words)))
        l.write('Avg backtracking: {0:.3f}\n'.format(itr-mean(avg_words)))
        l.write('Avg patch switches: {0:.3f} (SD {1:.3f})\n'.format(mean(avg_patch_switch),scipy.stats.tstd(avg_patch_switch)))
        l.write('Avg itms/patch: {0:.3f} (SD {1:.3f})\n'.format(mean(avg_itm_ptch),scipy.stats.tstd(avg_itm_ptch)))    
        


def has_irt_pattern(irts,binned_final,binned_sem,weak=False):
    '''Determine whether IRTs conform to the expected pattern observed in human data. If weak = True, use less stringesnt cut-offs for the first and last patch entry positions.
    Return 2 for yes,
    1 for yes but weak (see above),
    0 for no.'''
    upper = 1.2
    lower = 0.8
    
    if weak:
        upper = 1.1
        lower = 0.9
    
    lt_average = mean([mean(irt) for irt in irts])
    lt_sem = scipy.stats.sem([mean(irt)/lt_average for irt in irts])
    
    #print 'LT_SEM: ' + str(lt_sem)
    
    for i,v in binned_final.items():
        #check if items before patch entry are below 1
        
        #we exclude 0 because it represents the last category visited when calculating negative patch entries (i.e. [-1,-2,-3,0,0]
        if i == 0:
            continue
        
        #print i,v-binned_sem[i]
        
        if i == 1:
            if v+binned_sem[i] < upper:
                return False
        elif i in np.arange(-4,3,1): 
            if v-binned_sem[i] > 1+lt_sem:
                return False
            #check that second patch entry item is at least 0.8
            if i == 2 and v-binned_sem[i] > lower:
                return False
        #make sure first patch entry item is at least 1.2

    return True


def plot_irt(a,b,cat,title):
    '''Create a plot of IRTs.'''
    binned_final,binned_sem = irt_self_longterm_avg(b,cat,multi=True)
    
    r = [-3,-2,-1,1,2,3,4]
    
    x = range(0,7)
    #y = scipy.array([binned_final.get(i,None) for i in r])
    #yerr=[binned_sem.get(i,None) for i in r]
    y = scipy.array([binned_final.get(i,0) for i in r])
    yerr=[binned_sem.get(i,0) for i in r]    
    f = pylab.figure()
    #merge in one figure (TODO not working)
    ##pylab.subplot(x_dim,y_dim,p)                    
    ax = f.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.bar(x, y, align='center')
    ax.set_xticks(x)
    ax.set_xticklabels(r)
    ax.set_xlabel('Patch Entry Position')
    ax.set_ylabel('Average IRT/Long-term Average IRT')
    ax.set_title(title+' avg-words:'+str(mean([mean(a_len(z)) for z in cat])))
    pylab.plot([-1,7],[1,1])        
    ax.errorbar(x, y, yerr=yerr, fmt='o')
    #f.show()
    f.savefig('irts/'+title+'.png')
    
    
## scrap method for visualizing IRTs on parameter charts. Didn't work very well.
    
def annotate_curve_IRTs(fig,xs,ys,zs,prefix):
    '''Produce 3-dimensional plot with IRTs on graph.'''
    if not fig:
        return None
    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection = '3d')
    ax = fig.get_axes()[0]
    #points = np.array([(1,1,1), (2,2,2)])
    plotlabels = []
    #xs, ys, zs = np.split(points, 3, axis=1)
    #sc = ax.scatter(xs,ys,zs)

    for x, y, z in zip(xs, ys, zs):
        x2, y2, _ = proj3d.proj_transform(x,y,z, ax.get_proj())
        
        ##get image
        #fn = get_sample_data("grace_hopper.png", asfileobj=False)
        
        png_name= '_'.join(prefix+[str(y),'A'+str(x)])
        
        arr_lena = read_png('irts/'+png_name+'.png')
    
        imagebox = OffsetImage(arr_lena, zoom=0.2)
                                #
#
        ab = AnnotationBbox(imagebox, xy=(x2,y2),
                            xybox=(100., -60.),
                            xycoords='data',boxcoords="offset points",   pad=0.5,arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=90,rad=3"))    
        ax.add_artist(ab)
        
        ab.draggable()  
    
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)    
        #get image
        
        label = ab #plt.annotate(
            #txt, xy = (x2, y2), xytext = (-20, 20),
            #textcoords = 'offset points', ha = 'right', va = 'bottom',
            #bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
            #arrowprops = dict(arrowstyle = '-', connectionstyle = 'arc3,rad=0'))
        plotlabels.append(label)
    fig.canvas.mpl_connect('motion_notify_event', lambda event: update_position(event,fig,ax,zip(plotlabels, xs, ys, zs)))
    #plt.show()

def update_position(e,fig,ax,labels_and_points):
    '''Update position of labels on event e. Used by annotate_curve_IRTs.'''
    for label, x, y, z in labels_and_points:
        x2, y2, _ = proj3d.proj_transform(x, y, z, ax.get_proj())
        label.xy = x2,y2
        label.update_positions(fig.canvas.renderer)
    fig.canvas.draw()