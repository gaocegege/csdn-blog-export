#!/usr/bin/python
# coding=utf-8 
from bs4 import BeautifulSoup
import urllib2
import codecs
import re
import sys, getopt
# https://github.com/aaronsw/html2text
import html2text

# responsible for printing
class PrintLayer(object):
    """docstring for PrintLayer"""
    def __init__(self, arg):
        super(PrintLayer, self).__init__()
        self.arg = arg

    @staticmethod
    def printWorkingPage(page):
        print "Work in Page " + str(page)

    @staticmethod
    def printWorkingArticle(article):
        print "Work in " + str(article)

    @staticmethod
    def printWorkingPhase(phase):
        if phase == 'getting-link':
            print "Phase 1: Getting the link"
        elif phase == 'export':
            print "Phase 2: Exporting"

    @staticmethod
    def printArticleCount(count):
        print 'Count of Articles: ' + str(count)

    @staticmethod
    def printOver():
        print 'Over. If has any problem, contact me with https://github.com/gaocegege/csdn-blog-export/issues'
        

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

    # get the detail of the article
    def getContent(self, soup):
        return soup.find(id='container').find(id='body').find(id='main').find(class_='main')
        

class Exporter(Analyzer):
    """docstring for Exporter"""
    def __init__(self):
        super(Exporter, self).__init__()

    # get the title of the article
    def getTitle(self, detail):
        return detail.find(class_='article_title').h1

    # get the content of the article
    def getArticleContent(self, detail):
        return detail.find(class_='article_content')

    # export as markdown
    def export2markdown(self, f, detail):
        f.write(html2text.html2text(self.getTitle(detail).prettify()))
        f.write(html2text.html2text(self.getArticleContent(detail).prettify()))

    # export as html
    def export2html(self, f, detail):
        f.write(self.getTitle(detail).prettify())
        f.write(self.getArticleContent(detail).prettify())

    # export
    def export(self, link, filename, form):
        html_doc = self.get(link)
        soup = BeautifulSoup(html_doc)
        detail = self.getContent(soup).find(id='article_details')
        if form == 'markdown':
            f = codecs.open(filename + '.md', 'w', encoding='utf-8')
            self.export2markdown(f, detail)
            f.close()
            return
        elif form == 'html':
            f = codecs.open(filename + '.html', 'w', encoding='utf-8')
            self.export2html(f, detail)
            f.close()
            return

    def run(self, link, f, form):
        self.export(link, f, form)
        

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
        # papelist if a typo written by csdn front-end programmers?
        pageList = self.getContent(soup).find(id='papelist')
        # if there is only a little posts in one blog, the papelist element doesn't even exist
        if pageList == None:
        	print "Page is 1"
        	return 1
        res = pageList.span
        # get the page from text
        buf = str(res).split(' ')[3]
        strpage = ''
        for i in buf:
            if i >= '0' and i <= '9':
                strpage += i
        # cast str to int
        self.page =  int(strpage)
        return self.page

    # get all the link
    def getAllArticleLink(self, url):
    	# get the num of the page
        self.getPageNum(self.get(url))
        # iterate all the pages
        for i in range(1, self.page + 1):
            PrintLayer.printWorkingPage(i)
            self.parse(self.get(url + '/article/list/' + str(i)))

    # export the article
    def export(self, form):
        PrintLayer.printArticleCount(len(self.article_list))
        for link in self.article_list:
            PrintLayer.printWorkingArticle(link)
            exporter = Exporter()
            exporter.run(link, link.split('/')[7], form)

    # the page given
    def run(self, url, page=-1, form='markdown'):
        self.page = -1
        self.article_list = []
        PrintLayer.printWorkingPhase('getting-link')
        if page == -1:
            self.getAllArticleLink(url)
        else:
            if page <= self.getPageNum(self.get(url)):
                self.parse(self.get(url + '/article/list/' + str(page)))
            else:
                print 'page overflow:-/'
                sys.exit(2)
        PrintLayer.printWorkingPhase('export')
        self.export(form)
        PrintLayer.printOver()
    

def main(argv):
    page = -1
    directory = '-1'
    username = 'default'
    form = 'markdown'
    try:
        opts, args = getopt.getopt(argv,"hu:f:p:o:")
    except Exception, e:
        print 'main.py -u <username> [-f <format>] [-p <page>] [-o <outputDirectory>]'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'main.py -u <username> [-f <format>] [-p <page>] [-o <outputDirectory>]'
            sys.exit()
        elif opt == '-u':
            username = arg
        elif opt == '-p':
            page = arg
        elif opt == '-o':
            directory = arg
        elif opt == '-f':
            form = arg

    if username == 'default':
        print 'Err: Username err'
        sys.exit(2)
    if form != 'markdown' and form != 'html':
        print 'Err: format err'
        sys.exit(2)
    url = 'http://blog.csdn.net/' + username
    parser = Parser()
    parser.run(url, page, form)

if __name__ == "__main__":
   main(sys.argv[1:])