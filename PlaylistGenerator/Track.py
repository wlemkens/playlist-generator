#!/usr/bin/python3


class Track(object):
	def __init__(self,url,length):
		self.url = url
		self.length = length
		
	def __str__(self):
		return "[url: "+self.url+", length: "+str(self.length)+" s]"
	
	def __unicode__(self):
		return u(self.__str__())
	
	def __repr__(self):
		return self.__str__()
