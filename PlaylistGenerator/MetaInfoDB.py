#!/usr/bin/python3

import os.path
import sys

from PlaylistGenerator.Track import Track

class MetaInfoDB(object):
	"""
	Database to hold meta info (genre specific things)
	"""
	
	def __init__(self,url):
		self._url = url
		self.data = {}
		self.load()

	def is_int(self,s):
		try: 
			int(s)
			return True
		except ValueError:
			return False
			

	def load(self):
		if os.path.isfile(self._url):
			with open(self._url,'r', encoding='utf-8') as f:
				for line in f:
					params = line.split(";")
					if (len(params)==4):
						if self.is_int(params[1]):
							lowerBound = int(params[1])
						else:
							lowerBound = 0
						if self.is_int(params[2]):
							upperBound = int(params[2])
						else:
							upperBound = sys.maxsize
						if upperBound < lowerBound:
							print("Warning, upper bound was lower than lower bound. Ignoring boundaries.")
							lowerBound = 0
							upperBound = sys.maxsize
						if self.is_int(params[3]):
							measure = int(params[3])
						else:
							print("Warning: no bpm multiplier found for genre. Taking 2")
							measure = 2
						self.data[params[0]] = [lowerBound, upperBound, measure]
					else:
						print("Invalid line '{:}'".format(line))
