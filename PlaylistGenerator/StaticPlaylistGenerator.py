#!/usr/bin/python3

# custom imports
from PlaylistGenerator.PlaylistGenerator import PlaylistGenerator

class StaticPlaylistGenerator(PlaylistGenerator):
	def __init__(self,musicPath,playlistMetrics,outputFile, duration):
		super().__init__(musicPath,playlistMetrics)
		self.outputFile = outputFile
		self.duration = duration
