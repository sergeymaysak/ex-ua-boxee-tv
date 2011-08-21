'''
	excontroller.py
	Definition of controller class mediating model and view layer
	Copyright (C) 2011 Sergey Maysak a.k.a. sam

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

import mc
import xbmc
import exmodel

class excontroller:

	# private ivars
	__exmodel = exmodel.exmodel()

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

	def RestorePagesPanelFocusedItem(self):
		#do something to restore missed focus item after video player
		mc.LogInfo("Current pages panel focused item: %s" % self.GetPagesFocusedItem().GetLabel())

	def GetListFocuseditem(self, list):
		return list.GetItem(list.GetFocusedItem())

	def GetSectionFocusedItem(self):
		return self.GetListFocuseditem(self.GetSectionsList())

	def GetPagesFocusedItem(self):
		return self.GetListFocuseditem(self.GetPagesPanel())

	def GetSectionsList(self):
		return mc.GetActiveWindow().GetList(100)

	def GetPagesPanel(self):
		return mc.GetActiveWindow().GetList(200)

	def GetNextControl(self):
		return mc.GetActiveWindow().GetControl(340)

	def GetBackControl(self):
		return mc.GetActiveWindow().GetControl(330)

	def GetNavigationContainer(self):
		return mc.GetActiveWindow().GetList(500)

	def BuildListItemsForPagesList(self, pagesList):
		listItems = mc.ListItems()
		for page in pagesList:
			item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_OTHER)
			item.SetLabel(page["name"])
			item.SetPath(page["path"])
			item.SetThumbnail(page["image"])
			listItems.append(item)
		return listItems

	def GetNavSectionName(self):
		listControl = self.GetNavigationContainer()
		return listControl.GetItem(listControl.GetFocusedItem()).GetLabel()

	def GetNavSearchContext(self):
		listControl = self.GetNavigationContainer()
		return listControl.GetItem(listControl.GetFocusedItem()).GetProperty("search")

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
		nav.append(navItemCurrent)
		# reuse input next item if any
		if nextItem:
			nav.append(nextItem)
		self.GetNavigationContainer().SetItems(nav)
		# set current item as focused
		self.GetNavigationContainer().SetFocusedItem(0)

	def UpdateNavigationContainerForLoadedPages(self, newCurrentNavItem, newNextNavItem, pushNavItem):
		itemList = self.GetNavigationContainer().GetItems()
		mc.LogInfo("listItems items count: %s" % str(self.GetNavigationContainer().GetItems()))
		navList = mc.ListItems()
		for it in self.GetNavigationContainer().GetItems():
			navList.append(it)
		navList.pop()
		if pushNavItem:
			#moving to next
			mc.LogInfo("new paging: %s" % newCurrentNavItem.GetTitle())
			navList.append(newCurrentNavItem)
			navList.append(newNextNavItem)
			self.GetNavigationContainer().SetItems(navList)
			mc.LogInfo("added new nav item with paging: %s" % newCurrentNavItem.GetTitle())
			mc.LogInfo("nav items count: %s" % str(len(navList)))
			self.GetNavigationContainer().SetFocusedItem(len(navList)-2)
		else:
			# moving to previous
			self.GetNavigationContainer().SetItems(navList)
			self.GetNavigationContainer().SetFocusedItem(len(navList)-2)
		mc.LogInfo("nav list:")
		for resNav in navList:
			mc.LogInfo("paging: %s" % resNav.GetTitle())


	def BuildCurrentAndNextItemsForLoadedPagesDict(self, sourceItem, pagesDict):
		currentItem = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
		currentItem.SetLabel(sourceItem.GetLabel())
		currentItem.SetPath(sourceItem.GetPath())
		if pagesDict.has_key("paging"):
			currentItem.SetTitle(pagesDict["paging"])
		if pagesDict.has_key("search"):
			currentItem.SetProperty("search", pagesDict["search"])

		if pagesDict.has_key("next"):
			nextItem = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
			nextEXItem = pagesDict["next"]
			nextItem.SetLabel(sourceItem.GetLabel())
			nextItem.SetPath(nextEXItem["path"])
			nextItem.SetTitle(nextEXItem["name"])
			return currentItem, nextItem
		else:
			return currentItem, None

	# Action handlers from UI controls
	def OnMainWindowLoad(self):
		# load sections menu if it is empty
		mc.LogInfo("On Load Main Window")
		if 0 == len(self.GetSectionsList().GetItems()):
			mc.LogInfo("On Load:Generate sections menu")
			mc.ShowDialogWait()
			sectionsMenu = mc.ListItems()
			sectionsList = self.__exmodel.sectionsList()
			# fill sections list with available items
			for section in sectionsList:
				item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
				item.SetLabel(section["name"])
				item.SetPath(section["path"])
				sectionsMenu.append(item)
			self.GetSectionsList().SetItems(sectionsMenu)
			self.GetSectionsList().SetFocusedItem(0)
			self.OnSectionSelected()
			mc.HideDialogWait()
		self.RestorePagesPanelFocusedItem()

	def OnWindowPopState(self):
		mc.LogInfo("On UnLoad Main Window called")

	def OnSectionSelected(self):
		mc.GetActiveWindow().ClearStateStack(False)
		self.OnLoadSectionPages(self.GetSectionFocusedItem())

	def OnLoadSectionPages(self, listItem, startNewSection = True, pushState = False, pushNavItem = True):
		url = listItem.GetPath()
		mc.ShowDialogWait()
		pagesDict = self.__exmodel.pagesDict(url)
		listItems = self.BuildListItemsForPagesList(pagesDict["pages"])
		currentNavItem, nextNavItem = self.BuildCurrentAndNextItemsForLoadedPagesDict(listItem, pagesDict)
		if pushState is True:
			mc.GetActiveWindow().PushState()
		if pushState or startNewSection:
			self.StartNavNewSection(listItem.GetLabel(), currentNavItem, nextNavItem)
		else:
			self.UpdateNavigationContainerForLoadedPages(currentNavItem, nextNavItem, pushNavItem)
		self.GetPagesPanel().SetItems(listItems)
		mc.HideDialogWait()

	def OnSearchEverywhere(self):
		query = mc.ShowDialogKeyboard("Search EX.UA", "", False)
		if 0 != len(query):
			mc.LogInfo("string to search: %s" % query)
			pagesDict = self.__exmodel.searchAllPagesDict(query)
			listItems = exc.BuildListItemsForPagesList(pagesDict["pages"])
			listItem = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
			listItem.SetLabel("Results for " + query)
			listItem.SetPath(pagesDict["url"])
			currentNavItem, nextNavItem = self.BuildCurrentAndNextItemsForLoadedPagesDict(listItem, pagesDict)
			# start new section for search
			mc.GetActiveWindow().PushState()
			self.StartNavNewSection(listItem.GetLabel(), currentNavItem, nextNavItem)
			self.GetPagesPanel().SetItems(listItems)

	def OnSearchInActiveSection(self):
		if self.GetNavSearchContext():
			query = mc.ShowDialogKeyboard("Search in %s" % self.GetNavSectionName(), "", False)
			if 0 != len(query):
				pagesDict = self.__exmodel.searchInSectionPagesDict(self.GetNavSearchContext(), query)
				pagesList = pagesDict["pages"]
				listItems = exc.BuildListItemsForPagesList(pagesList)
				listItem = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
				listItem.SetLabel("Results for " + query)
				listItem.SetPath(pagesDict["url"])
				currentNavItem, nextNavItem = self.BuildCurrentAndNextItemsForLoadedPagesDict(listItem, pagesDict)
				# start new section for search
				mc.GetActiveWindow().PushState()
				self.StartNavNewSection(listItem.GetLabel(), currentNavItem, nextNavItem)
				self.GetPagesPanel().SetItems(listItems)
	
	def OnFavorites(self):
		mc.ShowDialogOk("User favorites", "Not implemented yet")

	def OnBack(self):
		if self.GetPreviousNavItem():
			mc.LogInfo("backing to item: %s" % self.GetPreviousNavItem().GetLabel())
			#load pages for "back" item without storing result in navigation stack
			self.OnLoadSectionPages(self.GetPreviousNavItem(), False, False, False)

	def OnNext(self):
		if self.GetNavNextPageItem():
			self.OnLoadSectionPages(self.GetNavNextPageItem(), False, False, True)

	def OnPageClick(self):
		focusedItem = self.GetPagesFocusedItem()
		url = focusedItem.GetPath()
		mc.ShowDialogWait()
		exPlaylistDict = self.__exmodel.pagePlaylistDict({"url": url})
		mc.HideDialogWait()
		if exPlaylistDict.has_key("playitems"):
			exPlayitemsList = exPlaylistDict["playitems"]
			if 1 == len(exPlayitemsList):
				exItem = exPlayitemsList[0]
				playItem = mc.ListItem(mc.ListItem.MEDIA_VIDEO_OTHER)
				playItem.SetThumbnail(focusedItem.GetThumbnail())
				playItem.SetTitle(exPlaylistDict["title"])
				playItem.SetDescription(exPlaylistDict["description"])
				playItem.SetLabel(exPlaylistDict["title"])
				playItem.SetPath(exItem["path"])
				mc.GetPlayer().PlayWithActionMenu(playItem)
			else:
				videoPlaylist = mc.PlayList(mc.PlayList.PLAYLIST_VIDEO)
				videoPlaylist.Clear()
				for theItem in exPlayitemsList:
					playItem = mc.ListItem(mc.ListItem.MEDIA_VIDEO_OTHER)
					playItem.SetThumbnail(focusedItem.GetThumbnail())
					#playItem.SetIcon(exPlaylistDict["image"])
					#playItem.SetImage(0, exPlaylistDict["image"])
					playItem.SetTitle(exPlaylistDict["title"])
					playItem.SetDescription(exPlaylistDict["description"])
					playItem.SetLabel(theItem["name"])
					playItem.SetPath(theItem["path"])
					mc.LogInfo("added to playlist item with name: %s" % theItem["name"])
					videoPlaylist.Add(playItem)
				#show playlist selection dialog (playlistSelect.xml)
				mc.ActivateWindow(14100)
				mc.LogInfo("show playlist selection dialog called")
		else:
			if self.GetNavNextPageItem() and self.GetNavNextPageItem().GetPath() == focusedItem.GetPath():
				# go to next manually to not push window state
				self.OnNext()
			else:
				#we have link to dig into with pushing window state
				self.OnLoadSectionPages(focusedItem, True, True, True)

#global ex controller instance accessible from main.xml
exc = excontroller()