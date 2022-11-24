import paho.mqtt.client as PahoMQTT
import json
from multiprocessing import Pipe

confFilename = "MQTT-conf.json"


def config_extract():
	configurations = {}
	"""Open and extract all the MQTT config"""
	try:
		with open(confFilename, 'r') as f:
			configurations = json.load(f)
	except FileNotFoundError as e:
		raise(e)

		return configurations


class Publisher(object):
	"""docstring for Client"""
	def __init__(self, configFile,name):
		f_conf=open(configFile)
		init_conf=json.load(f_conf)
		f_conf.close()
		self._paho_mqtt=PahoMQTT.Client(name,False)
		self._paho_mqtt.on_connect=self.OnConnect
		#self.topic=init_conf["mqtt"]["topic"]
		self.broker=init_conf["mqtt"]["brokerID"]
		self.port=init_conf["mqtt"]["brokerPort"]
		self.qos=init_conf["mqtt"]["QoS"]
		
	def start(self):
		self._paho_mqtt.connect(self.broker, self.port)
		self._paho_mqtt.loop_start()

	def OnConnect(self, paho_mqtt, userData, flags, rc):
		#print(f"Publisher connected to {self.broker} with result {rc}")
		logging.info("Publisher connected to {} with result {}".format(self.broker,rc))

	
	def Publish(self, topicID, data):		
		self._paho_mqtt.publish(topicID, data, self.qos)   #### data=> dictionary "value": int|float|string
		logging.info("Published new topic {}".format(topicID))
		logging.debug("Topic: {}\tpayload: {}".format(topicID, data))
	
	def stop(self):
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()


class Subscriber:
		def __init__(self, configFile, name, pipein, logging, devID):
			f_conf=open(configFile)
			init_conf=json.load(f_conf)
			f_conf.close()
			self._paho_mqtt=PahoMQTT.Client(name,False)
			self._paho_mqtt.on_connect=self.OnConnect
			self._paho_mqtt.on_message=self.MessageReceived
			self.logging=logging
			self.broker=init_conf["mqtt"]["brokerID"]
			self.port=init_conf["mqtt"]["brokerPort"]
			self.name=name
			self.pipein=pipein
			self.logging=logging
			self.devID=devID	

		def start (self, topic):
			#manage connection to broker
			self._paho_mqtt.connect(self.broker, self.port)			

			self._paho_mqtt.loop_start()
			# subscribe for a topic
			for elem in topic:
				self._paho_mqtt.subscribe(elem[0],elem[1])
			self.logging.info("Subscribed topic by {}:  {}".format())
			

		def stop (self):
			self._paho_mqtt.unsubscribe(topic)
			self._paho_mqtt.loop_stop()
			self._paho_mqtt.disconnect()

		def OnConnect (self, paho_mqtt, userdata, flags, rc):
			self.logging.info("Subscriber connected to %s with result code: %d" % (self.broker, rc))
			#print ("Subscriber connected to %s with result code: %d" % (self.broker, rc))

		def MessageReceived (self, paho_mqtt , userdata, msg):
			# A new message is received
			self.logging.info("New message received")
			self.logging.debug("Topic:<" + msg.topic+">, QoS: <"+str(msg.qos)+"> Message: <"+str(msg.payload) + ">")
			#print ("Topic:'" + msg.topic+"', QoS: '"+str(msg.qos)+"' Message: '"+str(msg.payload) + "'")
			#global output
			if "BLE/connect" in msg.topic:
				#proc=subprocess.Popen(["python","DeviceAgent.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
				data_in=json.loads(msg.payload.decode())
				self.logging.info("BLE connection forced to:  {}".format(data_in))
				self.pipein.send(["connect",data_in])	#["connect", '{"macaddr": "18:15:DA:25:45"}']
				
					
					
if __name__ == '__main__':
	logging.basicConfig(filename='syslog.log', filemode='a', format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s', level='DEBUG')	#tail -f syslog.log
	sub = Subscriber("MQTT-conf.json","NVT3_Test_Sub",output)		#subscriber conf
	sub.start(["0001","0002"])										#subscirber's topic
	pub = Publisher("MQTT-conf.json", "NVT3_Test_Pub")				#publisher conf
	pub.start()

	buffer = SimpleQueue()		#queue between eventToSend 


	config = config_extract()			

	with open('pipe_comin', 'w') as p:		#Incoming comunication from external world      RX
		pass

	pipein = open('pipe_comout', 'r')		#Outcoming comunication for the external world  TX

	payload = []
	timer_high_p = time.time()
	timer_low_p = time.time()

	while True:
		thread1 = threading.Thread(target=eventToSend, args=(buffer,))
		thread1.start()

		while buffer.qsize():
			payload.append(eval(buffer.get()))	### (priority, (event, data))

		payload.sort()
		for elem in payload:
			if elem[0] == 1:
				#if time.time() - config["ttl_high_priority"] > timer_high_p:
				pub.Publish(str(elem[1][0]),elem[1][1])
				timer_low_p = 0.0
				#timer_high_p = 0.0
			elif elem[0] == 2:
				if time.time() - config["ttl_low_pririty"] > timer_low_p:
					pub.Publish(str(elem[1][0]), elem[1][1])
					timer_low_p = 0.0

		if timer_low_p == 0.0:
			payload = []
			timer_low_p = time.time()
			#timer_high_p = time.time()


		while output:
			with open('pipe_comin','a') as pipein:
				pipein.write(str(output.pop())+'\n')
				



		



