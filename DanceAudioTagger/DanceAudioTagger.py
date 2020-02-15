#!/usr/bin/python3

import os
import sys
import taglib

# sudo pip3 install pydub
from pydub import AudioSegment
from Tools import DirectoryTools

class DanceAudioTagger(object):
	def __init__(self,musicPath,genrePath,outputPath):
		self.musicPath = musicPath.rstrip("/")
		self.genrePath = genrePath.rstrip("/")
		self.outputPath = outputPath.rstrip("/")
	
	def tagMusic(self):
		fileList = DirectoryTools.getFilesFromDirectory(self.musicPath)
		genreList = DirectoryTools.getFilesFromDirectory(self.genrePath)
		genreDict = self.getGenres(genreList)
		for song in fileList:
			self.createTaggedSong(song,genreDict)
	
	def getGenres(self,genreList):
		genreDict = {}
		for genreName in genreList:
			genre = os.path.splitext(os.path.basename(genreName))[0]
			genreDict[genre] = genreName
		return genreDict
			
	def createTaggedSong(self,songfile,genreDict):
		try:
			filename = os.path.splitext(songfile[len(self.musicPath):])[0]
			song = AudioSegment.from_file(songfile, DirectoryTools.getFileType(songfile))
			genreType = DirectoryTools.getGenre(songfile)
			if genreType and genreType in genreDict:
				genrefile = genreDict[genreType]
				genre = AudioSegment.from_mp3(genrefile)
				pause = AudioSegment.silent(duration=10000)
				taggedSong = genre+pause+genre+song+pause
				outfile = self.outputPath+filename+".mp3"
				outPath = os.path.dirname(outfile)
				if not os.path.exists(outPath):
					os.makedirs(outPath)
				taggedSong.export(outfile,format="mp3")
				self.copyTags(songfile,outfile)
			else:
				# Just to reduce the number of useless warnings
				if not genreType in ["folk","world","balfolk","celtic","folklore","national folk"]:
					print ("No tag for dance '"+genreType+"' found for file '"+songfile+"'")
		except:
			print ("Failed to prepend "+self.outputPath+filename+" : "+str(sys.exc_info()[0]))

	def copyTags(self,original, target):
		#print ("Moving tags from "+original+" to "+target)
		oldSong = taglib.File(original)
		#print (oldSong.tags)
		newSong = taglib.File(target)
		newSong.tags = oldSong.tags
		newSong.save()
