from bpb import BPB
import threading

import dbus

import AutoAgent

class BleutoothManager:
    def __init__(self, connectCalback, disconnectCallback, playerChanged):
		self.connectCallback = connectCalback
		self.disconnectCallback = disconnectCallback
		self.playerChanged = playerChanged
		self.bpb = BPB(self.cb)
		o = self.bpb.if_obj_mgr.GetManagedObjects()
		for path, interfaces in o.iteritems():
			if 'org.bluez.MediaPlayer1' in interfaces:
  				self.player_iface = dbus.Interface(
					self.bpb.bus.get_object('org.bluez', path),
					'org.bluez.MediaPlayer1')
			elif 'org.bluez.MediaTransport1' in interfaces:
				self.transport_prop_iface = dbus.Interface(
					self.bpb.bus.get_object('org.bluez', path),
					'org.freedesktop.DBus.Properties')

		# initial enable or disable pairing

		# autoconnect with phones ?

		t = threading.Thread(target=AutoAgent.startAutoAgent, args=())
		t.start()

    def cb(self, evt):
  		# id, data (changed), instance
		print('Event:', evt['id'], evt)
		if (evt['id'] == 'mediaplayer'):
  			# to Player
			self.playerChanged(evt['id'], evt['data'])
		elif (evt['id'] == 'device'):
  			if evt['data']['Connected']:
  				self.disable_pairing()
				self.connectCallback()
			else:
  				self.enable_pairing()
				self.disconnectCallback()

    def enable_pairing(self):
  		print('Enable pairing')
		self.bpb.set_discoverable('on')
		# smth else

    def disable_pairing(self):
  		print('Disable pairing')
		self.bpb.set_discoverable('off')
		# smth else