#!/usr/bin/python3

# Dependencies
# python3-taglib : sudo apt install python3-taglib
# sudo apt install python3-mutagen

# system imports
import os
import random

# external imports
from mutagen.id3._util import ID3NoHeaderError
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
import taglib

# custom imports

from PlaylistGenerator.Track import Track
from PlaylistGenerator.MusicLibrary import MusicLibrary
from PlaylistGenerator.PlaylistMetrics import PlaylistMetrics
from Tools import DirectoryTools

class PlaylistGenerator(object):
	def __init__(self,musicPath,playlistMetricsFile, refreshDB = False):
		self.library = MusicLibrary(musicPath)
		self.library.generateLookupTable()
		if refreshDB:
			self.library.updateLookupTable()
		self.playlistMetrics = PlaylistMetrics()
		self.fullLookupTable = self.library.lookupTable.copy()
		self.playlistMetrics.load(playlistMetricsFile)
		self.lastGenre = None
		self.songList = []
		self.danceSet = set()



	def setMusicPath(self,musicPath):
		if musicPath:
			self.library = MusicLibrary(musicPath)
		else:
			self.library = None
	
	def setMetrics(self,playlistMetricsFile):
		self.playlistMetrics.load(playlistMetricsFile)
		
	
	def generateSong(self):
		"""
		Pick a random song, based on the configured metrics
		"""

		# pick a random value between 0 and 1
		value = random.random()
		for item in self.playlistMetrics.cumulativeList:
			# If the sum of all earlier checked genres is larger then the random value, 
			# pick the last checked genre. (i.o.w. pick according to the chance distribution
			if item[0]>value:
				genre = item[1]
				if genre in self.library.lookupTable:
					nbOfSongs = len(self.library.lookupTable[genre])
					# Check if we still have more than one song left of this genre
					if nbOfSongs>0:
						if nbOfSongs>1:
							# pick a random song of this genre
							index = random.randint(0,nbOfSongs-1)
						else:
							# pick the last song of this genre
							index = 0
						try:
							song = self.library.lookupTable[genre][index]
						except (Exception):
							print ("Error loading song :d for genre ':s'".format(index,genre))
						self.library.lookupTable[genre] = self.library.lookupTable[genre][:index]+self.library.lookupTable[genre][index+1:]
					else:
						if not genre in self.danceSet:
							print("Didn't find any song for dance '{:}'".format(genre))
						else:
							print("Didn't find enough songs for dance '{:}'".format(genre))
						song = None

					# remove the song from the list so we don't pick it again
					if song:
						if not genre in self.danceSet:
							print("Found dance {:}".format(genre))
							self.danceSet.add(genre)
					return song
				else:
					print ("WARNING: dance '"+genre+"' not found in set")
					return self.generateSong()
	
	def generateUniqueSong(self):
		"""
		Pick a random song, based on the configured metrics and make sure the genre is 
		not the same two times after eachother
		"""

		# Pick a random song
		song = self.generateSong()
		# If we couldn't get any song, return empty
		if not song:
			return None
		# If the song was of the same genre as last song, get a new one
		while (not song or self.lastGenre==song.genre or song in self.songList):
			song = self.generateSong()
		# Mark a new most recent song
		self.lastGenre = song.genre
		self.songList += [song]
		return song