'''
Created on Apr 5, 2010

@author: JMS
'''
# This is a fairly large file, so I've cut out a lot of the extra stuff
# that isn't neccessary for this example. Image loading/parsing, gps, etc.

import sys
import gtk
import gobject
try:
    import hildon
    has_hildon = True
except ImportError:
    print "No hildon module"
    has_hildon = False
import threading

try:
    import location
    has_location = True
except ImportError:
    print "No location module"
    has_location = False

# My custom data manager module
from BeltConnection import *

# This is ESSENTIAL if you are using multi-threading in a GTK app.  There are
# cleaner ways to do the same using gobject, but I'm using the brute force for
# the sake of sanity
gtk.gdk.threads_init()

# The overall UI form class
class HapticGuideUI:
 # A thread lock, in case needed
 lock = threading.Lock()
 # A frequency of the loop call (in milliseconds)
 TIMEOUT = 500

 def on_window_destroy(self, widget, data=None):
   self.belt.disconnect()
   gtk.main_quit()

 def on_window_delete(self, widget, data=None):
   self.belt.disconnect()
   gtk.main_quit()
   return False

 def on_connect_click(self, widget, data=None):
   self.labelDebugData.set_text("BT Connecting...")
   if self.belt.isConnected == False:
     #self.belt.connect()
     gobject.idle_add(self.belt.connect)
     
     
 def on_GpsConnect_click(self, widget, data=None): 
   self.labelDebugData.set_text("GPS Connecting...") 
   gobject.idle_add(self.start_location, self.control)

 def loop(self):
   # Get latest heading update from belt manager and display update if different from prev
   self.sensor1 = self.belt.sensors[0]
   self.sensor2 = self.belt.sensors[1]
   
   self.sensor1Data.set_text('%d' %(self.sensor1))  
   self.sensor2Data.set_text('%d' %(self.sensor2))
   self.labelCounterData.set_text('%d' %(self.counter))
   self.labelDebugData.set_text(self.belt.status)
   
   self.counter+=1
   return True

 def __init__(self):
<<<<<<< HEAD
   self.app = hildon.Program.get_instance()    
   gtk.set_application_name("C3 Prototype v0.2")
=======
   try:
       self.app = hildon.Program.get_instance()    
   except:
       self.app = hildon.Program()

   try:
       gtk.set_application_name("C3 Prototype v0.1")
   except:
       pass
>>>>>>> e55b4e2c9490a555dd4bcf1e62c03d6962d97411

   # This is the brilliant GTK+ Glade builder that lets me keep the entire UI
   # code in a .glade (xml) file to be loaded dynamically.
   builder = gtk.Builder()
   builder.add_from_file("sensor.glade") 

   # Get variables to each of the ui widgets we will need to work with
   self.window = builder.get_object("windowMain")
   self.sensor1Data = builder.get_object("labelSensor1Data")
   self.sensor2Data = builder.get_object("labelSensor2Data")
   self.labelCounterData = builder.get_object("labelCounterData")
   self.labelDebugData = builder.get_object("labelDebugData")
   self.labelLatData = builder.get_object("labelLatData")
   self.labelLonData = builder.get_object("labelLonData")
   self.labelDatetime = builder.get_object("labelDatetime")

   # Create the belt object to handle data communication
   self.belt = BeltConnection()

   # Initialize tracking variables
   self.sensor1 = 0
   self.sensor2 = 0
   
   self.counter = 0

   # Connect signals exposed in the glade file to local functions
   signals = { "on_windowMain_destroy_event" : self.on_window_destroy,
               "on_windowMain_delete_event" : self.on_window_delete, 
               "on_buttonBtConnect_clicked" : self.on_connect_click,
               "on_buttonGpsConnect_clicked" : self.on_GpsConnect_click
               }
   builder.connect_signals(signals)
   
   if has_location:
       self.control = location.GPSDControl.get_default()
       
       self.device = location.GPSDevice()
       self.control.set_properties(preferred_method=location.METHOD_USER_SELECTED,
                              preferred_interval=location.INTERVAL_DEFAULT)
        
       self.control.connect("error-verbose", self.on_error, self)
       self.device.connect("changed", self.on_changed, self.control)
       self.control.connect("gpsd-stopped", self.on_stop, self)
   


 def on_error(self, control, error, data):
    print "location error: %d... quitting" % error
    self.labelDebugData.set_text("location error: %d... quitting" % error)
    self.belt.disconnect()
    gtk.main_quit()

 def on_changed(self, device, data):
    if not device:
        return
    if device.fix:
        if device.fix[1] & location.GPS_DEVICE_LATLONG_SET:
            print "lat = %f, long = %f" % device.fix[4:6]
            print device.fix
            self.labelLatData.set_text("%f" % device.fix[4])
            self.labelLonData.set_text("%f" % device.fix[5])
            self.labelDatetime.set_text("%s" % device.fix[2])

 def on_stop(self,control, data):
    print "quitting"
    self.labelDebugData.set_text("quitting..")
    self.belt.disconnect()
    gtk.main_quit()

 def start_location(self, data):
    data.start()
    return False

  

 def show(self):
   self.window.show_all()
   # Add a recurring timeout call so we can continuously update headingsq
   gobject.timeout_add(self.TIMEOUT, self.loop)

if __name__ == "__main__":
 # Show the UI window
 ui = HapticGuideUI()
 ui.show()

 # The threads_enter() and threads_leave() calls are ESSENTIAL for apps with
 # multi-threaded intereaction
 gtk.gdk.threads_enter()
 gtk.main()
 gtk.gdk.threads_leave()