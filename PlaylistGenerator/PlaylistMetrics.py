#!/usr/bin/python3


class PlaylistMetrics(object):
	def __init__(self):
		self.metrics = {}
		self.cumulativeList = []
		
	def load(self,url):
		with open(url) as f:
			total = 0.0
			for line in f:
				if len(line)>0 and line[0]!="#":
					items = line.split("=")
					if len(items)==2:
						key = items[0].strip(" ")
						value = (float)(items[1].strip(" "))
						self.metrics[key] = value
						total += value
			newValue = 0.0
			for key, value in self.metrics.items():
				newValue += value/total
				self.cumulativeList += [[newValue,key]]