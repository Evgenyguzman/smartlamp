import threading

# Tcp
import time
import socket
import json

# TempHumi
import Adafruit_DHT

# APDS

from apds9960.const import *
from apds9960 import APDS9960
import RPi.GPIO as GPIO
import smbus

# Player
#from blueagent5 import *
from blueplayernew import *

#import time
import signal
#import dbus
#import dbus.service
#import dbus.mainloop.glib
#import gobject
#import logging
#from handler import Handler

# Led
import wiringpi




class MessageBroker:
    
    def __init__(self):
        self.subscribes = []
        
    def subscribe(self, subscriber, topic, callback):
        self.subscribes += [[subscriber, topic, callback]]
        
    def publish(self, topic, message):
        for subscribe in self.subscribes:
            if topic == subscribe[1]:
                subscribe[2](message)


class Module(threading.Thread):
    
    def __init__(self, messageBroker):
        self.broker = messageBroker
        super(Module, self).__init__()
        
    def subscribe(self, topic, callback):
        self.broker.subscribe(self, topic, callback)
        
    def publish(self, topic, message):
        self.broker.publish(topic, message)


class Toaster(Module):

    port = 8084

    temperature = 0
    humidity = 0

    led_red = 0
    led_green = 0
    led_blue = 0

    alarm_status = "off"
    alarm_time = "8:00"

    player_status = "pause"
    player_artist = "undefined"
    player_song = "undefined"

    conn = object()
    addr = object()

    # status may be notActive, active, alarming
    status = "active"

    def handleTemperature(self, message):
        self.temperature = message
    def handleHumidity(self, message):
        self.humidity = message
    
    def handleAlarmStatus(self, message):
        self.alarm_status = message
    def handleAlarmTime(self, message):
        self.alarm_time = message
    def handleAlarmimg(self, message):
        self.status = "alarming"
        self.publish("player", "play")
        self.publish("flickering", "on")

    def handleMotion(self, message):
        #print(message.decode())
        if self.status == "active":
            if message == "left":
                #print("left")
                self.publish("player", "previous")
            if message == "right":
                #print("right")
                self.publish("player", "next")

        if self.status == "alarming":
            self.publish("flickering", "off")
            self.publish("player", "pause")


    def send_answer(self, conn, status="200 OK", typ="text/plain; charset=utf-8", data=""):
        data = data.encode("utf-8")
        conn.send(b"HTTP/1.1 " + status.encode("utf-8") + b"\n")
        conn.send(b"Server: simplehttp\n")
        conn.send(b"Connection: close\n")
        conn.send(b"Content-Type: " + typ.encode("utf-8") + b"\n")
        conn.send(b"Content-Length: " + bytes(len(data)) + b"\n")
        conn.send(b"\n")
        conn.send(data)

    def parse(self, conn, addr):
        data = b""
    
        while not b"\n" in data:
            tmp = conn.recv(1024)
            if not tmp:
                break
            else:
                data += tmp
    
        if not data:
            return
        
        udata = data.decode("utf-8")
        udata = udata.split("\n", 1)[0]
        method, address, protocol = udata.split(" ", 2)

        address_params = address.split("/")
        address_params.pop(0)
        
        answer = {}
        if method == "GET":
            if address.find("player") != -1:
                print("player")
                """answer = {
                    
                }"""
                print(self.player.getTrack())
                if address.find("pause") != -1:
                    print("pause")
                    self.publish("player", "next")
        
            if address_params[0] == "led":
                print("set Led")
                if address_params[1] == "red":
                    print("Set Red Color " + address_params[2])
                    self.led_red = address_params[2]
                    self.publish("red_value", address_params[2])
                if address_params[1] == "green":
                    self.led_green = address_params[2]
                    self.publish("green_value", address_params[2])
                if address_params[1] == "blue":
                    self.led_blue = address_params[2]
                    self.publish("blue_value", address_params[2])
                    
            if address_params[0] == "all":
                answer = {
                    "temperature": self.temperature,
                    "humidity": self.humidity,
                    "led_red": self.led_red,
                    "led_green": self.led_green,
                    "led_blue": self.led_blue,
                    "alarm_status": self.alarm_status,
                    "alarm_time": self.alarm_time,
                    "player_status": self.player_status,
                    "player_artist": self.player_artist,
                    "player_song": self.player_song,
                    #"playerArtist": self.player.bluePlayer.track['Artist']
                }

        elif method == "POST":
            pass

        json_data = json.dumps(answer)
        self.send_answer(conn, typ="application/json; charset=utf-8", data=json_data)

    def __init__(self, broker):
        Module.__init__(self, broker)
        self.subscribe("motion", self.handleMotion)
        self.subscribe("temperature", self.handleTemperature)
        self.subscribe("humidity", self.handleHumidity)
        self.subscribe("alarming", self.handleAlarmimg)
	
    def run(self):
        
        sock = socket.socket()
        sock.bind( ("", self.port) )
        sock.listen(5)

        try:
            while 1:
                conn, addr = sock.accept()
                print("New connection from " + addr[0])
                print(self.temperature)
                try:
                    print(conn, addr)
                    self.parse(conn, addr)
                except:
                    self.send_answer(conn, "500 Internal Server Error", data="Error")
                finally:
                    conn.close()
        finally: sock.close()

