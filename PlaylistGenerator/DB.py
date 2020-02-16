#!/usr/bin/python3

import os.path

from PlaylistGenerator.Track import Track

class DB(object):
	def __init__(self,url,musicPath):
		self._url = url
		self._musicPath = musicPath
		self.data = {}
		self.data[musicPath] = {}
		self.load()

	def load(self):
		if os.path.isfile(self._url):
			with open(self._url,'r', encoding='utf-8') as f:
				rightDb = False
				musicPath = ""
				for line in f:
					params = line.split(";")
					if (len(params)==7):
						item = Track(params[0],params[1],float(params[2]),params[3],params[4],params[5],float(params[6]))
						self.data[musicPath][item.url] = item
					elif (len(params)==1):
						musicPath = params[0].rstrip("\n")
						print ("Found '"+musicPath+"'")
						self.data[musicPath] = {}

	def save(self):
		with open(self._url,'w', encoding='utf-8') as f:
			for musicPath,db in self.data.items():
				f.write(musicPath+"\n")
				for key,item in db.items():
					line = self.sanitise(item.url)+";"+self.sanitise(item.genre)+";"+str(item.length)+";"+item.fileType+";"+self.sanitise(item.title)+";"+self.sanitise(item.band)+";"+str(item.bpm)+"\n"
					f.write(line)
			
	
	def addTrack(self,track):
		db = self.data[self._musicPath]
		db[track.url] = track
		
	def removeTrack(self,track):
		del self.data[self._musicPath][track.url]
		
	def contains(self,track):
		return track.url in self.data[self._musicPath]
	
	def sanitise(self,string):
		return string.replace(";",",")