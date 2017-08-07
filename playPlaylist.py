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

from PlaylistGenerator.PlaylistGenerator import PlaylistGenerator


metricsFile = ""
musicPath = ""
song = None
if len(sys.argv)>2:
	musicPath = sys.argv[1]
	metricsFile = sys.argv[2]
else:
	print ("Usage "+sys.argv[0]+" [path/to/music/] [path/to/playlist/metrics]")
	sys.exit(0)


class PlayerPanel(BoxLayout):
	def updatePanels(self,dt):
		self.updateDancePanel()
		self.updateTitlePanel()
		self.updateBandPanel()
		
	def updateDancePanel(self):
		global song
		self.dancePanel.font_size = (int)(np.min([self.size[1]/2.0,self.size[0]/20.0]))
		if song:
			self.dancePanel.text = song.genre
		else:
			self.dancePanel.text = "Nothing"
		
	def updateTitlePanel(self):
		self.titlePanel.font_size = (int)(np.min([self.size[1]/4.0,self.size[0]/40.0]))
		if song:
			self.titlePanel.text = song.title
		else:
			self.titlePanel.text = ""
		
	def updateBandPanel(self):
		self.bandPanel.font_size = (int)(np.min([self.size[1]/4.0,self.size[0]/40.0]))
		if song:
			self.bandPanel.text = song.band
		else:
			self.bandPanel.text = ""

	def __init__(self, **kwargs):
		super(PlayerPanel, self).__init__(**kwargs)
		
		self.dancePanel = Label(text="Test")
		self.add_widget(self.dancePanel)
		self.titlePanel = Label(text="Test")
		self.add_widget(self.titlePanel)
		self.bandPanel = Label(text="Test")
		self.add_widget(self.bandPanel)
		event = Clock.schedule_interval(self.updatePanels, 1 / 30.)

	
class PlaylistPlayer(App):
	def generateSong(self):
		global song
		song = self.playlistGenerator.generateUniqueSong()
		print ("Generated "+song.title)
		
	def build(self):
		self.playlistGenerator = PlaylistGenerator(musicPath,metricsFile)
		panel = PlayerPanel(orientation='vertical')
		#Window.fullscreen = 'auto'
		t = threading.Thread(target=self.generateSong)
		t.start()
		return panel
		
if __name__ == '__main__':
	PlaylistPlayer().run()
	