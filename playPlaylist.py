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
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView


import numpy as np
import sys
import threading
import vlc
from os.path import join, isdir
import os
import time

from PlaylistGenerator.PlaylistGenerator import PlaylistGenerator
from Tools import DirectoryTools
from Gui.TimeSlider import TimeSlider
from Player.AudioPlayer import AudioPlayer

metricsFile = ""
musicPath = ""
song = None
genrePath = ""
if len(sys.argv)>3:
	musicPath = sys.argv[1]
	metricsFile = sys.argv[2]
	enableAnnoucements = True
	delay = 10.0
	if len(sys.argv)>3:
		if sys.argv[3]=="0":
			enableAnnoucements = False
	if len(sys.argv)>4 and enableAnnoucements:
		genrePath = sys.argv[4]
	if len(sys.argv)>5:
		delay = float(sys.argv[5])
else:
	print ("CLI usage "+sys.argv[0]+" [path/to/music/] [path/to/playlist/metrics] [enable announcement 0/1] [path/to/genres/] <announcement delay (s)>")

class LoadDialog(FloatLayout):
	load = ObjectProperty(None)
	cancel = ObjectProperty(None)
	
	def is_dir(self, directory, filename):
		return isdir(join(directory, filename))

	def updatePanels(self,dt):
		self.mainPanel.pos=self.pos
	
	def loadMusic(self,button):
		self.load(self.fileView.path, self.fileView.selection)
		
	def __init__(self, **kwargs):
		super(LoadDialog, self).__init__(**kwargs)
		self.mainPanel = BoxLayout(size=self.size,orientation="vertical")
		self.add_widget(self.mainPanel)
		
		self.fileView = FileChooserListView(filters=[self.is_dir])
		self.mainPanel.add_widget(self.fileView)
		
		buttonPanel = BoxLayout(size_hint_y=None,height=30)
		self.mainPanel.add_widget(buttonPanel)
		cancelBtn = Button(text="Cancel")
		cancelBtn.bind(on_release=self.cancel)
		buttonPanel.add_widget(cancelBtn)
		loadBtn = Button(text="Load")
		loadBtn.bind(on_release=self.loadMusic)
		buttonPanel.add_widget(loadBtn)
		event = Clock.schedule_interval(self.updatePanels, 1 / 30.)
		
    
