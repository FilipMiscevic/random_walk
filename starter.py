from rw import *

if __name__ == '__main__':
    
    #Load models to test
    #nn=['all_dev_utt_learner_af_HILLS_SHARED_0.8_A0.4','gold_af_HILLS_SHARED_0.85_A0.45']
    names=['learner_af_78000']
    
        
    models = get_models(like='learner_af_78000',a_filter=False)
    
    
    weight_opts = {'wrw':True,'rw':False}
    restarts = {'restart':0.05,'':0}
    walk_lengths = np.arange(50,150,10) #can specify a range, i.e. np.arange(10,95,5)
    
    ##set up multiple plots (TODO)
    tot_plts = len(weight_opts)*len(restarts)*len(walk_lengths)
    x_dim = tot_plts/2
    y_dim = tot_plts-x_dim
    #plot_coord = [ [i,j] for i in range(0,x_dim) for j in range(0,y_dim)]

    ff=None
    markers=['o','x','.','+',',','*']
    for s,m in enumerate(models):
        #p=-1        
        if random_walk_possible(models[m]):
            for weight_opt in weight_opts:
                for rstrt in restarts:
                    wp = []
                    
                    for walk_length in walk_lengths:
                        #p+=1
                        
                        print models[m],m
                        
                        a,b,cat,title,full_paths,_full_cats = random_walk_trial(models[m],m,weight_opts[weight_opt],walk_length,restarts[rstrt])
                            
                        plot_irt(a,b,cat,title)
                        
                        wp.append(mean([mean(a_len(z)) for z in a]))
                        nodes = get_cluster(models[m],'animal:N').vcount()
                        
                        print title
                        
                        write_summary(title,a,cat,walk_length)
                        
                    if ff is None:
                        ff,ax = plot_scatter(walk_lengths,wp,None,x_lab='walk length',y_lab='words produced',title='Words produced',label=title+'NODES_{}'.format(nodes) )
                    else:
                        ax.scatter(walk_lengths,wp,label=title+'NODES_{}'.format(nodes),marker=markers[s])