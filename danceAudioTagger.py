#!/usr/bin/python3

# system imports
import sys

# custom imports
from DanceAudioTagger.DanceAudioTagger import DanceAudioTagger

if __name__ == '__main__':
	if len(sys.argv)<4:
		print("Usage danceAudioTagger.py [music/path] [genre/path] [output/path]")
		sys.exit()
	tagger = DanceAudioTagger(sys.argv[1],sys.argv[2],sys.argv[3])
	tagger.tagMusic()