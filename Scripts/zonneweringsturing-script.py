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

# logging opzetten

# Deafults
LOG_FILENAME = "/tmp/zonneweringsturing-script.log"
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



logger.info("zonneweringsturing-script started")

#GPIO instellen
GPIO.setmode(GPIO.BCM)
GPIO.setup(8, GPIO.OUT)  #Output 1 op het bordje
GPIO.setup(11, GPIO.OUT) #Output 2 op het bordje

GPIO.output(11, True)
logger.info("hoog")
time.sleep(1)
GPIO.output(11, False)
logger.info("laag")
GPIO.cleanup()

#code komen, hieronder is nog de code van zonneweringstatus

#code die checkt of de zon schijnt en bepaalt of de zonnewering moet naar boven moet of naar beneden


'''
#database openen en ingestelde waarden opzoeken

def tobe_position	#wat is de ideale positie van de zonnewering  TRUE --> zonnewering gesloten; FALSE --> zonnewering open
	logger.info("start uitrekenen wat ideale positie is")
	
	conn = sqlite3.connect('/home/bartje/Sqlite/Weather.db')
	c = conn.cursor()
		
	for row in c.execute("SELECT temp, temp_max FROM main WHERE id=1"):
		global temp, temp_max
		temp = row[0]
		temp_max = row[1]
		
		
	for row in c.execute("SELECT id_, main FROM weather WHERE id=1"):
		global weather_id, weather_main
		weather_id = row[0]
		weather_main = row[1]
		
	for row in c.execute("SELECT speed FROM wind WHERE id=1"):
		global wind_speed
		wind_speed = row[0]

# enkel functies bepalen

def setglobalvar():
	global inbeweging, activatietijd
	inbeweging = False
	activatietijd = 20
	
	
def bediening_op(channel):
	#print('naar boven')
	logger.info("bediening_op")
	global status
	logger.info("status voor commando is " + str(status))
	
	global inbeweging
	if inbeweging:  #gordijn is al aan het bewegen, het commando dat nu volgt is een stopcommando
		inbeweging = False
		
	else:			#gordijn beweegt nog niet, dit is het eerste commando
		
		#print status
		inbeweging = True	#de controller kent de stand van de gordijn ook niet, dus voor hem is de gordijn nu in beweging
		tijdcommando = time.time()
		conn = sqlite3.connect('/home/witje/Sqlite/Woning.db')
		c = conn.cursor()
		
		while inbeweging and tijdcommando + activatietijd > time.time():
			if status <> 0: 	# gordijn is niet open en kan dus naar boven gaan			
				#print time.time()
				time.sleep ((activatietijd-3)/10)
				#print time.time()
				if inbeweging and status > 0:
					status = status - 10
					if status < 0:
						status = 0
					#print status #schrijf de status weg naar de database
					c.execute("UPDATE zonnewering SET 'status' = ? where id= '1'", (status,))
					conn.commit()
		conn.close()
	
	logger.info("status na commando is " + str(status))

    
def bediening_neer(channel):
	#print('naar beneden')
	logger.info("bediening_neer")
	global status
	logger.info("status voor commando is " + str(status))

	
	global inbeweging
	if inbeweging:  #gordijn is al aan het bewegen, het commando dat nu volgt is een stopcommando
		inbeweging = False
		
	else:			#gordijn beweegt nog niet, dit is het eerste commando
		#print status
		inbeweging = True	#de controller kent de stand van de gordijn ook niet, dus voor hem is de gordijn nu in beweging
		tijdcommando = time.time()
		conn = sqlite3.connect('/home/witje/Sqlite/Woning.db')
		c = conn.cursor()
		
		while inbeweging and tijdcommando + activatietijd > time.time():
			if status <> 100: 	# gordijn is niet toe en kan dus naar beneden gaan			
				#print time.time()
				time.sleep ((activatietijd-3)/10)
				#print time.time()
				if inbeweging and status < 100:
					status = status + 10
					if status > 100:
						status = 100
					#print status #schrijf de status weg naar de database
					c.execute("UPDATE zonnewering SET 'status' = ? where id= '1'", (status,))
					conn.commit()
		conn.close()
	
	logger.info("status na commando is " + str(status))



'''

#while True:
#	ik = 0
		
#conn.commit()
#conn.close()
#time.sleep(10)