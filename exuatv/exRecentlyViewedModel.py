# -*- coding: utf-8 -*-
'''
	exRecentlyViewedModel.py
	exRecentlyViewedModel represent a model for ListItems that were recenly
	viewed. Provides facility to load/store viewed items in prefs and manages
	number of items stored.
	Copyright (C) 2011-2013 Sergey Maysak a.k.a. sam (segey.maysak@gmail.com)

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
__date__ ="$Sep 17, 2011 10:48:49 PM$"

import mc
import pickle

class exRecentlyViewedModel:

	def __init__(self):
		self.historyItems = self.RestoreFromDefaults()

	def SaveItem(self, item):
		mc.LogInfo("saving item: %s" % item.GetLabel())
		if item:
			itemToRemove = self.GetItemIdenticalToItem(item)
			if itemToRemove:
				mc.LogInfo("Replace history item")
				self.historyItems.remove(itemToRemove)
			self.historyItems.insert(0, item)
			if self.historyItems[0].GetProperty("timeToResume"):
				mc.LogInfo("item time to resume: %s" % str(self.historyItems[0].GetProperty("timeToResume")))
		# limit number of saved items to 25
		if len(self.historyItems) > 25:
			self.historyItems.pop()
		mc.LogInfo("number of saved items: %s" % str(len(self.historyItems)))
		self.StoreToDefaults()

	def GetHistoryItemsList(self):
		list = mc.ListItems()
		for item in self.historyItems:
			list.append(item)
		return list

	def GetItemIdenticalToItem(self, item):
		for i in self.historyItems:
			if i.GetPath() == item.GetPath():
				return i
		return None

	def StoreToDefaults(self):
		listToStore = []
		for item in self.historyItems:
			theDict = {"path" : item.GetPath(), "title" : item.GetLabel()}
			theDict["description"] = item.GetDescription()
			theDict["image"] = item.GetThumbnail()
			if item.GetProperty("timeToResume"):
				theDict["timeToResume"] = str(item.GetProperty("timeToResume"))
			if item.GetProperty("lastViewedEpisodeIndex"):
				theDict["lastViewedEpisodeIndex"] = str(item.GetProperty("lastViewedEpisodeIndex"))
			listToStore.append(theDict);

		stringRep = pickle.dumps(listToStore)
		if stringRep != None:
			mc.GetApp().GetLocalConfig().SetValue("history-items", stringRep)

	def RestoreFromDefaults(self):
		stringRep = mc.GetApp().GetLocalConfig().GetValue("history-items")
		if len(stringRep) > 0:
			#mc.LogInfo("string representation of items: %s" % stringRep)
			listLoaded = pickle.loads(stringRep)
			list = []
			for item in listLoaded:
				type = mc.ListItem.MEDIA_VIDEO_FEATURE_FILM
				playItem = mc.ListItem(type)
				playItem.SetThumbnail(item["image"])				
				playItem.SetTitle(item["title"])
				playItem.SetDescription(item["description"])
				playItem.SetLabel(item["title"])
				playItem.SetPath(item["path"])
				if item.has_key("timeToResume"):
					playItem.SetProperty("timeToResume", item["timeToResume"])
				if item.has_key("lastViewedEpisodeIndex"):
					playItem.SetProperty("lastViewedEpisodeIndex", item["lastViewedEpisodeIndex"])
				list.append(playItem)

			return list

		else:
			return []
