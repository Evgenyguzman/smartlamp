#!/usr/bin/python
# encoding=utf8
import threading
from bluez.bpb import BPB
import dbus
from gi.repository import GObject

# import AutoAgent

class BluetoothManager:
	
	deviceAddress = None
	connected = False
	player_iface = None
	transport_prop_iface = None
	fullyConnected = False
	
	def __init__(self, connectCalback, disconnectCallback, playerChanged):
		self.connectCallback = connectCalback
		self.disconnectCallback = disconnectCallback
		self.playerChanged = playerChanged

		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		self.bpb = BPB(self.cb)

		self.bpb.register_agent('KeyboardDisplay')
		print('Agent registered')

		# check for connection
		# initial enable or disable pairing

		# autoconnect with phones ?

		# t = threading.Thread(target=AutoAgent.startAutoAgent, args=(self.bpb.bus))
		# t.start()

	def start(self):
  		devices = self.bpb.get_device_list()
		# print(devices)
		for device in devices:
  			# print(device)
			if(device['Connected']):
  				if(self.deviceAddress is not None):
  					print('Need to disconnect extra phone')
					# print(device)
					self.bpb.disconnect(device['Address'])
					return True
				self.deviceAddress = device['Address']
  				self.connected = True
  				self.setPlayerInterface()
				self.setTransportPropInterface()
				self.checkConnected()
		if(not self.connected):
  			for device in devices:
  				# print(device['Address'])
				if(not self.connected):
  					try:
						# print('Try to connect to:', device['Address'])
						self.bpb.connect(device['Address'])
					except Exception as e:
						print(e)

	def cb(self, evt):
  		# id, data (changed), instance
		# print('Event:', evt['id'])
		if (evt['id'] == 'mediaplayer'):
  			# to Player
			print('MediaPlayer', evt['path'])
			self.playerChanged(evt['id'], evt['data'])
		elif (evt['id'] == 'interface-added'):
  			print('Interfaces', evt['path'])
			if(evt['data'] is not None):
  				# print(evt['data'])
  				if(evt['data'] == 'org.bluez.MediaPlayer1'):
					self.setPlayerInterface()
				if(evt['data'] == 'org.bluez.MediaTransport1'):
  					self.setTransportPropInterface()
		elif (evt['id'] == 'device'):
			data = evt['data']
			try:
				# print(data, evt['path'])
				# получить device adress
				devAddress = evt['path'][-17:]
				if ((self.deviceAddress is None or self.deviceAddress == devAddress) and data['Connected'] is not None):
					print('Connected:', devAddress, data['Connected'])
					self.deviceAddress = devAddress
					self.connected = data['Connected']
					self.checkConnected()
				if(self.deviceAddress is not None and self.deviceAddress != devAddress):
  					self.bpb.disconnect(devAddress)
			except KeyError as e:
				print('KeyError', e)
  		
		# print('Connection statuses', self.connected, self.fullyConnected)
		

	# def tempFunc(device):
  		
		

	def checkConnected(self):
  		if(self.connected != self.fullyConnected):
    		# print('Connection status changed:', self.connected and self.player_iface is not None and self.transport_prop_iface is not None)
  			if(self.connected):
  				if(self.player_iface is not None and self.transport_prop_iface is not None):
					self.fullyConnected = True
					# actions
					self.connectCallback()
					self.disable_pairing()
			else:
  				self.fullyConnected = False
				self.unsetPlayerInterfaces()
				self.disconnectCallback()
				self.enable_pairing()

	def setPlayerInterface(self):
  		print('setPlayerInterface')
		o = self.bpb.if_obj_mgr.GetManagedObjects()
		for path, interfaces in o.iteritems():
			if 'org.bluez.MediaPlayer1' in interfaces:
  				# print('MediaPlayer', format(path))
  				self.player_iface = dbus.Interface(
					self.bpb.bus.get_object('org.bluez', path),
					'org.bluez.MediaPlayer1')

	def setTransportPropInterface(self):
  		print('setTransportPropInterface')
		o = self.bpb.if_obj_mgr.GetManagedObjects()
		for path, interfaces in o.iteritems():
			if 'org.bluez.MediaTransport1' in interfaces:
  				# print('MediaTransport', format(path))
				self.transport_prop_iface = dbus.Interface(
					self.bpb.bus.get_object('org.bluez', path),
					'org.freedesktop.DBus.Properties')

	def unsetPlayerInterfaces(self):
  		self.player_iface = None
		self.transport_prop_iface = None

	def enable_pairing(self):
  		print('Enable pairing')
		self.bpb.set_discoverable('on')
		self.bpb.set_pairable('on')
		# smth else

	def disable_pairing(self):
  		print('Disable pairing')
		self.bpb.set_discoverable('off')
		self.bpb.set_pairable('off')
		# smth else