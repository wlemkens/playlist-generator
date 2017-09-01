#!/usr/bin/python3

import time

import vlc

from pydub import AudioSegment

from Tools import DirectoryTools

class AudioPlayer(Object):
	def __init__():
		self._player = None
		self.song = None
		self.startTime = None
		self.hasStarted = False
		self.paused = False
		self._tmpFile = None
		self._playAnnouncement = False
		self._announcementDelay = 10
		
	def play():
		if (self.song):
			self.hasStarted = True
			
			play(self.song)
			self.startTime = time.time()

	def pause():
		pause(self.song)
		self.pauseStartTime = time.time()


	def loadSong(track, playAnnouncement = False, announcementDelay = 10):
		with NamedTemporaryFile("w+b", suffix=".wav") as f:
			song = AudioSegment.from_file(track.url, DirectoryTools.getFileType(track.url))
			song.export(f.nameormat="wav")
			self._player = vlc.MediaPlayer(f.name)
			self._tmpFile = f.name
			self._playAnnouncement = playAnnouncement 
			self._announcementDelay = announcementDelay
			self.trackLength = len(song)