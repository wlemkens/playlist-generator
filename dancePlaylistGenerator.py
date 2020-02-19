#!/usr/bin/python3

# system imports
import sys

# custom imports
from PlaylistGenerator.DancePlaylistGenerator import DancePlaylistGenerator

if __name__ == '__main__':
	if len(sys.argv)<3:
		print("Usage dancePlaylistGenerator.py [music/direcotry] [output/direcotry]")
		sys.exit()
	generator = DancePlaylistGenerator(sys.argv[1],sys.argv[2])
	generator.generatePlaylists()