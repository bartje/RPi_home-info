import json
#import requests
import sys
import sqlite3
import time
import logging
import logging.handlers
#from datetime import datetime
#import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import RPi.GPIO as GPIO
import _thread


from variables import *

# logging opzetten

# Deafults
LOG_FILENAME = "/tmp/pulslogger.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
        def __init__(self, logger, level):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level

        def write(self, message):
                # Only log if there is a message (not just a new line)
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)

logger.info("pulslogger started")

#generiek functie om pulsen door te geven, variable is het type
#via een dict en het type de impulswaarde gaan bepalen
#publiceer via mqtt
def puls(meter):
	#meter = "gas"
	logger.info("puls binnengekomen")
	logger.info(meter)
	topic = "home/" + meter + "/verbruik"
	value = impulsgewicht[meter]
	publish.single(topic, value, qos=2, hostname=mqtthost)



#ingangen instellen
GPIO.setmode(GPIO.BCM)
#GPIO.setup(4, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)  #input 1 op het bordje
#GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #input 2 op het bordje
GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)  #input 3 op het bordje
GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #input 4 op het bordje

#GPIO.add_event_detect(4, GPIO.RISING, bouncetime=500)  # add rising edge detection on a channel
#GPIO.add_event_detect(17, GPIO.RISING, bouncetime=500)  # add rising edge detection on a channel
GPIO.add_event_detect(18, GPIO.RISING, bouncetime=500)  # add rising edge detection on a channel
GPIO.add_event_detect(27, GPIO.RISING, bouncetime=500)  # add rising edge detection on a channel

#voor eeuwig de volgende lus herhalen
while True:
	#if GPIO.event_detected(4):
	#	_thread.start_new_thread(bediening_op, ())
	#if GPIO.event_detected(17):
	#	_thread.start_new_thread(bediening_neer, ())
	if GPIO.event_detected(18):
		_thread.start_new_thread(puls, ("gas",))  	#gas zit op input 3
	if GPIO.event_detected(27):
		_thread.start_new_thread(puls, ("water",))	#water zit op input 4


