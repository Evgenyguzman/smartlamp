#!/usr/bin/env python

# Dependencies:
# sudo apt-get install -y python-gobject
# sudo apt-get install -y python-smbus

import time
import sys
import dbus
import dbus.service
import dbus.mainloop.glib
#import gobject
from gi.repository import GObject as gobject
import logging
#from optparse import OptionParser
import traceback
#from lcd import Lcd

SERVICE_NAME = "org.bluez"
AGENT_IFACE = SERVICE_NAME + '.Agent1'
ADAPTER_IFACE = SERVICE_NAME + ".Adapter1"
DEVICE_IFACE = SERVICE_NAME + ".Device1"
PLAYER_IFACE = SERVICE_NAME + '.MediaPlayer1'
TRANSPORT_IFACE = SERVICE_NAME + '.MediaTransport1'

LOG_LEVEL = logging.INFO
LOG_FILE = "/var/log/syslog"
#LOG_LEVEL = logging.DEBUG
#LOG_FILE = "/dev/stdout"
#LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"

"""Utility functions from bluezutils.py"""
def getManagedObjects():
    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
    return manager.GetManagedObjects()

def findAdapter():
    objects = getManagedObjects();
    bus = dbus.SystemBus()
    for path, ifaces in objects.items():
        adapter = ifaces.get(ADAPTER_IFACE)
        if adapter is None:
            continue
        obj = bus.get_object(SERVICE_NAME, path)
        return dbus.Interface(obj, ADAPTER_IFACE)
    raise Exception("Bluetooth adapter not found")

class BluePlayer(dbus.service.Object):
    AGENT_PATH = "/blueplayer/agent"
