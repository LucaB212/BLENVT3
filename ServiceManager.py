import subprocess
import threading
from multiprocessing import Process, Pipe

import MQTT_service
from DeviceAgent import Socketclient
import logging
from logging.handlers import RotatingFileHandler


def waitForCommand(command):
	command = pipeOut.recv()
	logging.info("Command = {}".format(command))
	'''
	command = ["connect", '{"macaddr": "18:15:DA:25:45"}']
	'''



#if __name__ == '__main__':
	
############ INITIALIZATION ############

handler = RotatingFileHandler("service.log", mode='a', maxBytes=500000, backupCount=1)
logging.basicConfig(format='%(asctime)s - %(funcName)s - %(message)s', level="DEBUG", handlers=[handler])

req_DeviceID = subprocess.Popen("ubootset -dmd rifsn", stdout=subprocess.PIPE, shell=True) #"Serial number 'NVT3-2111004'""
DeviceID = req_DeviceID.stdout.read().decode('utf-8')[:-1]
logging.info("Device ID acquired: {}".format(DeviceID))
#print("DeviceID {} ".format(req_DeviceID.stdout.read().decode('utf-8')))

pipeOut, pipeIn = Pipe(False)	
command = [0]

#######################################

#deviceAgentProcess = subprocess.Popen(["python","DeviceAgent.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
mqttServiceSub = MQTT_service.Subscriber("MQTT-conf.json","NVT3-sub",pipeIn, logging, DeviceID)
mqttServiceSub.start([(DeviceID + "/BLE/connect",0)])   #subscibe with [(topic_1, qos_1), (topic_2, qos_2), ...]

#mqttServicePub = MQTT_service.Publisher("MQTT-conf.json","NVT3-pub")
#mqttServiceSub.start()

#thread1 = threading.Thread(target=waitForCommand, args=(command,))
#thread1. start()

while True:
	#thread1.join()
	command = pipeOut.recv()
	logging.info("Command received > {}".format(command))

	if command[0] == "rfcomm_connect":
		logging.info("Received command > rfcomm_connect")
		sock = Socketclient(dict(command[1])["macaddr"])
		psock = Process(target=sock.run, args=())
		psock.start()
		psock.join()


	thread1 = threading.Thread(target=waitForCommand, args=(command,))
	thread1. start()


		

		




		
