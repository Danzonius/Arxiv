import nltk, string
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.collocations import *
from collections import Counter
import codecs
from sklearn.feature_extraction.text import TfidfVectorizer

def stem_tokens(tokens):
	'''
		Returns a stemmed version of a document as a list.
	'''
	stemmer = nltk.stem.porter.PorterStemmer()
	return [stemmer.stem(item) for item in tokens]


def tokenize(text, lan='english'):
	'''
		Returns a normal tokenized version of a document as a list.
		Stopwords are excluded based on english as default language.
		The language can be specified.
	'''
	stops = stopwords.words(lan)
	sciencewords = ['review', 'harvard', 'business', 'october']
	lower = text.lower()
	ttable = {ord(c): None for c in string.punctuation}
	tokenized = nltk.word_tokenize(lower.translate(ttable))
	return [w for w in tokenized if w not in stops and w not in sciencewords]


def normalize(text):
	'''
		Returns a normalized version of a document as a list.
	'''
	ttable = {ord(c): None for c in string.punctuation}
	tokens = text.lower().translate(ttable)
	return stem_tokens(nltk.word_tokenize(tokens))


def cosine_sim(text1, text2):
	'''
		Returns cosine similarity between two documents.
	'''
	vectorizer = TfidfVectorizer(tokenizer=normalize, min_df=1)
	tfidf      = vectorizer.fit_transform([text1, text2])
	return ((tfidf * tfidf.T).A)[0,1]


def commons(text, n):
	'''
		Returns a list of the n most common words.
	'''
	counted = Counter(tokenize(text))
	return counted.most_common(n)


def phrase_finder(tokens, n, gram, t=1, *args):
	'''
		Returns the most common phrase from a tokenized collection.
		The amount of times it occurs in a text can be specified with n.
		You can also choose to pick bigrams.
	'''
	if gram == 'trigram':
		measure = nltk.collocations.TrigramAssocMeasures()
		finder  = TrigramCollocationFinder.from_words(tokens) 
	elif gram == 'bigram':
		measure = nltk.collocations.BigramAssocMeasures()
		finder  = BigramCollocationFinder.from_words(tokens)
	else:
		return 'Only bi- or trigrams are allowed.'

	# Apply a frequency filter based on n
	finder.apply_freq_filter(n)
	phrase = ' '.join([w for s in finder.nbest(measure.pmi, t) for w in s if w not in args])
	return phrase