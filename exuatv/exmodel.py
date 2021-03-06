# -*- coding: utf-8 -*-
'''
	exmodel.py
	Definition of class representing model (in MVC) of ex.ua
	Copyright (C) 2011-2013 Sergey Maysak a.k.a. sam (segey.maysak@gmail.com)
	Based on original work of Vadim Skorba (vadim.skorba@gmail.com)

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
__author__="sam"
__date__ ="$Jul 30, 2011 6:09:45 PM$"

import sys
import os
import urllib
import urllib2
import cookielib
import re
import tempfile
import exlocalizer
from htmlentitydefs import name2codepoint

class exmodel:
	'''exmodel acts as a data model provider performing loading data from ex.ua'''
	USERAGENT = "Mozilla/5.0 (Windows NT 6.1; rv:5.0) Gecko/20100101 Firefox/5.0"
	ROWCOUNT = (15, 30, 50, 100)[1]
	LANGUAGE = ('ru', 'uk', 'en')[0]
	htmlCodes = (
		('&', '&amp;'),
		('<', '&lt;'),
		('>', '&gt;'),
		('"', '&quot;'),
		("'", '&#39;'),
	)
	stripPairs = (
		('<p>', '\n'),
		('<li>', '\n'),
		('<br>', '\n'),
		('<.+?>', ' '),
		('</.+?>', ' '),
		('&nbsp;', ' '),
	)

	def __init__(self, localizer = None, useGate = False):
		self.localizer = localizer
		if useGate:
			self.URL = 'http://fex.net'
		else:
			self.URL = 'http://www.ex.ua'

	# Private methods
	def log(self, text):
		try:
			import mc
			mc.LogInfo(text)
		except:
			print text

	def localizedString(self, text):
		if None != self.localizer:
			return self.localizer.localizedString(text)
		return text

	def unescape(self, string):
		for (symbol, code) in self.htmlCodes:
			string = re.sub(code, symbol, string)
		return string

	def stripHtml(self, string):
		for (html, replacement) in self.stripPairs:
			string = re.sub(html, replacement, string)
		return string

	def fetchData(self, url):
		try:
			self.log("Fetching data for url: %s" % url)
			request = urllib2.Request(url)
			request.add_header('User-Agent', self.USERAGENT)
			#if self.__settings__.getSetting("auth"):
			#	authString = '; ' + self.__settings__.getSetting("auth")
			#else:
			authString = ''
			request.add_header('Cookie', 'uper=' + str(self.ROWCOUNT) + authString)
			
			connection = urllib2.urlopen(request)
			result = connection.read()
			connection.close()
			return (result)
		except urllib2.HTTPError, e:
			self.log(self + " fetchData(" + url + ") exception: " + str(e))
			return

	def nextPageItem(self, videos):
		next = re.compile("<td><a href='([\w\d\?=&/_]+)'><img src='/t2/arr_r.gif'").search(videos)
		if None == next:
			next = re.compile("<td><a href='(.+?)'><img src='/t2/arr_r.gif'").search(videos)
		if None == next:
			next = re.compile("<link rel=\"next\" id=\"browse_next\" href=\"(.+?)\">").search(videos)
		nextPageItem = {}
		if next:
			nextPageItem = {"name": self.localizedString("Next") + ' >>', "path": self.URL + next.group(1), "image": ''}
			self.log("next found: %s" % nextPageItem["path"])
		return nextPageItem

	def sectionsList(self):
		'''Returns a list of available video sections'''
		sectionsList = list()
		sections = self.fetchData("%s/%s/video" % (self.URL, self.LANGUAGE))
		for (link, sectionName, count) in re.compile("<a href='(.+?)'><b>(.+?)</b></a><p><a href='.+?' class=info>.+?: (\d+)</a>").findall(sections):
			sectionsList.append({"name": sectionName, "path": str(self.URL + link)})
		#move megogo.net to the end
		itemToMoveToBack = None
		for section in sectionsList:
			if section["name"].startswith('MEGOGO.NET'):
				itemToMoveToBack = section
				sectionsList.remove(section)
		if None != itemToMoveToBack:
			sectionsList.append(itemToMoveToBack)
		return sectionsList

	def pagesDict(self, url):
		'''Returns a dictionary containing list of pages in section and suplementary metadata to this list'''
		url = urllib.unquote_plus(url)
		videos = self.fetchData(url)
		# fill pages list
		pagesList = []
		for (link, image, title, comments) in re.compile(">?<a href='([^><']+?)'><img src='([^><']+?)\?\d+?' .+? alt='(.+?)'></a>.+?</small><p>(.*?)&nbsp;").findall(videos):
			if comments:
				comments = " [%s]" % re.sub('.+?>(.+?)</a>', '\g<1>', comments)
			pagesList.append({"name": self.unescape(title + comments), "path": self.URL + link, "image": image + '?200'})
		# find current subsection name
		pagesName = re.compile("<font color=#808080><b>(.+?)</b>").search(videos)
		pagesDict = {"pages": pagesList, "url": url}
		if pagesName:
			pagesDict["paging"] = pagesName.group(1)
		# detect next item
		nextPageItem = self.nextPageItem(videos)
		if nextPageItem.has_key("path"):
			pagesList.append(nextPageItem)
			pagesDict["next"] = nextPageItem
		# detect seach context
		self.log("search for context in url %s" % url)
		#context = re.search("(\d+)", url)
		context = re.compile("<input type=hidden name=original_id value='(\d+)'>").search(videos)
		if None != context:
			pagesDict["search"]= context.group(1)
			self.log("search context is %s" % context.group(1))
		return pagesDict

	def playItemsList(self, playlist, content):
		playItemsList = []
		for episode in playlist:
			episodeName = re.compile("<a href='(/get/" + episode + ")' .*?>(.*?)</a>").search(content)
			if episodeName:
				playItemsList.append({"path": self.URL + episodeName.group(1), "name": self.unescape(self.stripHtml(episodeName.group(2)))})
		return playItemsList

	def pagePlaylistDict(self, params = {}):
		get = params.get
		playlistDict = {}
		content = self.fetchData(urllib.unquote_plus(get("url")))
		filelist = re.compile("<a href='/filelist/(\d+).urls' rel='nofollow'>").search(content)
		details = re.compile(">(.+?)?<h1>(.+?)</h1>(.+?)</td>", re.DOTALL).search(content)
		if details and filelist:
			m3uPlaylistUrl = re.compile(".*<a href='(.*?).m3u' rel='nofollow'><b>.*</b></a>").search(content)
			if  m3uPlaylistUrl:
				m3uPlaylist = re.compile(".*/get/(\d+).*").findall(self.fetchData(self.URL + m3uPlaylistUrl.group(1) + '.m3u'))
				playlistDict["playitems"] = self.playItemsList(m3uPlaylist, content)
			image = re.compile("<img src='(http.+?(\?800|\?1600))'").search(details.group(1))
			if image:
				image = image.group(1)
			else:
				image = ''
			playlistDict["image"] = image
			title = details.group(2)
			description = str()
			description += details.group(3).replace('—Å–º–æ—Ç—Ä–µ—Ç—å –æ–Ω–ª–∞–π–Ω', '')
			comments = re.compile("<a href='(/view_comments/\d+).+?(\d+)</a>").search(content)
			if comments:
				description += self.localizedString('[B]Comments[/B]\n\n')
				commentsContent = self.fetchData(self.URL + comments.group(1))
				for (commentTitle, comment) in re.compile("<a href='/view_comments/\d+'><b>(.+?)</b>.+?<p>(.+?)<p>", re.DOTALL).findall(commentsContent):
					description += "[B]%s[/B]%s" % (commentTitle, comment)
			playlistDict["title"] = self.unescape(self.stripHtml(title))
			playlistDict["description"] = self.unescape(self.stripHtml(description))
		return playlistDict

	def searchAllPagesDict(self, query):
		'''Returns a dictionary with search results of 'search everywhere' '''
		url = urllib.quote_plus(self.URL + '/search?s=' + query)
		url = urllib.unquote_plus(url)
		return self.searchPagesDict(url)

	def searchInSectionPagesDict(self, context, query):
		'''Returns a dictionary with search results of 'search in specific section' '''
		url = '%s/search?original_id=%s&s=%s' % (self.URL, context, urllib.quote_plus(query))
		return self.searchPagesDict(url)

	def searchPagesDict(self, url):
		'''Returns a dictionary with list of items containing search results and corresponding metadata'''
		videos = self.fetchData(url)
		pagesList = []
		for (link, image, title, comments) in re.compile(">?<a href='([^><']+?)'><img src='([^><']+?)\?\d+?' .+? alt='(.+?)'></a>.+?</small>.*?>(.+?)</td>", re.DOTALL).findall(videos):
			comments = re.search("<a href='/view_comments.+?>(.+?)</a>", comments)
			if comments:
				title = "%s [%s]" % (title, comments.group(1))
			pagesList.append({"name": self.unescape(title), "path": self.URL + link, "image": image + '?200'})
		pagesName = re.compile("<font color=#808080><b>(\d+\.\.\d+)</b>").search(videos)
		pagesDict = {"pages": pagesList, "url": url}
		if pagesName:
			pagesDict["paging"] = pagesName.group(1)
		# detect next item
		nextPageItem = self.nextPageItem(videos)
		if nextPageItem.has_key("path"):
			nextPageItem["isSearch"] = True
			pagesList.append(nextPageItem)
			pagesDict["next"] = nextPageItem
		# detect seach context
		context = re.search("/view/(\d+)", url)
		if None != context:
			pagesDict["search"]= context.group(1)
		return pagesDict
