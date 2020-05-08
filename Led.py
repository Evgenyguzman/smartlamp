import RPi.GPIO as GPIO
from time import sleep

import threading
import random
# import math

class Led(object):

	pins = {'pin_R': 33, 'pin_G': 36, 'pin_B': 37}
	red = 0
	green = 0
	blue = 0
	speed = ''
	period = 5
	stepTime = 0.5
	mode = 'off' #on off blink

	playing = False

	opacity = 1.0
	step = 0.1

	def __init__(self):
		# self.colors = [0xFF0000, 0x00FF00, 0x0000FF,
		#     0xFFFF00, 0x00FFFF, 0xFF00FF, 0xFFFFFF, 0x9400D3]
		GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
		for i in self.pins:
  			GPIO.setup(self.pins[i], GPIO.OUT)   # Set pins' mode is output
			GPIO.output(self.pins[i], GPIO.HIGH)  # Set pins to high(+3.3V) to off led
		self.p_R = GPIO.PWM(self.pins['pin_R'], 2000)  # set Frequece to 2KHz
		self.p_G = GPIO.PWM(self.pins['pin_G'], 2000)
		self.p_B = GPIO.PWM(self.pins['pin_B'], 2000)
		self.p_R.start(0)
		self.p_G.start(0)
		self.p_B.start(0)

	def start(self, mode):
  		print('Led started')
		if(mode):
  			self.setMode(mode)
		self.updatingThread = threading.Thread(target=self.updateColor, args=())
		self.updatingThread.start()
		return True
	
	def updateColor(self):
  		while True:
			if(self.mode == 'off' or not self.playing):
  				self.opacity = 0.0
				print(self.red, self.green, self.blue, self.opacity)
				sleep(0.5)
			elif(self.mode == 'on'):
  				self.opacity = 1.0
				print(self.red, self.green, self.blue, self.opacity)
				sleep(0.5)
			elif(self.mode == 'blick'):
  				self.BlickCycle()

	def BlickCycle(self):
		for number in range(int(round(self.period / self.stepTime))):
			nextOpacity = round(self.opacity + self.step, 1)
			print('nextOpacity', nextOpacity)
			if( nextOpacity < 0 or nextOpacity > 1):
				self.step *= -1
				# print('Step inversed', self.step)
				# nextOpacity = self.opacity + self.step
				continue
			self.opacity = nextOpacity

			self.setColorsWithOpacity()
			sleep(self.stepTime)

	def setColorsWithOpacity(self):
  		print(self.red, self.green, self.blue, self.opacity)
  		self.setColorWithOpacity(self.p_R, self.red, self.opacity)
		self.setColorWithOpacity(self.p_G, self.green, self.opacity)
		self.setColorWithOpacity(self.p_B, self.blue, self.opacity)
		
	def setColorWithOpacity(self, pin, color, opacity):
  		pin.ChangeDutyCycle(100-(color*opacity))

	def setColor(self, col):  # For example : col = 0x112233
		R_val = (col & 0x110000) >> 16
		G_val = (col & 0x001100) >> 8
		B_val = (col & 0x000011) >> 0
		# print(R_val, G_val, B_val)
		# R_val = map(R_val, 0, 255, 0, 100)
		self.red = (R_val / 255) * 100
		self.green = (G_val / 255) * 100
		self.blue = (B_val / 255) * 100
		return True

	def setMode(self, mode):
  		print("Led: setMode", mode)
		if mode.startswith('disconnected'):
  			self.red = 100
			self.green = 0
			self.blue = 0
			self.mode = 'on'
		elif mode.startswith('connected'):
			self.mode = 'on'
			self.red = 0
			self.green = 100
			self.blue = 0
		elif mode.startswith('random'):
  			self.mode = 'blick'
			self.red = self.getRandomInt()
			self.green = self.getRandomInt()
			self.blue = self.getRandomInt()
  		return True
	
	def getRandomInt(self):
  		return random.randint(50, 100)

	def play(self):
		self.playing = True

	def pause(self):
		self.playing = False

	def stop(self):
		self.p_R.stop()
		self.p_G.stop()
		self.p_B.stop()
		self.updatingThread.stop()
		for i in pins:
			GPIO.output(pins[i], GPIO.HIGH)    # Turn off all leds
		GPIO.cleanup([33, 36, 37])
		return True
