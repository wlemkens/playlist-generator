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

class MusicLibrary(object):
	def __init__(self,musicPath):
		self.musicPath = musicPath.rstrip('/')
		self.lookupTable = {}
		self.generateLookupTable()
		
	def generateLookupTable(self):
		fileList = DirectoryTools.getFilesFromDirectory(self.musicPath)
		for f in fileList:
			danceType = DirectoryTools.getGenre(f)
			length = self.getAudioLength(f)
			fileType = DirectoryTools.getFileType(f)
			title = self.getTitle(f)
			band = self.getBand(f)
			if danceType and length>0:
				track = Track(f,danceType,length,fileType,title,band)
				if danceType in self.lookupTable:
					self.lookupTable[danceType]+=[track]
				else:
					self.lookupTable[danceType]=[track]

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
		return os.path.splitext(os.path.basename(filename))[0]
		
	def getBand(self,filename):
		try:
			id3info = taglib.File(filename)
			band = id3info.tags["ARTIST"]
			if len(band)>0:
				bandName = band[0]
				return bandName
			else:
				print("Not found band for file '"+filename+"'")
		except (OSError):
			print("Error loading file '"+filename+"'")
		except (KeyError):
			print("Not found any band tag for '"+filename+"'")
		return None