from apds9960 import APDS9960
from apds9960.const import *
import RPi.GPIO as GPIO
import smbus
from time import sleep

import threading

dirs = {
	APDS9960_DIR_NONE: "none",
	APDS9960_DIR_LEFT: "left",
	APDS9960_DIR_RIGHT: "right",
	APDS9960_DIR_UP: "up",
	APDS9960_DIR_DOWN: "down",
	APDS9960_DIR_NEAR: "near",
	APDS9960_DIR_FAR: "far",
}

class Apds(object):
  	
	running = False

	def __init__(self):
		self.onGesture = None
		try:
			port = 1
			bus = smbus.SMBus(port)
			self.apds = APDS9960(bus)
		except Exception as e:
			print(e)
		
	def intH(self, channel):
  		pass
		# print("INTERRUPT")

	def start(self, pin, onGesture = lambda: None):  		
		try:
			pin = 7
			self.onGesture = onGesture

			print('Starting APDS', pin)

			GPIO.setmode(GPIO.BOARD)
			GPIO.setup(pin, GPIO.IN)
			GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.intH)
			self.apds.setProximityIntLowThreshold(50)
			self.apds.enableGestureSensor()

			# must be async
			t = threading.Thread(target=self.startAsync, args=())
			t.start()
			print('APDS started')
		except Exception as e:
			print('Error starting APDS', e)

	def startAsync(self):
		while True:
  			sleep(0.5)
			try:
				isGestureAvailable = self.apds.isGestureAvailable()
				# print(isGestureAvailable)
				if isGestureAvailable:
  					if(not self.running):
						print('Gesture available')
  					self.running = True
					motion = self.apds.readGesture()
					name = dirs.get(motion, "unknown")
					# print("Gesture={}".format(name))
					self.onGesture(name)	
			except Exception as e:
				print(e)	
				self.running = False
				sleep(10)

	def stop(self):
  		GPIO.cleanup(7)
		return True
