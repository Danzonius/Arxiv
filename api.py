from bs4 import BeautifulSoup
import urllib2
from collections import defaultdict, Iterable
from itertools import chain

class API:
	'''
		A class for working with the Arxiv API.

		It enables the user to GET data based on a query.
		It offers functions to select certain data attributes.

		Can return a big collection of selected data.
	'''

	def __init__(self, query):
		self.query = query.replace(' ', '%20')
		self.att_error = '\nThere is no data yet.\nMake sure to make a get call first.\n'

	def get(self, n):
		'''
			Makes a get call to the api and retrieves data.

			@returns data
		'''
		# Create url and read
		url = 'http://export.arxiv.org/api/query?search_query=all:%s&start=0&max_results=%s' % (self.query, n)
		raw = urllib2.urlopen(url).read()

		# Parse raw url data to soup
		self.data = BeautifulSoup(raw) 

		# Notify the user
		print 'Data has been retrieved as self.data\n'

		return self.data

	def select(self, *args):
		'''
			Select data based on requests

			@returns dictionary of lists
		'''
		# Check if there's data available
		try:
			data = self.data
		except AttributeError:
			return self.att_error

		# Create dictionary to hold the results
		self.results = defaultdict(list)

		# Convert list to tuple of uniques if input is a list
		args = tuple(list(set([el for el in self.flatten(args)])))

		# Loop through arguments
		for request in args:

			# Some possible attributes are not intuitive
			request = 'arxiv:journal_ref' if request == 'journal' else request

			try:
				attributes = (result for result in data.findAll(request))
				for attr in attributes:

					# Can't be something with the first result
					if attr.text.startswith('ArXiv Query') == 0:
						self.results[request] += [attr.text.replace('\n', '')]

			except:
				print 'The attribute %s does not exist.' % (request)
		
		return self.results

	def collect(self, *args):
		'''
			A more sophisticated version of select().
			This function will return a similar collection.
			This collection will be grouped per article, however.
			
			Arguments that are name parsed are:
				"url"     -> <link title="pdf" href="...">
				"journal" -> <arxiv:journal_ref ...>

			Will always include attribute title
			@returns dictionary with dictionaries
		'''
		# Check if there's data available
		try:
			data = self.data
		except AttributeError:
			return self.att_error

		# Initialize collection and arguments
		self.collection = defaultdict(dict)

		# Make sure title is in the list of arguments and is unique
		attributes = list(set([el for el in self.flatten(args)]))
		
		# Remove title from the list as it will be inserted automatically
		attributes.remove('title') if 'title' in attributes else attributes

		# Create generator to loop through all the entries
		entries = (entry for entry in data.findAll('entry'))

		# Loop through the data
		for entry in entries:
			# Create empty entry dict
			article = defaultdict(str)

			# Loop through the arguments
			for arg in attributes:

				# Make list of names of authors
				if arg == 'author':
					authors = [author.find('name').text for author in entry.findAll(arg)]
					article[arg] = authors

				# Make sure the right tag is found
				elif arg == 'journal':
					journal = entry.find('arxiv:journal_ref')
					article[arg] = journal.text if journal != None else ''

				# Same for links
				elif arg == 'url':
					link = entry.find('link', {'title': 'pdf'})['href']
					article[arg] = link

				# Just add it to the collection
				else:
					article[arg] = entry.find(arg).text

			# Put in the collection
			title = entry.find('title')		
			self.collection[title.text] = article

		return self.collection

	def flatten(self, iterable, ltypes=Iterable):
		'''
			Will flatten out any kind of list

			@source: http://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python
		'''
		# Create remainder
		remainder = iter(iterable)
		while True:
			first = next(remainder)
			if isinstance(first, ltypes) and not isinstance(first, basestring):
				remainder = chain(first, remainder)
			else:
				yield first


if __name__ == '__main__':
	# only for output testing
	import json
	
	arxiv = API('semantic web')
	arxiv.get(20)
	select = arxiv.select('author', 'title', 'journal')
	collect = arxiv.collect('author', 'journal', 'published', 'summary', 'url')
	print json.dumps(collect, sort_keys=True, indent=4)







