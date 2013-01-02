# -*- coding: utf-8 -*-
'''
	exPlayMediaDialogController.py
	exPlayMediaDialogController is a controler of dialog of play media with options.
	Copyright (C) 2012 Sergey Maysak a.k.a. sam

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
__date__ ="$Sep 4, 2012 23:34:14 PM$"

import mc
import xbmc
import exlocalizer
import exPlayer

class exPlayMediaDialogController:
	# constants
	WINDOW_ID = 14120
	ITEM_LIST_ID = 5000
	ACTION_LIST_ID = 7110
	playItem = None

	# Outlets section
	def GetItemList(self):
		return mc.GetWindow(self.WINDOW_ID).GetList(self.ITEM_LIST_ID)
	
	def GetActionsList(self):
		return mc.GetWindow(self.WINDOW_ID).GetList(self.ACTION_LIST_ID)

	# public
	# shows play media window with
	def ShowWithItem(self, playItem):
		self.playItem = playItem
		mc.ActivateWindow(self.WINDOW_ID)

	# private
	# called each time window to play media is loaded on screen
	def OnDialogLoad(self):
		items = mc.ListItems()
		items.append(self.playItem)
		self.GetItemList().SetItems(items)
		self.GetItemList().SetFocusedItem(0)

		# fill up actions buttons list
		actionItems = mc.ListItems()

		actionItem = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
		# localize with 'add to favorites'
		actionItem.SetLabel(mc.GetLocalizedString(14086))
		actionItem.SetThumbnail('action_play.png')
		actionItems.append(actionItem)

		actionItem = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
		# localize with 'add to favorites'
		actionItem.SetLabel(exlocalizer.GetSharedLocalizer().localizedString('Add to Favorites'))
		actionItem.SetThumbnail('action_queue_add.png')
		actionItems.append(actionItem)
		self.GetActionsList().SetItems(actionItems)

	# private
	# handler of click on actions list - currently only one action supported -
	# toggle add/remove to favorites
	def OnAction(self):
		index = self.GetActionsList().GetFocusedItem()
		item = self.GetActionsList().GetItem(index)
		if 0 == index:
			self.onPlayMedia()
		elif 1 == index:
			self.OnToggleFavorites()
		else:
			mc.LogInfo("selected action (%s) is not supported yet" % item.GetLabel());

	def onPlayMedia(self):
		exPlayer.GetPlayer().OnPlayItemFromMediaDialog()

	def OnToggleFavorites(self):
		pass
