#!/usr/bin/python3

# Dependencies
# python3-taglib : sudo apt install python3-taglib

# system imports
import os
from mutagen.id3._util import ID3NoHeaderError
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import taglib

# custom imports

class PlaylistGenerator:
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
			if danceType:
				if danceType in self.lookupTable:
					self.lookupTable[danceType]+=[f]
				else:
					self.lookupTable[danceType]=[f]
		#print (self.lookupTable)
		
	def getMP3Type(self, filename):
		try:
			id3info = EasyID3(filename)
			#print (id3info)
			genre = id3info["genre"]
			if len(genre)>0:
				return genre[0]
		except (FileNotFoundError):
			print("Error loading file '"+filename+"'")
		except (KeyError):
			print("Not found any genre tag for '"+filename+"'")
		except (ID3NoHeaderError):
			print("No ID3 tag present for file '"+filename+"'")
		return None
		
	def getFlacType(self,filename):
		try:
			id3info = taglib.File(filename)
			#print ("-->'"+str(id3info.tags)+"'")
			genre = id3info.tags["GENRE"]
			if len(genre)>0:
				#print("Found genre for file '"+filename+"'")
				return genre[0]
			else:
				print("Not found genre for file '"+filename+"'")
		except (OSError):
			print("Error loading file '"+filename+"'")
		except (KeyError):
			print("Not found any genre tag for '"+filename+"'")
		return None
		
	def getType(self, filename):
		#if filename.split(".")[-1]=="mp3":
			#return self.getMP3Type(filename)
		#else:
			return self.getFlacType(filename)
		
		
	def getFilesFromDirectory(self, directory):
		#print ("In dir "+directory)
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
	
	#def getFilesFromDirectory(self, directory):
		#print ("In dir "+directory)
		#fileList = []
		#for root,dirs,files in os.walk(directory):
			#for d in dirs:
				#print ("Processing dir "+d)
				#if (directory==""):
					#newdir = d
				#else:
					#newdir = directory+"/"+d
				#subFiles = self.getFilesFromDirectory(newdir)
				#fileList += subFiles
			#print ("Done dirs")
			#for f in files:
				#filenameParts = f.split(".")
				#if (filenameParts[-1] in self.extensions):
					#print ("Processing "+directory+"/"+f)
					#fileList += [directory+"/"+f]
		#return fileList
		
	