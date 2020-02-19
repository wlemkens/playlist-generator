#!/usr/bin/python3


class PlaylistMetrics(object):
	def __init__(self):
		self.metrics = {}
		self.cumulativeList = []
		
	def load(self,url):
		'''
		Loads the metrics from file

		:param url:
		:return:
		'''
		self.metrics = {}
		self.cumulativeList = []
		if url:
			with open(url, encoding='utf-8') as f:
				total = 0.0
				for line in f:
					if len(line)>0 and line[0]!="#":
						items = line.split("=")
						if len(items)==2:
							key = items[0].strip(" ")
							value = (float)(items[1].strip(" "))
							if value > 0 and not key in self.metrics.keys():
								self.metrics[key] = value
								total += value
							elif key in self.metrics.keys():
								print("WARNING : Dupplicate entry for '{:}' in metrics".format(key))
				newValue = 0.0
				for key, value in self.metrics.items():
					newValue += value/total
					self.cumulativeList += [[newValue,key]]