##############################
# Web retrievers and parsers #
##############################
import urllib2

###############
# PDF parsing #
###############
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO

from text_analyzing import *

class PDF:
	'''
		A class that can retrieve pdf files from an given url.
		The retrieved pdf file can be parsed and returned.
	'''
	def __init__(self, url):
		self.url = url

	def parse(self):
		'''
		Parse a local pdf document.

			Note --> I DID NOT MADE THIS CODE MYSELF. 
				 --> url: http://stackoverflow.com/questions/22800100/parsing-a-pdf-via-url-with-python-using-pdfminer
				 --> url: http://stackoverflow.com/questions/25665/python-module-for-converting-pdf-to-text/1257121    <-- this one does not work with url
			Note to self --> I have to learn and understand it tho.
		'''
		try:
			request  = urllib2.Request(self.url)
			response = urllib2.urlopen(request).read()
			fp       = StringIO(response)
			rsrcmgr  = PDFResourceManager()
			retstr   = StringIO()
			codec    = 'utf-8'
			laparams = LAParams()
			device   = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

			# Create a PDF interpreter object.
			interpreter = PDFPageInterpreter(rsrcmgr, device)

			# Process each page contained in the document.
			for page in PDFPage.get_pages(fp):
			    interpreter.process_page(page)
			    data = retstr.getvalue()
			return data

		except urllib2.URLError:
			return 'Something went wrong while opening the url'

if __name__ == '__main__':
	print 'Testing'

	article = PDF('https://arxiv.org/pdf/1502.00823v1.pdf')
	article1 = PDF('http://arxiv.org/pdf/1505.06158v2')

	c1 = article.parse()
	c2 = article1.parse()

	print cosine_sim(c1, c2)



