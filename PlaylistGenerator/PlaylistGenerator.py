#!/usr/bin/python3

# Dependencies
# python3-taglib : sudo apt install python3-taglib

# system imports
import os
from mutagen.id3._util import ID3NoHeaderError
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
import taglib
from PlaylistGenerator.Track import Track
from PlaylistGenerator.PlaylistMetrics import PlaylistMetrics
import random

# custom imports

class PlaylistGenerator(object):
	def __init__(self,musicPath,playlistMetricsFile):
		self.extensions = ["mp3","flac"]
		self.musicPath = musicPath.rstrip('/')
		self.playlistMetrics = PlaylistMetrics()
		self.lookupTable = {}
		self.generateLookupTable()
		self.playlistMetrics.load(playlistMetricsFile)
		
	def generateLookupTable(self):
		fileList = self.getFilesFromDirectory(self.musicPath)
		for f in fileList:
			danceType = self.getType(f)
			length = self.getAudioLength(f)
			fileType = self.getFileType(f)
			title = self.getTitle(f)
			if danceType and length>0:
				track = Track(f,danceType,length,fileType,title)
				if danceType in self.lookupTable:
					self.lookupTable[danceType]+=[track]
				else:
					self.lookupTable[danceType]=[track]
		#print (self.lookupTable)

	def getFileType(self,filename):
		return filename.split(".")[-1]

	def getAudioLength(self,filename):
		if filename.split(".")[-1]=="mp3":
			audio = MP3(filename)
			return audio.info.length
		else:
			audio = FLAC(filename)
			return audio.info.length
		return 0
		
	def getType(self,filename):
		try:
			id3info = taglib.File(filename)
			genre = id3info.tags["GENRE"]
			if len(genre)>0:
				genreName = genre[0].lower()
				if genreName[:5] == "folk ":
					genreName = genreName[5:]
				return genreName
			#else:
				#print("Not found genre for file '"+filename+"'")
		except (OSError):
			print("Error loading file '"+filename+"'")
		except (KeyError):
			print("Not found any genre tag for '"+filename+"'")
		return None
		
	def getTitle(self,filename):
		try:
			id3info = taglib.File(filename)
			genre = id3info.tags["TITLE"]
			if len(genre)>0:
				genreName = genre[0].lower()
				if genreName[:5] == "folk ":
					genreName = genreName[5:]
				return genreName
			else:
				print("Not found title for file '"+filename+"'")
		except (OSError):
			print("Error loading file '"+filename+"'")
		except (KeyError):
			print("Not found any title tag for '"+filename+"'")
		return None
		
	def getFilesFromDirectory(self, directory):
		fileList = []
		for filename in os.listdir(directory):
			if os.path.isfile(directory+"/"+filename):
				filenameParts = filename.split(".")
				if (filenameParts[-1] in self.extensions):
					#print ("Processing "+directory+"/"+filename)
					fileList += [directory+"/"+filename]
			else:
				fileList += self.getFilesFromDirectory(directory+"/"+filename)
		return fileList
	
	def generateSong(self):
		value = random.random()
		for item in self.playlistMetrics.cumulativeList:
			if item[0]>value:
				genre = item[1]
				if genre in self.lookupTable:
					nbOfSongs = len(self.lookupTable[genre])
					index = random.randint(0,nbOfSongs-1)
					return self.lookupTable[genre][index]
				else:
					print ("WARNING: dance '"+genre+"' not found in set")
					return self.generateSong()