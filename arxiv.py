###################
# General modules #
###################
from collections import defaultdict

##################
# Output modules #
##################
import csv, json

#################
# Local modules #
#################
from pdf_parser import PDF
from text_analyzing import *
from api import API

class Arxiv:

	def __init__(self, filename, amount, language='english'):
		try:
			self.text = open(filename, 'rb').read().decode('latin-1')
		except:
			return 'Something went wrong. Probably something with the codec.'

		# Set base variables
		self.language = language
		self.search_term = phrase_finder(tokenize(self.text, self.language), n=5, gram='bigram')

		# Initialize api class
		self.api = API(self.search_term)

		# Get the data
		self.api.get(amount)


	def dump(self):
		'''
			Returns pretty soupified web page.
		'''
		return self.api.data.prettify()


	def summary(self):
		'''
			Returns the first 15 sentences of the input document.
			This amount is around the size of a short introduction.
		'''
		words = self.text.split('.')[5:20]
		return '.'.join(words)

	def similars(self, lvl, sort, *args):
		'''
			Funcion that loops through articles,
			retrieves the data specified by sort.

			-- Variables --
			@lvl is the minimum level of similarity. Int between 0 and 1.
			@sort is the content where the similarity is based on. String of 'full', 'phrase', 'summary'
			@args are additional parameters for adding extra values to the final collection.
				- Such as author, journal etc.
			
			returns
			@dictionary  similarities with titles.
		'''
		local     = self.text;
		others    = (article for article in self.api.collect('url', 'summary', args).iteritems()) 

		# Set for later use
		self.fields   = [field for field in self.api.flatten([args, 'similarity', 'summary', 'url'])]
		self.similars = defaultdict(dict)

		# Loop through articles
		for article in others:
			info = {}

			# Specify content on which to calculate similarity
			if sort == 'full':
				url = article[1]['url']
				pdf = PDF(url)
				try:
					external = pdf.parse()
					info['similarity'] = cosine_sim(local, external)
				except:
					return 'PDFTextExtractionNotAllowed is raised for %s' % url

			elif sort == 'summary':
				summarized = self.summary()
				external   =  article[1]['summary']
				info['similarity'] = cosine_sim(summarized, external)

			elif sort == 'phrase':
				external = phrase_finder(tokenize(article[1]['summary'], self.language), n=5, gram='bigram')
				info['similarity'] = cosine_sim(self.search_term, external)

			# Add additional attributes
			if args:
				for arg in self.api.flatten(args):
					info[arg] = article[1][arg]

			info['url'] = article[1]['url']
			info['summary'] = article[1]['summary']

			if info['similarity'] > lvl:
				self.similars[article[0]] = info

		# Return collection
		return self.similars

	def to_csv(self):
		'''
			Writes data retrieved from similars to csv file.
		'''
		# See if the data already exists
		try:
			data = self.similars
		except AttributeError: 
			return 'Make sure to run similars first, to create the data.'

		# Create new csv file with search term as name
		with open(self.search_term + '.csv', 'wb') as c:

			# Initialize fields and add title for keys
			fields = self.fields
			fields.insert(0, 'title')

			# Init base values for csv file
			writer = csv.DictWriter(c, fieldnames = fields, delimiter = ',')
			writer.writeheader()

			# Write rows
			for key, val in data.iteritems():
				row = { 'title': key }
				row.update(val)
				writer.writerow(row)

		# Return
		return 'A csv file has been created as %s.' % (self.search_term + '.csv')




if __name__ == '__main__':
	opzet = Arxiv('Docs/FinalOpzet-2.0.txt', amount=10)
	params = ['author', 'journal']
	# print json.dumps(opzet.similars(.3, 'phrase', params), sort_keys=True, indent=4)
	data = opzet.similars(.2, 'phrase', params)
	opzet.to_csv()


