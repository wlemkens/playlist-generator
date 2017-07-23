#!/usr/bin/python3

# custom imports
from PlaylistGenerator.PlaylistGenerator import PlaylistGenerator

class StaticPlaylistGenerator(PlaylistGenerator):
	def __init__(self,musicPath,playlistMetrics,outputFile, duration):
		super().__init__(musicPath,playlistMetrics)
		self.outputFile = outputFile
		self.duration = float(duration*60)
		self.playlist = []

	def generatePlaylist(self):
		print ("Generating playlist of "+str(self.duration/60)+" minutes")
		totalDuration = 0.0
		lastGenre = None
		while (totalDuration<self.duration):
			song = self.generateSong()
			if (lastGenre!=song.genre):
				lastGenre = song.genre
				self.playlist += [song]
				totalDuration += song.length
		print (self.playlist)
