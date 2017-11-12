#!/usr/bin/env python

import os.path
import json
import requests
import sys
import sqlite3
import time
import logging
import logging.handlers
import RPi.GPIO as GPIO
import paho.mqtt.publish as publish 
import _thread



# logging opzetten

# Deafults
LOG_FILENAME = "/tmp/zonneweringstatus-script.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

needRoll = os.path.isfile(LOG_FILENAME)

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, backupCount=3)
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

if needRoll:    
###    # Add timestamp
###    #logger.info('\n---------\nLog closed on %s.\n---------\n' % time.asctime())
###
###    # Roll over on application start
    logger.handlers[0].doRollover()



logger.info("zonneweringstatus-script started")

#GPIO instellen
GPIO.setmode(GPIO.BCM)
# met pull_up weerstand
#GPIO.setup(4, GPIO.IN, pull_up_down = GPIO.PUD_UP)  #input 1 op het bordje
#GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_UP) #input 2 op het bordje

# met pull_down weerstand
GPIO.setup(4, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)  #input 1 op het bordje
GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #input 2 op het bordje



#database openen en ingestelde waarden opzoeken
conn = sqlite3.connect('/home/bartje/Sqlite/Woning.db')
c = conn.cursor()
	
for row in c.execute("SELECT status, last_close_command, last_open_command FROM zonnewering WHERE id=1"):
	global status, last_close_command, last_open_command
	status = row[0]  #0 is open 100 is volledig toe
	last_close_command = row[1]
	last_open_command = row[2]

# enkel functies bepalen

def setglobalvar():
	global inbeweging, activatietijd, crosstalk , host, topic_move, topic_status
	inbeweging = False
	crosstalk = False
	activatietijd = 28
	host = "woezel.local"
	topic_move = "home/zonnewering/commando"  #no global
	topic_status = "home/zonnewering/status"  #no global
	#logger.info("setglobavar is done")
	
#def bediening_op(channel):
def bediening_op():
	logger.info("bediening_neer")
	publish.single(topic_move, "up", qos=2, hostname=host)
	
	#via crosstalk zien of er pas een commando gegeven is, indien zo, stop de code)
	global crosstalk
	##publish.single(topic_move, "crosstalk =" + str(crosstalk), qos=2, hostname=host)
	if crosstalk:
		logger.info("bediening_op - crosstalk detected")
		return 1
	
	#crosstalk op true zetten om ander ingange te blokkeren	voor 100ms
	crosstalk = True
	time.sleep(0.1)
	crosstalk = False
	
	global status
	#logger.info("status voor commando is " + str(status))
	
	global inbeweging
	#logger.info("in beweging is " + str(inbeweging)) #probsolv
	if inbeweging:  #gordijn is al aan het bewegen, het commando dat nu volgt is een stopcommando
		inbeweging = False
		logger.info("beweging gestopt door 2de keer te drukken")
		
	else:			#gordijn beweegt nog niet, dit is het eerste commando
		inbeweging = True	#de controller kent de stand van de gordijn ook niet, dus voor hem is de gordijn nu in beweging
		logger.info("beweging ingezet: " + str(inbeweging))
		tijdcommando = time.time()
		
		conn = sqlite3.connect('/home/bartje/Sqlite/Woning.db')
		c = conn.cursor()
		
		while inbeweging and tijdcommando + activatietijd > time.time():
			if status != 0: 	# gordijn is niet open en kan dus naar boven gaan			
				#print time.time()
				time.sleep ((activatietijd-8)/10)
				#print time.time()
				if inbeweging and status > 0:
					status = status - 10
					if status < 0:
						status = 0
					#print status #schrijf de status weg naar de database
					logger.info("status moving:  " + str(status)) #probsolv
					c.execute("UPDATE zonnewering SET 'status' = ? where id= '1'", (status,))
					conn.commit()
					publish.single(topic_status, status, qos=2, hostname=host)
		inbeweging = False
		logger.info("beweging gestopt") #probsolv
		#logger.info("na uitvoering van de bediening is de beweging " + str(inbeweging)) #probsolv
		
		conn.close()
	
	logger.info("status na commando is " + str(status))


#def bediening_neer(channel):   
def bediening_neer():
	logger.info("bediening_neer")
	publish.single(topic_move, "down", qos=2, hostname=host)
	
	#via crosstalk zien of er pas een commando gegeven is, indien zo, stop de code)
	global crosstalk
	if crosstalk:
		logger.info("bediening_neer - crosstalk detected")
		return 1
	
	#crosstalk op true zetten om ander ingange te blokkeren	voor 100ms
	crosstalk = True
	time.sleep(0.1)
	crosstalk = False
	
	global status
	#logger.info("status voor commando is " + str(status))
    
	global inbeweging
	#logger.info("in beweging is " + str(inbeweging)) #probsolv
	if inbeweging:  #gordijn is al aan het bewegen, het commando dat nu volgt is een stopcommando
		inbeweging = False
		logger.info("beweging gestopt door 2de keer te drukken")
		
	else:			#gordijn beweegt nog niet, dit is het eerste commando
		#print status
		inbeweging = True	#de controller kent de stand van de gordijn ook niet, dus voor hem is de gordijn nu in beweging
		logger.info("beweging ingezet: " + str(inbeweging))
		tijdcommando = time.time()
		conn = sqlite3.connect('/home/bartje/Sqlite/Woning.db')
		c = conn.cursor()
		
		while inbeweging and tijdcommando + activatietijd > time.time():
			if status != 100: 	# gordijn is niet toe en kan dus naar beneden gaan			
				#print time.time()
				time.sleep ((activatietijd-8)/10)
				#print time.time()
				if inbeweging and status < 100:
					status = status + 10
					if status > 100:
						status = 100
					#print status #schrijf de status weg naar de database
					logger.info("status moving:  " + str(status)) #probsolv
					c.execute("UPDATE zonnewering SET 'status' = ? where id= '1'", (status,))
					conn.commit()
					publish.single(topic_status, status, qos=2, hostname=host)
		
		inbeweging = False
		logger.info("beweging gestopt") #probsolv

		conn.close()
	
	logger.info("status na commando is " + str(status))



#functie laten starten in aparte tread (callback) bij een rising flank.  de bouncetime is een filter om dender tegen te gaan 300ms)
setglobalvar()
#met pull-up  en dus wachten op een falling flank
#GPIO.add_event_detect(4, GPIO.FALLING, callback=bediening_op, bouncetime=900) 		#input 1 op het bordje
#GPIO.add_event_detect(17, GPIO.FALLING, callback=bediening_neer, bouncetime=900) 	#input 2 op het bordje

#met pull-down  en dus wachten op een rising flank
#GPIO.add_event_detect(4, GPIO.RISING, callback=_thread.start_new_thread(bediening_op, ()), bouncetime=200) 		#input 1 op het bordje
#GPIO.add_event_detect(17, GPIO.RISING, callback=_thread.start_new_thread(bediening_neer, ()), bouncetime=200) 	#input 2 op het bordje

GPIO.add_event_detect(4, GPIO.RISING, bouncetime=500)  # add rising edge detection on a channel
GPIO.add_event_detect(17, GPIO.RISING, bouncetime=500)  # add rising edge detection on a channel


while True:
	if GPIO.event_detected(4):
		_thread.start_new_thread(bediening_op, ())
	if GPIO.event_detected(17):
		_thread.start_new_thread(bediening_neer, ())

	ik = 0
		
#conn.commit()
#conn.close()
#time.sleep(10)