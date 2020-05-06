import Led
import Player
import AutoPair
import Apds

class SmartLamp(object):
  	
	def __init__(self):
  		pass
	
	def startTest(self):
		print('Start Test')
		self.led = Led()
		self.led.start(0, 0, 0, 0)

		self.autopair = AutoPair.BtAutoPair(self.onConnect, self.onDisconnect)
		self.autopair.enable_pairing()
		self.led.setMode('connected')
		self.player = Player()
		self.player.start(onPlayerPropChange)
		self.apds = Apds()
		self.apds.start(None, self.onGesture)
		
		# must be no end

	def start(self):
  		print('Start')
		self.led = Led()
		self.led.start(0, 0, 0, 0)
		self.autopair = AutoPair.BtAutoPair(self.onConnect, self.onDisconnect)
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
		# self.apds.start(None, self.onGesture)
  		
	def onDisconnect(self): 
		print('Disconnected')
		# self.autopair.enable_pairing()
		# self.led.setMode('disconnected')
		# self.player.stop()
		# self.apds.stop()

	def onPlayerPropChange(self, name, value):
  		print("Player Prop changed:", name, value, self.player.state, self.player.volume)
  		if name == 'Status':
			print('Playback Status: {}'.format(value))
			if value == 'paused':
				self.led.pause()
			elif value == 'played':
				self.led.play()
			elif value == 'next':
  				self.led.setMode('random')
			elif value == 'prev':
				self.led.setMode('random')
        # elif prop == 'Track':
        #     print('Music Info:')

	def onGesture(self, name):
  		print("Gesture:", name)
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
		self.autopair.disable_pairing()
		self.led.stop()
		self.player.stop()
		self.apds.stop()

if __name__ == "__main__":
	try:
		app = SmartLamp()
		app.startTest()
	except KeyboardInterrupt:
		app.stop()
