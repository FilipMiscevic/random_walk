from rw import *

prefix = 'learner_af_78000'

test = get_model(prefix+'_0.4_A0.4',a_filter=False)

for i in [0.4,0.5,0.6,0.7,0.8,0.85]:
	for j in [0.4,0.5,0.6,0.7,0.8,0.85]:
		f = filter_edges(test, i)
		f = filter_edges(f,j,animal_edges='only')
		name = prefix+'_'+str(i)+'_A'+str(j)
		plot_graph(f,'plots/'+name)
		write_graphml(f,'graphs/'+name+'.graphml')
		print i
		g = get_model(name)
		write_graphml(g,'graphs/animals_'+name+'.graphml')
		plot_graph(g,'plots/animals_'+name)
