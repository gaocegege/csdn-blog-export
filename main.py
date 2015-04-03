#!/usr/bin/python
# coding=utf-8 
from bs4 import BeautifulSoup
import urllib2
import codecs
import re

class Analyzer(object):
	"""docstring for Analyzer"""
	def __init__(self):
		super(Analyzer, self).__init__()
	
	# get the page of the blog by url
	def get(self, url):
		headers = {'User-Agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
		req = urllib2.Request(url, headers=headers)
		html_doc = urllib2.urlopen(req).read()
		return html_doc

	def getContent(self, soup):
		return soup.find(id='container').find(id='body').find(id='main').find(class_='main')
		

class Exporter(Analyzer):
	"""docstring for Exporter"""
	def __init__(self):
		super(Exporter, self).__init__()

	# get the title of the article
	def getTitle(self, detail):
		return detail.find(class_='article_title').h1.span.a.get_text().split('\r\n')[1]

	def export(self, link, f):
		html_doc = self.get(link)
		soup = BeautifulSoup(html_doc)
		detail = self.getContent(soup).find(id='article_details')
		f.write(u'#' + self.getTitle(soup) + u'\n')
		article_content = detail.find(class_='article_content')
		f.write(article_content.text)

	def run(self, link, f):
		self.export(link, f)
		

class Parser(Analyzer):
	"""docstring for parser"""
	def __init__(self):
		super(Parser, self).__init__()
		self.article_list = []
		self.page = -1

	# get the articles' link
	def parse(self, html_doc):
		soup = BeautifulSoup(html_doc)
		res = self.getContent(soup).find(class_='list_item_new').find(id='article_list').find_all(class_='article_item')
		i = 0
		for ele in res:
			self.article_list.append('http://blog.csdn.net/' + ele.find(class_='article_title').h1.span.a['href'])

	# get the page of the blog
	# may have a bug, because of the encoding
	def getPageNum(self, html_doc):
		soup = BeautifulSoup(html_doc)
		self.page = 1;
		res = self.getContent(soup).find(id='papelist').span
		self.page =  int(str(res).split(' ')[3][3:5])

	# get all the link
	def getAllArticleLink(self, url):
		self.getPageNum(self.get(url))
		# self.parse(self.get(url))
		for i in range(1, self.page + 1):
			self.parse(self.get(url + '/article/list/' + str(i)))


	def export2markdown(self):
		for link in self.article_list:
			exporter = Exporter()
			f = codecs.open(link.split('/')[7] + '.md', 'w', encoding='utf-8')
			exporter.run(link, f)
			f.close()


	# run the prog
	def run(self, url):
		self.page = -1
		self.article_list = []
		self.getAllArticleLink(url)
		self.export2markdown()

		
def main():
	url = 'http://blog.csdn.net/shijiebei2009'
	parser = Parser()
	parser.run(url)

# main()
def debug():
	url = 'http://blog.csdn.net/shijiebei2009/article/details/7099513'
	exporter = Exporter()
	exporter.run(url, codecs.open('test.md', 'w', encoding='utf-8'))

main()