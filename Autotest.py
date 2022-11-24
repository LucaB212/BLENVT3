import subprocess

class DUT(object):
	"""This class provides all methods to test the NVT3 device"""
	def __init__(self):
		pass

	def getSybokStatus(self):
		req_Sybok = subprocess.Popen("pgrep sybok", stdout=subprocess.PIPE, shell=True)
		Sybok = req_Sybok.stdout.read().decode('utf-8')
		return len(Sybok)

	def getInStatus(self):
		req_InMask = subprocess.Popen("udpctrl -alt property-read f901", stderr=subprocess.PIPE, shell=True) 
		InMask = req_InMask.stderr.read().decode('utf-8').split('=')[1][-3:-1] #'01'
		return None if InMask == "-1001" else InMask

	def getOutStatus(self):
		req_OutMask = subprocess.Popen("udpctrl -alt property-read f902", stderr=subprocess.PIPE, shell=True)
		OutMask = req_OutMask.stderr.read().decode('utf-8').split('=')[1][-3:-1]
		return None if OutMask == "-1001" else OutMask

	def getGPSAntennaStatus(self):
		req_GPSAntennaStatus = subprocess.Popen("udpctrl in-get 14", stderr=subprocess.PIPE, shell=True)
		GPSAntennaStatus = req_GPSAntennaStatus.stderr.read().decode('utf-8')
		return True if GPSAntennaStatus.split('= ')[1][:-1] == 'on' else False

	def getLastPowerFlags(self):
		req_lstPowerFlags = subprocess.Popen("udpctrl power-flags", stderr=subprocess.PIPE, shell=True)
		lstPowerFlags = req_lstPowerFlags.stderr.read().decode('utf-8')
		currentOn = lstPowerFlags.splitlines()[0].split()[-1][-2:]
		lastOff = lstPowerFlags.splitlines()[1].split()[-1][-2:] 
		return currentOn, lastOff

	def getHistoryPowerFlags(self):
		req_hstPowerFlags = subprocess.Popen("udpctrl power-events", stderr=subprocess.PIPE, shell=True)
		hstPowerFlags = req_hstPowerFlags.stderr.read().decode('utf-8')
		####return TODO

	def getBatteryLevel(self):
		req_BatteryLevel = subprocess.Popen("udpctrl battery-charge", stderr=subprocess.PIPE, shell=True)
		BatteryLevel = req_BatteryLevel.stderr.read().decode('utf-8')
		
