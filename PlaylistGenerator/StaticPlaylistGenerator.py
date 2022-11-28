#!/usr/bin/python3

import os

# custom imports
from PlaylistGenerator.PlaylistGenerator import PlaylistGenerator

class StaticPlaylistGenerator(PlaylistGenerator):
	"""
	A tool to generate probability distribution based m3u playlists
	"""
	def __init__(self, musicPath: str, playlistMetrics: str, outputFile: str, duration, forced_path : str = None, refreshDB = False):
		"""
		Constructor

		Parameters
		----------
		musicPath : str
			The root directory the music can be found in
		playlistMetrics : str
			The file containing the playlist metrics
		outputFile : str
			The m3u playlist file to create
		duration : int
			The number of minutes the playlist will at least be.
			The last track will probably bring the playlist just over this limit
		forced_path : str, optional
			Normally the playlist is generated with a relative path.
			In some cases you want to overwrite this with an absolute path
			If empty, the path will be relative
		refreshDB : bool, optional
			Refresh the database. The database is not refreshed by default.
		"""

		super().__init__(musicPath,playlistMetrics, refreshDB)
		self.musicPath = musicPath
		self.outputFile = outputFile
		self.forced_path = forced_path
		self.duration = float(duration*60)
		self.playlist = []
		self.extinf = {'mp3':"#EXTINF:",'flac':"#EXTINF:"}

	def generatePlaylist(self):
		"""
		Generate the playlist with the configured settings
		"""

		print ("Generating playlist of "+str(self.duration/60)+" minutes")
		totalDuration = 0.0
		# The last genre that was selected to avoid two times the same genre after eachother
		lastGenre = None
		while (totalDuration<self.duration):
			# While the requested time is not reach, select new songs
			song = self.generateUniqueSong()
			if song:
				# Make the library is lang enough to pick a song
				self.playlist += [song]
				totalDuration += song.length
			else:
				# Library is empty
				print("Found no song")
		# Save the playlist to file
		self.savePlaylist()

	def savePlaylist(self):
		"""
		Save the playlist to file
		"""

		directory = os.path.dirname(self.outputFile)
		isExist = os.path.exists(directory)
		if not isExist:
			# Make sure the output directory exists. Create it if neccessary
			os.makedirs(directory)
		header = "#EXTM3U\n"
		with open(self.outputFile,'w') as f:
			# Write the m3u header
			f.write(header)
			for song in self.playlist:
				# Get the track meta information
				extinf = self.extinf[song.fileType]
				# Create the meta information line for the m3u playlist
				extline = extinf+str(int(song.length))+","+song.title+"\n"
				# Get the relative path for the track
				path = os.path.relpath(song.url,os.path.dirname(self.outputFile))
				if self.forced_path:
					# If a forced path is configured, replace the relative path with the forced path
					relpath = os.path.relpath(song.url, self.musicPath)
					path = os.path.join(self.forced_path, relpath)
				fileline = path+"\n"
				# Write the track info to the playlist file
				f.write(extline)
				f.write(fileline)