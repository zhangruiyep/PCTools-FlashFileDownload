import os
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk as ttk
import types
import serial
from PyCRC.CRCCCITT import CRCCCITT
import csvop
import cfg


class AddFrame(ttk.Frame):
	def __init__(self, master=None, parentIdx=""):
		ttk.Frame.__init__(self, master)
		self.grid()
		self.tv = master
		self.parentIdx = parentIdx
		self.createWidgets()
		
	def createWidgets(self):
		dataframe = ttk.Frame(self)
		dataframe.grid(row = 0, pady=3)
		
		label = ttk.Label(dataframe, text="File:", justify=tk.LEFT)
		label.grid(row=0, sticky=tk.E, padx=6, pady=3)

		self.fileEntry = ttk.Entry(dataframe)
		self.fileEntry.delete(0, tk.END)
		self.fileEntry.grid(row=0, column=1, padx=6, pady=3)		

		self.getFileBtn = ttk.Button(dataframe, text="Choose", command=self.chooseFile, width=10)
		self.getFileBtn.grid(row=0, column=2, padx=6, pady=3)

		label = ttk.Label(dataframe, text="Index(1~13):", justify=tk.LEFT)
		label.grid(row=1, sticky=tk.E, padx=6, pady=3)

		self.offEntry = ttk.Entry(dataframe)
		self.offEntry.delete(0, tk.END)
		self.offEntry.grid(row=1, column=1, padx=6, pady=3)		

		btnframe = ttk.Frame(self)
		btnframe.grid(row = 1, pady=3)
		
		OKBtn = ttk.Button(btnframe, text="OK", command=self.addRecord)
		OKBtn.grid(row=0, padx=6)
		CancelBtn = ttk.Button(btnframe, text="Cancel", command=self.cancelAdd)
		CancelBtn.grid(row=0, column=1, padx=6)

	def addRecord(self):
		filename = self.fileEntry.get()
		if not os.path.exists(filename):
			tkinter.messagebox.showwarning("Warning", "File not found")
			return
		
		offsetStr = self.offEntry.get()
		index = int(offsetStr)
		if index < 1 or index > 13:
			tkinter.messagebox.showwarning("Warning", "Index Invalid")
			return
		
		self.tv.insert(self.parentIdx, "end", values=(filename, offsetStr))

		self.destroy()

	def cancelAdd(self):
		self.destroy()
		
	def chooseFile(self):
		filename = tkinter.filedialog.askopenfilename()
		if (filename != None) and (filename != ""):
			self.fileEntry.delete(0, tk.END)
			self.fileEntry.insert(0, os.path.realpath(filename))

def takeOffset(elem):
	return elem[1]

class filesTreeview(ttk.Treeview):
	def __init__(self, master=None):
		ttk.Treeview.__init__(self, master)
		self['columns']=("filename", "index")
		self.filesdata = []
		self.grid(sticky=tk.NSEW)
		self.createWidgets()
	
	def createWidgets(self):
		self.column("#0", width=20, stretch=0)
		self.column("filename", width=400)
		self.column("index", width=100)

		self.heading('filename', text='File Name')
		self.heading('index', text='Index')
		
	def fill_treeview(self, filesdata):
		self.filesdata = filesdata
		for item in self.get_children():
			self.delete(item)
			
		for f in self.filesdata:
			self.insert('',"end",values=(f[0], f[1]))

	
	def update_filesdata(self):
		self.filesdata = []
		for i in self.get_children():
			self.filesdata.append([self.item(i)["values"][0], self.item(i)["values"][1]])
		self.filesdata.sort(key=takeOffset)
					