#    CAPABILITY = "DisplayOnly"
    CAPABILITY = "NoInputNoOutput"

    #pin_code = None

    lcd = None
    bus = None
    adapter = None
    device = None
    deviceAlias = None
    player = None
    transport = None
    connected = None
    state = None
    status = None
    discoverable = None
    track = None
    mainloop = None
    volume = None

    def __init__(self):
        print("Starting Service")

        try:
            #self.registerAgent()
            self.startPairing()
        except Exception as ex:
            pass
        
        """self.pin_code = pin_code
        logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)
        logging.info("Starting BlueAgent with PIN [{}]".format(self.pin_code))"""

        
    def start(self):
        print("Initialize gobject,and find any current media players")
        gobject.threads_init()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        self.bus = dbus.SystemBus()
        dbus.service.Object.__init__(self, dbus.SystemBus(), BluePlayer.AGENT_PATH)

        self.bus.add_signal_receiver(self.playerHandler,
                bus_name="org.bluez",
                dbus_interface="org.freedesktop.DBus.Properties",
                signal_name="PropertiesChanged",
                path_keyword="path")

        self.registerAgent()

        adapter_path = findAdapter().object_path
        self.bus.add_signal_receiver(self.adapterHandler,
                bus_name = "org.bluez",
                path = adapter_path,
                dbus_interface = "org.freedesktop.DBus.Properties",
                signal_name = "PropertiesChanged",
                path_keyword = "path")


        self.findPlayer()
        self.updateDisplay()

        """Start the BluePlayer by running the gobject mainloop()"""
        self.mainloop = gobject.MainLoop()
        self.mainloop.run()

    def findPlayer(self):
        print("Find any current media players and associated device")
        manager = dbus.Interface(self.bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()

        player_path = None
        transport_path = None
        for path, interfaces in objects.items():
            for iface in interfaces:
                print(iface)
            if PLAYER_IFACE in interfaces:
                player_path = path
            if TRANSPORT_IFACE in interfaces:
                transport_path = path
            if "org.bluez.Media1" in interfaces:
                #player_path = path
                pass
            if "org.bluez.Media1" in interfaces:
                #transport_path = path
                pass

        if player_path:
            print("Found player on path [{}]".format(player_path))
            self.connected = True
            self.getPlayer(player_path)
            player_properties = self.player.GetAll(PLAYER_IFACE, dbus_interface="org.freedesktop.DBus.Properties")
            if "Status" in player_properties:
                self.status = player_properties["Status"]
            if "Track" in player_properties:
                self.track = player_properties["Track"]
        else:
            print("Could not find player")
            pass

        if transport_path:
            #logging.debug("Found transport on path [{}]".format(player_path))
            self.transport = self.bus.get_object("org.bluez", transport_path)
            #logging.debug("Transport [{}] has been set".format(transport_path))
            transport_properties = self.transport.GetAll(TRANSPORT_IFACE, dbus_interface="org.freedesktop.DBus.Properties")
            if "State" in transport_properties:
                self.state = transport_properties["State"]

    def getPlayer(self, path):
        print("Get a media player from a dbus path, and the associated device")
        self.player = self.bus.get_object("org.bluez", path)
        #logging.debug("Player [{}] has been set".format(path))
        device_path = self.player.Get("org.bluez.MediaPlayer1", "Device", dbus_interface="org.freedesktop.DBus.Properties")
        self.getDevice(device_path)

    def getDevice(self, path):
        """Get a device from a dbus path"""
        self.device = self.bus.get_object("org.bluez", path)
        self.deviceAlias = self.device.Get(DEVICE_IFACE, "Alias", dbus_interface="org.freedesktop.DBus.Properties")

    def playerHandler(self, interface, changed, invalidated, path):
        """Handle relevant property change signals"""
        #logging.debug("Interface [{}] changed [{}] on path [{}]".format(interface, changed, path))
        iface = interface[interface.rfind(".") + 1:]

        print(changed, iface)

        if iface == "Device1":
            if "Connected" in changed:
                self.connected = changed["Connected"]
        if iface == "MediaControl1":
            if "Connected" in changed:
                self.connected = changed["Connected"]
                if changed["Connected"]:
                    #logging.debug("MediaControl is connected [{}] and interface [{}]".format(path, iface))
                    self.findPlayer()
        elif iface == "MediaTransport1":
            if "State" in changed:
                #logging.debug("State has changed to [{}]".format(changed["State"]))
                self.state = (changed["State"])
            if "Connected" in changed:
                self.connected = changed["Connected"]
            if "Volume" in changed:
                self.volume = changed["Volume"]
        elif iface == "MediaPlayer1":
            if "Track" in changed:
                #logging.debug("Track has changed to [{}]".format(changed["Track"]))
                self.track = changed["Track"]
            if "Status" in changed:
                #logging.debug("Status has changed to [{}]".format(changed["Status"]))
                self.status = (changed["Status"])
    
        self.updateDisplay()

    def adapterHandler(self, interface, changed, invalidated, path):
        """Handle relevant property change signals"""
        if "Discoverable" in changed:
                #logging.debug("Adapter dicoverable is [{}]".format(self.discoverable))
                self.discoverable = changed["Discoverable"]
                self.updateDisplay()

    def updateDisplay(self):
        """Display the current status of the device on the LCD"""
        #logging.debug("Updating display for connected: [{}]; state: [{}]; status: [{}]; discoverable [{}]".format(self.connected, self.state, self.status, self.discoverable))
        if self.discoverable:
            self.wake()
            self.showDiscoverable()
        else:
            if self.connected:
                if self.state == "idle":
                    self.sleep()
                else:
                    self.wake()
                    if self.status == "paused":
                        self.showPaused()
                    else:
                        self.showTrack()
            else:
                self.sleep()

    def showDevice(self):
        """Display the device connection info on the LCD
        self.lcd.clear()
        self.lcd.writeLn("Connected to:", 0)
        self.lcd.writeLn(self.deviceAlias, 1)
        time.sleep(2)
        """
        print(self.deviceAlias)

    def showTrack(self):
        #print(self.track["Artist"])
        #print(self.track["Title"])
        pass

    def getTrack(self):
        return {
            "Artist": self.track["Artist"],
            "Title": self.track["Title"]
        }

    def showPaused(self):
        print("Device is paused")
        pass

    def showDiscoverable(self):
        print("Waiting to pair")
        pass


    def next(self):
        self.player.Next(dbus_interface=PLAYER_IFACE)

    def previous(self):
        self.player.Previous(dbus_interface=PLAYER_IFACE)

    def play(self):
        self.player.Play(dbus_interface=PLAYER_IFACE)

    def pause(self):
        self.player.Pause(dbus_interface=PLAYER_IFACE)

    def volumeUp(self):
        print("Volume Up")
        self.control.VolumeUp(dbus_interface=CONTROL_IFACE)
        self.transport.VolumeUp(dbus_interface=TRANSPORT_IFACE)

    def volumeDown(self):
        print("Volume Down")
        self.control.VolumeDown(dbus_interface=CONTROL_IFACE)
        self.transport.VolumeDown(dbus_interface=TRANSPORT_IFACE)

    def wake(self):
        pass

    def shutdown(self):
        if self.mainloop:
            self.mainloop.quit()

    def sleep(self):
        pass

    def getStatus(self):
        return self.status

    """Pairing agent methods"""
    @dbus.service.method(AGENT_IFACE, in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print("RequestPinCode (%s)" % (device))
        self.trustDevice(device)
        return "0000"

    @dbus.service.method(AGENT_IFACE, in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        """Always confirm"""
        #logging.debug("RequestConfirmation returns")
        self.trustDevice(device)
        return

    @dbus.service.method(AGENT_IFACE, in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        """Always authorize"""
        #logging.debug("Authorize service returns")
        return

    def trustDevice(self, path):
        """Set the device to trusted"""
        device_properties = dbus.Interface(self.bus.get_object(SERVICE_NAME, path), "org.freedesktop.DBus.Properties")
        device_properties.Set(DEVICE_IFACE, "Trusted", True)

    def registerAgent(self):
        print("Register BluePlayer as the default agent")
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object(SERVICE_NAME, "/org/bluez"), "org.bluez.AgentManager1")
        manager.RegisterAgent(BluePlayer.AGENT_PATH, BluePlayer.CAPABILITY)
        manager.RequestDefaultAgent(BluePlayer.AGENT_PATH)
        #logging.debug("Blueplayer is registered as a default agent")

    def startPairing(self):
        #logging.debug("Starting to pair")
        print("Make the adapter discoverable")
        bus = dbus.SystemBus()
        adapter_path = findAdapter().object_path
        adapter = dbus.Interface(bus.get_object(SERVICE_NAME, adapter_path), "org.freedesktop.DBus.Properties")
        adapter.Set(ADAPTER_IFACE, "Discoverable", True)
        print("BlueAgent is waiting to pair with device")
        logging.info("BlueAgent is waiting to pair with device")

"""
def navHandler(buttons):
    logging.debug("Handling navigation for [{}]".format(buttons))
    if buttons == Lcd.BUTTON_SELECT:
        player.startPairing()
    elif buttons == Lcd.BUTTON_LEFT:
        player.previous()
    elif buttons == Lcd.BUTTON_RIGHT:
        player.next()
    elif buttons == Lcd.BUTTON_UP:
        if player.getStatus() == "playing":
            player.pause()
        else:
            player.play()
"""

if __name__ == "__main__":
    #logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)
    #logging.info("Starting BluePlayer")

    #gobject.threads_init()
    #dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    #lcd = Lcd()
    #lcd.begin(16, 2, handler=navHandler)
    #lcd.backlight(Lcd.TEAL)
    #lcd.clear()
    #lcd.writeLn("Starting", 0)
    #lcd.writeLn("BluePlayer", 1)
    time.sleep(2)

    player = None
    try:
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        player = BluePlayer()
        player.startPairing()

        player.start()

        mainloop = gobject.MainLoop()
        mainloop.run()
        
        #player = BluePlayer()
        #player.start()
        #time.sleep(5)
        #time.sleep(5)
        #time.sleep(5)
    except KeyboardInterrupt as ex:
        #logging.info("BluePlayer cancelled by user")
        pass
    except Exception as ex:
        #logging.error("How embarrassing. The following error occurred {}".format(ex))
        traceback.print_exc()
    finally:
        player.shutdown()
