#!/usr/bin/python3

import os

# custom imports
from PlaylistGenerator.MusicLibrary import MusicLibrary

class DancePlaylistGenerator(object):
	def __init__(self,musicDirectory,outputDirectory):
		self.library = MusicLibrary(musicDirectory)
		self.library.loadLookupTable()
		self.fullLookupTable = self.library.lookupTable.copy()
		self.songList = []
		self.outputDirectory = outputDirectory
		self.playlist = []
		self.extinf = {'mp3':"#EXTINF:221",'flac':"#EXTINF:331"}

	def generatePlaylists(self):
		print ("Generating playlist for {:} dances".format(len(self.library.lookupTable.keys())))
		for dance in self.library.lookupTable.keys():
			print ("Generating playlist for {:}".format(dance))
			playlist = self.library.lookupTable[dance]
			self.savePlaylist(playlist, dance)

	def savePlaylist(self, playlist, dance):
		header = "#EXTM3U\n"
		outputFile = os.path.join(self.outputDirectory, dance+".m3u")
		with open(outputFile,'w') as f:
			print("Writing to {:}".format(outputFile))
			f.write(header)
			for song in playlist:
				extinf = self.extinf[song.fileType]
				extline = extinf+","+song.title+"\n"
				path = os.path.commonpath([song.url,outputFile])
				relpath = os.path.relpath(song.url,self.outputDirectory)
				url = song.url[len(path)+1:]
				fileline = relpath+"\n"
				f.write(extline)
				f.write(fileline)