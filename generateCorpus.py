import os,sys
p = os.path.abspath('../')
# next line adds the directory to a path which "imports" searches for files.
# Alternatively, this path could be added to PYTHONPATH.
sys.path.append(p) 
os.chdir('../')

#!/usr/bin/X11/python

import sys, os
import getopt
import re
import random
import math
lib_path = os.path.abspath('../../aida_code_pre_2013/core')
# next line adds the directory to a path which "imports" searches for files.
# Alternatively, this path could be added to PYTHONPATH.
sys.path.append(lib_path) 
import lexicon
import wmmapping
import statistics

# --------------------------------------------- #
# --------------------------------------------- #
class InputCorpus:
    def __init__(self, name):
        self.name = name
        self.handle = open(self.name, 'r')

    def getNextUtterance(self):
        line = self.handle.readline()
        if line == "":
            return ("",[])
        else:
            utterance = line
            line = line.strip("\n")
            line = line + " "
            wordsL = re.findall("([^ ]+) ", line)
            return (utterance,wordsL)

    def close(self):
        self.handle.close()

# --------------------------------------------- #
#						usage					#
# --------------------------------------------- #
def usage():
   print "usage:"
   print "  main.py -i (--inputcorpus) -h (--help) -l (--inputlexicon) -c (--outputcorpus) -o (--outputlexicon) -d (--outdir) -m (--prims) -t (--type)"
   print ""
   print "  --inputfile: input file containing all MHARM features for ADJ and Function words"
   print "  --lexiconfile: output file containing features in desired lexicon format"
   print "  --outdir: output directory"
   print "  --help:    prints this usage"
   print ""

# --------------------------------------------- #
# --------------------------------------------- #
def getPoSTag(w):
    word_pos = w + ":"
    wpL = re.findall("([^:]+):", word_pos)
    return wpL[1]

# --------------------------------------------- #
# Swaps the probability of some of the relevant #
# features (those with high ratings) with some  #
# irrelevant features (those with low ratings). #                          
# --------------------------------------------- #
def SwapFeatures(primsLL):
    cutoff = 0.3    # swap half of the top 30% features with half of the bottom 30% ones
    N = len(primsLL)
    R = int(N * 0.3)
    chosenL = []
    # swap items in range(R) with those in range(N-R,N)
    if R <= 0:
        return
    for i in range(R):  # feature is relevant
        v,f = primsLL[i] 
        prob = float(v)
        swap_prob = random.random()                
        if swap_prob >= 0.5:  # then we swap this feature
            # choose a new random index from range(N-R,N)
            while 1:
                r = random.random()
                index = int(r * R + (N-R))
                if not index in chosenL:
                    break
            chosenL.append(index)
            # swap current prob @i with the prob in that index
            vp, fp = primsLL[index]
            primsLL[i] = [vp,f]
            primsLL[index] = [v,fp]

    return primsLL

# --------------------------------------------- #
# --------------------------------------------- #
def calculateSumInv(a, b, s):
    Sum = 0.0
    for i in range(a, b+1):
        Sum += 1.0 / math.pow(float(i), s)
    return Sum

# --------------------------------------------- #
# --------------------------------------------- #
def getRank(value, numbins):
    r = int((1.0-value) * numbins) + 1
    return r

# --------------------------------------------- #
#						main					#
# --------------------------------------------- #
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:l:c:o:d:m:t:", ["help", "inputcorpus=", "inputlexicon=", "outputcorpus=", "outputlexicon=", "outdir=", "prims=", "type="])
    except getopt.error, msg:
        print msg
        usage()
        sys.exit(2)

    if len(opts) < 7:
        usage()
        sys.exit(0)

    for o, a in opts: 
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        if o in ("-i", "--inputcorpus"):
            incorpus = a
        if o in ("-l", "--inputlexicon"):
            inlexicon = a
        if o in ("-c", "--outputcorpus"):
            outcorpus = a
        if o in ("-o", "--outputlexicon"):
            outlexicon = a
        if o in ("-d", "--outdir"):
            outdir = a
        if o in ("-m", "--prims"):
            M = int(a)
        if o in ("-t", "--type"):
            semtype = a


    # read the input lexicon file and store lexemes in a probabilistic lexicon in memory
    problex, truemeaning = lexicon.readAll(inlexicon, M)

    # open OUTPUT lexicon for writing
    outlexicon = outdir + "/" + outlexicon
    outLexiconH = open(outlexicon, 'w')

# -------------------------------------------------- #
#     linear rescaling
# -------------------------------------------------- #
    # rescale the ratings in the input lexicon, and write down the output lexicon
    for w in problex.getWords():
        line = w + " "
        outLexiconH.write(line)
        sumV = 0.0
        for v,f in problex.getSortedPrims(w):
            prob = float(v)
            sumV = sumV + prob 
        for v,f in problex.getSortedPrims(w):
            prob = float(v) / sumV
            line = "%s:%f," % (f,prob)
            outLexiconH.write(line)
        outLexiconH.write("\n\n")
    outLexiconH.close()

    # if generating broken input, modify probabilities in the input lexicon, problex
    # AIDA: here, I am replacing the original "FULL" problex with a new "BROKEN" one.
    #       You should probably change this, so you don't change the lexicon, but only
    #       do this when you are generating a scene representation for a particular token.
    if semtype == "BROKEN":
        for w in problex.getWords():
            postag = getPoSTag(w)
            if postag in ['V', 'N']:
                # randomly swap probabilities for relevant and irrelevant features
                primsLL = problex.getSortedPrims(w)
                SwapFeatures(primsLL)
                # modify the meaning of w in problex
                for v,f in primsLL:
                    problex.setValue(w,f,v)

    # read utterances from the input corpus, and generate a scene representation for each
    # utterance using the probabilistic lexicon problex
    indata = InputCorpus(incorpus)

    # open OUTPUT corpus for Writing
    outcorpus = outdir + "/" + outcorpus
    outCorpusH = open(outcorpus, 'w')

    (utterance, wordtagL) = indata.getNextUtterance()
    while not utterance=="":
        omit = 0
        scene = ""
        for w in wordtagL:
            if not w in problex.getWords():
                omit = 1
                break
            else: 
                #postag = getPoSTag(w)
                for v,f in problex.getSortedPrims(w):
                    prob = float(v)
                    r = random.random()                
                    if prob > r:
                        wsem = ",%s" % (f)
                        scene = scene + wsem

        # add the scene representation to the output corpus
        if not omit:
            outCorpusH.write("1-----\nSENTENCE: ")
            outCorpusH.write(utterance)
            outCorpusH.write("SEM_REP:  ")
            scene = scene + "\n"
            outCorpusH.write(scene)

        (utterance, wordtagL) = indata.getNextUtterance()

    indata.close()
    outCorpusH.close()


if __name__ == "__main__":
    main()
