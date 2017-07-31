#!/usr/bin/python3

import os


extensions = ["mp3","flac"]

def getFilesFromDirectory(directory):
	fileList = []
	for filename in os.listdir(directory):
		if os.path.isfile(directory+"/"+filename):
			filenameParts = filename.split(".")
			if (filenameParts[-1] in extensions):
				#print ("Processing "+directory+"/"+filename)
				fileList += [directory+"/"+filename]
		else:
			fileList += getFilesFromDirectory(directory+"/"+filename)
	return fileList
