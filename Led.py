import RPi.GPIO as GPIO
import time

class Led(object):

	def __init__(self):
		self.colors = [0xFF0000, 0x00FF00, 0x0000FF,
		    0xFFFF00, 0x00FFFF, 0xFF00FF, 0xFFFFFF, 0x9400D3]
		self.pins = {'pin_R': 11, 'pin_G': 12, 'pin_B': 13}
		GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location

	def start(self, mode):
  		for i in self.pins:
			GPIO.setup(self.pins[i], GPIO.OUT)   # Set pins' mode is output
			GPIO.output(self.pins[i], GPIO.HIGH)  # Set pins to high(+3.3V) to off led
		self.p_R = GPIO.PWM(self.pins['pin_R'], 2000)  # set Frequece to 2KHz
		self.p_G = GPIO.PWM(self.pins['pin_G'], 2000)
		self.p_B = GPIO.PWM(self.pins['pin_B'], 2000)
		self.p_R.start(0)
		self.p_G.start(0)
		self.p_B.start(0)
		return True
	
	def setColor(self, col):  # For example : col = 0x112233
		R_val = (col & 0x110000) >> 16
		G_val = (col & 0x001100) >> 8
		B_val = (col & 0x000011) >> 0
		print(R_val, G_val, B_val)
		# R_val = map(R_val, 0, 255, 0, 100)
		# G_val = map(G_val, 0, 255, 0, 100)
		# B_val = map(B_val, 0, 255, 0, 100)
		# print(R_val, G_val, B_val)
		self.p_R.ChangeDutyCycle(100-R_val)     # Change duty cycle
		self.p_G.ChangeDutyCycle(100-G_val)
		self.p_B.ChangeDutyCycle(100-B_val)
		return True

	def setMode(self, mode):
		if mode.startswith('disconnected'):
			self.setColor(0xFF0000)
		elif mode.startswith('connected'):
			self.setColor(0x00FF00)
		elif mode.startswith('random'):
			self.setColor(self.getRandomColor())
  		return True

	def getRandomColor(self):
		return 0xFFFFFF

	def play(self):
		self.playing = True

	def pause(self):
		self.playing = False

	def stop(self):
		self.p_R.stop()
		self.p_G.stop()
		self.p_B.stop()
		for i in pins:
			GPIO.output(pins[i], GPIO.HIGH)    # Turn off all leds
		GPIO.cleanup()
		return True
