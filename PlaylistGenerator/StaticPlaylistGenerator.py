#!/usr/bin/python3

# custom imports
from PlaylistGenerator.PlaylistGenerator import PlaylistGenerator

class StaticPlaylistGenerator(PlaylistGenerator):
	def __init__(self,musicPath,playlistMetrics,outputFile, duration):
		super().__init__(musicPath,playlistMetrics)
		self.outputFile = outputFile
		self.duration = float(duration*60)
		self.playlist = []
		self.extinf = {'mp3':"#EXTINF:221",'flac':"#EXTINF:331"}

	def generatePlaylist(self):
		print ("Generating playlist of "+str(self.duration/60)+" minutes")
		totalDuration = 0.0
		lastGenre = None
		while (totalDuration<self.duration):
			song = self.generateSong()
			if (song and lastGenre!=song.genre):
				if (not song in self.playlist):
					lastGenre = song.genre
					self.playlist += [song]
					totalDuration += song.length
		self.savePlaylist()

	def savePlaylist(self):
		header = "#EXTM3U\n"
		with open(self.outputFile,'w') as f:
			f.write(header)
			for song in self.playlist:
				extinf = self.extinf[song.fileType]
				extline = extinf+","+song.title+"\n"
				fileline = song.url+"\n"
				f.write(extline)
				f.write(fileline)