class TempHumiSensor(Module):

    temperature = "0"
    humidity = "0"

    sensor = '22'
    pin = 4

    def __init__(self, broker):
        Module.__init__(self, broker)
	
    def run(self):
        
        sensor_args = {
            '11': Adafruit_DHT.DHT11,
            '22': Adafruit_DHT.DHT22,
            '2302': Adafruit_DHT.AM2302
        }
        sensor = sensor_args[self.sensor]

        while True:
            self.humidity, self.temperature = Adafruit_DHT.read_retry(sensor, self.pin)

            self.publish("temperature", str(self.temperature))
            self.publish("humidity", str(self.humidity))
            time.sleep(15)

class MotionCapturer(Module):

    motion = "none"

    dirs = {
        APDS9960_DIR_NONE: "none",
        APDS9960_DIR_LEFT: "left",
        APDS9960_DIR_RIGHT: "right",
        APDS9960_DIR_UP: "up",
        APDS9960_DIR_DOWN: "down",
        APDS9960_DIR_NEAR: "near",
        APDS9960_DIR_FAR: "far",
    }

    pin = 7

    def __init__(self, broker):
        Module.__init__(self, broker)
	
    def run(self):

        port = 1
        bus = smbus.SMBus(port)
        apds = APDS9960(bus)

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin , GPIO.IN)

        try:
            # Interrupt-Event hinzufuegen, steigende Flanke
            GPIO.add_event_detect(self.pin, GPIO.FALLING, callback = intH)

            apds.setProximityIntLowThreshold(150)

            print("Gesture Test")
            print("============")
            apds.enableGestureSensor()
            while True:
                time.sleep(0.5)
                if apds.isGestureAvailable():
                    motion = apds.readGesture()
                    self.motion = motion
                    self.publish("motion", self.dirs.get(motion, "unknown"))
                    print("Gesture={}".format(self.dirs.get(motion, "unknown")))
        finally:
            GPIO.cleanup()


def intH(channel):
    print("INTERRUPT")

class Alarm(Module):

    status = False

    alarm_time = "8:00"

    def handleStatus(self, message):
        self.status = message

    def handleTime(self, message):
        self.alarm_time = message
    
    def __init__(self, broker):
        Module.__init__(self, broker)
        self.subscribe("alarm_status", self.handleStatus)
        self.subscribe("alarm_time", self.handleTime)
	
    def run(self):
        while True:
            if self.status:
                now = time.strftime("%H:%M", time.localtime())
                if now == self.alarm_time:
                    self.publish("alarming", "on")
                    self.status = False
                time.sleep(1)
            else:
                time.sleep(30)

class Led(Module):

    r_pin = 33
    g_pin = 36
    b_pin = 37

    r_val = 0
    g_val = 0
    b_val = 0

    freq_val = None

    status = "off"
    flickering = False

    def handleRedValue(self, message):
        action = "default"
        self.r_val = message
        print("player gets motion: " + str(message) + ", " + action)
        self.changeValue("red")
    def handleGreenValue(self, message):
        #handling logic
        action = "default"
        self.g_val = message
        print("player gets motion: " + str(message) + ", " + action)
        self.changeValue("green")
    def handleBlueValue(self, message):
        #handling logic
        action = "default"
        self.b_val = message
        print("player gets motion: " + str(message) + ", " + action)
        self.changeValue("blue")

    def changeValue(self, color):

        if color == "red":
            wiringpi.pwmWrite(self.r_pin, self.r_val)
        if color == "green":
            wiringpi.pwmWrite(self.g_pin, self.g_val)
        if color == "blue":
            wiringpi.pwmWrite(self.b_pin, self.b_val)


    def __init__(self, broker):
        Module.__init__(self, broker)
        self.subscribe("red_value", self.handleRedValue)
        self.subscribe("green_value", self.handleGreenValue)
        self.subscribe("blue_value", self.handleBlueValue)
    
        wiringpi.wiringPiSetupPhys()
        wiringpi.pinMode(self.r_pin, 2)
        wiringpi.pinMode(self.g_pin, 2)
        wiringpi.pinMode(self.b_pin, 2)
	
    def run(self):
        print("Run Led Driver")
        while True:
            print(self.r_val, self.g_val, self.b_val)
            time.sleep(5)
            if self.flickering:
                pass
            
class Player(Module):

    bluePlayer = None
    blueAgent = None

    def handleAction(self, message):
        if message == "next":
            self.bluePlayer.next()
        elif message == "previous":
            self.bluePlayer.next()
        elif message == "pause":
            self.bluePlayer.pause()
        print("player gets motion: " + str(message))

    def __init__(self, broker):
        Module.__init__(self, broker)
        self.subscribe("player", self.handleAction)
        # self.subscribe("", self.value)

    def run(self):

        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        
        self.bluePlayer = BluePlayer()
        """try:
            self.bluePlayer.registerAgent()
        except Exception as ex1:
            #print(format(ex))
            pass
        self.bluePlayer.startPairing()
        """
        print("let's start")
        self.bluePlayer.start()

        mainloop = gobject.MainLoop()
        mainloop.run()

    def getTrack(self):
        return 1
        #return self.bluePlayer.getTrack()
    

        


#if __name__ == '__main__':
#    try:
        
#    except KeyboardInterrupt:
        

broker = MessageBroker()

led = Led(broker)
tempHumiSensor = TempHumiSensor(broker)
capturer = MotionCapturer(broker)
alarm = Alarm(broker)

time.sleep(2)

player = Player(broker)
player.start()

toaster = Toaster(broker)

led.start()
tempHumiSensor.start()
capturer.start()
alarm.start()

toaster.start()

