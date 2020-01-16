import os
import types
import tkinter.messagebox

import csvop
import cfg


class filesData():
	def __init__(self, filename="data.csv"):
		self.filename = filename
		self.data = csvop.readDataFile(filename)
		
	def getIdxByName(self, filename):
		# get index by name
		basename = os.path.basename(filename)
		#print(basename)
		try:
			idx = int(basename[4:6])
		except:
			tkinter.messagebox.showerror("Invalid", "File Name Invalid: " + basename)
			return -1
		
		if idx < 1 or idx > 13:
			tkinter.messagebox.showerror("Invalid", "File Index Invalid: " + basename)
			return -1
		
		return idx

	def isExist(self, filename):
		idx = self.getIdxByName(filename)
		for f in self.data:
			if self.getIdxByName(f[0]) == idx:
				return True
		return False
	
	def idxValid(self, filename):
		idx = self.getIdxByName(filename)
		if idx < 0:
			return False
		return True
	
	def write(self):
		csvop.writeDataFile(self.data, self.filename)	
