import nltk
from nltk.collocations import *
bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()

# change this to read in your data
finder = BigramCollocationFinder.from_words(
   nltk.corpus.genesis.words("theText.txt"))

# only bigrams that appear 3+ times
finder.apply_freq_filter(3) 

# return the 10 n-grams with the highest PMI
finder.nbest(bigram_measures.pmi, 10)  