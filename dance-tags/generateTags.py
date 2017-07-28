#!/usr/bin/python3

# needs pico2wave (sudo apt install ttspico-utils)

# system imports
import sys
from subprocess import call

#call(["espeak","-v", "dutch", "-a", "200", "-p", "70", "-w", "test.wav", "scottish"])

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
