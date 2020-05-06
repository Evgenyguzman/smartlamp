import threading, time

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

	def handleMotion(self, message):
		#handling logic
		print("toaster gets motion: " + message + ", it doesn't know what to do")

	def handleSmth(self, message):
		#handling logic
		print("toaster gets smth: " + message)

	def __init__(self, broker):
		Module.__init__(self, broker)
		self.subscribe("motion", self.handleMotion)
		self.subscribe("leviy-topic", self.handleSmth)
		#your init
	
	def run(self):
		#your runtime logic, remove next loop
		time.sleep(3)
		i = 1
		while True:
			self.publish("motion", "opa opa " + str(i))
			i = i + 1
			time.sleep(0.1)

class Player(Module):

	def handleMotion(self, message):
		#handling logic
		action = "default"
		if message == "middle finger up":
			action = "it pauses"
		if message == "kukish":
			action = "it shuts down"
		print("player gets motion: " + message + ", " + action)

	def __init__(self, broker):
		Module.__init__(self, broker)
		self.subscribe("motion", self.handleMotion)
		#your init
	
	def run(self):
		#your runtime logic, remove next loop
		time.sleep(3)
		i = 1
		while True:
			self.publish("motion", "cha cha cha " + str(i))
			i = i + 1
			time.sleep(0.1)


class MotionCapturer(Module):

	def __init__(self, broker):
		Module.__init__(self, broker)
		#your init
	
	def run(self):
		#your runtime logic, remove next loop
		self.publish("motion", "middle finger up")
		time.sleep(0.1)
		self.publish("motion", "kukish")
		time.sleep(0.1)
		self.publish("leviy-topic", "ladno pacani ya pognal ne skuchaite")


broker = MessageBroker()

capturer = MotionCapturer(broker)
player = Player(broker)
toaster = Toaster(broker)

player.start()
toaster.start()
capturer.start()
	
