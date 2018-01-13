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
from lxml import etree
#from io import StringIO
#import urllib


token_max = 15
token = token_max
sleeptime = 60
host = "woezel.local"
topic_now = "weather/now"
topic_forecast = "weather/forecast"

#wunderground_key =  e18dc0713576db3b

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

# # Replace stdout with logging to file at INFO level
# sys.stdout = MyLogger(logger, logging.INFO)
# # Replace stderr with logging to file at ERROR level
# sys.stderr = MyLogger(logger, logging.ERROR)

logger.info("openweather-script started")


while True:
	logger.info("read weather")
	
	#openweathermap api gebruien en info opvragen in JSON-formaat en XML formaat
	
		
	#Current Weater
	try:    
		u = "http://api.openweathermap.org/data/2.5/weather?q=Schoten,be&units=metric&APPID=413426c26940f65e16f4a6097aa095d6&mode"
		r = requests.get(u)
		data = json.loads(r.text)
		u = "http://api.openweathermap.org/data/2.5/weather?q=Schoten,be&units=metric&APPID=413426c26940f65e16f4a6097aa095d6&mode=xml&lang=nl"
		data_xml=etree.parse(u)
		
		
				
	except:
	    sys.stderr.write("Couldn't load current conditions\n")
	else:
		#j_now anders organiseren tot wat ik wil
		
		empty_data = {'wind':{'deg':-1,'speed':0},'clouds':{'all':0},'rain':{'3h':0},'snow':{'3h':0}}
				
		for k in empty_data.keys():
			if not(k in data):
				data[k] = empty_data[k]
		
		data['weather']=data['weather'][0]
		data['rain']['rain_3h'] = data['rain'].pop('3h')
		data['rain']['snow_3h'] = data['snow'].pop('3h')
		data['wind']['wind_speed'] = data['wind'].pop('speed')
		data['wind']['wind_deg'] = data['wind'].pop('deg')
		data['clouds']['clouds'] = data['clouds'].pop('all')
		data['weather']['weather_id'] = data['weather'].pop('id')
		
		#in main, steken we ook de tijd, sunrise en sunset mee als data
		data['main']['time'] = data['dt']
		data['main']['sunrise'] = data['sys']['sunrise']
		data['main']['sunset'] = data['sys']['sunset']
		
		#overtollige data verwijderen
		data_to_keep = ['main','wind','weather','clouds','rain','snow']
		
		j_now = {}
		for k in data_to_keep:
			for i in data[k]:	
				j_now[i]=data[k][i]
				
		j_now['clouds_name']=data_xml.find('clouds').attrib['name']
		#j_now['wind_deg_name']=data_xml.find('wind/direction').attrib['name']
		j_now['wind_deg_code']=data_xml.find('wind/direction').attrib['code']
		
		# vertaal de windrichting naar het Nederlands
		str = j_now['wind_deg_code']
		str = str.replace("N","noord")
		str = str.replace("S","zuid")
		str = str.replace("E","oost")
		str = str.replace("W","west")
		j_now['wind_deg_name'] = str
		
		j_now['clouds_speed_name']=data_xml.find('wind/speed').attrib['name']
		j_now['weather_value']=data_xml.find('weather').attrib['value']
		
		
		publish.single(topic_now, json.dumps(j_now), qos=2, hostname=host, retain=True)
	
	#Forecast 5day every 3hours
	if token >= token_max:
		try:    
		    u = "http://api.openweathermap.org/data/2.5/forecast?q=Schoten,be&units=metric&APPID=413426c26940f65e16f4a6097aa095d6&lang=nl"
		    r = requests.get(u)
		    data = json.loads(r.text)
		    #u = "http://api.openweathermap.org/data/2.5/forecast?q=Schoten,be&units=metric&APPID=413426c26940f65e16f4a6097aa095d6&mode=xml&lang=nl"
			#data_xml=etree.parse(u)
		except:
		    sys.stderr.write("Couldn't load current conditions\n")	
		else:
			# op eenzelfde manier inrichten als de j_now
			#data_to_keep_forecast = ['list']
			#j_forecast = {}
			#for k in data_to_keep_forecast:
			#	for i in data[k]:	
			#		j_now[i]=data[k][i]
			
			#elke item in de list moet minstens volgende data hebben
			empty_data = {'wind':{'deg':-1,'speed':0},'clouds':{'all':0},'rain':{'3h':0},'snow':{'3h':0}}
			data_to_keep = ['main','wind','weather','clouds','rain','snow']
			
			#nog te checken of dit klopt... schijnt te kloppen (eerst deel toch)
			#print(data['list'])
			#elk item in de list afgaan, en hiermee het zelfde doen als de data_now
			
			j_forecast = {}
			j_forecast['list']= []
			for l in data['list']:	
				empty_data = {'wind':{'deg':-1,'speed':0},'clouds':{'all':0},'rain':{'3h':0},'snow':{'3h':0}}
				#print(l)
				for k in empty_data.keys():
					if not(k in l):				#check of de key bestaat
						l[k] = empty_data[k]
					if l[k] == {}:		#key bestaat misschien wel, maar is leeg
						l[k] = empty_data[k]
				l['weather']=l['weather'][0]
				l['rain']['rain_3h'] = l['rain'].pop('3h')
				l['snow']['snow_3h'] = l['snow'].pop('3h')
				l['wind']['wind_speed'] = l['wind'].pop('speed')
				l['wind']['wind_deg'] = l['wind'].pop('deg')
				l['clouds']['clouds'] = l['clouds'].pop('all')
				l['weather']['weather_id'] = l['weather'].pop('id')
				
				
				#in main, steken we ook de tijd, sunrise en sunset mee als data
				l['main']['time'] = l['dt']
				#l['main']['sunrise'] = l['sys']['sunrise']
				#l['main']['sunset'] = l['sys']['sunset']
				#print(i)
				#j_forecast['list'][i] = {}
				#for k in data_to_keep:
				#	for j in l[k]:	
				#		j_forecast['list'][i][j]=l[k][j]
			
				j_forecast_temp = {}
				for k in data_to_keep:
					for i in l[k]:	
						j_forecast_temp[i]=l[k][i]
				
				j_forecast['list'].append(j_forecast_temp)
				#print(j_forecast['list'][i])

			#for k in empty_data.keys():
			#	for l in data['list']:
			#		#print(l)
			#		if not(k in l):  
			#			l[k] = empty_data[k]
			#			#print(l)
			#print(j_forecast)
			publish.single(topic_forecast, json.dumps(j_forecast), qos=2, hostname=host, retain=True)
			token = 0
	else:
		token +=1
	
	
		time.sleep(sleeptime)
	
	# connectie met DB --> moet in ander stuk gestoken worden
	
	
	
	
	
	
	
	
	
	
