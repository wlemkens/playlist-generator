#!/usr/bin/python3

import os
import taglib


extensions = ["mp3","flac"]

def getFilesFromDirectory(directory):
	directory = directory.rstrip("/")
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

def getFileType(filename):
	return filename.split(".")[-1]

def getGenre(filename):
	try:
		id3info = taglib.File(filename)
		genre = id3info.tags["GENRE"]
		if len(genre)>0:
			genreName = genre[0].lower()
			if genreName[:5] == "folk ":
				genreName = genreName[5:]
			return genreName
		else:
			print("Not found genre for file '"+filename+"'")
			return None
	except (OSError):
		print("Error loading file '"+filename+"'")
		return None
	except (KeyError):
		print("Not found any genre tag for '"+filename+"'")
		return None
	return None
	
