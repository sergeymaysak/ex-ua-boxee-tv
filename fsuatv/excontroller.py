# -*- coding: utf-8 -*-
'''
	excontroller.py
	Definition of controller class mediating model and view layer
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
__date__ ="$Aug 9, 2011 12:53:46 AM$"

import os
import mc
import xbmc
import fsmodel
import exlocalizer
import exRecentlyViewedModel
import exPlayer
import tracker

class excontroller(exPlayer.exPlayerEventListener):
	
	SECTIONS_LIST_ID = 100
	PAGES_PANEL_ID = 200
	SEARCH_ALL_ID = 310
	SEARCH_ID = 320

	def __init__(self):
		self.localizer = exlocalizer.GetSharedLocalizer()
		self.model = fsmodel.fsmodel(self.localizer)
		self.historyModel = exRecentlyViewedModel.exRecentlyViewedModel()
		exPlayer.GetPlayer().listener = self
	
	def localizedString(self, text):
		return self.localizer.localizedString(text)
	
	def SavePagesFocusedItem(self):
		currentNavItem = self.GetListFocusedItem(self.GetNavigationContainer())
		currentNavItem.SetProperty("pagesFocusedIndex", str(self.GetPagesPanel().GetFocusedItem()))

	def SaveSectionsFocusedItem(self):
		currentNavItem = self.GetListFocusedItem(self.GetNavigationContainer())
		currentNavItem.SetProperty("sectionsFocusedIndex", str(self.GetSectionsList().GetFocusedItem()))

	def RestorePagesPanelFocusedItem(self):
		mc.LogInfo("RestorePagesPanelFocusedItem")
		navFocusedItem = self.GetListFocusedItem(self.GetNavigationContainer())
		if navFocusedItem.GetProperty("pagesFocusedIndex"):
			mc.LogInfo("FixupNavigation restored pages panel focused index to %s" % str(navFocusedItem.GetProperty("pagesFocusedIndex")))
			self.GetPagesPanel().SetFocusedItem(int(navFocusedItem.GetProperty("pagesFocusedIndex")))

	def RestoreSectionsFocusedItem(self):
		navFocusedItem = self.GetListFocusedItem(self.GetNavigationContainer())
		if navFocusedItem.GetProperty("sectionsFocusedIndex"):
			self.GetSectionsList().SetFocusedItem(int(navFocusedItem.GetProperty("sectionsFocusedIndex")))

	def SaveWindowState(self):
		# save all focused items
		currentFocusControlId = self.PAGES_PANEL_ID
		# find current focused control
		if self.GetControl(self.SEARCH_ALL_ID).HasFocus():
			currentFocusControlId = self.SEARCH_ALL_ID
		elif self.GetControl(self.SEARCH_ID).HasFocus():
			currentFocusControlId = self.SEARCH_ID
		elif self.GetControl(self.PAGES_PANEL_ID).HasFocus():
			currentFocusControlId = self.PAGES_PANEL_ID
		# store current focus info in nav container's focused item
		currentNavItem = self.GetListFocusedItem(self.GetNavigationContainer())
		currentNavItem.SetProperty("focusId", str(currentFocusControlId))
		self.SavePagesFocusedItem()
		self.GetNavAnchorControl().SetFocus()
		mc.GetActiveWindow().PushState()
		self.GetControl(currentFocusControlId).SetFocus()
		# tell user how to go back ;)
		mc.ShowDialogNotification(mc.GetLocalizedString(53112))

	def FixupNavigation(self):
		mc.LogInfo("Playback FixupNavigation")
		pagesList = self.GetPagesPanel().GetItems()
		panelUrl = ''
		if len(pagesList) > 0: panelUrl = pagesList[0].GetProperty("panelurl")
		listControl = self.GetNavigationContainer()
		navFocusedItem = self.GetListFocusedItem(listControl)
		if navFocusedItem.GetPath() != panelUrl:
			indexOfNavItemToFocus = self.FindIndexOfNavItemWithPanelUrl(panelUrl)
			listControl.SetFocusedItem(indexOfNavItemToFocus)
		# restore focused control
		navFocusedItem = self.GetListFocusedItem(listControl)
		controlIDToFocus = -1
		if navFocusedItem.GetProperty("focusId"):
			controlIDToFocus = int(navFocusedItem.GetProperty("focusId"))
		if controlIDToFocus != -1:
			mc.LogInfo("FixupNavigation restored focus to control with id %s" % str(controlIDToFocus))
			self.GetControl(controlIDToFocus).SetFocus()
		# restore focused item in pages panel and in sections list
		self.RestorePagesPanelFocusedItem()
		self.RestoreSectionsFocusedItem()		
		if exPlayer.GetPlayer().referenceItem != None:
			exPlayer.GetPlayer().referenceItem = None

	def FindIndexOfNavItemWithPanelUrl(self, panelUrl):
		navItems = self.GetNavigationContainer().GetItems()
		index = 0
		for i in range(len(navItems)):
			if navItems[i].GetPath() == panelUrl:
				index = i
				break
		return index

	def GetNavFocusedIndex(self):
		listControl = self.GetNavigationContainer()
		return listControl.GetFocusedItem()

	def GetPreviousNavItem(self):
		listControl = self.GetNavigationContainer()
		focusedIndex = listControl.GetFocusedItem()
		if focusedIndex - 1 < 0:
			mc.LogInfo("nav Items has no previous item")
			return None
		else:
			mc.LogInfo("return prev nav item: %s" % listControl.GetItem(focusedIndex-1).GetTitle())
			return listControl.GetItem(focusedIndex-1)

	def GetNavNextPageItem(self):
		listControl = self.GetNavigationContainer()
		focusedIndex = listControl.GetFocusedItem()
		mc.LogInfo("nav focused index: %s" % str(focusedIndex))
		mc.LogInfo("nav items count: %s" % str(len(listControl.GetItems())))
		if focusedIndex + 1 < len(listControl.GetItems()):
			mc.LogInfo("returning next nav item with paging: %s" % listControl.GetItem(focusedIndex+1).GetTitle())
			return listControl.GetItem(focusedIndex+1)
		else:
			return None

	def GetControl(self, id):
		return mc.GetActiveWindow().GetControl(id)

	def GetListFocusedItem(self, list):
		return list.GetItem(list.GetFocusedItem())

	def GetSectionFocusedItem(self):
		return self.GetListFocusedItem(self.GetSectionsList())

	def GetPagesFocusedItem(self):
		return self.GetListFocusedItem(self.GetPagesPanel())

	def GetSectionsList(self):
		return mc.GetActiveWindow().GetList(self.SECTIONS_LIST_ID)

	def GetPagesPanel(self):
		return mc.GetActiveWindow().GetList(self.PAGES_PANEL_ID)

	def GetSearchAllControl(self):
		return self.GetControl(self.SEARCH_ALL_ID)

	def GetSearchControl(self):
		return self.GetControl(self.SEARCH_ID)

	def GetNextControl(self):
		return self.GetControl(340)

	def GetBackControl(self):
		return self.GetControl(330)

	def GetNavigationContainer(self):
		return mc.GetActiveWindow().GetList(500)

	def GetNavAnchorControl(self):
		return self.GetControl(510)

	def BuildPanelItemsList(self, pagesDict):
		listItems = mc.ListItems()
		for page in pagesDict["pages"]:
			item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_OTHER)
			item.SetLabel(page["name"])
			item.SetPath(page["path"])
			item.SetThumbnail(page["image"])
			if page.has_key("isSearch"):
				item.SetProperty("isSearch", "true")
			if pagesDict.has_key("url"):
				item.SetProperty("panelurl", pagesDict["url"])
			if page.has_key("referer"):
				item.SetProperty("referer", page["referer"])			
			if page.has_key("folder"):
				item.SetProperty("folder", page["folder"])
			if page.has_key("id"):
				item.SetProperty("id", page["id"])
			listItems.append(item)
		return listItems

	def GetNavSectionName(self):
		listControl = self.GetNavigationContainer()
		return listControl.GetItem(listControl.GetFocusedItem()).GetLabel()

	def GetNavSearchContext(self):
		listControl = self.GetNavigationContainer()
		return listControl.GetItem(listControl.GetFocusedItem()).GetProperty("search")

	def IsRecentlyViewedActive(self):
		listControl = self.GetNavigationContainer()
		return "history://" == listControl.GetItem(listControl.GetFocusedItem()).GetPath()

	def StartNavNewSection(self, name, currentItem, nextItem):
		mc.LogInfo("start new section navigation for name: %s" % name)
		nav = mc.ListItems()
		# build current item from scratch
		navItemCurrent = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
		navItemCurrent.SetLabel(name)
		navItemCurrent.SetTitle(currentItem.GetTitle())
		navItemCurrent.SetPath(currentItem.GetPath())
		if currentItem.GetProperty("search"):
			navItemCurrent.SetProperty("search", currentItem.GetProperty("search"))
		if currentItem.GetProperty("isSearch"):
			navItemCurrent.SetProperty("isSearch", "true")
		nav.append(navItemCurrent)
		# reuse input next item if any
		if nextItem:
			nextItem.SetLabel(name)
			nav.append(nextItem)
		self.GetNavigationContainer().SetItems(nav)
		# set current item as focused
		self.GetNavigationContainer().SetFocusedItem(0)

	def UpdateNavigationContainerForLoadedPages(self, newCurrentNavItem, newNextNavItem, pushNavItem):
		#rebuild nav list for new items
		navList = mc.ListItems()
		for it in self.GetNavigationContainer().GetItems():
			navList.append(it)
		# remove previosly stored next if any - it will be replaced by input new current item
		if len(navList) > 0: navList.pop()
		if pushNavItem:
			#moving to next
			navList.append(newCurrentNavItem)
			if newNextNavItem: navList.append(newNextNavItem)
		else:
			#moving to back - add next in case if list has inly one item that represents current item
			if len(navList) < 2 and newNextNavItem: navList.append(newNextNavItem)
		self.GetNavigationContainer().SetItems(navList)
		if newNextNavItem:
			indexToFocus = len(navList) - 2
		else:
			indexToFocus = len(navList) - 1
		if indexToFocus < 0: indexToFocus = 0
		mc.LogInfo("focus index item: %s nav list len: %s" % (str(indexToFocus), str(len(navList))))

		self.GetNavigationContainer().SetFocusedItem(indexToFocus)

	def BuildCurrentAndNextItemsForLoadedPagesDict(self, sourceItem, pagesDict):
		currentItem = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
		currentItem.SetLabel(sourceItem.GetLabel())
		currentItem.SetPath(sourceItem.GetPath())
		if pagesDict.has_key("paging"):
			currentItem.SetTitle(pagesDict["paging"])
		if pagesDict.has_key("search"):
			currentItem.SetProperty("search", pagesDict["search"])
		if sourceItem.GetProperty("isSearch"):
			currentItem.SetProperty("isSearch", "true")
		mc.LogInfo("current item: %s %s" % (currentItem.GetTitle(), currentItem.GetPath()))
		if pagesDict.has_key("next"):
			nextItem = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
			nextEXItem = pagesDict["next"]
			nextItem.SetLabel(sourceItem.GetLabel())
			nextItem.SetPath(nextEXItem["path"])
			nextItem.SetTitle(nextEXItem["name"])
			if pagesDict.has_key("search"):
				nextItem.SetProperty("search", pagesDict["search"])
			if nextEXItem.has_key("isSearch"):
				nextItem.SetProperty("isSearch", "true")
			mc.LogInfo("next item: %s %s" % (nextItem.GetTitle(), nextItem.GetPath()))
			return currentItem, nextItem
		else:
			return currentItem, None

	def LoadSectionsList(self, loadAttempt = 1):
		mc.ShowDialogWait()
		sectionsList = self.model.sectionsList()
		if 0 == len(sectionsList) and loadAttempt < 3:
			mc.HideDialogWait()
			self.model = fsmodel.fsmodel(self.localizer, True)
			sectionsList = self.LoadSectionsList(loadAttempt + 1)
		mc.HideDialogWait()
		return sectionsList

	# Action handlers from UI controls
	def OnMainWindowLoad(self):
		# load sections menu if it is empty
		#systemVersion = xbmc.getInfoLabel('System.BuildVersion')
		#mc.LogInfo("system version: %s" % systemVersion)

		mc.LogInfo("On Load Main Window")
		if 0 == len(self.GetSectionsList().GetItems()):
			tracker.trackMainView('UA-25431823-1')
			mc.LogInfo("On Load: Generate sections menu")
			sectionsMenu = mc.ListItems()
			sectionsList = self.LoadSectionsList()
			if 0 == len(sectionsList):
				mc.LogInfo("Failed to load data from url: %s" % self.model.URL)
				mc.ShowDialogOk(self.localizedString("No access to www.ex.ua and fex.net"), self.localizedString("Please make sure you have proxy disabled and check access to www.ex.ua or fex.net in internet browser"))
				mc.GetApp().Close()
				return
			mc.ShowDialogWait()
			# fill sections list with available items
			for section in sectionsList:
				item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
				item.SetLabel(section["name"])
				item.SetPath(section["path"])
				item.SetProperty("search", str(section["cleanUrl"]))
				sectionsMenu.append(item)
			self.GetSectionsList().SetItems(sectionsMenu)
			self.GetSectionsList().SetFocusedItem(0)
			self.GetControl(self.SECTIONS_LIST_ID).SetVisible(True)
			self.OnSectionSelected()
			mc.HideDialogWait()
		else:
			mc.LogInfo("Main Window Re-load")
			self.FixupNavigation()
			if self.IsRecentlyViewedActive():
				self.ReloadRecentlyViewedSection()

	def OnSectionSelected(self):
		mc.GetActiveWindow().ClearStateStack(False)
		sectionItem = self.GetSectionFocusedItem()
		if sectionItem is None: sectionItem = self.GetSectionsList().GetItem(0)
		self.OnLoadSectionPages(sectionItem)
	
	def OnLoadSubfolders(self, listItem, playDict):
		subfolders = playDict['subfolders']
		mc.ShowDialogWait()
		pagesDict = {'pages' : subfolders, 'url' : listItem.GetPath(), 'paging': ''}
		listItems = self.BuildPanelItemsList(pagesDict)
		currentNavItem, nextNavItem = self.BuildCurrentAndNextItemsForLoadedPagesDict(listItem, pagesDict)
		#if pushState is True:
		self.SaveWindowState()
		#if pushState or startNewSection:
		self.StartNavNewSection(listItem.GetLabel(), currentNavItem, nextNavItem)
		#else:
		#self.UpdateNavigationContainerForLoadedPages(currentNavItem, nextNavItem, True)
		self.GetPagesPanel().SetItems(listItems)
		mc.HideDialogWait()
	
	def OnLoadSectionPages(self, listItem, startNewSection = True, pushState = False, pushNavItem = True):
		url = listItem.GetPath()
		mc.LogInfo("url to load: %s" % url)
		mc.ShowDialogWait()
		if listItem.GetProperty("isSearch"):
			pagesDict = self.model.searchPagesDict(url)
		else:
			cleanURL = listItem.GetProperty('search')
			mc.LogInfo('cleanURL for input item is: %s' % cleanURL)
			pagesDict = self.model.pagesDict({'path' : url, 'cleanUrl' : cleanURL})
		listItems = self.BuildPanelItemsList(pagesDict)
		currentNavItem, nextNavItem = self.BuildCurrentAndNextItemsForLoadedPagesDict(listItem, pagesDict)
		if pushState is True:
			self.SaveWindowState()
		if pushState or startNewSection:
			self.StartNavNewSection(listItem.GetLabel(), currentNavItem, nextNavItem)
		else:
			self.UpdateNavigationContainerForLoadedPages(currentNavItem, nextNavItem, pushNavItem)
		self.GetPagesPanel().SetItems(listItems)
		mc.HideDialogWait()

	def OnSearchEverywhere(self):
		query = mc.ShowDialogKeyboard(mc.GetLocalizedString(137) + " FS.UA", "", False)
		if 0 != len(query):
			mc.LogInfo("string to search: %s" % query)
			mc.ShowDialogWait()
			pagesDict = self.model.searchAllPagesDict(query)
			self.UpdatePagesPanelWithSearchResults(query, pagesDict)
			mc.HideDialogWait()

	def OnSearchInActiveSection(self):
		if self.GetNavSearchContext():
			query = mc.ShowDialogKeyboard(mc.GetLocalizedString(137) + " " + mc.GetLocalizedString(1405) + " " + self.GetNavSectionName(), "", False)
			if 0 != len(query):
				mc.ShowDialogWait()
				pagesDict = self.model.searchInSectionPagesDict(self.GetNavSearchContext(), query)
				self.UpdatePagesPanelWithSearchResults(query, pagesDict)
				mc.HideDialogWait()
		else:
			mc.LogInfo("No search context present - unable to perform search in active section")

	def UpdatePagesPanelWithSearchResults(self, query, pagesDict):
		listItems = exc.BuildPanelItemsList(pagesDict)
		listItem = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
		listItem.SetLabel(mc.GetLocalizedString(283) + ': ' + query)
		listItem.SetPath(pagesDict["url"])
		listItem.SetProperty("isSearch", "true")
		currentNavItem, nextNavItem = self.BuildCurrentAndNextItemsForLoadedPagesDict(listItem, pagesDict)
		# start new section for search
		self.SaveWindowState()
		self.StartNavNewSection(listItem.GetLabel(), currentNavItem, nextNavItem)
		self.GetPagesPanel().SetItems(listItems)

	def OnRecentlyViewed(self):
		if not self.IsRecentlyViewedActive():
			listItem = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
			listItem.SetLabel(self.localizedString("Recently Viewed"))
			listItem.SetPath("history://")
			self.SaveWindowState()
			self.StartNavNewSection(listItem.GetLabel(), listItem, None)
		self.ReloadRecentlyViewedSection()

	def ReloadRecentlyViewedSection(self):
		listItems = self.historyModel.GetHistoryItemsList()
		self.GetPagesPanel().SetItems(listItems)
		self.GetPagesPanel().SetFocusedItem(0)

	def OnBack(self):
		if self.GetPreviousNavItem():
			mc.LogInfo("backing to item: %s" % self.GetPreviousNavItem().GetLabel())
			#load pages for "back" item without storing result in navigation stack
			self.OnLoadSectionPages(self.GetPreviousNavItem(), False, False, False)

	def OnNext(self):
		if self.GetNavNextPageItem():
			mc.LogInfo("next item path: %s" % self.GetNavNextPageItem().GetPath())
			self.OnLoadSectionPages(self.GetNavNextPageItem(), False, False, True)

	def GetPlayableItemForItemInDict(self, item, playDict):
		mc.LogInfo("Flow: Created item of type MEDIA_VIDEO_CLIP")
		#mc.LogInfo("playDict image: %s" % playDict["image"])
		type = mc.ListItem.MEDIA_VIDEO_CLIP
		playItem = mc.ListItem(type)
		playItem.SetThumbnail(playDict["image"])
		#playItem.SetIcon(playDict["image"])
		#playItem.SetImage(0, playDict["image"])
		playItem.SetTitle(playDict["title"])
		playItem.SetDescription(playDict["description"])
		playItem.SetLabel(playDict["title"])
		playItem.SetPath(item["path"])
		playItem.SetAddToHistory(True)
		playItem.SetProviderSource('www.fs.ua')
		return playItem

	def DoesItemPointToTrailer(self, itemDict):
		names = ['trailer', 'sample', 'трейлер']
		name, ext = os.path.splitext(itemDict["name"])
		if name.lower() in names:
			return True
		return False

	def DoesPlaylistContainTrailer(self, playItemsList):
		for item in playItemsList:
			if self.DoesItemPointToTrailer(item):
				return True
		return False

	def GetFullMovieItemFromList(self, playItemsList):
		for item in playItemsList:
			if False == self.DoesItemPointToTrailer(item):
				return item
		return playItemsList[0]

	def RunPlayerForItemsFromDict(self, sourcePageItem, playDict):
		exPlayitemsList = playDict["playitems"]
		if 1 == len(exPlayitemsList):
			exItem = exPlayitemsList[0]
			playItem = self.GetPlayableItemForItemInDict(exItem, playDict)
			exPlayer.GetPlayer().PlayItemWithMenu(playItem, sourcePageItem)
		elif 2 == len(exPlayitemsList) and self.DoesPlaylistContainTrailer(exPlayitemsList):
			exItem = self.GetFullMovieItemFromList(exPlayitemsList)
			playItem = self.GetPlayableItemForItemInDict(exItem, playDict)
			exPlayer.GetPlayer().PlayItemWithMenu(playItem, sourcePageItem)
		else:
			eposodesList = mc.ListItems()
			for theItem in exPlayitemsList:
				playItem = self.GetPlayableItemForItemInDict(theItem, playDict)
				playItem.SetLabel(theItem["name"])
				eposodesList.append(playItem)
			exPlayer.GetPlayer().PlayEpisodesWithMenu(sourcePageItem, eposodesList)

	def OnPageClick(self):
		focusedItem = self.GetPagesFocusedItem()
		self.SavePagesFocusedItem()
		self.SaveSectionsFocusedItem()
		url = focusedItem.GetPath()
		mc.ShowDialogWait()
		params = {'path' : url, 'name' : focusedItem.GetLabel(),
			'image' : focusedItem.GetThumbnail(),
			'referer' : focusedItem.GetProperty('referer'),
			'folder' : focusedItem.GetProperty('folder')}
		mc.LogInfo("params for loading play list dict %s" % str(params))
		playDict = self.model.pagePlaylistDict(params)
		mc.HideDialogWait()
		if playDict.has_key("playitems"):
			self.RunPlayerForItemsFromDict(focusedItem, playDict)
		elif playDict.has_key("subfolders"):
			self.OnLoadSubfolders(focusedItem, playDict)
		else:
			if self.GetNavNextPageItem() and self.GetNavNextPageItem().GetPath() == url:
				# go to next manually to not push window state
				self.OnNext()
			else:
				#we have link to dig into with pushing window state
				self.OnLoadSectionPages(focusedItem, True, True, True)

	# playback listener adoption
	def onPlaybackStarted(self, exPlayer, playItem):
		mc.LogInfo("Playback started for item: %s" % playItem.GetLabel())
		self.historyModel.SaveItem(playItem)

	def onPlaybackStopped(self, exPlayer, playItem, time):
		mc.LogInfo("Playback stopped for item: %s at time: %s" % (playItem.GetLabel(), str(time)))
		# update saved item with sto time
		self.historyModel.SaveItem(playItem)
		exPlayer.referenceItem = None

	def onPlaybackEnded(self, exPlayer, playItem):
		mc.LogInfo("Playback ended for item: %s" % playItem.GetLabel())
		self.historyModel.SaveItem(playItem)
		exPlayer.referenceItem = None

#global ex controller instance accessible from main.xml
exc = excontroller()