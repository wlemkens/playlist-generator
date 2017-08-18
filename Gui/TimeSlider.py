#!/usr/bin/python3

import kivy
kivy.require('1.10.0') # replace with your current kivy version !

from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

import time


class TimeSlider(BoxLayout):
	def __init__(self, max, **kwargs):
		self.slider = Slider()
		self.orientation="vertical"
		super(TimeSlider, self).__init__(**kwargs)
		self.display = Label(text="-5:00",font_size=30,size=(30,30),size_hint=(1,None))
		self.add_widget(self.display)
		self.add_widget(self.slider)
		self.slider.value_track=True
		self.slider.value_track_color=[0.2, 0.71, 0.9, 1]
		self.slider.size=(30,30)
		self.slider.size_hint=(1,None)
		
	@property
	def max(self):
		return self.slider.max
	
	@max.setter
	def max(self,max):
		self.slider.max = max

	@property
	def font_size(self):
		return self.display.font_size
	
	@font_size.setter
	def font_size(self,font_size):
		self.display.font_size = font_size

	@property
	def value(self):
		return self.slider.value
	
	@value.setter
	def value(self,value):
		self.display.text="-"+time.strftime("%M:%S",time.gmtime(self.slider.max-value))
		self.slider.value = value
