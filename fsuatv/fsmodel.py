# -*- coding: utf-8 -*-
'''
	fsmodel.py
	Definition of class representing model (in MVC) of ex.ua
	Copyright (C) 2013 Sergey Maysak a.k.a. sam (segey.maysak@gmail.com)
	Based on original work of Khrysev D.A., E-mail: x86demon@gmail.com

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
import urllib
import urllib2
import re
import sys
import os
import cookielib

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import socket
socket.setdefaulttimeout(50)

siteUrl = 'fs.to'
httpSiteUrl = 'http://' + siteUrl

headers  = {
	'User-Agent' : 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00',
	'Accept'     :' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
	'Accept-Language':'ru-RU,ru;q=0.9,en;q=0.8',
	'Accept-Charset' :'utf-8, utf-16, *;q=0.1',
	'Accept-Encoding':'identity, *;q=0'
}

def htmlEntitiesDecode(string):
	return BeautifulStoneSoup(string, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]

class fsmodel:
	
	def __init__(self, localizer = None, useGate = False):
		self.section = 'video'
		self.filter = ''
		self.localizer = localizer
		self.URL = httpSiteUrl

	# Private methods
	def log(self, text):
		try:
			import mc
			mc.LogInfo(text)
		except:
			print text
	
	def getCookieJarPath(self):
		try:
			import mc
			#cookies = mc.GetCookieJar()
			cookies = os.path.join(mc.GetTempDir(), 'fs.ua.cookies.lwp')
			return cookies
		except:
			return os.path.join('', 'fs.ua.cookies.lwp')

	def localizedString(self, text):
		if None != self.localizer:
			return self.localizer.localizedString(text)
		return text
	
	def getUrlWithSortBy(self, url, section):
		#__settings__.getSetting("Sort by")
		sortBy = '0'
		sortByMap = {'0': 'new', '1': 'rating', '2': 'year'}
		if '?' in url:
			return url
		else:
			return url + '?view=list&sort=' + sortByMap[sortBy] + self.getFilters(section)

	def getFilters(self, section):
		params = [];
		ret = ''
		sectionSettings = {
			'video': ['mood', 'vproduction', 'quality', 'translation'],
			'audio': ['genre', 'aproduction']
		}
		for settingId in sectionSettings[section]:
			setting = 'Any'#__settings__.getSetting(settingId)
			if setting != 'Any':
				params.append(setting)
		if len(params) > 0:
			ret = '&fl=' + ','.join(params)
		return ret
	
	def GET(self, url, referer, post_params = None):
		headers['Referer'] = referer

		if post_params != None:
			post_params = urllib.urlencode(post_params)
			headers['Content-Type'] = 'application/x-www-form-urlencoded'
		elif headers.has_key('Content-Type'):
			del headers['Content-Type']

		cookiepath = self.getCookieJarPath()
		jar = cookielib.LWPCookieJar(cookiepath)
		if os.path.isfile(cookiepath):
			jar.load()

		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
		urllib2.install_opener(opener)
		req = urllib2.Request(url, post_params, headers)

		response = opener.open(req)
		the_page = response.read()
		response.close()

		jar.save()
		return the_page
	
	def sectionsList(self):
		categoryUrl = urllib.unquote_plus(httpSiteUrl + '/video/')

		http = self.GET(categoryUrl, httpSiteUrl)
		if http == None: return list()

		beautifulSoup = BeautifulSoup(http)
		topMenu = beautifulSoup.find('ul', 'b-header-menu')
		if topMenu == None: return list()
		categorySubmenu = topMenu.find('li', 'm-%s' % self.section)
		if categorySubmenu == None: return list()

		subcategories = categorySubmenu.findAll('a')
		if len(subcategories) == 0:
			return list()
		sectionsList = list()
		for subcategory in subcategories:
			li = {'name' : subcategory.string.encode('utf-8', 'ingnore'),
				'path': str(self.getUrlWithSortBy(httpSiteUrl + subcategory['href'], self.section)),
				'cleanUrl': (httpSiteUrl + subcategory['href']).encode('utf-8', 'ingnore') }
			sectionsList.append(li)

		return sectionsList

	def pagesDict(self, params):
		categoryUrl = self.getUrlWithSortBy(urllib.unquote_plus(params['path']), self.section)
		http = self.GET(categoryUrl, httpSiteUrl)
		if http == None: return {'name' : self.localizedString('absent'), 'pages' : []}

		#showUpdateInfo = __settings__.getSetting("Show update info") == "true"
		showUpdateInfo = False
		beautifulSoup = BeautifulSoup(http)
		items = beautifulSoup.findAll('a', 'subject-link')
		
		if len(items) == 0:
			return {'name' : self.localizedString('absent'), 'pages' : []}
		pages = []
		for item in items:
			title = None
			cover = None
			href = None

			img = item.find('img')
			if img != None:
				cover = img['src']
				title = img['alt']
				href = httpSiteUrl + item['href']

			if title != None:
				if showUpdateInfo:
					additionalInfo = ''
					numItem = item.find('b', 'num')
					if numItem != None:
						additionalInfo = " / " + numItem.string.strip() + " "
					dateInfo = item.find('b', 'date')
					if dateInfo != None:
						additionalInfo += dateInfo.string.strip()
					title += additionalInfo

				id = str(item['href'].split('/')[-1])				

				page = { 'name' : htmlEntitiesDecode(title).encode('utf-8'),
					'path': href.encode('utf-8'),
					'referer': categoryUrl.encode('utf-8'),
					'image': cover.encode('utf-8'),
					'folder': '0',
					'id' : id }
				pages.append(page)

		paging = ''
		try:
			bPagerDiv = beautifulSoup.find('div', 'b-pager')
			paging = str(bPagerDiv.find('a', 'selected').string)
		except:
			paging = ''
		
		nextPageLink = beautifulSoup.find('a', 'next-link')
		nextPageItem = {}
		if nextPageLink != None:
			nextPageItem = { 'name' : self.localizedString('Next') + ' >>',
				'path': (httpSiteUrl + nextPageLink['href']).encode('utf-8'), 'image' : '', 'folder': '0'}
			pages.append(nextPageItem)
		pagesDict = { 'pages' : pages, 'url' : params['path'], 'paging' : paging,
			'search' : params['cleanUrl'] }
		if nextPageItem.has_key('path'):
			pagesDict['next'] = nextPageItem
		return pagesDict

	def folderDescription(self, folderUrl):
		#return 'description here'
		http = self.GET(folderUrl, httpSiteUrl)
		fullSoup = BeautifulSoup(http)
		itemInfo = fullSoup.find('div', 'item-info')
		if None == itemInfo: return ''
		
		plot = fullSoup.find('meta', attrs = {'name' : 'description'})
		try:
			if plot != None: plot = plot['content']
			if plot == None: plot = ''
		except:
			plot = ''
		
		detailsString = ''
		try:
			for pair in itemInfo.findAll('tr'):
				right = ''
				for r in pair.findAll('a'): right += r.string + ','
				right = right.rstrip(',')
				detailsString += pair.find('td').string.strip() + " " + right + "\n"
		except:
			detailsString = ''
		description = detailsString + '\n\n' + plot
		return description.encode('utf-8')

	def loadFilelistItems(self, folderUrl, httpSiteUrl, folder):
		http = self.GET(folderUrl + '?ajax&folder=' + folder, httpSiteUrl)
		if http == None: http = ''
		beautifulSoup = BeautifulSoup(http)
		mainItems = beautifulSoup.find('ul', 'filelist')
		#self.log('folder parametes is: %s' % folder)
		if mainItems == None and 0 == int(folder):
			http = self.GET(folderUrl + '?ajax&folder=', httpSiteUrl)
			beautifulSoup = BeautifulSoup(http)
			mainItems = beautifulSoup.find('ul', 'filelist')
		return mainItems

	def pagePlaylistDict(self, params = {}):
		playlistDict = {}
		folderUrl = urllib.unquote_plus(params['path'])
		cover = urllib.unquote_plus(params['image'])
		folder = params['folder']
		if False == folder.isdigit(): folder = '0'
		
		playlistDict['image'] = cover
		playlistDict['title'] = params['name']
		self.log('pageDict title: %s folder: %s' % (params['name'], folder))
		
		mainItems = self.loadFilelistItems(folderUrl, httpSiteUrl, folder)
		if mainItems == None:
			self.log('no filelist element found - returning...')
			return playlistDict

		items = mainItems.findAll('li')
		self.log("items: %s" % str(mainItems))
		
		playItems = []
		subfolders = []
		folderRegexp = re.compile('(\d+)')
		if len(items) == 0:
			return playlistDict
		else:
			for item in items:
				isFolder = item['class'] == 'folder'
				linkItem = None
				playLink = None
				episodeName = None
				if isFolder:
					linkItem = item.find('a', 'title')
				else:
					linkItem = item.find('a', 'b-file-new__link-material')#'link-material')
					playLink = item.find('a', 'b-file-new__link-material-download')#'b-player-link')
				#self.log("linkItem: %s" % linkItem)
				#self.log("playLink: %s" % playLink)
				#self.log("episodeName: %s" % episodeName)
				
				if linkItem is not None:
					title = ""
					if isFolder:
						titleB = linkItem.find('b')
						if titleB == None:
							title = str(linkItem.string)
						else:
							title = str(titleB.string)
						quality = item.findAll('span', 'material-size')
						if len(quality) > 1:
							 title = title + " [" + str(quality[0].string) + "]"
					else:
						episodeName = linkItem.find('span', 'b-file-new__link-material-filename-text')
						#self.log("lets use episodeName: %s" % episodeName)
						if episodeName is not None:
							title = episodeName.string
						

					useFlv = False#__settings__.getSetting('Use flv files for playback') == 'true'
					fallbackHref = httpSiteUrl + linkItem['href']
					#if useFlv and playLink is not None:
					if playLink is not None:
						try:
							href = httpSiteUrl + str(playLink['href'])
							#href = str(playLink['href'])
						except:
							href = fallbackHref
					else:
						href = fallbackHref
						try:
							#self.log("href: %s" % href)
							folder = folderRegexp.findall(linkItem['rel'])[0].encode('utf-8')
							#self.log("folder found is : %" % folder)
						except:
							pass
					
					li = None
					uri = None
					
					fullTitle = playlistDict['title'] + ' - ' + htmlEntitiesDecode(title).encode('utf-8')
					if isFolder:
						li = {'name' : fullTitle,
							'image' : cover,
							'path': folderUrl.encode('utf-8'),
							'referer': folderUrl.encode('utf-8'),
							'folder': folder }
						subfolders.append(li)
					else:
						if len(items) > 1 : fullTitle = htmlEntitiesDecode(title).encode('utf-8')
						li = { 'name' : fullTitle,
							'image' : cover,
							'path' : href.encode('utf-8') }
						if type == 'music':
							li['path'] = str(href.encode('utf-8'))
							li['referer'] = folderUrl.encode('utf-8')
						playItems.append(li)
			if len(playItems) > 0:
				playlistDict['playitems'] = playItems
			if len(subfolders) > 0:
				playlistDict['subfolders'] = subfolders
		
		#load movie description for actual playitems only
		if playlistDict.has_key('playitems'):
			if params.has_key('description'):
				playlistDict['description'] = params['description']
			else:
				playlistDict['description'] = self.folderDescription(folderUrl)
		
		return playlistDict

	def searchAllPagesDict(self, query):
		'''Returns a dictionary with search results of 'search everywhere' '''
		return self.searchInSectionPagesDict('http://fs.to/video/', query)

	def searchInSectionPagesDict(self, cleanUrl, query):
		'''Returns a dictionary with search results of 'search in specific section' '''
		url = '%ssearch.aspx?search=%s' % (urllib.unquote_plus(cleanUrl), urllib.quote_plus(query))
		return self.searchPagesDict(url)

	def searchPagesDict(self, url):
		searchUrl = url
		#searchUrl = urllib.unquote_plus(searchUrl)
		http = self.GET(searchUrl, httpSiteUrl)
		if http == None: return {'name' : self.localizedString('Nothing found'), 'pages' : []}

		beautifulSoup = BeautifulSoup(http)
		items = beautifulSoup.find('div', 'l-content').find('table').findAll('tr')
		
		paging = ''
		try:
			bPagerDiv = beautifulSoup.find('div', 'b-pager')
			paging = str(bPagerDiv.find('a', 'selected').string)
		except:
			paging = ''
		
		pages = []
		if len(items) == 0:
			return {'name' : self.localizedString('Nothing found'), 'pages' : []}
		else:
			for item in items:
				link = item.find('a')
				if link != None:
					title = str(link['title'].encode('utf-8'))
					href = httpSiteUrl + link['href']
					cover = item.find('img')['src']

					if title != None:
						page = { 'name' : htmlEntitiesDecode(title).encode('utf-8'),
							'image' : cover.encode('utf-8'),
							'path': href.encode('utf-8'), 'referer': searchUrl.encode('utf-8'),
							'folder': '0' }
					pages.append(page)

			nextPageLink = beautifulSoup.find('a', 'next-link')
			nextPageItem = {}
			if nextPageLink != None:
				nextPageItem = { 'name' : self.localizedString('Next') + ' >>',
					'path' : (httpSiteUrl + nextPageLink['href']).encode('utf-8'),
					'image' : '', 'isSearch' : True, 'folder': '0' }
				pages.append(nextPageItem)
				
		pagesDict = { 'pages' : pages, 'url' : searchUrl, 'paging' : paging }
		if nextPageItem.has_key('path'):
			pagesDict['next'] = nextPageItem
		return pagesDict
