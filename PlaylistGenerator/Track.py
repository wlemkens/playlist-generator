#!/usr/bin/python3


class Track(object):
	def __init__(self,url,genre,length,fileType,title,band):
		self.url = url
		self.genre = genre
		self.length = length
		self.fileType = fileType
		self.title = title
		self.band = band
		
	def __str__(self):
		return "[url: "+self.url+", genre: "+self.genre+", length: "+str(self.length)+" s]"
	
	def __unicode__(self):
		return u(self.__str__())
	
	def __repr__(self):
		return self.__str__()
