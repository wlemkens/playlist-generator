#!/usr/bin/python3

#sudo add-apt-repository ppa:kivy-team/kivy
#sudo apt-get update
#sudo apt-get install python3-kivy -y
#sudo apt-get install python-kivy-examples -y

import kivy
kivy.require('1.10.0') # replace with your current kivy version !

from kivy.clock import Clock
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.config import Config

import numpy as np
import sys
import threading
import vlc

from PlaylistGenerator.PlaylistGenerator import PlaylistGenerator


metricsFile = ""
musicPath = ""
song = None
genrePath = ""
if len(sys.argv)>2:
	musicPath = sys.argv[1]
	metricsFile = sys.argv[2]
	enableAnnoucements = True
	delay = 10.0
	if len(sys.argv)>3:
		genrePath = sys.argv[3]
	if len(sys.argv)>4:
		delay = float(sys.argv[4])
	if len(sys.argv)>5:
		if sys.argv[5]=="0":
			enableAnnoucements = False
else:
	print ("Usage "+sys.argv[0]+" [path/to/music/] [path/to/playlist/metrics] <path/to/genres/> <announcement delay (s)> <enable announcement 0/1>")
	sys.exit(0)


class PlayerPanel(BoxLayout):
	def updatePanels(self,dt):
		self.updateDancePanel()
		self.updateTitlePanel()
		self.updateBandPanel()
		
	def updateDancePanel(self):
		global song
		self.dancePanel.font_size = (int)(np.min([self.size[1]/2.0,self.size[0]/20.0]))
		if song and song.genre:
			self.dancePanel.text = song.genre
		else:
			self.dancePanel.text = "Nothing"
		
	def updateTitlePanel(self):
		self.titlePanel.font_size = (int)(np.min([self.size[1]/4.0,self.size[0]/40.0]))
		if song and song.title:
			self.titlePanel.text = song.title
		else:
			self.titlePanel.text = ""
		
	def updateBandPanel(self):
		self.bandPanel.font_size = (int)(np.min([self.size[1]/4.0,self.size[0]/40.0]))
		if song and song.band:
			self.bandPanel.text = song.band
		else:
			self.bandPanel.text = ""

	def __init__(self, **kwargs):
		super(PlayerPanel, self).__init__(**kwargs)
		
		self.newSong = False
		self.songIndex = -1
		self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
		self._keyboard.bind(on_key_down=self._on_keyboard_down)
		self.p = None
		self.playlistGenerator = PlaylistGenerator(musicPath,metricsFile)
		self.dancePanel = Label(text="Test")
		self.add_widget(self.dancePanel)
		self.titlePanel = Label(text="Test")
		self.add_widget(self.titlePanel)
		self.bandPanel = Label(text="Test")
		self.add_widget(self.bandPanel)
		self.paused = True
		t = threading.Thread(target=self.generateSong)
		t.start()
		event = Clock.schedule_interval(self.startSong, 1 / 30.)
		event = Clock.schedule_interval(self.updatePanels, 1 / 30.)

	def _keyboard_closed(self):
			self._keyboard.unbind(on_key_down=self._on_keyboard_down)
			self._keyboard = None

	def pause(self):
		if self.paused:
			self.p.play()
			self.paused = False
		else:
			self.p.pause()
			self.paused = True
	def backward(self):
		self.p.set_time(self.p.get_time()-1000)
	def forward(self):
		self.p.set_time(self.p.get_time()+1000)
		
	def playPrevious(self):
		global song
		if self.songIndex>0:
			self.songIndex -= 1
			song = self.playlistGenerator.songList[self.songIndex]
			self.newSong = True
	def playNext(self):
		global song
		if self.songIndex<len(self.playlistGenerator.songList)-1:
			self.songIndex += 1
			song = self.playlistGenerator.songList[self.songIndex]
			self.newSong = True
		else:
			self.generateSong()
	
	def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
			if keycode[1] == 'spacebar':
				self.pause()
			elif keycode[1] == 'left':
				if len(modifiers)>0 and modifiers[0] == 'shift':
					self.backward()
				else:
					self.playPrevious()
			elif keycode[1] == 'right':
				if len(modifiers)>0 and modifiers[0] == 'shift':
					self.forward()
				else:
					self.playNext()
			return True

	def generateSong(self):
		global song
		song = self.playlistGenerator.generateUniqueSong()
		self.newSong = True
		self.songIndex += 1
	
	def songEndReachedCallback(self,ev):
		self.generateSong()

	def delayAnnouncement(self,dt):
		self.playAnnouncement(song.genre)
		
	def announcementEndReachedCallback(self,ev):
		global delay
		if self.announcementCount > 0:
			self.announcementCount = 0
			self.playSong()
		elif self.announcementCount == 0:
			self.announcementCount += 1
			Clock.schedule_once(self.delayAnnouncement, delay)
		
	def playAnnouncement(self,genre):
		global genrePath
		genreFile = genrePath+"/"+genre+".mp3"
		self.p = vlc.MediaPlayer(genreFile)
		pevent = self.p.event_manager()
		pevent.event_attach(vlc.EventType().MediaPlayerEndReached, self.announcementEndReachedCallback)
		self.p.play()
		
		
	def playSong(self):
		self.p = vlc.MediaPlayer(song.url)
		pevent = self.p.event_manager()
		pevent.event_attach(vlc.EventType().MediaPlayerEndReached, self.songEndReachedCallback)
		self.p.play()
		
		
	def startSong(self,dt):
		global enableAnnoucements
		if self.newSong:
			if self.p:
				self.p.stop()
			self.newSong = False
			self.paused = False
			if enableAnnoucements:
				self.announcementCount = 0
				self.playAnnouncement(song.genre)
			else:
				self.playSong()

class PlaylistPlayer(App):
		
	def build(self):
		self.newSong = False
		self.panel = PlayerPanel(orientation='vertical')
		#Window.fullscreen = 'auto'
		return self.panel


		
if __name__ == '__main__':
	PlaylistPlayer().run()
	