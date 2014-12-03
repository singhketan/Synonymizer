import nltk
from nltk.wsd import lesk
from nltk.corpus import stopwords
from nltk.corpus import brown, senseval
from nltk.corpus import wordnet as wn
from nltk.probability import *
import pattern.en
import operator
from nltk.corpus import lin_thesaurus as thes
import pywsd.lesk as pylesk

#estimator1 = lambda fdist, bins: LidstoneProbDist(fdist, 0.2)
#lm = nGramModel.NgramModel(2, brown.words(), estimator = estimator1)
#print lm.prob("good", ["very"])         
#print lm.prob("good", ["not"])          
#print lm.prob("good", ["unknown_term"])

def ourLesk(sentence, word, pos1, forceResponse = False):
	
	leskList = []
	if pos is not None:
		possibility1 = pylesk.cosine_lesk(sentence, word, pos1)
		possibility2 = pylesk.adapted_lesk(sentence, word)
		
	else:
		possibility1 = pylesk.cosine_lesk(sentence, word)
		possibility2 = pylesk.adapted_lesk(sentence, word)

	
	if possibility1 is not None and possibility2 is not None:
		possibility1 = [str(lemma.name()) for lemma in possibility1.lemmas()]
		possibility2 = [str(lemma.name()) for lemma in possibility2.lemmas()]
		leskList = set(possibility1).intersection(possibility2)
	else:
		if possibility1 is None:
			if possibility2 is not None:
				leskList = [str(lemma.name()) for lemma in possibility2.lemmas()]
			else:
				return None
		else:
			leskList = [str(lemma.name()) for lemma in possibility1.lemmas()]

	
	if len(leskList) > 0:
		print "-------"
		print word
		print leskList
		return list(leskList)
	else:
		return None

def getRightSyns(word, tokenized, pos1, sentence, fdist):
	pos = pos1[0:2]
	corelationDict = {'VB':wn.VERB, 'JJ':wn.ADJ, 'RB':wn.ADV,'NN':wn.NOUN}
	otherDict = {'VB':'v', 'JJ':'a', 'RB':'r','NN':'n'}

	if (pos in otherDict) and fdist[word] > 1:
		myPos = otherDict[pos]
		returnList = ourLesk(sentence, word, myPos, False)
		finalReturnList = []
		if returnList is not None:
			return returnList
		else:
			return None
	else:
		return None
		
def getRightSyns2(word, tokenized, pos1, sentence, fdist):
	pos = pos1[0:2]
	otherDict = {'VB':"simV.lsp", 'JJ':"simA.lsp", 'RB':"simA.lsp",'NN':"simN.lsp"}
	toReturn = None
	if (pos in otherDict):
		myPos = otherDict[pos]
		source = ourLesk(sentence, word, None)
		
		
		if source is not None:
			synonyms = sorted(thes.scored_synonyms(word, fileid = myPos),key=lambda x: x[1], reverse=True)[0:9]
			if len(synonyms) > 0:
				
				finalList = []
				for synonym in synonyms:
					
					code = ourLesk(sentence, synonym[0], None)
					if code is not None:
						if source == code:
							finalList.append(synonym[0])
				if len(finalList) != 0:
					
					toReturn = finalList

	return toReturn	
	
def getRightSyns3(word, tokenized, pos1, sentence, fdist):
	pos = pos1[0:2]
	otherDict = {'VB':"simV.lsp", 'JJ':"simA.lsp", 'RB':"simA.lsp",'NN':"simN.lsp"}
	
	if pos in otherDict:
		myPos = otherDict[pos]
		
		synonyms = sorted(thes.scored_synonyms(word, fileid = myPos),key=lambda x: x[1], reverse=True)[0:4]
		if len(synonyms) > 0:
			return [synonym[0] for synonym in synonyms]
		else:
			return None
	else:
		return None
	
