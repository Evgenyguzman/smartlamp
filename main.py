import Led
import Player
import AutoPair
import Apds

import threading

class SmartLamp(object):
  	
	def __init__(self):
  		self.led = Led.Led()
		self.autopair = AutoPair.AutoPair(self.onConnect, self.onDisconnect)
		self.player = Player.Player()
		self.apds = Apds.Apds()
	
	def startTest(self):
		print('Start Test')
		self.led.start('random')

		self.autopair.enable_pairing()
		self.led.setMode('connected')
		print('Led started')
		self.player.start(self.onPlayerPropChange)
		print('Player started')
		self.apds.start(7, self.onGesture)
		print('APDS started')

		# must be no end
		# while True:
  		# 	pass
		

	def start(self):
  		print('Start')
		self.led = Led.Led()
		self.led.start(0, 0, 0, 0)
		self.autopair = AutoPair.AutoPair(self.onConnect, self.onDisconnect)
		self.autopair.enable_pairing()
		# self.autopair.on('connect', self.onConnect)
		# self.autopair.on('disconnect', self.onDisconnect)

	def onConnect(self):
  		print('Connected')
		# self.autopair.disable_pairing()
		# self.led.setMode('connected')
		# self.player = Player()
		# self.player.start(self.onPlayerPropChange)
		# self.apds = Apds()
		# self.apds.start(7, self.onGesture)
  		
	def onDisconnect(self): 
		print('Disconnected')
		# self.autopair.enable_pairing()
		# self.led.setMode('disconnected')
		# self.player.stop()
		# self.apds.stop()

	def onPlayerPropChange(self, name, value):
  		if name == 'Status':
  			# print("Status changed:", name, value, self.player.state, self.player.volume)
			print('Playback Status: {}'.format(value))
			if value == 'paused':
				self.led.pause()
			elif value == 'playing':
				self.led.play()
		elif name == 'Track':
			self.led.setMode('random')

	def onGesture(self, name):
  		print("Gesture action:", name)
  		if name.startswith('right'):
  			self.player.next()
  			self.led.setMode('random')
		elif name.startswith('left'):
  			self.player.prev()
			self.led.setMode('random') # or prev
		elif name.startswith('up'):
			self.player.volumeUp(10)
		elif name.startswith('down'):
  			self.player.volumeDown(10)
		elif name.startswith('near') or name.startswith('far'):
  			if self.player.state.startswith('pause'):
  				self.player.play()
				self.led.play()
			else: 
				self.player.pause()
				self.led.pause()

	def stop(self):
  		print('Stop')
		# self.autopair.disable_pairing()
		# self.led.stop()
		# self.player.stop()
		# self.apds.stop()

if __name__ == "__main__":
	try:
		app = SmartLamp()
		t = threading.Thread(target=app.startTest, args=())
		t.start()
	except KeyboardInterrupt:
		app.stop()
