# -*- coding: utf-8 -*-
'''
	exPlaylistController.py
	exPlaylistController is a playlist selection dialog controler.
	Copyright (C) 2011-2012 Sergey Maysak a.k.a. sam

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
__date__ ="$Aug 31, 2011 1:11:47 AM$"

import mc
import xbmc
import exPlayer

class exPlaylistController:
	# constants
	WINDOW_ID = 14100
	PLOT_WINDOW_ID = 14101
	PLAYLIST_LIST_ID = 105
	DIALOG_LABEL_ID = 106
	ACTIONS_GROUP_ID = 1500
	ACTIONS_LIST_ID = 1510
	OUTLINE_GROUP_ID = 1600
	OUTLINE_TEXT_ID = 1620
	OUTLINE_SCROLLER_ID = 1630

	# Outlets section - accessors to dialog controls and labels
	def GetPlaylistList(self):
		return mc.GetWindow(self.WINDOW_ID).GetList(self.PLAYLIST_LIST_ID)

	def GetDialogTitleLabel(self):
		return mc.GetWindow(self.WINDOW_ID).GetLabel(self.DIALOG_LABEL_ID)

	def GetActionsList(self):
		return mc.GetWindow(self.WINDOW_ID).GetList(self.ACTIONS_LIST_ID)

	def OnDialogLoad(self):
		# external caller is responsible to prepare shared boxee video playlist
		# before show this dialog
		videoPlaylist = mc.PlayList(mc.PlayList.PLAYLIST_VIDEO)
		videos = mc.ListItems()
		for i in range(videoPlaylist.Size()):
			playlistItem = videoPlaylist.GetItem(i)
			item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_EPISODE)
			item.SetLabel(playlistItem.GetLabel())
			item.SetDescription(playlistItem.GetDescription())
			item.SetPath(playlistItem.GetPath())
			videos.append(item)
		self.GetPlaylistList().SetItems(videos)
		index = exPlayer.GetPlayer().GetLastViewedEpisodeIndexInPlaylist()
		self.GetPlaylistList().SetFocusedItem(index)
		self.GetPlaylistList().SetSelected(index, True)
		
		dialogTitle = mc.GetLocalizedString(559) + ": " + videoPlaylist.GetItem(0).GetTitle()
		self.GetDialogTitleLabel().SetLabel(dialogTitle)

		# fill up actions buttons list
		actionItems = mc.ListItems()
		actionItem = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
		# localize with 'more info'
		actionItem.SetLabel(mc.GetLocalizedString(53710))
		actionItem.SetThumbnail('action_more.png')
		actionItems.append(actionItem)

		actionItem = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
		# localize with 'add to queue/watch later'
		actionItem.SetLabel(mc.GetLocalizedString(53711))
		actionItem.SetThumbnail('action_queue_add.png')
		actionItems.append(actionItem)

		self.GetActionsList().SetItems(actionItems)
		mc.LogInfo("Select playlist window is loaded")
	
	def OnPlayListItemSelected(self):
		exPlayer.GetPlayer().PlayEpisode(self.GetPlaylistList().GetFocusedItem())

	def OnAction(self):
		index = self.GetActionsList().GetFocusedItem()
		item = self.GetActionsList().GetItem(index)
		if 0 == index:
			self.OnMoreInfoForItem(item)
		elif 1 == index:
			self.OnAddItemToQueue(item)
		else:
			mc.LogInfo("selected action (%s) is not supported yet" % item.GetLabel());

	def OnMoreInfoForItem(self, item):
		mc.ActivateWindow(self.PLOT_WINDOW_ID)

	def OnAddItemToQueue(self, item):
		pass

	def OnLoadPlaylistPlotDialog(self):
		items = mc.ListItems()
		items.append(self.GetPlaylistList().GetItem(self.GetPlaylistList().GetFocusedItem()))
		mc.GetWindow(self.PLOT_WINDOW_ID).GetList(111).SetItems(items)
		mc.GetWindow(self.PLOT_WINDOW_ID).GetList(111).SetFocusedItem(0)
