#!/usr/bin/env python

import json
import requests
import sys
import sqlite3
import time
import logging
import logging.handlers
from datetime import datetime
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish


# logging opzetten

# Deafults
LOG_FILENAME = "/tmp/openweather-script.log"
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

logger.info("openweather-script started")

while True:
	logger.info("read weather")
	
	#openweathermap api gebruien en info opvragen in JSON-formaat
	try:    
	    u = "http://api.openweathermap.org/data/2.5/weather?q=Schoten,be&units=metric&APPID=413426c26940f65e16f4a6097aa095d6"
	    r = requests.get(u)
	    j = json.loads(r.text)
	except:
	    sys.stderr.write("Couldn't load current conditions\n")
	
	logger.info("tijd bepalen")
	logger.info(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	#print (datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	#database openen en update uitvoeren op tabellen
	conn = sqlite3.connect('/home/bartje/Sqlite/Weather.db')
	c = conn.cursor()
	
	c.execute("UPDATE main SET temp = ?, humidity = ?, pressure = ?, temp_min = ?, temp_max = ? where id= '1'", (j['main']['temp'],j['main']['humidity'],j['main']['pressure'],j['main']['temp_min'],j['main']['temp_max']))
	c.execute("UPDATE sys SET country = ?, sunrise = ?, sunset = ? where id= '1'", (j['sys']['country'],j['sys']['sunrise'],j['sys']['sunset']))
	c.execute("UPDATE weather SET 'id_' = ?, main = ?, description = ?, icon = ? where id= '1'", (j['weather'][0]['id'],j['weather'][0]['main'],j['weather'][0]['description'],j['weather'][0]['icon']))
	##c.execute("UPDATE wind SET speed = ?, deg = ? where id= '1'", (j['wind']['speed'],j['wind']['deg']))
	#c.execute("UPDATE rain SET '3h' = ? where id= '1'", (j['rain']['3h'],))  #bestaat niet voor Schoten
	c.execute("UPDATE clouds SET 'all' = ? where id= '1'", (j['clouds']['all'],))
	#c.execute("UPDATE status SET 'time' = ? where id='1'", (datetime.now()))
	
	conn.commit()
	conn.close()
	
	##client = mqtt.Client()
	#client.connect("10.0.0.16",1883,60)
	##client.connect("10.0.0.16")
	#client.publish("test",j['wind']['speed'],qos=2, retain=True)
	host = "woezel.local"
	#logger.info(j)
	for key1,val1 in j.items():
		if key1 in ["wind", "main", "clouds","snow","sys","weather"]:  #probleem is dat weahter een list geeft
			if isinstance(val1, list):  # het probleem oplossen dat weather als een list is gemaakt
				val1 = val1[0]
			
			for key2,val2 in val1.items():
				#logger.info(key2)
				#logger.info(val2)
				topic = "weather/now/" + key1 + "/"+ key2
				#logger.info(topic)
				##client.publish(topic,val2, qos=0)
				publish.single(topic, val2, qos=2, hostname=host)
				
		
	##client.disconnect
	

	#aantal seconden wachten tot volgende keer dat de loop wordt doorlopen
	time.sleep(60)
