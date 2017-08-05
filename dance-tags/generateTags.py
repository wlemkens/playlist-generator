#!/usr/bin/python3

# needs pico2wave (sudo apt install ttspico-utils)

# system imports
import sys
import os
from subprocess import call
from pydub import AudioSegment

#call(["espeak","-v", "dutch", "-a", "200", "-p", "70", "-w", "test.wav", "scottish"])
if (len(sys.argv)<2):
	print ("usage "+sys.argv[0]+" [genre/file]")
else:

	with open(sys.argv[1],'r') as f:
		for line in f:
			parts = line.split("=")
			if (len(parts)>1):
				dance = parts[1].lstrip(" ").rstrip(" ")
				name = parts[0].lstrip(" ").rstrip(" ")
				lang = "dutch"
				if (len(parts)>2):
					lang = parts[2].lstrip(" \n").rstrip(" \n")
				call(["espeak","-v", lang, "-a", "200", "-p", "70", "-w", name+".wav", dance])
				AudioSegment.from_wav(name+".wav").export(name+".mp3", format="mp3")
				os.remove(name+".wav")
