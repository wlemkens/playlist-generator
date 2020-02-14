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
from kivy.uix.textinput import TextInput
from kivy.uix.listview import ListView
from kivy.adapters.dictadapter import DictAdapter
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListItemButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup

import numpy as np
import sys
import threading
import vlc

from PlaylistGenerator.MusicLibrary import MusicLibrary
from Gui.TimeSlider import TimeSlider
from Gui.Spinner import Spinner
from Player.AudioPlayer import AudioPlayer




'''
The player panel doing most of the work
'''
class PlayerPanel(BoxLayout):
	'''
	Callback to update the panels periodically
	:dt	The time increment
	'''
	def updatePanels(self,dt):
		# Does the song list need a refresh (because new song is discovered)
		if self.songsNeedRefresh:
			self.populateSongList(self.songs)
			self.songsNeedRefresh = False

		# Update the player if it exists
		if self._player:
			self.timeSlider.value = self._player.getTime()

	'''
	Callback if some text has been entered in the genre text field
	:instance	The instance of the genre text field
	:value		The value entered
	'''
	def onGenreText(self,instance, value):
		genres = self.getGenres(value)
		self.genreListAdapter.data = genres

	'''
	Callback if some text has been entered in the song name text field
	:instance	The instance of the song name text field
	:value		The value entered
	'''
	def onSongTitleText(self,instance, value):
		self.titleFilter = value
		self.songs = self.getFilteredSongs(self.titleFilter,self.bandFilter)
		self.populateSongList(self.songs)

	'''
	Callback if some text has been entered in the band name text field
	:instance	The instance of the band text field
	:value		The value entered
	'''
	def onBandNameText(self,instance, value):
		self.bandFilter = value
		self.songs = self.getFilteredSongs(self.titleFilter,self.bandFilter)
		self.populateSongList(self.songs)

	'''
	Fill the GUI with the songs that have been found
	:songs	list of songs
	'''
	def populateSongList(self,songs):
		print ("populating")
		self.songListGrid.clear_widgets()
		index = 0
		lastBtn = None
		for song in songs:
			songBtn = ToggleButton(text=song.title, size_hint_y=None, height=25,group='song')
			songBtn.bind(on_release=self.songSelectionChanged)
			songBtn.item=song
			songBtn.index = index
			songBtn.previousBtn = lastBtn
			if lastBtn:
				lastBtn.nextBtn = songBtn
			lastBtn = songBtn
			index+=1
			bandLbl = Label(text=song.band,size_hint_x=0.4, width=150)
			durationLbl = Label(text=song.duration(),size_hint_x=None, width=70)
			if song.bpm < 100:
				spdTxt = "*"
			elif song.bpm < 120:
				spdTxt = "**"
			elif song.bpm < 140:
				spdTxt = "***"
			elif song.bpm < 160:
				spdTxt = "****"
			else: 
				spdTxt = "*****"				
			speedLbl = Label(text=spdTxt,size_hint_x=0.4, width=40)
			self.songListGrid.add_widget(songBtn)
			self.songListGrid.add_widget(bandLbl)
			self.songListGrid.add_widget(durationLbl)
			self.songListGrid.add_widget(speedLbl)
		print ("populating done")
		
		
	def getGenres(self,filterString=""):
		genres = sorted(genre for genre in list(self.library.lookupTable) if filterString in genre)
		return genres
		
	def getFilteredSongs(self,nameFilterString="",bandFilterString=""):
		if self.selectedGenre in self.library.lookupTable:
			songList = [song for song in self.library.lookupTable[self.selectedGenre] if nameFilterString in song.title and bandFilterString in song.band]
		else:
			songList = [song for songs in list(self.library.lookupTable) for song in self.library.lookupTable[songs] if nameFilterString in song.title and bandFilterString in song.band]
		songs = sorted(songList)
		return songs
		
	def selectionChanged(self, *args):
		if len(args[0].selection)>0:
			self.selectedGenre = args[0].selection[0].text
		else:
			self.selectedGenre = ""
		self.songs = self.getFilteredSongs(self.titleFilter,self.bandFilter)
		self.populateSongList(self.songs)

	def onCheckboxActive(self,checkbox,value):
		self._player.setFastSpeedChange(value)

	def songSelectionChanged(self, button):
		global song
		self.selectedSong = button
		button.state = "down"
		self.selectedSongIndex = button.index
		if (self.selectedGenre):
			for testSong in self.library.lookupTable[self.selectedGenre]:
				if testSong.title == self.selectedSong.item.title:
					song = testSong
					break
		else:
			for key,value in self.library.lookupTable.items():
				for testSong in value:
					if testSong.title == self.selectedSong.item.title:
						song = testSong
						break
		self.newSong = True
		self.timeSlider.value=0
		self.startSong()

	def onLibraryLoaded(self,nbOfSongs,nbOfGenres):
		genres = self.getGenres()
		self.genreListAdapter.data = genres
		self.songs = self.getFilteredSongs()
		self.songsNeedRefresh = True
		if self._popup:
			self._popup.dismiss()
		print ("Found {:d} songs and {:d} dances".format(nbOfSongs,nbOfGenres))

	def onSongFound(self,nbOfSongs,nbOfGenres):
		if self._popup:
			self._popup.content.text = "Found {:d} songs and {:d} dances".format(nbOfSongs,nbOfGenres)
			
	def showPopup(self,ev):
		self._popup.open()

		
	def __init__(self, **kwargs):
		print("__init__")
		super(PlayerPanel, self).__init__(**kwargs)

		# Init all member variables
		self.titleFilter = ""
		self.bandFilter = ""
		self.newSong = False
		self.songIndex = -1
		self.selectedGenre=""
		self.library = None
		self.selectedSongIndex=0
		self.allowSetTime = False
		self.orientation = "vertical"
		self.speed = 1.0
		self._popup = None
		self.songsNeedRefresh = False

		# Attach keyboard
		self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
		self._keyboard.bind(on_key_down=self._on_keyboard_down)

		# Setup layout
		mainPanel = BoxLayout()
		self.add_widget(mainPanel)
		controlPanel = BoxLayout(orientation='vertical',size_hint=(.3,1))
		mainPanel.add_widget(controlPanel)
		dataPanel = BoxLayout(orientation='vertical',size_hint=(.7,1))
		mainPanel.add_widget(dataPanel)
		filterPanel = BoxLayout()
		filterPanel.size=(300,30)
		filterPanel.size_hint=(1,None)
		dataPanel.add_widget(filterPanel)
		
		self.genreInput = TextInput(text='', multiline=False,height=30)
		self.genreInput.bind(text=self.onGenreText)
		controlPanel.add_widget(self.genreInput)
		self.genreListAdapter = ListAdapter(data=[],cls=ListItemButton,selection_mode='single')
		self.genreListAdapter.bind(on_selection_change=self.selectionChanged)
		self.genreList = ListView(adapter=self.genreListAdapter)
		controlPanel.add_widget(self.genreList)
		self.genreInput.size=(300,30)
		self.genreInput.size_hint=(1,None)
		
		self.songInput = TextInput(text='')
		self.songInput.bind(text=self.onSongTitleText)
		filterPanel.add_widget(self.songInput)
		self.bandInput = TextInput(text='', multiline=False,size=(300,30),size_hint=(.4,None))
		self.bandInput.bind(text=self.onBandNameText)
		filterPanel.add_widget(self.bandInput)
		placeholder = Label(size_hint_x=None, width=70)
		filterPanel.add_widget(placeholder)
		
		
		self.songListGrid = GridLayout(cols=4, size_hint_y=None)
		self.songListGrid.bind(minimum_height=self.songListGrid.setter('height'))
		self.songListView = ScrollView()
		dataPanel.add_widget(self.songListView)
		self.songListView.add_widget(self.songListGrid)
		self._player = AudioPlayer()
		self._player.endReachedCallback = self.songEndReachedCallback
		self._player.loadedCallback = self.songLoadedCallback

		speedBox = BoxLayout(size=(300,30),size_hint=(1,None))
		self.add_widget(speedBox)
		self.speedSpinner = Spinner(np.arange(0.5,2.1,0.1),5)
		self.speedSpinner.indexChangeCallback = self.speedChangeCallback
		speedBox.add_widget(self.speedSpinner)
		speedChkBox = BoxLayout(size=(200,30),size_hint=(1,None))
		speedBox.add_widget(speedChkBox)
		speedChkLabel = Label(text="Fast speed change",halign="right")
		speedChkBox.add_widget(speedChkLabel)
		self.fastSpeedChangeChk = CheckBox(size=(30,30),size_hint=(None,None),active=True)
		self.fastSpeedChangeChk.bind(active=self.onCheckboxActive)
		speedChkBox.add_widget(self.fastSpeedChangeChk)
		
		self.timeSlider = TimeSlider(max=100,size=(30,60),size_hint=(1,None))
		self.timeSlider.on_value=self.onSliderValueChange
		self.add_widget(self.timeSlider)

		# Create and show loading popup
		self._popup = Popup(title="Loading library", content=Label(text="Loading library"),
												size_hint=(0.8, 0.8))
		self._popup.open()

		# Load music library
		if musicPath:
			self.library = MusicLibrary(musicPath)
			self.library.onLibraryLoaded = self.onLibraryLoaded
			self.library.onSongFound = self.onSongFound

		# Attach clock callback for gui updates
		event = Clock.schedule_interval(self.updatePanels, 1 / 30.)

		# Attach clock callback for loading of music
		event = Clock.schedule_once(self.loadMusic,1)

		#if self._popup:
			#self._popup.dismiss()
		
	def loadMusic(self,dt):
		self.library.loadMusic()
		
	def speedChangeCallback(self,speed):
		self.speed = speed
		
	def onSliderValueChange(self,instance,value):
		self._player.setTime(value)

	def _keyboard_closed(self):
			self._keyboard.unbind(on_key_down=self._on_keyboard_down)
			self._keyboard = None

	def pause(self):
		if self._player:
			self._player.togglePause()
			
	def backward(self):
		if self._player:
			self._player.setTime(self._player.getTime()-1)
		
	def forward(self):
		if self._player:
			self._player.set_time(self._player.getTime()+1)
		
	def playPrevious(self):
		if self.selectedSong:
			self.selectedSong = self.selectedSong.previousBtn
			self.selectedSong.trigger_action()

	def playNext(self):
		if self.selectedSong:
			self.selectedSong = self.selectedSong.nextBtn
			self.selectedSong.trigger_action()
	
	def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
			if keycode[1] == 'spacebar' or keycode[1] == 'numpadenter':
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
			elif keycode[1] == 'down':
					self.backward()
			elif keycode[1] == 'up':
					self.forward()
			return True

	def songEndReachedCallback(self,ev):
		self.playNext()

	def songLoadedCallback(self):
		self.timeSlider.max = self._player.trackLength/1000.0

	def playSong(self):
		self._player.loadAndPlay(song,self.speed)

		
	def startSong(self):
		self.playSong()

'''
The app itself although all the work is done by the component
'''
class PlaylistPlayer(App):
		
	def build(self):
		self.panel = PlayerPanel()
		Window.fullscreen = 'auto'
		return self.panel

	def on_stop(self):
		self.panel.library.close()

'''
Main, checking command line parameters
'''
if __name__ == '__main__':
	metricsFile = ""
	musicPath = ""
	song = None
	genrePath = ""
	if len(sys.argv)>1:
		musicPath = sys.argv[1].rstrip('/')
		PlaylistPlayer().run()
	else:
		print ("Usage "+sys.argv[0]+" [path/to/music/]")
		sys.exit(0)