class PlayerPanel(BoxLayout):
	def updatePanels(self,dt):
		self.updateAnnouncementsPanel()
		self.updateDancePanel()
		self.updateTitlePanel()
		self.updateBandPanel()
		self.updateSliderPanel()
		
	def updateAnnouncementsPanel(self):
		self.announcementBtnLbl.text_size=self.announcementBtnLbl.size
		self.announcementChkLbl.text_size=self.announcementChkLbl.size
		self.enableAnnoucementsChk.active = enableAnnoucements
		self.announcementDelayInput.text = str(delay)
		
	def updateDancePanel(self):
		global song
		self.dancePanel.font_size = (int)(np.min([self.size[1]/2.0,self.size[0]/20.0]))
		if song and song.genre:
			self.dancePanel.text = song.genre
		else:
			self.dancePanel.text = "Nothing"
		
	def updateSliderPanel(self):
		global song
		self.timeSlider.font_size = (int)(np.min([self.size[1]/2.0,self.size[0]/60.0]))
		self.timeSlider.value = self.player.getTime()
		
	def onSliderValueChange(self,instance,value):
		if self.player:
			self.player.setTime(value)

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

	def onCheckboxActive(self,checkbox,value):
		global enableAnnoucements
		if enableAnnoucements != value:
			self.player.setPlayAnnouncements(value)
			enableAnnoucements = value
		
	def dismiss_popup(self):
		self._popup.dismiss()
		
	def loadMusicPath(self, path, filename):
		#print("'"+path+"', '"+str(filename)+"'")
		global musicPath
		musicPath = path
		self.dismiss_popup()
		self.playlistGenerator.setMusicPath(musicPath)
            
	def loadAnnouncementPath(self, path, filename):
		global genrePath
		genrePath = path
		self.player.setAnnouncementDirectory(path)
		self.dismiss_popup()

	def loadMetricsFile(self, path, filename):
		global metricsFile
		metricsFile = filename[0]
		self.dismiss_popup()
		self.playlistGenerator.setMetrics(metricsFile)

	def loadMusic(self,instance):
		content = LoadDialog(load=self.loadMusicPath, cancel=self.dismiss_popup)
		content.fileView.path = musicPath
		
		self._popup = Popup(title="Load music", content=content,
												size_hint=(0.9, 0.9))
		self._popup.open()
	
	def isMetricsFile(self,diretory,filename):
		return DirectoryTools.getFileType(filename)=="metrics"
	
	def loadMetrics(self,instance):
		content = LoadDialog(load=self.loadMetricsFile, cancel=self.dismiss_popup)
		content.fileView.filters = [self.isMetricsFile]
		content.fileView.path = os.path.dirname(os.path.abspath(metricsFile))
		self._popup = Popup(title="Load playlist metrics", content=content,
												size_hint=(0.9, 0.9))
		self._popup.open()
		
	def loadAnnouncements(self,instance):
		content = LoadDialog(load=self.loadAnnouncementPath, cancel=self.dismiss_popup)
		content.fileView.path = genrePath
		self._popup = Popup(title="Load annmouncements", content=content,
												size_hint=(0.9, 0.9))
		self._popup.open()
		
	def onDelayText(self,instance,value):
		global delay
		if self.announcementDelayInput.text:
			delay = float(self.announcementDelayInput.text)
			self.player.setAnnouncementDelay(delay)
	
	def __init__(self, **kwargs):
		super(PlayerPanel, self).__init__(**kwargs)
		self.state = 0
		self.songIndex = -1
		self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
		self._keyboard.bind(on_key_down=self._on_keyboard_down)
		self.p = None
		self.playlistGenerator = PlaylistGenerator(musicPath,metricsFile)
		self.menuPanel = BoxLayout(height=30,size_hint=(1,None))
		self.add_widget(self.menuPanel)
		self.loadMusicBtn = Button(text="Load music",on_press=self.loadMusic)
		self.menuPanel.add_widget(self.loadMusicBtn)
		self.loadMetricsBtn = Button(text="Load metrics",on_press=self.loadMetrics)
		self.menuPanel.add_widget(self.loadMetricsBtn)
		self.loadAnnouncementsBtn = Button(text="Load announcements",on_press=self.loadAnnouncements)
		self.menuPanel.add_widget(self.loadAnnouncementsBtn)
		self.announcementBtnLbl = Label(text="Announcement delay",halign="right",valign="center")
		self.menuPanel.add_widget(self.announcementBtnLbl)
		self.announcementDelayInput = TextInput(text='', multiline=False,size=(100,30),size_hint=(None,None),input_filter='float',unfocus_on_touch=True)
		self.announcementDelayInput.bind(text=self.onDelayText)
		self.menuPanel.add_widget(self.announcementDelayInput)
		self.announcementChkLbl = Label(text="Enable announcements",halign="right",valign="center")
		self.menuPanel.add_widget(self.announcementChkLbl)
		self.enableAnnoucementsChk = CheckBox(size=(30,30),size_hint=(None,None))
		self.enableAnnoucementsChk.bind(active=self.onCheckboxActive)
		self.menuPanel.add_widget(self.enableAnnoucementsChk)
		self.dancePanel = Label(text="Test")
		self.add_widget(self.dancePanel)
		self.titlePanel = Label(text="Test")
		self.add_widget(self.titlePanel)
		self.bandPanel = Label(text="Test")
		self.add_widget(self.bandPanel)

	
		self.player = AudioPlayer(enableAnnoucements, genrePath, delay)
		self.player.endReachedCallback = self.songEndReachedCallback
		self.timeSlider = TimeSlider(max=100)
		self.timeSlider.on_value=self.onSliderValueChange
		self.add_widget(self.timeSlider)
		self.paused = False
		t = threading.Thread(target=self.generateSong)
		t.start()
		event = Clock.schedule_interval(self.songStatusCallback, 1 / 30.)
		event = Clock.schedule_interval(self.updatePanels, 1 / 30.)
		self.fullscreen = True

	def _keyboard_closed(self):
			self._keyboard.unbind(on_key_down=self._on_keyboard_down)
			self._keyboard = None

	def pause(self):
		self.player.togglePause()

	def backward(self):
		self.player.setTime(self.player.getTime()-1)
	def forward(self):
		self.player.setTime(self.player.getTime()+1)
		
	def playPrevious(self):
		global song
		if self.songIndex>0:
			self.songIndex -= 1
			song = self.playlistGenerator.songList[self.songIndex]
			self.player.loadAndPlay(song)
			
	def playNext(self):
		global song
		if self.songIndex<len(self.playlistGenerator.songList)-1:
			self.songIndex += 1
			song = self.playlistGenerator.songList[self.songIndex]
			self.player.loadAndPlay(song)
		else:
			self.generateSong()
	
	def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
			if keycode[1] == 'escape':
				sys.exit(0)
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
			elif keycode[1] == 'f':
				if self.fullscreen:
					Window.fullscreen = False
					self.fullscreen = False
				else:
					Window.fullscreen = "auto"
					self.fullscreen = True
			return True

	def generateSong(self):
		print ("Generating song")
		global song
		song = self.playlistGenerator.generateUniqueSong()
		self.songIndex += 1
		self.timeSlider.max = song.length
		self.timeSlider.value=0
		self.player.loadSong(song)
		self.player.play()
	
	def songEndReachedCallback(self):
		print ("End")
		self.generateSong()

		
	def songStatusCallback(self,dt):
		pass

class PlaylistPlayer(App):
		
	def build(self):
		self.panel = PlayerPanel(orientation='vertical')
		Window.fullscreen = 'auto'
		return self.panel


		
if __name__ == '__main__':
	PlaylistPlayer().run()
	
