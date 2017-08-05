#!/usr/bin/python3

import os

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
			print ("Loading file '"+songfile+"'")
			filename = songfile[len(self.musicPath):]
			if DirectoryTools.getFileType(songfile)=="mp3":
				song = AudioSegment.from_mp3(songfile)
			else:
				song = AudioSegment.from_flac(songfile)
			print ("Fetching genre")
			genreType = DirectoryTools.getGenre(songfile)
			print ("Getting genre file")
			genrefile = genreDict[genreType]
			print ("Loading genre '"+genrefile+"'")
			genre = AudioSegment.from_mp3(genrefile)
			print ("Generating tagged file")
			pause = AudioSegment.silent(duration=10000)
			taggedSong = genre+pause+genre+song
			outfile = self.outputPath+filename
			outPath = os.path.dirname(outfile)
			if not os.path.exists(outPath):
				os.makedirs(outPath)
			print ("Exporting to '"+outfile+"'")
			taggedSong.export(outfile,format="mp3")
		except:
			print ("Failed to prepend "+self.outputPath+filename)
