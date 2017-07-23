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

# custom imports

class PlaylistGenerator(object):
	def __init__(self,musicPath,playlistMetrics):
		self.extensions = ["mp3","flac"]
		self.musicPath = musicPath.rstrip('/')
		self.playlistMetrics = playlistMetrics
		self.lookupTable = {}
		self.generateLookupTable()
		
	def generateLookupTable(self):
		fileList = self.getFilesFromDirectory(self.musicPath)
		for f in fileList:
			danceType = self.getType(f)
			length = self.getAudioLength(f)
			if danceType and length>0:
				track = Track(f,length)
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
		
	def getType(self,filename):
		try:
			id3info = taglib.File(filename)
			genre = id3info.tags["GENRE"]
			if len(genre)>0:
				return genre[0].lstrip('Folk ')
			else:
				print("Not found genre for file '"+filename+"'")
		except (OSError):
			print("Error loading file '"+filename+"'")
		except (KeyError):
			print("Not found any genre tag for '"+filename+"'")
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
	