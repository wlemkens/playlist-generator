#!/usr/bin/python3

import os

# custom imports
from PlaylistGenerator.PlaylistGenerator import PlaylistGenerator

class StaticPlaylistGenerator(PlaylistGenerator):
	def __init__(self,musicPath,playlistMetrics,outputFile, duration, refreshDB = False):
		super().__init__(musicPath,playlistMetrics, refreshDB)
		self.outputFile = outputFile
		self.duration = float(duration*60)
		self.playlist = []
		self.extinf = {'mp3':"#EXTINF:",'flac':"#EXTINF:"}

	def generatePlaylist(self):
		print ("Generating playlist of "+str(self.duration/60)+" minutes")
		totalDuration = 0.0
		lastGenre = None
		while (totalDuration<self.duration):
			song = self.generateUniqueSong()
			if song:
				self.playlist += [song]
				totalDuration += song.length
			else:
				print("Found no song")
		self.savePlaylist()

	def savePlaylist(self):
		header = "#EXTM3U\n"
		with open(self.outputFile,'w') as f:
			f.write(header)
			for song in self.playlist:
				extinf = self.extinf[song.fileType]
				extline = extinf+str(int(song.length))+","+song.title+"\n"
				path = os.path.commonpath([song.url,self.outputFile])
				relpath = os.path.relpath(song.url,os.path.dirname(self.outputFile))
				url = song.url[len(path)+1:]
				fileline = relpath+"\n"
				f.write(extline)
				f.write(fileline)