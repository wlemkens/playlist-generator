#!/usr/bin/python3

import os

# custom imports
from PlaylistGenerator.PlaylistGenerator import PlaylistGenerator

class StaticPlaylistGenerator(PlaylistGenerator):
	def __init__(self,musicPath,playlistMetrics,outputFile, duration, forced_path = None, refreshDB = False):
		super().__init__(musicPath,playlistMetrics, refreshDB)
		self.musicPath = musicPath
		self.outputFile = outputFile
		self.forced_path = forced_path
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
		directory = os.path.dirname(self.outputFile)
		isExist = os.path.exists(directory)
		if not isExist:
			os.makedirs(directory)
		header = "#EXTM3U\n"
		with open(self.outputFile,'w') as f:
			f.write(header)
			for song in self.playlist:
				extinf = self.extinf[song.fileType]
				extline = extinf+str(int(song.length))+","+song.title+"\n"
				path = os.path.relpath(song.url,os.path.dirname(self.outputFile))
				if self.forced_path:
					relpath = os.path.relpath(song.url, self.musicPath)
					path = os.path.join(self.forced_path, relpath)
				fileline = path+"\n"
				f.write(extline)
				f.write(fileline)