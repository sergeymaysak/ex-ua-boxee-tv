# -*- coding: utf-8 -*-

#  testFsModel.py
#  exuatv
#
#  Created by Sergey Maysak on 1/13/13.
#

import fsmodel
import unittest

class TestFsModel(unittest.TestCase):

	def setUp(self):
		self.model = fsmodel.fsmodel()
		
	def testLoadSections(self):
		sections = self.model.sectionsList()
		print sections
		for section in sections:
			print 'section name %s' % section['name']

	def testPagingStructure(self):
		sectionInfo = self.model.sectionsList()[0]
		pagingInfo = self.model.pagesDict(sectionInfo)
		#print pagingInfo
		pageInfo = pagingInfo['pages'][3]
		#print pageInfo
		playDict = self.model.pagePlaylistDict(pageInfo)
		#print playDict
		subfolderInfo = playDict['subfolders'][0]
		#print subfolderInfo
		playSpec = self.model.pagePlaylistDict(subfolderInfo)
		#print "playSpec: %s" % playSpec

	def testLoadNext(self):
		params = { 'path': 'http://fs.ua/video/?view=list&sort=new&page=1',
			'image': '', 'folder': '', 'referer': '',
			'name': 'Next >>' }
		pagingInfo = self.model.pagesDict(params)
		print pagingInfo

#	def testSearchInFilms(self):
#		sectionInfo = self.model.sectionsList()[1]
#		pagingInfo = self.model.searchInSectionPagesDict(sectionInfo, 'Terminator 2')
#		#print pagingInfo
#		pageInfo = pagingInfo['pages'][0]
#		playDict = self.model.pagePlaylistDict(pageInfo)
#		#print playDict
#		subfolderInfo = playDict['subfolders'][0]
#		#print subfolderInfo
#		playSpec = self.model.pagePlaylistDict(subfolderInfo)
#		#print playSpec

def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(TestFsModel))
	return suite