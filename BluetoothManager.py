import threading
from bluez.bpb import BPB
import dbus
from gi.repository import GObject

import AutoAgent

class BluetoothManager:
    def __init__(self, connectCalback, disconnectCallback, playerChanged):
		self.connectCallback = connectCalback
		self.disconnectCallback = disconnectCallback
		self.playerChanged = playerChanged

		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		self.bpb = BPB(self.cb)

		self.bpb.register_agent('KeyboardDisplay')

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

		mainloop = GObject.MainLoop()
		mainloop.run()


		# initial enable or disable pairing

		# autoconnect with phones ?

		# t = threading.Thread(target=AutoAgent.startAutoAgent, args=(self.bpb.bus))
		# t.start()

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