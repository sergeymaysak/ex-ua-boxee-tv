# -*- coding: utf-8 -*-
'''
	exPlayer.py
	Player is responsible to play media - extends mc.Player with functinality
	absent in it - resume of item from stopped time and "play playlist with
	options dialog". Based on idea of MyPlayer from bartsidee.
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
__date__ ="$Sep 18, 2011 10:05:38 PM$"

import xbmc
import mc
import exPlaylistController
import time
import threading
import exVideoResumeDialog
import exPlayMediaDialogController

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
		self.exVideoResumeDialog = exVideoResumeDialog.exVideoResumeDialog()
		self.playMediaController = exPlayMediaDialogController.exPlayMediaDialogController()
		self.last = self.GetLastPlayerEvent()
		self.referenceItem = None
		self.listener = None
		self.time = 0.0
		self.call = {
			self.EVENT_STOPPED : self.onPlayBackStopped,
            self.EVENT_ENDED  : self.onPlayBackEnded,
            self.EVENT_STARTED : self.onPlayBackStarted
			}

	def lastEventDescription(self):
		if self.last == self.EVENT_STARTED: return "event_started"
		elif self.last == self.EVENT_ENDED: return "event_ended"
		elif self.last == self.EVENT_STOPPED: return "event_stopped"
		elif self.last == self.EVENT_NONE: return "event_none"
		elif self.last == self.EVENT_NEXT_ITEM: return "event_next_item"
		else: return "unknown_event"

	def runEventLoop(self):
		mc.LogInfo("Playback event monitoring started")
		#mc.LogInfo("player last event %s" % self.lastEventDescription())
		self.time = 0.000
		self.last = self.GetLastPlayerEvent()
		#mc.LogInfo("player last event %s" % self.lastEventDescription())
		while True:
			event = self.GetLastPlayerEvent()
			if event != self.last:
				if event in self.call.keys():
					self.last = event
					self.call[event]()
					if event in [self.EVENT_ENDED, self.EVENT_STOPPED]:
						mc.LogInfo("Playback event monitoring stopped")
						break
			try: self.time = self.GetTime()
			except:
				mc.LogInfo("Player not ready")
				if (self.last == self.EVENT_STARTED):
					break
			#mc.LogInfo("Time updated to %s" % str(self.time))
			#mc.LogInfo("player last event %s" % self.lastEventDescription())
			xbmc.sleep(5000)
	
	def onPlayBackStarted(self, **kwargs):
		if self.listener: self.listener.onPlaybackStarted(self, self.referenceItem)
	
	def onPlayBackEnded(self):
		if self.listener:
			mc.LogInfo("Playback Time ended: %s" % str(self.time))
			self.referenceItem.SetProperty("timeToResume", str(0.0))
			self.listener.onPlaybackEnded(self, self.referenceItem)
	
	def onPlayBackStopped(self):
		if self.listener:
			mc.LogInfo("Playback Time stopped: %s" % str(self.time))
			self.referenceItem.SetProperty("timeToResume", str(self.time))			
			self.listener.onPlaybackStopped(self, self.referenceItem, self.time)

	def seekTo(self, seconds):
		while(self.IsPlayingVideo() != True):
			i = 0
		mc.LogInfo("Perform seek to: %s" % str(seconds))
		seconds = float(seconds)
		self.SeekTime(seconds)

	def PlayItemWithMenu(self, playItem, referenceItem):
		self.referenceItem = referenceItem
		self.time = 0.0
		#self.PlayWithActionMenu(playItem)
		self.playMediaController.ShowWithItem(playItem)

	# this method called when user clikc on play media button in play media dailog
	def OnPlayItemFromMediaDialog(self):
		playItem = self.playMediaController.playItem
		if self.referenceItem.GetProperty("timeToResume"):
			timeToResumeInSeconds = float(self.referenceItem.GetProperty("timeToResume"))
			if 0 != timeToResumeInSeconds:
				self.exVideoResumeDialog.OnShowVideoResumeDialog(playItem, self.referenceItem, False)
				return
		self.Play(playItem)
		self.runEventLoop()

	def PlayEpisode(self, index):
		self.time = 0.0
		previousIndex = self.GetLastViewedEpisodeIndexInPlaylist()
		if self.referenceItem:
			self.referenceItem.SetProperty("lastViewedEpisodeIndex", str(index))
			# if user selected another item in list then reset resume time
			if previousIndex != index: self.referenceItem.SetProperty("timeToResume", str(0))

		if self.referenceItem.GetProperty("timeToResume"):
			timeToResumeInSeconds = float(self.referenceItem.GetProperty("timeToResume"))
			if 0 != timeToResumeInSeconds:
				self.exVideoResumeDialog.OnShowVideoResumeDialog(None, self.referenceItem, True)
				return
		# unlock all actions in player for playlist including move to next and back episodes
		self.LockPlayerAction(self.XAPP_PLAYER_ACTION_NONE)
		self.PlaySelected(index, mc.PlayList.PLAYLIST_VIDEO)
		self.runEventLoop()

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

	# This method is called when user select action on 'resume from' dialog
	def OnVideoResumeSelected(self):
		selectedIndex = self.exVideoResumeDialog.GetList().GetFocusedItem()
		if 0 == selectedIndex:
			if self.referenceItem.GetProperty("timeToResume"):
				timeToResumeInSeconds = float(self.referenceItem.GetProperty("timeToResume"))
				if 0 != timeToResumeInSeconds:
					t = threading.Thread(target=self.seekTo, args=(timeToResumeInSeconds,))
					t.start()
		if self.exVideoResumeDialog.isPlaylistActive:
			mc.LogInfo("Start player with playlist item")
			self.LockPlayerAction(self.XAPP_PLAYER_ACTION_NONE)			
			self.PlaySelected(self.GetLastViewedEpisodeIndexInPlaylist(), mc.PlayList.PLAYLIST_VIDEO)
		else:
			mc.LogInfo("Start player with item: %s" % self.exVideoResumeDialog.playItem.GetLabel())
			self.Play(self.exVideoResumeDialog.playItem)
		self.runEventLoop()

def GetPlayer():
	global exSharedPlayer
	if (exSharedPlayer is None):
		exSharedPlayer = exPlayer()
	return exSharedPlayer

