#!/usr/bin/python3

import time
from tempfile import NamedTemporaryFile

import vlc

from pydub import AudioSegment
from pydub.utils import make_chunks
import os.path

from Tools import DirectoryTools
from Player import AudioEffects

class AudioPlayer(object):
	def __init__(self,playAnnouncement=False,announcementDirectory = ".", announcementDelay = 6.0):
		self._player = None
		self._paused = True
		self._tmpFile = None
		self._playAnnouncement = playAnnouncement
		self._announcementDelay = announcementDelay
		self.announcementDirectory = announcementDirectory
		self.trackLength = 0
		self._fastSpeedChange = True
		
	def play(self):
		if (self._player):
			self._paused = False
			self._player.play()

	def pause(self):
		if (self._player):
			self._paused = True
			self._player.pause()
			
	def togglePause(self):
		if self._paused:
			self.play()
		else:
			self.pause()

	def setAnnouncementDirectory(self,announcementDirectory):
		self.announcementDirectory = announcementDirectory
		
	def setPlayAnnouncements(self,playAnnouncement):
		self.playAnnouncement = playAnnouncement
		
	def setAnnouncementDelay(self,announcementDelay):
		self.announcementDelay = announcementDelay
		
	def processSong(self,sound,announcement,playAnnouncement,announcementDelay,speed=1.0):
		if self._fastSpeedChange:
			song = AudioEffects.fallbackSpeedChange(sound,speed)
		else:
			song = AudioEffects.speedChange(sound,speed)
		if playAnnouncement and announcement:
			pause = AudioSegment.silent(duration=announcementDelay*1000)
			return announcement+pause+announcement+song
		else:
			return song
	
	def loadAndPlay(self,track,speed=1.0):
		self.loadSong(track,speed)
		self.play()
	
	def loadSong(self,track,speed=1.0):
		self.cleanPlayer()
			
		self._tmpFile = NamedTemporaryFile("w+b", suffix=".wav")
		song = AudioSegment.from_file(track.url, DirectoryTools.getFileType(track.url))
		announcement = None
		if self._playAnnouncement:
			announcementFileName = self.announcementDirectory+"/"+track.genre+".mp3"
			if os.path.isfile(announcementFileName) :
				announcement = AudioSegment.from_file(announcementFileName, "mp3")
		audio = self.processSong(song,announcement,self._playAnnouncement,self._announcementDelay,speed)
		audio.export(self._tmpFile.name,format="wav")
		self._player = vlc.MediaPlayer(self._tmpFile.name)
		pevent = self._player.event_manager()
		pevent.event_attach(vlc.EventType().MediaPlayerEndReached, self.songEndReachedCallback)
		self.trackLength = len(audio)

	# To be overwritten by parent
	def endReachedCallback(self):
		pass
	
	def setFastSpeedChange(self,value):
		self._fastSpeedChange = value
		
	def songEndReachedCallback(self,ev):
		self.cleanPlayer()
		self.endReachedCallback()
	
	def cleanPlayer(self):
		if self._player:
			if self._player.get_state() == vlc.State.Playing:
				self._player.stop()
			self._player = None
			self._tmpFile.close()
			self._tmpFile = None
		self._paused = True

	def getTime(self):
		if self._player:
			return self._player.get_time()/1000.0
		else:
			return 0
		
	def isPaused(self):
		return self._paused
	
	def setTime(self,playTime):
		if self._player:
			self._player.set_time(int(playTime*1000))
	
