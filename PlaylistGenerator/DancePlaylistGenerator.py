#!/usr/bin/python3

import os

# custom imports
from PlaylistGenerator.MusicLibrary import MusicLibrary

class DancePlaylistGenerator(object):
	"""
	A generator for creating a playlist for each dance
	"""

	def __init__(self, musicDirectory : str, outputDirectory : str, refreshDB : bool = False):
		"""
		Constructor

		Parameters
		----------
		musicDirectory : str
			The root directory to look for the music
		outputDirectory : str
			The directory to output the playlists
		refreshDB : bool, optional
			Refresh the database, defaults to not refreshing
		"""

		self.library = MusicLibrary(musicDirectory)
		self.library.generateLookupTable()
		if refreshDB:
			self.library.updateLookupTable()
		self.fullLookupTable = self.library.lookupTable.copy()
		self.songList = []
		self.outputDirectory = outputDirectory
		self.playlist = []
		self.extinf = {'mp3':"#EXTINF:",'flac':"#EXTINF:"}

	def generatePlaylists(self):
		"""
		Generate the playlist with the configured settings
		"""
		print ("Generating playlist for {:} dances".format(len(self.library.lookupTable.keys())))
		for dance in self.library.lookupTable.keys():
			print ("Generating playlist for {:}".format(dance))
			playlist = self.library.lookupTable[dance]
			self.savePlaylist(playlist, dance)

	def savePlaylist(self, playlist : list, dance : str):
		"""
		Save the playlist for the given dance to the configured output directory

		Parameters
		----------
		playlist : list
			The list of tracks to be included in the playlist
		dance : str
			The dance for which to create a playlist
		"""
		header = "#EXTM3U\n"
		outputFile = os.path.join(self.outputDirectory, dance+".m3u")
		with open(outputFile,'w') as f:
			print("Writing to {:}".format(outputFile))
			f.write(header)
			for song in playlist:
				extinf = self.extinf[song.fileType]
				extline = extinf+str(int(song.length))+","+song.title+"\n"
				path = os.path.commonpath([song.url,outputFile])
				relpath = os.path.relpath(song.url,self.outputDirectory)
				url = song.url[len(path)+1:]
				fileline = relpath+"\n"
				f.write(extline)
				f.write(fileline)