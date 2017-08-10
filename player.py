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

import numpy as np
import sys
import threading
import vlc

from PlaylistGenerator.MusicLibrary import MusicLibrary



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
		pass
		
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
		
	def onSongText(self,instance, value):
		songs = self.getSongs(value)
		self.songListAdapter.data = songs
		
	def getGenres(self,filterString):
		genres = sorted(genre for genre in list(self.library.lookupTable) if filterString in genre)
		return genres
		
	def getSongs(self,filterString):
		if self.selectedGenre in self.library.lookupTable:
			songList = [song.title for song in self.library.lookupTable[self.selectedGenre] if filterString in song.title]
		else:
			songList = [song.title for songs in list(self.library.lookupTable) for song in self.library.lookupTable[songs] if filterString in song.title]
		#songList = [song for song in songList if filterString in song]
		songs = sorted(songList)
		return songs
		
	def selectionChanged(self, *args):
		if len(args[0].selection)>0:
			self.selectedGenre = args[0].selection[0].text
		else:
			self.selectedGenre = ""
		songList = []
		if self.selectedGenre in self.library.lookupTable:
			songList = [song.title for song in self.library.lookupTable[self.selectedGenre]]
		else:
			songList = [song.title for songs in list(self.library.lookupTable) for song in self.library.lookupTable[songs]]
		songs = sorted(songList)
		self.songListAdapter.data = songs

	def songSelectionChanged(self, *args):
		global song
		if len(args[0].selection)>0:
			self.selectedSong = args[0].selection[0].text
			for testSong in self.library.lookupTable[self.selectedGenre]:
				if testSong.title == self.selectedSong:
					song = testSong
					break
			self.newSong = True
			self.startSong()

	def __init__(self, **kwargs):
		super(PlayerPanel, self).__init__(**kwargs)
		
		self.newSong = False
		self.songIndex = -1
		self.selectedGenre=""
		self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
		self._keyboard.bind(on_key_down=self._on_keyboard_down)
		self.p = None
		self.library = MusicLibrary(musicPath)
		
		controlPanel = BoxLayout(orientation='vertical',size_hint=(.3,1))
		self.add_widget(controlPanel)
		dataPanel = BoxLayout(orientation='vertical',size_hint=(.7,1))
		self.add_widget(dataPanel)
		
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
		
		self.songInput = TextInput(text='', multiline=False,size=(300,30),size_hint=(1,None))
		self.songInput.bind(text=self.onSongText)
		dataPanel.add_widget(self.songInput)
		songList = []
		print ()
		if self.selectedGenre in self.library.lookupTable:
			songList = [song.title for song in self.library.lookupTable[self.selectedGenre]]
		else:
			songList = [song.title for songs in list(self.library.lookupTable) for song in self.library.lookupTable[songs]]
			#songList = [songs for songs in list(self.library.lookupTable)]
		songs = sorted(songList)
		self.songListAdapter = ListAdapter(data=songs,cls=ListItemButton,selection_mode='single')
		self.songListAdapter.bind(on_selection_change=self.songSelectionChanged)
		self.songList = ListView(adapter=self.songListAdapter)
		dataPanel.add_widget(self.songList)
		
		self.paused = True
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
			song = self.library.songList[self.songIndex]
			self.newSong = True
	def playNext(self):
		global song
		if self.songIndex<len(self.library.songList)-1:
			self.songIndex += 1
			song = self.library.songList[self.songIndex]
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

	def songEndReachedCallback(self,ev):
		self.generateSong()

	def playSong(self):
		self.p = vlc.MediaPlayer(song.url)
		pevent = self.p.event_manager()
		pevent.event_attach(vlc.EventType().MediaPlayerEndReached, self.songEndReachedCallback)
		self.p.play()
		
		
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
	