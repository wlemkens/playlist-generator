#!/usr/bin/python3

# Dependencies
# python3-taglib : sudo apt install python3-taglib
# sudo apt install python3-mutagen

# system imports
import os
from mutagen.id3._util import ID3NoHeaderError
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
import taglib
from PlaylistGenerator.Track import Track
from PlaylistGenerator.MusicLibrary import MusicLibrary
from PlaylistGenerator.PlaylistMetrics import PlaylistMetrics
from Tools import DirectoryTools
import random

# custom imports

class PlaylistGenerator(object):
	def __init__(self,musicPath,playlistMetricsFile):
		self.library = MusicLibrary(musicPath)
		self.playlistMetrics = PlaylistMetrics()
		self.fullLookupTable = self.library.lookupTable.copy()
		self.playlistMetrics.load(playlistMetricsFile)
		self.lastGenre = None
		self.songList = []
		

	def setMusicPath(self,musicPath):
		self.library = MusicLibrary(musicPath)
	
	def setMetrics(self,playlistMetricsFile):
		self.playlistMetrics.load(playlistMetricsFile)
		
		
	def generateSong(self):
		value = random.random()
		for item in self.playlistMetrics.cumulativeList:
			if item[0]>value:
				genre = item[1]
				if genre in self.library.lookupTable:
					nbOfSongs = len(self.library.lookupTable[genre])
					if nbOfSongs>1:
						index = random.randint(0,nbOfSongs-1)
					else:
						index = 0
					song = self.library.lookupTable[genre][index]
					self.library.lookupTable[genre] = self.library.lookupTable[genre][:index]+self.library.lookupTable[genre][index+1:]
					return song
				else:
					print ("WARNING: dance '"+genre+"' not found in set")
					return self.generateSong()
	
	def generateUniqueSong(self):
		song = self.generateSong()
		while (not song or self.lastGenre==song.genre or song in self.songList):
			song = self.generateSong()
		self.lastGenre = song.genre
		self.songList += [song]
		return song