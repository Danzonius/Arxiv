##############################
# Web retrievers and parsers #
##############################
import urllib2
from bs4 import BeautifulSoup

##################
# Text analyzing #
##################
import nltk, string
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.collocations import *
from collections import Counter
import codecs
from sklearn.feature_extraction.text import TfidfVectorizer

###############
# PDF parsing #
###############
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO

##################
# Output modules #
##################W
import csv

#################
# Local modules #
#################
from pdf_parser import PDF
from text_analyzing import *

class Arxiv:

	def __init__(self, filename, amount, language='english'):
		try:
			self.text = open(filename, 'rb').read().decode('latin-1')
		except:
			print 'Something went wrong. Probably something with the codec.'
			return
		self.language    = language
		self.search_term = phrase_finder(tokenize(self.text, self.language), n=5, gram='bigram')
		self.query(n=amount)

	def query(self, **kwargs):
		query     = self.search_term if kwargs.get('query', None) == None else kwargs.get('query', None)
		n         = 20 if kwargs.get('n', None) == None else kwargs.get('n', None) 
		url       = 'http://export.arxiv.org/api/query?search_query=all:%s&start=0&max_results=%s' % (query.replace(' ', '%20'), n)
		raw       = urllib2.urlopen(url).read()
		self.soup = BeautifulSoup(raw) 

		print 'The data has been retrieved as self.soup!'

	def dump(self):
		'''
			Returns pretty soupified web page.
		'''
		try:
			return self.soup.prettify()
		except:
			print 'Make sure you query first and then retrieve the output!'
			return

	def authors(self):
		'''
			Finds all unique authors of all articles
			Returns a list.
		'''
		try:
			authors = self.soup.findAll('author')
			names   = list(set([author.find('name').text for author in authors]))
			return names
		except:
			print 'Make sure you query first and then retrieve the authors!'

	def titles(self):
		'''
			Finds the title of each article.
			Returns a list.
		'''
		try:
			return [title.text for title in self.soup.findAll('title') if title.text.startswith('ArXiv Query') == 0]
		except:
			print 'Make sure you query first and then retrieve the titles!'

	def articles(self):
		'''
			Finds the author, title and summary of each article.
			Returns a dictionary.
				Title is key.
				Author, title, summary, url are values.
		'''
		try:
			self.entries = self.soup.findAll('entry')
		except:
			print 'Something went wrong while trying to retreive all entries'
			return

		papers       = {}

		for entry in self.entries:
			title   = entry.find('title').text
			author  = entry.find('author').text.replace('\n', '')
			summary = entry.find('summary').text.replace('\n', '')
			url     = entry.find('link', {'title':'pdf'})['href']
			papers[title] = {
				'author'  : author,
				'summary' : summary,
				'url'     : url,
			}
		return papers

	def similars(self, lvl, sort):
		'''
			Funcion that loops through articles,
			retrieves the data specified by sort.

			-- Variables --
			@int  	 	 lvl  = number between 0 and 1.								
			@string 	 sort = 'full', 'summary', 'phrase'.
			
			returns
			@dictionary  similarities with titles.
		'''
		local     = self.text;
		others    = (article for article in self.articles().iteritems())
		similars  = {}

		for article in others:
			if sort == 'full':
				url = article[1]['url']
				pdf = PDF(url)
				try:
					external = pdf.parse()
					sim      = cosine_sim(local, external)
				except:
					return 'PDFTextExtractionNotAllowed is raised for %s' % url

			elif sort == 'summary':
				summarized = self.get_summary()
				external   =  article[1]['summary']
				sim        = cosine_sim(summarized, external)

			elif sort == 'phrase':
				external = phrase_finder(tokenize(article[1]['summary'], self.language), n=5, gram='bigram')
				sim      = cosine_sim(self.search_term, external)

			if sim > lvl:
				similars[article[0]] = [article[1]['author'], sim]

		# return dict
		return similars

	def to_csv(self, sort, lvl):
		'''
			Writes data to a csv file.
		'''
		def writerow(key, values):
			return writer.writerow({
				'title'      : key.encode('utf-8'),
				'author'	 : values[0],
				'similarity' : values[1],
			})

		with open(self.search_term + '.csv', 'wb') as c:
			writer = csv.DictWriter(c, fieldnames = ['title', 'author', 'similarity'], delimiter=',')
			writer.writeheader()
			for key, value in self.similars(lvl, sort).iteritems():
				writerow(key, [value[0], value[1]])

		print 'A file has been created as %s.csv.' % (self.query)

	def get_summary(self):
		'''
			Returns the first 15 sentences of the input document.
			This amount is around the size of a short introduction.
		'''
		words = self.text.split('.')[5:20]
		return '.'.join(words)

if __name__ == '__main__':
	opzet = Arxiv('FinalOpzet-2.0.txt', amount=200)
	query = opzet.search_term
	articles = opzet.articles()
	titles   = opzet.titles()
	authors  = opzet.authors() 
	summary  = opzet.get_summary()
	print opzet.similars(0.9, 'full')


