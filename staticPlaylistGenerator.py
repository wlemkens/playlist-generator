#!/usr/bin/python3

# system imports
import sys

# custom imports
from PlaylistGenerator.StaticPlaylistGenerator import StaticPlaylistGenerator

if __name__ == '__main__':
	if len(sys.argv)<5:
		print("Usage generatePlaylist.py [music/path] [playlist/metrics/path] [output/filename] [duration (min)] <refresh-db> </forced/path/>")
		print("")
		print("  </forced/path/> : Paths in the playlist will be relative to the working directory. To enforce a different path, you can give one here.")
		sys.exit()
	refreshDB = False
	forced_path = None
	if len(sys.argv) >= 7:
		forced_path = sys.argv[6]
	if len(sys.argv) >= 6:
		refreshDB = (bool)(sys.argv[5])
	generator = StaticPlaylistGenerator(sys.argv[1],sys.argv[2],sys.argv[3],(float)(sys.argv[4]), forced_path, refreshDB)
	generator.generatePlaylist()