class Application(ttk.Frame):
	def __init__(self, master=None):
		ttk.Frame.__init__(self, master) 
		self.cfg = cfg.configFile()
		self.columnconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		self.grid(sticky=tk.NSEW) 
		self.createWidgets()
		
	def createWidgets(self):
		tv_frame = ttk.Frame(self)
		tv_frame.grid(row = 2, sticky=tk.NSEW, pady = 3)
		
		self.tv = filesTreeview(tv_frame)
		self.tv.grid(row = 0, sticky=tk.NSEW)
		try:
			filesdata = csvop.readDataFile("data.csv")
		except:
			filesdata = []
		self.tv.fill_treeview(filesdata)
				
		self.sb = ttk.Scrollbar(tv_frame, orient=tk.VERTICAL, command=self.tv.yview)
		self.sb.grid(row = 0, column=1, sticky=tk.NS)
		
		self.tv.configure(yscrollcommand=self.sb.set)

		self.context_menu = tk.Menu(self.tv, tearoff=0)
		self.context_menu.add_command(label="Add", command=self.add_handler)
		self.context_menu.add_command(label="Delete", command=self.delete_handler)
		self.tv.bind('<3>', self.show_context_menu)
		self.entryPopup = ""
		self.record_frame = ""

		serial_frame = ttk.Frame(self)
		serial_frame.grid(row = 0, sticky=tk.NSEW, pady = 3)
		
		self.Info = ttk.Label(serial_frame, text="COM 1:", justify=tk.LEFT)
		self.Info.grid(row=0, sticky=tk.W, padx=10)
		
		self.serialCOMEntry = ttk.Entry(serial_frame, width = 5)
		self.serialCOMEntry.grid(row=0, column=1, padx=10)
		if self.cfg:
			try:
				self.serialCOMEntry.delete(0, tk.END)
				self.serialCOMEntry.insert(0, self.cfg.cp['Serial']['COM1'])
			except:
				print("can not get file name from cfg")

		#self.getFileBtn = ttk.Button(serial_frame, text="Choose", command=self.chooseOutputFile, width=10)
		#self.getFileBtn.grid(row=0, column=2, padx=10)
		
		#flashOptionFrame = ttk.Frame(self)
		#flashOptionFrame.grid(row = 1, sticky=tk.NSEW, pady=3)
		
		#self.flashSizeInfo = ttk.Label(flashOptionFrame, text="Flash size(MB):", justify=tk.LEFT)
		#self.flashSizeInfo.grid(row = 0, sticky=tk.W, padx=10)

		#optionList = ["", "8", "4", "2", "1"]
		#self.v = tk.StringVar()
		#self.v.set(optionList[1])
		#if self.cfg:
		#	try:
		#		self.v.set(self.cfg.cp['OutFile']['Size'])
		#	except:
		#		print("can not get file size from cfg")
			
		#self.platformOpt = ttk.OptionMenu(flashOptionFrame, self.v, *optionList)
		#self.platformOpt.grid(row = 0, column=1, sticky=tk.W, padx=10)

		progressFrame = ttk.Frame(self)
		progressFrame.grid(row = 3, sticky=tk.NSEW, pady=3)
		
		#self.pbar = ttk.Progressbar(progressFrame,orient ="horizontal",length = 500, mode ="determinate")
		#self.pbar.grid(padx=10, sticky=tk.NSEW)
		#self.pbar["maximum"] = 100

		actionFrame = ttk.Frame(self)
		actionFrame.grid(row = 4, sticky=tk.NSEW, pady=3)
		
		self.dloadBtn = ttk.Button(actionFrame, text="Download", command=self.dloadAll)
		self.dloadBtn.grid(padx=10, row = 0, column = 0)

		#self.saveCfgFileBtn = ttk.Button(actionFrame, text="Save Configuration", command=self.saveCfgFile)
		#self.saveCfgFileBtn.grid(padx=10, row = 0, column = 1)		

	def show_context_menu(self, event):
		self.context_menu.post(event.x_root,event.y_root)
		self.event = event
 

	def delete_handler(self):
		# close previous popups
		if self.entryPopup:
			self.entryPopup.destroy()
			
		self.edit_row = self.tv.identify_row(self.event.y)
		
		self.tv.focus(self.edit_row)
		
		item = self.tv.focus()
		if item != '':
			self.tv.delete(item)

		
	def add_handler(self):
		if self.entryPopup:
			self.entryPopup.destroy()

		self.edit_row = self.tv.identify_row(self.event.y)
		self.edit_column = self.tv.identify_column(self.event.x)
		
		parent = self.tv.parent(self.edit_row)
		self.addDataFrame(parent)
			
			
	def addDataFrame(self, parentItem):
		#x,y,width,height = self.tv.bbox(parentItem)
		
		if self.record_frame:
			self.record_frame.destroy()

		self.record_frame = AddFrame(self.tv, parentItem)
		self.record_frame.place(x=0, y=20, anchor=tk.NW)			
	
	def entryEntryDestroy(self, event):
		self.entryPopup.destroy()
			
	def dloadAll(self):
		comNum = self.serialCOMEntry.get().strip()
		if not comNum:
			tkinter.messagebox.showwarning("Warning", "COM not set")
			return
		
		comNum = 'COM' + comNum
		self.tv.update_filesdata()
		
		with serial.Serial(comNum, 115200, timeout=1) as ser:
			cmd = b'AT+IAPSRT=%x\r\n' % self.tv.filesdata[0][1]
			print(cmd)
			ser.write(cmd)
			line = ser.readline().decode("utf-8")
			getACK = "+ACK:" in line
			while not getACK:
				line = ser.readline().decode("utf-8")
				getACK = "+ACK:" in line
			print(line)
			if "ERROR" in line:
				tkinter.messagebox.showwarning("Warning", line)
				return
			
			filename = os.path.realpath(self.tv.filesdata[0][0])
			filesize = os.path.getsize(filename)
			print(filesize)
			
			with open(filename, "rb") as f:
				content = f.read()
				#print(content)
				
				filecrc = CRCCCITT().calculate(content)
				print(filecrc)
				
				f.close()
			
			cmd = b'AT+IAPSOH=%d,%d\r\n' % (filesize, filecrc)
			print(cmd)
			ser.write(cmd)
			line = ser.readline().decode("utf-8")
			getACK = "+ACK:" in line
			while not getACK:
				line = ser.readline().decode("utf-8")
				getACK = "+ACK:" in line
			print(line)
			if "ERROR" in line:
				tkinter.messagebox.showwarning("Warning", line)
				return

			i = 0
			idx = 0
			framesizeMax = 1024
			while i < filesize:
				
				# get real frame size
				if i + framesizeMax <= filesize:
					framesize = framesizeMax
				else:
					framesize = filesize - i
				
				# get frame data
				frame = b''
				for j in range(0,framesize):
					frame += bytes([content[i+j]])
				
				#print(frame)
				
				# calculate frame crc
				framecrc = CRCCCITT().calculate(frame)
				
				cmd = b'AT+IAPDWN=%d,%d,%d,%s\r\n' % (idx, framesize, framecrc, frame.hex().encode("utf-8"))
				#print(cmd)
				print("downloading %d, %d, %d" % (idx, framesize, framecrc))
				ser.write(cmd)
				line = ser.readline().decode("utf-8")
				getACK = "+ACK:" in line
				while not getACK:
					line = ser.readline().decode("utf-8")
					getACK = "+ACK:" in line
				print(line)
				if "ERROR" in line:
					tkinter.messagebox.showwarning("Warning", line)
					return
				
				# set index to next frame
				i += framesizeMax
				idx += 1
				
			cmd = b'AT+IAPEOT=1\r\n'
			print(cmd)
			ser.write(cmd)
			line = ser.readline().decode("utf-8")
			getACK = "+ACK:" in line
			while not getACK:
				line = ser.readline().decode("utf-8")
				getACK = "+ACK:" in line
			print(line)
			if "ERROR" in line:
				tkinter.messagebox.showwarning("Warning", line)
				return

			ser.close()
			tkinter.messagebox.showwarning("Warning", "Download Complete.")
			
		
	def saveCfgFile(self):
		try:
			self.cfg.cp.add_section("OutFile")
		except:
			print("section exist")
		outFileName = self.serialCOMEntry.get().strip()
		self.cfg.cp['OutFile']['Name'] = outFileName
		self.cfg.cp['OutFile']['Size'] = self.v.get()
		self.cfg.write()

		self.tv.update_filesdata()
		csvop.writeDataFile(self.tv.filesdata, "data.csv")	

		return
	
	def updateProgress(self, value):
		self.pbar["value"] = int(value * self.pbar["maximum"])
		self.update_idletasks()

app = Application() 
app.master.title('FlashImgGen') 
app.master.rowconfigure(0, weight=1)
app.master.columnconfigure(0, weight=1)
app.mainloop() 