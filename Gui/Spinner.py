#!/usr/bin/python3

import kivy
kivy.require('1.10.0') # replace with your current kivy version !

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class Spinner(BoxLayout):
	def up(self,instance):
		self.index = min(self.index+1,len(self.presets)-1)
		self.onIndexChange()
		
	def down(self,instance):
		self.index = max(self.index-1,0)
		self.label.text = str(self.presets[self.index])
		self.onIndexChange()
		
	def setIndex(self,index):
		self.index = max(min(index,len(self.presets)-1),0)
		self.onIndexChange()
		
	def __init__(self, presets = [0,1], index=0, **kwargs):
		super(Spinner, self).__init__(**kwargs)
		self.halign="center"
		height = 30
		upBtn = Button(text="+",on_press=self.up,size=(height,height),size_hint=(None,None),halign="left")
		downBtn = Button(text="-",on_press=self.down,size=(height,height),size_hint=(None,None),halign="right")
		#btnPanel = BoxLayout(size=(height/2,height),size_hint=(None,None),orientation="vertical")
		self.presets = presets
		self.label = Label(height=height,width=2*height,size_hint=(None,None),halign="center",valign="center")
		self.add_widget(downBtn)
		self.add_widget(self.label)
		#self.add_widget(btnPanel)
		self.add_widget(upBtn)
		self.setIndex(index)

	def onIndexChange(self):
		self.label.text = str(self.presets[self.index])
		self.indexChangeCallback(self.presets[self.index])

	def indexChangeCallback(self,value):
		pass