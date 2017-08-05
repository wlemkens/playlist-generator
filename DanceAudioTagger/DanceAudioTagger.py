#!/usr/bin/python3

# sudo pip install pydub
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
		print (genreDict)
	
	def getGenres(self,genreList):
		genreDict = {}
		for genreName in genreList:
			genre = genreName.split(".")[:-1].join("")
			genreDict[genre] = genreName
		return genreDict
			