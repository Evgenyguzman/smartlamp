import Led
import Player2
import BluetoothManager
import Apds

import threading
from gi.repository import GObject

class SmartLamp(object):
  	
	def __init__(self):
  		self.led = Led.Led()
		self.player = Player2.Player()
		self.btManager = BluetoothManager.BluetoothManager(self.onConnect, self.onDisconnect, self.player.on_property_changed)
		self.apds = Apds.Apds()
	
	# def startTest(self):
	# 	print('Start Test')
	# 	self.led.start('random')
	# 	self.btManager.enable_pairing()
	# 	self.led.setMode('connected')
	# 	print('Led started')
	# 	self.player.start(self.onPlayerPropChange)
	# 	print('Player started')
	# 	self.apds.start(7, self.onGesture)
	# 	print('APDS started')
		
	def start(self):
  		print('App starting')
		self.led.start('random')
		print('Led started')
		self.apds.start(7, self.onGesture)
		print('APDS started')
		self.btManager.start()
		self.mainloop = GObject.MainLoop()
		self.mainloop.run()

	def onConnect(self):
  		print('Connected')
		self.led.setMode('connected')
		if(self.btManager.player_iface is not None and self.btManager.transport_prop_iface is not None):
  			# print(self.btManager.player_iface, self.btManager.transport_prop_iface)
			self.player.start(self.onPlayerPropChange, self.btManager.player_iface, self.btManager.transport_prop_iface)
			print('Player started')
  		
	def onDisconnect(self): 
		# print('Disconnected')
		# self.led.setMode('disconnected')
		self.player.stop()
		print('Player stopped')
		# self.apds.stop()
		# print('APDS stopped')

	def onPlayerPropChange(self, name, value):
  		if name == 'Status':
  			# print("Status changed:", name, value, self.player.state, self.player.volume)
			# print('Playback Status: {}'.format(value))
			if value == 'paused':
				self.led.pause()
			elif value == 'playing':
				self.led.play()
		elif name == 'Track':
			self.led.setMode('random')

	def onGesture(self, name):
  		# print("Gesture action:", name)
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
		self.led.stop()
		self.player.stop()
		self.apds.stop()
		self.mainloop.stop()

if __name__ == "__main__":
	try:
		app = SmartLamp()
		# t = threading.Thread(target=app.start, args=())
		# t.start()
		app.start()
		print('App end')
	except KeyboardInterrupt:
		app.stop()
		# t.stop() ???
