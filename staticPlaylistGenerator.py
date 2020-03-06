#!/usr/bin/python3

# system imports
import sys

# custom imports
from PlaylistGenerator.StaticPlaylistGenerator import StaticPlaylistGenerator

if __name__ == '__main__':
	if len(sys.argv)<5:
		print("Usage generatePlaylist.py [music/path] [playlist/metrics/path] [output/filename] [duration (min)] <source/playlist> <refresh-db>")
		sys.exit()
	refreshDB = False
	if len(sys.argv) >= 6:
		refreshDB = (bool)(sys.argv[6])
	generator = StaticPlaylistGenerator(sys.argv[1],sys.argv[2],sys.argv[3],(float)(sys.argv[4]), refreshDB)
	generator.generatePlaylist()