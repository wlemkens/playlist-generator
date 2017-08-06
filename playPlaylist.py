#!/usr/bin/python3

# sudo add-apt-repository ppa:kivy-team/kivy
# sudo apt-get update
# sudo apt-get install python3-kivy
# sudo apt-get install python-kivy-examples

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

class PlayerPanel(BoxLayout):
	def updatePanels(self,dt):
		self.updateDancePanel()
		self.updateTitlePanel()
		self.updateBandPanel()
		
	def updateDancePanel(self):
		self.dancePanel.font_size = (int)(np.min([self.size[1]/2.0,self.size[0]/20.0]))
		
	def updateTitlePanel(self):
		self.titlePanel.font_size = (int)(np.min([self.size[1]/4.0,self.size[0]/40.0]))
		
	def updateBandPanel(self):
		self.bandPanel.font_size = (int)(np.min([self.size[1]/4.0,self.size[0]/40.0]))

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
	def build(self):
		panel = PlayerPanel(orientation='vertical')
		#Window.fullscreen = 'auto'
		return panel
		
if __name__ == '__main__':
     PlaylistPlayer().run()
	