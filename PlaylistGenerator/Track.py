#!/usr/bin/python3

import numpy as np

class Track(object):
	def __init__(self,url,genre,length,fileType,title,band):
		self.url = url
		self.genre = genre
		self.length = length
		self.fileType = fileType
		self.title = title
		self.band = band
		if not self.title:
			self.title = ""
		if not self.band:
			self.band = ""
		
	def duration(self):
		minutes = int(np.floor(self.length/60))
		seconds = np.round(self.length-minutes*60)
		return str(minutes)+":"+"%02d" % (seconds,)
		
	def __str__(self):
		return "[url: "+self.url+", genre: "+self.genre+", length: "+str(self.length)+" s]"
	
	def __unicode__(self):
		return u(self.__str__())
	
	def __repr__(self):
		return self.__str__()

	def __lt__(self,other):
		return self.title < other.title