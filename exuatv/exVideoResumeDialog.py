# -*- coding: utf-8 -*-
'''
	exVideoResumeDialog.py
	exVideoResumeDialog is a video resume dialog controler (a dialog which
	allows to resume video playback from specific time).
	Copyright (C) 2012-2013 Sergey Maysak a.k.a. sam (segey.maysak@gmail.com)

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
__date__ ="$Aug 29, 2012 11:08:14 PM$"

import mc
import xbmc
import exPlayer
import datetime
import time

class exVideoResumeDialog:
	# constants
	WINDOW_ID = 14110
	LIST_ID = 11
	playItem = None
	isPlaylistActive = False

	# Outlets section - accessors to dialog controls and labels
	def GetList(self):
		return mc.GetWindow(self.WINDOW_ID).GetList(self.LIST_ID)

	def OnLoadDialog(self):
		pass

	def OnShowVideoResumeDialog(self, playItem, referenceItem, isPlaylist):
		self.playItem = playItem
		self.isPlaylistActive = isPlaylist
		timeToResumeInSeconds = 0
		if referenceItem.GetProperty("timeToResume"):
			timeToResumeInSeconds = float(referenceItem.GetProperty("timeToResume"))

		mc.ActivateWindow(self.WINDOW_ID)
		actionItems = mc.ListItems()

		# first (default) iyem represents "continue from ..."
		actionItem = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
		#timeStr = time.strftime("%H:%M:%S", timeToResumeInSeconds)
		#timeStr = datetime.timedelta(seconds=timeToResumeInSeconds)
		actionItem.SetLabel(mc.GetLocalizedString(12022) % self.GetInHMS(timeToResumeInSeconds))
		actionItems.append(actionItem)

		# second item is "start from the beginning"
		actionItem = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
		actionItem.SetLabel(mc.GetLocalizedString(12021))
		actionItems.append(actionItem)

		self.GetList().SetItems(actionItems)

	def GetInHMS(self, seconds):
		hours = int(seconds / 3600)
		seconds -= 3600.0*hours
		minutes = int(seconds / 60)
		seconds -= 60.0*minutes		
		if hours == 0:
			return "%02d:%02d" % (minutes, seconds)
		return "%02d:%02d:%02d" % (hours, minutes, seconds)
