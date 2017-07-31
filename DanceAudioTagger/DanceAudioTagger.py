#!/usr/bin/python3

# sudo pip install pydub
from pydub import AudioSegment

class DanceAudioTagger(object):
	def __init__(self,musicPath,genrePath,outputPath):
		self.musicPath = musicPath
		self.genrePath = genrePath
		self.outputPath = outputPath
	
	def tagMusic(self):
		pass