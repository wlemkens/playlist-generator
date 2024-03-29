#!/usr/bin/python3

# Dependencies
# python3-taglib : sudo apt install python3-taglib
# sudo apt install python3-mutagen

# system imports
import os
from mutagen.id3._util import ID3NoHeaderError
from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen.flac import FLAC, FLACNoHeaderError
from mutagen.easyid3 import EasyID3
import taglib
from PlaylistGenerator.Track import Track
from PlaylistGenerator.PlaylistMetrics import PlaylistMetrics
from PlaylistGenerator.DB import DB
from PlaylistGenerator.MetaInfoDB import MetaInfoDB
from Tools import DirectoryTools
import random

import threading

from aubio import source, tempo
from numpy import median, diff
from tempfile import NamedTemporaryFile
from pydub import AudioSegment


# custom imports

class MusicLibrary(object):
	
	def __init__(self,musicPath):
		"""
		The constructor of the library
		Sets the music path
		"""
		
		# Load the database
		self.musicPath = musicPath.rstrip('/')
		self._db = DB("music.db",self.musicPath)
		self.metadb = MetaInfoDB("meta.db")
		# Initialise global variables
		self.running  = True
		self.lookupTable = {}
		self.nbOfSongs = 0
		# The tags we don't want in our list
		self.blackList = ["balfolk","buikdans?","celtic","other","folk","folklore","trad."]
		
	def loadMusic(self):
		"""
		Start loading the music
		"""
		
		t = threading.Thread(target=self.loadLookupTable)
		t.start()
		
	def loadLookupTable(self):
		"""
		Load the lookup table from the database
		"""
		
		self.generateLookupTable()
		self.onLibraryLoaded(self.nbOfSongs,len(self.lookupTable))
		t = threading.Thread(target=self.updateLookupTable)
		t.start()
			
	def generateLookupTable(self):
		"""
		Create the lookup table based on the database
		"""
		
		print("Loading lookup table")
		if self.musicPath in self._db.data.keys():
			for path,track in self._db.data[self.musicPath].items():
				if track.genre in self.lookupTable:
					self.lookupTable[track.genre]+=[track]
				else:
					self.lookupTable[track.genre]=[track]
				self.nbOfSongs+=1
				self.onSongFound(self.nbOfSongs,len(self.lookupTable))
				
				
	def updateLookupTable(self):
		"""
		Update the lookup table according to the file system
		"""
		
		print("Updating lookup table")
		fileList = DirectoryTools.getFilesFromDirectory(self.musicPath)
		for f in fileList:
			if not self.running:
				break
			danceType = DirectoryTools.getGenre(f)
			length = self.getAudioLength(f)
			if length > 0:
				fileType = DirectoryTools.getFileType(f)
				title = self.getTitle(f)
				band = self.getBand(f)
				if danceType and length>0:
					if not danceType in self.blackList:
						track = Track(f,danceType,length,fileType,title,band)
						if not self._db.contains(track):
							bpm = self.getFileBpm(f)
							bpm = self.filterGenreBpm(danceType, bpm, title)
							track.bpm = bpm
							self._db.addTrack(track)
							if danceType in self.lookupTable:
								self.lookupTable[danceType]+=[track]
							else:
								self.lookupTable[danceType]=[track]
							self.nbOfSongs+=1
							self.onSongFound(self.nbOfSongs,len(self.lookupTable))
							self._db.save()

	def getAudioLength(self,filename):
		if filename.split(".")[-1]=="mp3":
			try:
				audio = MP3(filename)
				return audio.info.length
			except HeaderNotFoundError:
				print(f"No mp3 header {filename}")
		else:
			try:
				audio = FLAC(filename)
				return audio.info.length
			except FLACNoHeaderError:
				print(f"Invalid FLAC file {filename}")
		return 0
		
	def getTitle(self,filename):
		try:
			id3info = taglib.File(filename)
			title = id3info.tags["TITLE"]
			if len(title)>0:
				titleName = title[0]
				return titleName
			else:
				print("Not found title for file '"+filename+"'")
		except (OSError):
			print("Error loading file '"+filename+"'")
		except (KeyError):
			print("Not found any title tag for '"+filename+"'")
		return os.path.splitext(os.path.basename(filename))[0]
		
	def getBand(self,filename):
		try:
			id3info = taglib.File(filename)
			band = id3info.tags["ARTIST"]
			if len(band)>0:
				bandName = band[0]
				return bandName
			else:
				print("Not found band for file '"+filename+"'")
		except (OSError):
			print("Error loading file '"+filename+"'")
		except (KeyError):
			print("Not found any band tag for '"+filename+"'")
		return None
	
	def onLibraryLoaded(self,nbOfSongs,nbOfGenres):
		pass
	
	def onSongFound(self,nbOfSongs,nbOfGenres):
		pass
	
	def filterGenreBpm(self, genre, bpm, song):
		"""
		Often it is hard to detect the correct bpm, but the detected bpm should be a multiple
		of the real bpm
		"""
		if genre in self.metadb.data and bpm > 0:
			bestBpm = bpm
			while bestBpm < self.metadb.data[genre][0]:
				bestBpm *= self.metadb.data[genre][2]
			while bestBpm > self.metadb.data[genre][1]:
				bestBpm /= self.metadb.data[genre][2]
			if self.metadb.data[genre][2] != 2:
				n = 2
				while bestBpm < self.metadb.data[genre][0]:
					bestBpm = bpm * n / self.metadb.data[genre][2]
					n += 1
				n = 2
				while bestBpm > self.metadb.data[genre][1]:
					bestBpm = bpm / n
					n *= 2
				
			if bestBpm < self.metadb.data[genre][0] or bestBpm > self.metadb.data[genre][1]:
				print("Warning: Could not fit bpm ({:}) within boundaries [{:}, {:}] for {:} of genre {:}".format(bpm, self.metadb.data[genre][0], self.metadb.data[genre][1], song, genre))
				bestBpm = bpm
				
		return bpm
				
	
	def getFileBpm(self,path, params = None):
		try:
			id3info = taglib.File(path)
			bpm = None
			if "BPM" in id3info.tags:
				bpm = int(id3info.tags["BPM"][0])
				return bpm
			with NamedTemporaryFile("w+b", suffix=".wav") as tmpFile:
				song = AudioSegment.from_file(path, DirectoryTools.getFileType(path))
				song.export(tmpFile.name,format="wav")

			#""" Calculate the beats per minute (bpm) of a given file.
					#path: path to the file
					#param: dictionary of parameters
			#"""
				if params is None:
						params = {}
				try:
						win_s = params['win_s']
						samplerate = params['samplerate']
						hop_s = params['hop_s']
				except KeyError:
						"""
						# super fast
						samplerate, win_s, hop_s = 4000, 128, 64 
						# fast
						samplerate, win_s, hop_s = 8000, 512, 128
						"""
						# default:
						samplerate, win_s, hop_s = 44100, 1024, 512

				s = source(tmpFile.name, samplerate, hop_s)
				samplerate = s.samplerate
				o = tempo("specdiff", win_s, hop_s, samplerate)
				# List of beats, in samples
				beats = []
				# Total number of frames read
				total_frames = 0

				while True:
						samples, read = s()
						is_beat = o(samples)
						if is_beat:
								this_beat = o.get_last_s()
								beats.append(this_beat)
								#if o.get_confidence() > .2 and len(beats) > 2.:
								#    break
						total_frames += read
						if read < hop_s:
								break

				# Convert to periods and to bpm 
				if len(beats) > 1:
						if len(beats) < 4:
								print("few beats found in {:s}".format(path))
						bpms = 60./diff(beats)
						b = median(bpms)
				else:
						b = 0
						print("not enough beats found in {:s}".format(path))
				return b
		except Exception:
			return 0
		
	def close(self):
		self.running = False