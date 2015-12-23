import os
from core.wgraph import *

sim = 0.7
g = WordsGraph(20,sim,'hub-categories-prob-random',0,0.00001,20,0,1,'map')

for gg in os.listdir('graphs/'):
     WordsGraph.calc_small_worldness(g,load_graph('graphs/'+gg,fmt='xml'),gg)
