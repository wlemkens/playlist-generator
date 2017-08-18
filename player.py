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
import numpy as np
import sys
import threading
import vlc

from PlaylistGenerator.MusicLibrary import MusicLibrary
from Gui.TimeSlider import TimeSlider



metricsFile = ""
musicPath = ""
song = None
genrePath = ""
if len(sys.argv)>1:
	musicPath = sys.argv[1]
else:
	print ("Usage "+sys.argv[0]+" [path/to/music/]")
	sys.exit(0)


class PlayerPanel(BoxLayout):
	def updatePanels(self,dt):
		if self.p:
			self.timeSlider.value = self.p.get_time()/1000
		
	#def updateDancePanel(self):
		#global song
		#self.dancePanel.font_size = (int)(np.min([self.size[1]/2.0,self.size[0]/20.0]))
		#if song and song.genre:
			#self.dancePanel.text = song.genre
		#else:
			#self.dancePanel.text = "Nothing"
		
	def onGenreText(self,instance, value):
		#self.songInput.text = ""
		genres = self.getGenres(value)
		self.genreListAdapter.data = genres
		
	def onSongTitleText(self,instance, value):
		self.titleFilter = value
		self.songs = self.getFilteredSongs(self.titleFilter,self.bandFilter)
		self.populateSongList(self.songs)
		
	def onBandNameText(self,instance, value):
		self.bandFilter = value
		self.songs = self.getFilteredSongs(self.titleFilter,self.bandFilter)
		self.populateSongList(self.songs)
		
	def populateSongList(self,songs):
		self.songListGrid.clear_widgets()
		index = 0
		for song in songs:
			songBtn = ToggleButton(text=song.title, size_hint_y=None, height=25,group='song')
			songBtn.bind(on_release=self.songSelectionChanged)
			songBtn.item=song
			songBtn.index = index
			index+=1
			bandLbl = Label(text=song.band,size_hint_x=0.4, width=150)
			durationLbl = Label(text=song.duration(),size_hint_x=None, width=70)
			self.songListGrid.add_widget(songBtn)
			self.songListGrid.add_widget(bandLbl)
			self.songListGrid.add_widget(durationLbl)
		
		
	def getGenres(self,filterString):
		genres = sorted(genre for genre in list(self.library.lookupTable) if filterString in genre)
		return genres
		
	def getFilteredSongs(self,nameFilterString,bandFilterString):
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

	def songSelectionChanged(self, button):
		global song
		self.selectedSong = button.item.title
		self.selectedSongIndex = button.index
		if (self.selectedGenre):
			for testSong in self.library.lookupTable[self.selectedGenre]:
				if testSong.title == self.selectedSong:
					song = testSong
					break
		else:
			for key,value in self.library.lookupTable.items():
				for testSong in value:
					if testSong.title == self.selectedSong:
						song = testSong
						break
		self.newSong = True
		self.timeSlider.max = song.length
		self.timeSlider.value=0
		self.startSong()

	def __init__(self, **kwargs):
		super(PlayerPanel, self).__init__(**kwargs)

		self.titleFilter = ""
		self.bandFilter = ""
		self.newSong = False
		self.songIndex = -1
		self.selectedGenre=""
		self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
		self._keyboard.bind(on_key_down=self._on_keyboard_down)
		self.p = None
		self.library = MusicLibrary(musicPath)
		self.selectedSongIndex=0
		self.allowSetTime = False
		self.orientation = "vertical"

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
		genres = sorted(list(self.library.lookupTable))
		self.genreListAdapter = ListAdapter(data=genres,cls=ListItemButton,selection_mode='single')
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
		
		
		songList = []
		if self.selectedGenre in self.library.lookupTable:
			songList = self.library.lookupTable[self.selectedGenre]
		else:
			songList = [song for songs in list(self.library.lookupTable) for song in self.library.lookupTable[songs]]
		self.songs = sorted(songList)
		self.songListGrid = GridLayout(cols=3, size_hint_y=None)
		self.songListGrid.bind(minimum_height=self.songListGrid.setter('height'))
		self.populateSongList(self.songs)
		self.songListView = ScrollView()
		dataPanel.add_widget(self.songListView)
		self.songListView.add_widget(self.songListGrid)

		self.timeSlider = TimeSlider(max=100,size=(30,60),size_hint=(1,None))
		self.timeSlider.on_value=self.onSliderValueChange
		self.add_widget(self.timeSlider)
		
		self.paused = True
		event = Clock.schedule_interval(self.updatePanels, 1 / 30.)
		
	def onSliderValueChange(self,instance,value):
		if self.allowSetTime:
			self.p.set_time(int(value*1000))

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
		if len(self.songs)>0:
			self.selectedSongIndex = (self.selectedSongIndex-1) % len(self.songs)
		song = self.songs[self.selectedSongIndex]
		self.timeSlider.max=song.length
		self.newSong = True
		self.startSong()

	def playNext(self):
		#print ("Playing next of "+str(len(self.songs))+" songs")
		global song
		if len(self.songs)>0:
			self.selectedSongIndex = (self.selectedSongIndex+1) % len(self.songs)
		song = self.songs[self.selectedSongIndex]
		self.timeSlider.max=song.length
		self.newSong = True
		self.startSong()
	
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

	def songEndReachedCallback(self,ev):
		self.p = None
		self.allowSetTime = False
		self.playNext()

	def playSong(self):
		self.p = vlc.MediaPlayer(song.url)
		pevent = self.p.event_manager()
		pevent.event_attach(vlc.EventType().MediaPlayerEndReached, self.songEndReachedCallback)
		self.p.play()
		self.allowSetTime = True
		
		
	def startSong(self):
		if self.newSong:
			if self.p:
				self.p.stop()
			self.newSong = False
			self.paused = False
			self.playSong()

class PlaylistPlayer(App):
		
	def build(self):
		self.newSong = False
		self.panel = PlayerPanel()
		#Window.fullscreen = 'auto'
		return self.panel


		
if __name__ == '__main__':
	PlaylistPlayer().run()
	