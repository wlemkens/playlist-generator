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
from PlaylistGenerator.PlaylistMetrics import PlaylistMetrics
from Tools import DirectoryTools
import random

# custom imports

class PlaylistGenerator(object):
	def __init__(self,musicPath,playlistMetricsFile):
		self.musicPath = musicPath.rstrip('/')
		self.playlistMetrics = PlaylistMetrics()
		self.lookupTable = {}
		self.generateLookupTable()
		self.fullLookupTable = self.lookupTable.copy()
		self.playlistMetrics.load(playlistMetricsFile)
		self.lastGenre = None
		self.songList = []
		
	def generateLookupTable(self):
		fileList = DirectoryTools.getFilesFromDirectory(self.musicPath)
		for f in fileList:
			danceType = DirectoryTools.getGenre(f)
			length = self.getAudioLength(f)
			fileType = DirectoryTools.getFileType(f)
			title = self.getTitle(f)
			if danceType and length>0:
				track = Track(f,danceType,length,fileType,title)
				if danceType in self.lookupTable:
					self.lookupTable[danceType]+=[track]
				else:
					self.lookupTable[danceType]=[track]
		#print (self.lookupTable)

	def getAudioLength(self,filename):
		if filename.split(".")[-1]=="mp3":
			audio = MP3(filename)
			return audio.info.length
		else:
			audio = FLAC(filename)
			return audio.info.length
		return 0
		
	def getTitle(self,filename):
		try:
			id3info = taglib.File(filename)
			title = id3info.tags["TITLE"]
			if len(title)>0:
				titleName = title[0]
				return titleName
			else:
				print("Not found title for file '"+filename+"'")
		except (OSError):
			print("Error loading file '"+filename+"'")
		except (KeyError):
			print("Not found any title tag for '"+filename+"'")
		return None
		

	def generateSong(self):
		value = random.random()
		for item in self.playlistMetrics.cumulativeList:
			if item[0]>value:
				genre = item[1]
				if genre in self.lookupTable:
					nbOfSongs = len(self.lookupTable[genre])
					index = random.randint(0,nbOfSongs-1)
					song = self.lookupTable[genre][index]
					self.lookupTable[genre] = self.lookupTable[genre][:index]+self.lookupTable[genre][index+1:]
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