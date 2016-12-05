import os
#from rw import *
from graph_tool.all import *
from core.wgraph import *
from animals import *
#m = get_models()

wg = WordsGraph(20,0.7,'hub-categories-prob-random',0,0.00001,20,0,1,'map')

in_dir = 'graphs/'
out_dir = 'swc_latest/'

files = os.listdir(in_dir)

for path in files:
    if 'graphml' in path:
        graph = load_graph(in_dir+path,fmt='xml')
	del_list = []
	#animal word condition
	for i in range(0,graph.num_vertices()):
	    if graph.vertex_properties['label'][i] not in A_NAME.keys()+['animal:N']:
		del_list.append(i)

	l,x = label_components(graph)
	# find component containing animal
	a_comp = l.a[ [i for i in range(0,graph.num_vertices()) if graph.vertex_properties['label'][i] == 'animal:N' ][0] ]
	#u = GraphView(graph, vfilt=l)

	for i in range(0,graph.num_vertices()):
	    #connectivity condition
	    if l.a[i] != a_comp:
		del_list.append(i)

	graph.remove_vertex(set(del_list))

        #make sure there are no unlearned
        print path
        #es = find_edge(graph, graph.ep['distance'],0.0)
        #if es is not []:
        #       print "Deleting unlearned words from {}.".format(path)
        #       #continue
        #       del_list = set()
        #       for e in es:
        #               del_list.add(e.source())
        #               del_list.add(e.target())
        #       for d in reversed(list(del_list)):
        #               graph.remove_vertex(d)
        if os.path.isfile(out_dir + path + '.txt'):
                print path + ' already calculated, skipping.'
                continue

        try:
                wg.calc_small_worldness(graph,out_dir+path)
        except Exception as e:
                print e
		continue
