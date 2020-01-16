import serial
from PyCRC.CRCCCITT import CRCCCITT

class mcuDeviceRet():
	def __init__(self, result, msg):
		self.result = result
		self.msg = msg

class mcuDevice():
	def __init__(self, comNum, retry):
		self.comNum = comNum
		self.ser = None
		self.retryCount = retry
		
	def open(self):
		comName = 'COM' + self.comNum
		
		try:
			self.ser = serial.Serial(comName, 115200, timeout=1)
		except:
			ret = mcuDeviceRet("ERROR", "%s can not open." % comName)
			return ret
		
		ret = mcuDeviceRet("OK", "Open done.")
		return ret
		
	def close(self):
		self.ser.close()
		
		ret = mcuDeviceRet("OK", "Close done.")
		return ret

	def runCmd(self, cmd):
		cmdRetry = self.retryCount
		ret = None
		
		while(cmdRetry > 0):
			cmdRetry -= 1
			self.ser.write(cmd)
			
			line = self.ser.readline().decode("utf-8")
			getACK = "+ACK:" in line
			rspRetry = self.retryCount
			while (not getACK) and (rspRetry > 0):
				line = self.ser.readline().decode("utf-8")
				getACK = "+ACK:" in line
				rspRetry -= 1
			
			if (rspRetry <= 0):
				ret = mcuDeviceRet("Warning", "Can not get +ACK from device")
				print(ret.msg)
				continue
				
			print(line)
			if "ERROR" in line:
				ret = mcuDeviceRet("ERROR", line)
				print(ret.msg)
				continue
	
			ret = mcuDeviceRet("OK", "runCmd done.")
			return ret
		
		return ret