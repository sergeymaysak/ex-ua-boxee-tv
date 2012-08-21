# -*- coding: utf-8 -*-
'''
	exPlayer.py
	Player is responsible to play media - extends mc.Player with functinality
	absent in it - resume of item from stopped time and "play playlist with
	options dialog". Based on idea of MyPlayer from bartsidee.
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
__date__ ="$Sep 18, 2011 10:05:38 PM$"

import xbmc
import mc
import exPlaylistController
import time

class exPlayerEventListener:
	''' Interface of player event listener. Any method is optional for
	implementor. Listener is posed to be assigned to exPlayer.'''
	def onPlaybackStarted(self, exPlayer, playItem):
		'''Called each time playback has started - playItem is instance of
		ListItem'''
		pass

	def onPlaybackStopped(self, exPlayer, playItem, time):
		'''Called each time playback has stopped - playItem is instance of ListItem,
		time is float representing time of stop event. This time can be reused
		later by caller for resume palyback form this time'''
		pass

	def onPlaybackEnded(self, exPlayer, playItem):
		'''Called each time playback has ended for specific palyItem.
		playItem is instance of ListItem'''
		pass

exSharedPlayer = None #holds the global player object

class exPlayer(mc.Player):
	
	def __init__(self):
		mc.Player.__init__(self, True)
		self.playlistController = exPlaylistController.exPlaylistController()
		self.last = self.GetLastPlayerEvent()
		self.referenceItem = None
		self.listener = None
		self.time = 0.0
		self.call = {
			self.EVENT_STOPPED : self.onPlayBackStopped,
            self.EVENT_ENDED  : self.onPlayBackEnded,
            self.EVENT_STARTED : self.onPlayBackStarted
			}

	def runEventLoop(self):
		mc.LogInfo("Playback event monitoring started")
		self.last = self.GetLastPlayerEvent()
		self.time = 0.000
		while True:
			event = self.GetLastPlayerEvent()
			if event != self.last:
				if event in self.call.keys():
					self.last = event
					self.call[event]()
					if event in [self.EVENT_ENDED, self.EVENT_STOPPED]:
						mc.LogInfo("Playback event monitoring stopped")
						break
			elif event == self.EVENT_STARTED:
				try: self.time = self.GetTime()
				except: mc.LogInfo("Player not ready")
			xbmc.sleep(5000)
	
	def onPlayBackStarted(self, **kwargs):
		if self.referenceItem.GetProperty("timeToResume"):
			timeToResume = float(self.referenceItem.GetProperty("timeToResume"))
			mc.LogInfo("Playback resuming to time: %s" % str(timeToResume))
			self.SeekTime(timeToResume)
		if self.listener: self.listener.onPlaybackStarted(self, self.referenceItem)
	
	def onPlayBackEnded(self):
		if self.listener:
			self.referenceItem.SetProperty("timeToResume", str(self.time))
			mc.LogInfo("Playback Time ended: %s" % str(self.time))
			self.listener.onPlaybackEnded(self, self.referenceItem)
	
	def onPlayBackStopped(self):
		if self.listener:
			self.referenceItem.SetProperty("timeToResume", str(self.time))
			mc.LogInfo("Playback Time stopped: %s" % str(self.time))
			self.listener.onPlaybackStopped(self, self.referenceItem, self.time)

	def PlayItemWithMenu(self, playItem, referenceItem):
		self.referenceItem = referenceItem
		self.time = 0.0
		if self.referenceItem.GetProperty("timeToResume"):
			self.Play(playItem)
		else:
			self.PlayWithActionMenu(playItem)
		#event monitoring is disabled - just useless on device
			#xbmc.sleep(4000)
			#if False == self.IsPlayingVideo():
			#	mc.LogInfo("Playback did not started - exit")
			#	return
		#self.runEventLoop()

	def PlayEpisode(self, index):
		self.time = 0.0
		if self.referenceItem:
			self.referenceItem.SetProperty("lastViewedEpisodeIndex", str(index))
		# unlock all actions in player for playlist including move to next and back episodes
		self.LockPlayerAction(self.XAPP_PLAYER_ACTION_NONE)
		self.PlaySelected(index, mc.PlayList.PLAYLIST_VIDEO)
		#event monitoring is disabled
		#self.runEventLoop()

	def PlayEpisodesWithMenu(self, playListItem, episodesList):
		self.referenceItem = playListItem
		videoPlaylist = mc.PlayList(mc.PlayList.PLAYLIST_VIDEO)
		videoPlaylist.Clear()
		for episode in episodesList:
			mc.LogInfo("added to playlist item with name: %s" % episode.GetLabel())
			videoPlaylist.Add(episode)
		#show playlist selection dialog (playlistSelect.xml)
		mc.ActivateWindow(14100)
		mc.LogInfo("show playlist selection dialog called")

	def GetLastViewedEpisodeIndexInPlaylist(self):
		index = 0
		if self.referenceItem.GetProperty("lastViewedEpisodeIndex"):
			index = int(self.referenceItem.GetProperty("lastViewedEpisodeIndex"))
		return index

def GetPlayer():
	global exSharedPlayer
	if (exSharedPlayer is None):
		exSharedPlayer = exPlayer()
	return exSharedPlayer
