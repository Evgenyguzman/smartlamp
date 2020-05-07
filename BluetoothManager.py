#!/usr/bin/python
# encoding=utf8
import threading
from bluez.bpb import BPB
import dbus
from gi.repository import GObject

import AutoAgent

class BluetoothManager:
	
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

		# mainloop = GObject.MainLoop()
		# mainloop.run()


		# initial enable or disable pairing

		# autoconnect with phones ?

		# t = threading.Thread(target=AutoAgent.startAutoAgent, args=(self.bpb.bus))
		# t.start()

	def cb(self, evt):
  		# id, data (changed), instance
		# print('Event:', evt['id'])
		if (evt['id'] == 'mediaplayer'):
  			# to Player
			self.playerChanged(evt['id'], evt['data'])
		elif (evt['id'] == 'interface-added'):
			if(evt['data'] is not None):
  				print(evt['data'])
  				if(evt['data'] == 'org.bluez.MediaPlayer1'):
					self.setPlayerInterfaces()
					pass
				if(evt['data'] == 'org.bluez.MediaTransport1'):
  					self.setPlayerInterfaces()
					pass
		elif (evt['id'] == 'device'):
			data = evt['data']
  			if (data['Connected'] is not None):
  				print('Connected:', data['Connected'])
				self.connected = data['Connected']
  				if evt['data']['Connected']:
					# self.setPlayerInterfaces()
					self.connectCallback()
					self.disable_pairing()
				else:
  					# self.fullyConnected = False
					self.unsetPlayerInterfaces()
					self.disconnectCallback()
					self.enable_pairing()
  		
		print('Connection statuses', self.connected, self.fullyConnected)
		if(self.connected != self.fullyConnected):
  			print('Connection status changed:', self.connected and self.player_iface is not None and self.transport_prop_iface is not None)
  			if(self.connected):
  				if(self.player_iface is not None and self.transport_prop_iface is not None):
					self.fullyConnected = True
					# actions
			else:
  				self.fullyConnected = False
				#   actions
		

	def setPlayerInterfaces(self):
  		print('setPlayerInterfaces')
		o = self.bpb.if_obj_mgr.GetManagedObjects()
		for path, interfaces in o.iteritems():
  			print(format(path))
			if 'org.bluez.MediaPlayer1' in interfaces:
  				print('MediaPlayer', format(path))
  				self.player_iface = dbus.Interface(
					self.bpb.bus.get_object('org.bluez', path),
					'org.bluez.MediaPlayer1')
			elif 'org.bluez.MediaTransport1' in interfaces:
  				print('MediaTransport', format(path))
				self.transport_prop_iface = dbus.Interface(
					self.bpb.bus.get_object('org.bluez', path),
					'org.freedesktop.DBus.Properties')

	def unsetPlayerInterfaces(self):
  		self.player_iface = None
		self.transport_prop_iface = None

	def enable_pairing(self):
  		print('Enable pairing')
		self.bpb.set_discoverable('on')
		# smth else

	def disable_pairing(self):
  		print('Disable pairing')
		self.bpb.set_discoverable('off')
		# smth else