def correctPartOfSpeech(originalTuple, replacementWord, tokenized):
	finalReplacement = replacementWord
	originalWord = originalTuple[0]
	
	
	if replacementWord != originalWord:
		

		posFirstChar = originalTuple[1][0]
		lastChar = originalTuple[1][-1]

		
		if (posFirstChar == "V"):
			finalReplacement = pattern.en.conjugate(replacementWord, str(originalTuple[1]))
			
		if (posFirstChar == "J" or posFirstChar == "R" ):
			if lastChar == "R":
				finalReplacement = pattern.en.comparative(replacementWord)
			if lastChar == "S":
				finalReplacement = pattern.en.superlative(replacementWord)
				
		if (posFirstChar == "N" and lastChar == "S"):
			finalReplacement = pattern.en.pluralize(replacementWord)
		
	return finalReplacement
	
def cleanEntitiesList(pos_tokens, tokenized):
	
	bgs = nltk.bigrams(tokenized)
	tgs = nltk.trigrams(tokenized)
	punctuations = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~']
	count = 0
	namedEntities = []
	for entity in nltk.ne_chunk(pos_tokens):
		if len(entity) == 1:
			del tokenized[count]
			count = count - 1
			namedEntities.append(entity[0][0].lower())
		count = count + 1

	tokenized =  [i for i in tokenized if i not in stopwords.words('english')+punctuations]
	
	
	fdistBgs = nltk.FreqDist(bgs)
	fdistTgs = nltk.FreqDist(tgs)
	
	for k,v in fdistTgs.items():
		print k,v
	
	overriderDict = []
	return tokenized, namedEntities, overriderDict
	
def chooseFinalSynonym(pair, synonyms, tokenized, fdist, difficulty="normal"):

	word = pair[0]
	originalCount = fdist[word]

	myDict = {}
	finalWord = word
	if synonyms is not None:
		for candidate in synonyms:
			
			
			cleanedCandidate = correctPartOfSpeech(pair, candidate, tokenized)
			
			score = fdist[cleanedCandidate.replace("_", " ")]
			
			cleanedCandidate =  cleanedCandidate.replace("_", "-")
			go = False
			if cleanedCandidate != word:
				
				if difficulty == "difficult":
					if score <= originalCount:
						go = True
				if difficulty == "easy":
					if score >= originalCount:
						go = True
				if difficulty == "normal":
					go = True
						
				if go == True:
					myDict[cleanedCandidate] = score

		if any(myDict):
			finalWord = min(myDict.iteritems(), key=operator.itemgetter(1))[0]

	return finalWord

def appendNewWord(finalString, word):
	punctuations = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', "'s"]
	if word in punctuations:
		finalString = finalString + word
	else:
		finalString = finalString + " " +word
	return finalString
	
def finalCleaning(word, namedEntities, count):
	if word in namedEntities or count == 0:
		return word.title()
	else:
		return word

corelationDict = {'VB':wn.VERB, 'JJ':wn.ADJ, 'RB':wn.ADV,'NN':wn.NOUN}



finalString = ""	


with open ("theText.txt", "r") as myfile:
	text=myfile.read().replace('\n', '')



fdist = nltk.probability.FreqDist(brown.words())
for sentence in nltk.sent_tokenize(text):
	
	tokenized = nltk.word_tokenize(sentence)
	
	#bgs = nltk.bigrams(tokens)
	#bgs = nltk.bigrams(tokens)
	
	ourList = nltk.pos_tag(tokenized)
	replacementCandidates, namedEntities, overriderDict = cleanEntitiesList(ourList, tokenized)

	count = 0
	for pair in ourList:
		
		word = pair[0].lower()
	
		pos = pair[1]
		if word not in replacementCandidates:
			appender = word
		else:

			
			if word not in overriderDict:
				synonyms = getRightSyns(word, tokenized, pos, sentence, fdist)
			else:
				synonyms = overriderDict[word]
			
			finalSynonym = chooseFinalSynonym(pair, synonyms, tokenized, fdist, "difficult")
			appender = finalSynonym
			

		appender = finalCleaning(appender, namedEntities, count)
		finalString = appendNewWord(finalString, appender)
		count = count + 1	
		
finalString = finalString.strip()		
print finalString

text_file = open("Output.txt", "w")
text_file.write(finalString)
text_file.close()