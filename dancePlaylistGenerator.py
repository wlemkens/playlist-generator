#!/usr/bin/python3

# system imports
import sys

# custom imports
from PlaylistGenerator.DancePlaylistGenerator import DancePlaylistGenerator

if __name__ == '__main__':
	if len(sys.argv)<3:
		print("Usage dancePlaylistGenerator.py [music/directory] [output/directory] <refresh db>")
		print("")
		print("Creates a playlist for each dance (genre)")
		sys.exit()
	refreshDB = False
	if len(sys.argv) >= 4:
		refreshDB = (bool)(sys.argv[3])
	generator = DancePlaylistGenerator(sys.argv[1],sys.argv[2], refreshDB)
	generator.generatePlaylists()