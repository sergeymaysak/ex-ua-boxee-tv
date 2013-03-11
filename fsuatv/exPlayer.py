# -*- coding: utf-8 -*-
'''
	exPlayer.py
	Player is responsible to play media - extends mc.Player with functinality
	absent in it - resume of item from stopped time and "play playlist with
	options dialog". Based on idea of MyPlayer from bartsidee.
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
__date__ ="$Sep 18, 2011 10:05:38 PM$"

import string
import os
import sys
import re
import xbmc
import mc
import exPlaylistController
import time
import threading
import exVideoResumeDialog
import exPlayMediaDialogController
import pickle

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
		# inspect playlists every time we create player (i.e. during each app start)
		self.InspectAndCleanUpPlaylistsDir()

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
		self.PlaySingleItemAsFile(playItem)
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
		self.PlaySelectedIndexInPlaylistAsFile(index)
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
			#self.PlaySelected(self.GetLastViewedEpisodeIndexInPlaylist(), mc.PlayList.PLAYLIST_VIDEO)
			self.PlaySelectedIndexInPlaylistAsFile(self.GetLastViewedEpisodeIndexInPlaylist())
		else:
			mc.LogInfo("Start player with item: %s" % self.exVideoResumeDialog.playItem.GetLabel())
			#self.Play(self.exVideoResumeDialog.playItem)
			self.PlaySingleItemAsFile(self.exVideoResumeDialog.playItem)
		self.runEventLoop()

	def SavePlaylistItemsAsFiles(self):
		videoPlaylist = mc.PlayList(mc.PlayList.PLAYLIST_VIDEO)
		for index in range(videoPlaylist.Size()):
			singleItem = videoPlaylist.GetItem(index)
			filePath = self.GeneratePlayFileForItem(singleItem, True)
			if None != filePath:
				singleItem.SetPath(filePath)

	def PlaySelectedIndexInPlaylistAsFile(self, index):
		self.SavePlaylistItemsAsFiles()
		# unlock all actions in player for playlist including move to next and back episodes
		self.LockPlayerAction(self.XAPP_PLAYER_ACTION_NONE)
		self.PlaySelected(index, mc.PlayList.PLAYLIST_VIDEO)

	# play item replacing its path from http url to local file path to .m3u8 playlist -
	# this technique allows to bring back subtitles and language selection is OSD during playback
	def PlaySingleItemAsFile(self, playItem):
		filePath = self.GeneratePlayFileForItem(playItem)
		if None != filePath:
			playItem.SetPath(filePath)
		self.Play(playItem)
	
	def GetPlaylistFileNameForItem(self, playItem):
		lastPathComponent = None
		pathComponents = os.path.split(playItem.GetPath())
		if pathComponents != None: lastPathComponent = pathComponents[1]
		valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
		filename = ''.join(c for c in lastPathComponent if c in valid_chars)
		filename = filename.lstrip().replace(' ', '').lstrip('.')
		if 0 == len(filename): filename = "playlist"
		return filename + '.m3u8'

	def GetPlaylistsMediaDir(self):
		mediaDir = xbmc.translatePath(mc.GetApp().GetAppMediaDir())
		mediaDir = os.path.join(mediaDir, "playlists")
 		if False == os.path.exists(mediaDir):
			os.mkdir(mediaDir)
		return mediaDir

	def GetEpisodesMediaDir(self):
		mediaDir = xbmc.translatePath(mc.GetApp().GetAppMediaDir())
		mediaDir = os.path.join(mediaDir, "episodes")
 		if False == os.path.exists(mediaDir):
			os.mkdir(mediaDir)
		return mediaDir

	# Returns playlists filenames sorted by modification date,
	# the oldest files are at the beginning of the list
	def GetFilenamesSortedByModificationDate(self):
		storedItems = self.GetStoredPlaylistNamesByPlayingTimes()
		filesList = sorted(storedItems.keys(), key = lambda x: storedItems[x])
		mc.LogInfo("sorted list: %s" % str(filesList))
		return filesList

	def InspectAndCleanUpPlaylistsDir(self):
		try:
			mediaDir = self.GetPlaylistsMediaDir()
			savedFilesList = os.listdir(mediaDir)
			# allow grow list to 150 items - then remove oldest 50
			if (len(savedFilesList) - 50) >= 100:
				storedFileNames = self.GetStoredPlaylistNamesByPlayingTimes()
				savedFilesList = self.GetFilenamesSortedByModificationDate()
				mc.LogInfo("Deleting oldest files from list: %s" % str(savedFilesList))
				for i in range(len(savedFilesList) - 50):
					fileName = savedFilesList[i]
					pathToRemove = os.path.join(mediaDir, fileName)
					mc.LogInfo("path to remove: %s" % pathToRemove)
					os.remove(pathToRemove)
					if storedFileNames.has_key(fileName): del storedFileNames[fileName]
				self.StorePlaylistNamesByPlayingTimes(storedFileNames)
			# clean up episodes
			episodesDir = self.GetEpisodesMediaDir()
			episodesSavedList = os.listdir(episodesDir)
			if len(episodesSavedList) >= 5:
				for file in episodesSavedList:
					os.remove(os.path.join(episodesDir, file))
		except:
			pass

	# Constructs m3u8 (extended m3u format) playlist for specified playItem and
	# writes it to special directory inside app (to make sure it is accessible later from system history)
	def GeneratePlayFileForItem(self, playItem, isEpisode = False):
		tmpFileName = None
		try:
			playListContent = '#EXTM3U' + '\n' + '#EXTINF:-1,' + playItem.GetLabel() + '\n'
			playListContent += playItem.GetPath() + '\n' + '#EXT-X-ENDLIST'

			if isEpisode:
				mediaDir = self.GetEpisodesMediaDir()
			else:
				mediaDir = self.GetPlaylistsMediaDir()
			name = self.GetPlaylistFileNameForItem(playItem)
			tmpFileName = os.path.join(mediaDir, name)
			#mc.LogInfo("Playlist file path: %s" % tmpFileName)
			#mc.LogInfo("Opening file: %s" % tmpFileName)
			f = open(tmpFileName, 'w')
			f.write(playListContent)
			f.close()

			if False == isEpisode:
				self.StoreLastPlayedTimeForItemWithPath(name)
		except:
			mc.LogInfo("Failed to open and write .m3u8 file - continue without it")
			tmpFileName = None
		return tmpFileName

	def GetStoredPlaylistNamesByPlayingTimes(self):
		stringRep = mc.GetApp().GetLocalConfig().GetValue("playlistnames-by-times")
		storedItems = dict()
		if len(stringRep) > 0: storedItems = pickle.loads(stringRep)
		if None == storedItems: storedItems = dict()
		return storedItems

	def StorePlaylistNamesByPlayingTimes(self, itemsToStore):
		stringRep = pickle.dumps(itemsToStore)
		if stringRep != None:
			mc.GetApp().GetLocalConfig().SetValue("playlistnames-by-times", stringRep)

	def StoreLastPlayedTimeForItemWithPath(self, fileName):
		storedItems = self.GetStoredPlaylistNamesByPlayingTimes()
		storedItems[fileName] = str(time.time())
		self.StorePlaylistNamesByPlayingTimes(storedItems)

def GetPlayer():
	global exSharedPlayer
	if (exSharedPlayer is None):
		exSharedPlayer = exPlayer()
	return exSharedPlayer

