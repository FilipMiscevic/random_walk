import core.learn as learn
import core.learnconfig as config
import core.plot as plot
import core.input as corpus

if __name__ == "__main__":
    
    base_config = config.LearnerConfig('config.ini')
    
    learner = learn.Learner('data/lexicon_cs.all',base_config)
    
    learner.process_corpus('data/input_fu_cs.dev','./output')    
    
    plot.plot_avg_acquisition_score('./output/time_props_itr_{}.csv'.format(learner._time),'.',learner._time,learner.get_lambda())
