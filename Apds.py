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

	def startAsync(self):
		while True:
  			sleep(0.5)
			if self.apds.isGestureAvailable():
				motion = self.apds.readGesture()
				name = dirs.get(motion, "unknown")
				# print("Gesture={}".format(name))
				self.onGesture(name)		

	def stop(self):
  		GPIO.cleanup()
		return True
