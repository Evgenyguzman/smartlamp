from apds9960 import APDS9960
from apds9960.const import *
import RPi.GPIO as GPIO
import smbus
from time import sleep

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
  		port = 1
		bus = smbus.SMBus(port)
		self.apds = APDS9960(bus)
		self.onGesture = None
		
	def intH(self, channel):
		print("INTERRUPT")

	def start(self, none = None, onGesture = lambda: None):
  		
		pin = 7
		self.onGesture = onGesture

		print('Starting APDS', pin)

		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(pin, GPIO.IN)
		GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.intH)
		self.apds.setProximityIntLowThreshold(50)

		print("Gesture Test")
		print("============")
		self.apds.enableGestureSensor()
		while True:
			sleep(0.5)
			if self.apds.isGestureAvailable():
				motion = self.apds.readGesture()
				print("Gesture={}".format(dirs.get(motion, "unknown")))
				self.onGesture(dirs.get(motion, "unknown"))

	def stop(self):
  		GPIO.cleanup()
		return True
