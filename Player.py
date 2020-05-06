import dbus
import dbus.mainloop.glib
import sys
from gi.repository import GLib
import threading


class Player(object):

	def __init__(self):
		self.onPlayerPropChange = None
		self.state = 'paused'
		self.volume = None

	def start(self, onPlayerPropChange):
  		
		self.onPlayerPropChange = onPlayerPropChange

  		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		bus = dbus.SystemBus()
		obj = bus.get_object('org.bluez', "/")
		mgr = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')
		self.player_iface = None
		self.transport_prop_iface = None
		for path, ifaces in mgr.GetManagedObjects().items():
			if 'org.bluez.MediaPlayer1' in ifaces:
				self.player_iface = dbus.Interface(
					bus.get_object('org.bluez', path),
					'org.bluez.MediaPlayer1')
			elif 'org.bluez.MediaTransport1' in ifaces:
				self.transport_prop_iface = dbus.Interface(
					bus.get_object('org.bluez', path),
					'org.freedesktop.DBus.Properties')
		if not self.player_iface:
			sys.exit('Error: Media Player not found.')
		if not self.transport_prop_iface:
			sys.exit('Error: DBus.Properties iface not found.')

		self.volume = self.transport_prop_iface.Get(
			'org.bluez.MediaTransport1',
			'Volume')

		bus.add_signal_receiver(
			self.on_property_changed,
			bus_name='org.bluez',
			signal_name='PropertiesChanged',
			dbus_interface='org.freedesktop.DBus.Properties')

		t = threading.Thread(target=self.startAsync, args=())
		t.start()
		

	def startAsync(self):
  		GLib.io_add_watch(sys.stdin, GLib.IO_IN, self.on_playback_control)
		GLib.MainLoop().run()
	
	def on_property_changed(self, interface, changed, invalidated):
		if interface != 'org.bluez.MediaPlayer1':
			return
		for prop, value in changed.items():
  			self.onPlayerPropChange(prop, value)
			# print(prop, value)
			if prop == 'Status':
				# print('Playback Status: {}'.format(value))
				self.state = format(value)
				pass
			elif prop == 'Track':
				# print('Music Info:')
				# for key in ('Title', 'Artist', 'Album'):
				# 	print('   {}: {}'.format(key, value.get(key, '')))
				pass

	def on_playback_control(self, fd, condition):
		str = fd.readline()
		if str.startswith('play'):
			self.play()
		elif str.startswith('pause'):
			self.pause()
		elif str.startswith('next'):
			self.next()
		elif str.startswith('prev'):
			self.prev()
		elif str.startswith('vol'):
			vol = int(str.split()[1])
			self.setVolume(vol)
		return True

	def play(self):
  		print('Player: play')
  		self.state = 'playing'
		self.player_iface.Play()

	def pause(self):
  		print('Player: pause')
  		self.state = 'paused'
		self.player_iface.Pause()

	def next(self):
  		print('Player: next')
  		self.player_iface.Next()

	def prev(self):
  		print('Player: prev')
		self.player_iface.Previous()

	def setVolume(self, value):
  		if value not in range(0, 128):
			print('Possible Values: 0-127')
			return True
		print('Player: setVolume', value)
		self.volume = value
		self.transport_prop_iface.Set(
			'org.bluez.MediaTransport1',
			'Volume',
			dbus.UInt16(value))

	def volumeUp(self, step):
  		print('Player: volumeUp', step)
		self.setVolume(self.volume + step)

	def volumeDown(self, step):
  		print('Player: volumeDown', step)
  		self.setVolume(self.volume - step)

	def stop(self):
  		self.player_iface = None
		self.transport_prop_iface = None
		# etc
		return True
