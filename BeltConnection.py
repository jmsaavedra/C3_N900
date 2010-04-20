import threading
from bluetooth import *

# Because the application is multi-threaded, this is keep it thread-safe
_bclock = threading.Lock()

# This class Manages all connection stuff
class BeltConnection:
 def __init__(self):
   # Variable declaration
   self.isConnected = False
   self.sensors = [0,0]
   self.counter = 0
   self.status = "" 

 def connect(self):
   # This is the prefix of the device name to match
   target_name = "FireFly-"
   target_address = None
   number_of_tries = 2

   # Loop a couple times in case the device/name isn't found the first time
   while target_address is None and number_of_tries > 0:
     number_of_tries = number_of_tries - 1

     # Discover bluetooth devices in the vicinity
     print "Searching for belt..."
     self.status = "Searching for belt... "
     nearby_devices = discover_devices()

     # Loop through each device and check its name for a prefix match
     for btaddr in nearby_devices:
       btname = lookup_name(btaddr)
       print " -Found device: %s (%s)" % (btname, btaddr)
       self.status = " -Found device: %s (%s)" % (btname, btaddr)
       if btname is not None and btname.startswith(target_name) == True:
         # Use the first device it finds that matches name
         print '    Found firefly.'
         self.status = "    Found FireFly"
         target_address = btaddr
         break

   if target_address is not None:
     # Begin the actual connection device using BT network socket communication
     self.sock = BluetoothSocket(RFCOMM)
     try: self.sock.connect((target_address, 1))
     except:
       print "Unable to connect to belt"
       self.status = "Unable to connect to belt"
       self.isConnected = False
     else:
       # if connection succeeded, create the multi-thread "receiver"
       # which will handle receiving data in the background automatically
       print "Connected to belt (%s)" % (target_address)
       self.status = "Connected to belt (%s)" % (target_address)
       self.isConnected = True
       self.receiver = __ReceiverThread__(self)
       self.receiver.start()
   else:
     print "Could not locate belt."
     self.status = "Could not locate belt."
     self.isConnected = False

# def sendHeading(self, newheading):
#   # If connected, send the heading byte (0-255) to the belt
#   if self.isConnected == True:
#     self.sock.send(newheading)
#
# def getCurrentHeading(self):
#   heading = 0
#   # Acquire a thread lock (for safety) and return the last received heading
#   _bclock.acquire()
#   try: heading = self.lastKnownHeading
#   finally: _bclock.release()
#   return heading

 def disconnect(self):
   # If connected, do the socket cleanup stuff
   if self.isConnected == True:
     self.sock.close()
     self.isConnected = False
     print "Disconnected from belt"
     self.status = "Disconnect from belt"

# This is a private class that uses threading to receive data from the belt
class __ReceiverThread__ (threading.Thread):
 def __init__(self, parent):
   self.parent = parent
   threading.Thread.__init__(self)

 def run(self):
   data = ""
   while self.parent.isConnected == True:
     # Wait indefinitely until a byte is received.  This is likely not the
     # best way to do this.  For production, it would be better to use the
     # 'select' module to get notification when data is ready.
     data = self.parent.sock.recv(1)

     # Verify received
     if data != "":
       # Convert the byte (0-255) to a heading (0-359) and update belt
       # manager with new heading within the thread lock
       value = ord(data)
       sensor = value/128
       if value >= 128:
           value -= 128
                                    
       _bclock.acquire()
       try: 
           self.parent.sensors[sensor] = value
       finally: _bclock.release()
     else:
       # If nothing was received, this usually means the socket closed from the
       # remote end, so notify that the belt is disconnected.
       print "Remote client disconnected"
       self.parent.status = "Remote client disconnected" 
       self.parent.disconnect()
