import os,sys
p = os.path.abspath('../')
# next line adds the directory to a path which "imports" searches for files.
# Alternatively, this path could be added to PYTHONPATH.
sys.path.append(p) 
os.chdir('../')

import core.learn as learn
import core.learnconfig as config
import core.plot as plot
import core.input as corpus

if __name__ == "__main__":
    
    base_config = config.LearnerConfig('config.ini')
    
    learner = learn.Learner('data/all_catf_norm_prob_lexicon_cs.all',base_config)
    
    learner.process_corpus('data/input_wn_fu_cs_scaled_categ.dev','./output')    
    
    plot.plot_avg_acquisition_score('./output/time_props_itr_{}.csv'.format(learner._time),'.',learner._time,learner.get_lambda())
