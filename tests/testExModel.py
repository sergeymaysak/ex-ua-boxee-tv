# -*- coding: utf-8 -*-

#  testExModel.py
#  exuatv
#
#  Created by Sergey Maysak on 1/12/13.
#

import unittest
import exmodel

class TestExModel(unittest.TestCase):

	def setUp(self):
		self.model = exmodel.exmodel()
		
	def testLoadSections(self):
		sections = self.model.sectionsList()
		#print sections
		self.assertTrue(len(sections) > 0)
		#self.assertTrue(sections[0]['name'].)
		for section in sections:
			self.assertTrue(section.has_key('path'))
			self.assertTrue(section.has_key('name'))

	def testPagingStructure(self):
		# take first section
		sectionURL = self.model.sectionsList()[0]['path']
		pagingInfo = self.model.pagesDict(sectionURL)
		self.assertIsNotNone(pagingInfo)
		#print pagingInfo
		self.assertTrue(len(pagingInfo['url']))# url pointing to current paging
		self.assertTrue(len(pagingInfo['search']))# search context
		self.assertTrue(len(pagingInfo['paging']))#title of section
		self.assertTrue(len(pagingInfo['pages']))#list of pages
		self.assertTrue(len(pagingInfo['next']))#pointer to next pages
		# testing single pageInfo
		pages = pagingInfo['pages']
		self.assertTrue(len(pages) > 0)
		pageInfo = pages[0]
		#print pageInfo
		self.assertTrue(len(pageInfo['name']))
		self.assertTrue(len(pageInfo['path']))
		self.assertTrue(len(pageInfo['image']))

	def testSinglePlayItemLoad(self):
		url = 'http://www.ex.ua/view/19475502?r=2,23775'
		playItem = self.model.pagePlaylistDict({'url' : url})
		#print playItem['playitems']
		self.assertTrue(len(playItem['image']) > 0)
		self.assertTrue(1 == len(playItem['playitems']))
		self.assertTrue(len(playItem['description']) > 0)
		self.assertTrue(len(playItem['title']) > 0)
		
		singleItem = playItem['playitems'][0]
		self.assertEqual('http://www.ex.ua/get/43468168', singleItem['path'])
		self.assertEqual('What\'s Eating Gilbert Grape (1993) HDTVRip 720p.mkv', singleItem['name'])

	def testPlaylistLoad(self):
		url = 'http://www.ex.ua/view/17157998?r=1988,23775'
		playlistItem = self.model.pagePlaylistDict({'url' : url})
		#print playItem['playitems']
		self.assertTrue(len(playlistItem['image']) > 0)
		self.assertTrue(len(playlistItem['playitems']) > 1)
		self.assertTrue(len(playlistItem['description']) > 0)
		self.assertTrue(len(playlistItem['title']) > 0)
		#print playlistItem['playitems']
		for episode in playlistItem['playitems']:
			self.assertTrue(len(episode['path']) > 0)
			self.assertTrue(len(episode['name']) > 0)

	def testSearch(self):
		pagingInfo = self.model.searchInSectionPagesDict(2, 'iron man 1080p')
		self.assertIsNotNone(pagingInfo)
		#print pagingInfo
		self.assertTrue(len(pagingInfo['url']))
		self.assertEqual('http://www.ex.ua/search?original_id=2&s=iron+man+1080p', pagingInfo['url'])
		self.assertTrue(len(pagingInfo['paging']))
		self.assertTrue(21 == len(pagingInfo['pages']))
		self.assertFalse(pagingInfo.has_key('search'))
		self.assertFalse(pagingInfo.has_key('next'))
		# testing single pageInfo
		pages = pagingInfo['pages']
		self.assertTrue(len(pages) > 0)
		pageInfo = pages[0]
		#print pageInfo
		self.assertTrue(len(pageInfo['name']))
		self.assertTrue(len(pageInfo['path']))
		self.assertTrue(len(pageInfo['image']))

def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(TestExModel))
	return suite

