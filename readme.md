# CSDN 博客导出工具

一个用python2.7写的博客导出工具，导出为markdown或者html，markdown目前没有实现图片的导出。

## 使用

依赖：
	
	Python 2.7
		beautifulsoup4

使用方法：
	
	main.py -u <username> [-f <format>] [-p <page>] [-o <outputDirectory>]
	<format>： html | markdown
	<page>为导出特定页面的文章，缺省导出所有文章
	<outputDirectory>暂不可用

Example：

如果想导出[http://blog.csdn.net/cecesjtu](http://blog.csdn.net/cecesjtu)的文章，格式为markdown，命令为：

	./main.py -u cecesjtu -f markdown

## To Do

1. 导出到指定目录
2. markdown格式完善，支持图片