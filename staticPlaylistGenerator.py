#!/usr/bin/python3

# system imports
import sys

# custom imports
from PlaylistGenerator.StaticPlaylistGenerator import StaticPlaylistGenerator

if __name__ == '__main__':
	if len(sys.argv)<5:
		print("Usage generatePlaylist.py [music/path] [playlist/metrics/path] [output/filename] [duration (min)] <source/playlist>")
		sys.exit()
	generator = StaticPlaylistGenerator(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])