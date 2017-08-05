#!/usr/bin/python3

import os

# sudo pip3 install pydub
from pydub import AudioSegment
from Tools import DirectoryTools

class DanceAudioTagger(object):
	def __init__(self,musicPath,genrePath,outputPath):
		self.musicPath = musicPath
		self.genrePath = genrePath
		self.outputPath = outputPath
	
	def tagMusic(self):
		fileList = DirectoryTools.getFilesFromDirectory(self.musicPath)
		genreList = DirectoryTools.getFilesFromDirectory(self.genrePath)
		genreDict = self.getGenres(genreList)
		for song in fileList:
			createTaggedSong(song)
	
	def getGenres(self,genreList):
		genreDict = {}
		for genreName in genreList:
			genre = os.path.splitext(os.path.basename(genreName))[0]
			genreDict[genre] = genreName
		return genreDict
			
	def createTaggedSong(self,song):
		pass