#!/usr/bin/env python

import os.path
import json
import requests
import sys
import sqlite3
import time
import logging
import logging.handlers
import paho.mqtt.client as mqtt
import ast
# logging opzetten


db_solar = "/home/bartje/Sqlite/Solar.db"
db_weather = "/home/bartje/Sqlite/Weather.db"

'''
Afhankelijk van het topic moeten er andere actie ondernomen worden

topic
power/solar/energy
weather/now/
'''




def on_connect(mqttclient, obj, flags, rc):
    if rc==0:
    	print("connection succeeded")
    	mqttclient.subscribe("#", 2)  #subscribe to all topics
    else:
    	print("connection problem")
    
    
	
def on_message(mqttclient, obj, msg):
    #afhankelijk van welke topic moeten er verschillende routines gestart worden
    #eerst de topic splitsen in zijn onderdelen ('/')
	topic = msg.topic.split('/')
    #if solar -->
	if topic[0]=="power" and topic[1]=="solar" and topic[2]=="energy":
		#doe vanalles
		data = json.loads(msg.payload.decode()) #--> dit is een Strdict
		#print(data.keys())
		#print(data.values())
		#het bericht zo aanpassen zodat 
    	
		conn = sqlite3.connect(db_solar)
		c = conn.cursor()
    	
    	##om van een dict een db te vullen
		columns = ', '.join(data.keys())
		placeholders = ', '.join('?' * len(data))
		sql = 'INSERT INTO data ({}) VALUES ({})'.format(columns, placeholders)
		c.execute(sql, tuple(data.values()))
		
		conn.commit()
		conn.close()
    
    #if weather, now -->
	if topic[0]=="weather" and topic[1]=="now":
    	#doe vanalles
		data = json.loads(msg.payload.decode()) #--> dit is een Strdict
		conn = sqlite3.connect(db_weather)
		c = conn.cursor()
		
		#print(data.keys())
		#print(data.values())
		
    	##om van een dict een db te vullen
		#columns = ', '.join(data.keys())
		#placeholders = ', '.join('?' * len(data))
		#sql = 'INSERT INTO data ({}) VALUES ({})'.format(columns, placeholders)
		#c.execute(sql, tuple(data.values()))
		
# 	c.execute("UPDATE main SET temp = ?, humidity = ?, pressure = ?, temp_min = ?, temp_max = ? where id= '1'", (j['main']['temp'],j['main']['humidity'],j['main']['pressure'],j['main']['temp_min'],j['main']['temp_max']))
# 	c.execute("UPDATE sys SET country = ?, sunrise = ?, sunset = ? where id= '1'", (j['sys']['country'],j['sys']['sunrise'],j['sys']['sunset']))
# 	c.execute("UPDATE weather SET 'id_' = ?, main = ?, description = ?, icon = ? where id= '1'", (j['weather'][0]['id'],j['weather'][0]['main'],j['weather'][0]['description'],j['weather'][0]['icon']))
# 	##c.execute("UPDATE wind SET speed = ?, deg = ? where id= '1'", (j['wind']['speed'],j['wind']['deg']))
# 	#c.execute("UPDATE rain SET '3h' = ? where id= '1'", (j['rain']['3h'],))  #bestaat niet voor Schoten
# 	c.execute("UPDATE clouds SET 'all' = ? where id= '1'", (j['clouds']['all'],))
# 	#c.execute("UPDATE status SET 'time' = ? where id='1'", (datetime.now()))

		
		
		
		conn.commit()
		conn.close()

    
    #if weather, forecast -->
	if topic[0]=="weather" and topic[1]=="forecast":
    	#doe vanalles  
		data = json.loads(msg.payload.decode()) #--> dit is een Strdict

def on_publish(mqttclient, obj, mid):
	print("mid: "+str(mid))

def on_subscribe(mqttclient, obj, mid, granted_qos):
    print("subscrided")
    #print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_log(mqttclient, obj, level, string):
    print(string)

host="woezel.local"  #hier zou eigen een global variable van gemaakt moeten worden ofzo

mqttclient = mqtt.Client()
mqttclient.on_message = on_message
mqttclient.on_connect = on_connect
mqttclient.on_publish = on_publish
mqttclient.on_subscribe = on_subscribe

# Uncomment to enable debug messages
#mqttclient.on_log = on_log


mqttclient.connect(host)
#inschrijven op topics zit in de functie on_connect


mqttclient.loop_forever()
#tot in der eeuwigheid wachten op info...

'''

#print("creating new instance")
client = mqtt.Client("P1") #create new instance
client.on_message=on_message #attach function to callback

print("connecting to broker")
client.connect(broker_address) #connect to broker

client.loop_start() #start the loop
print("Subscribing to topic","#")
client.subscribe("#")
print("Publishing message to topic","house/bulbs/bulb1")
#client.publish("house/bulbs/bulb1","OFF")
time.sleep(120) # wait
client.loop_stop() #stop the loop

'''
'''

#database openen en ingestelde waarden opzoeken

conn = sqlite3.connect('/home/bartje/Sqlite/mqtt.db')
c = conn.cursor()
	
##for row in c.execute("SELECT status, last_close_command, last_open_command FROM zonnewering WHERE id=1"):
##	global status, last_close_command, last_open_command
##	status = row[0]  #0 is open 100 is volledig toe
##	last_close_command = row[1]
##	last_open_command = row[2]

# enkel functies bepalen

##def setglobalvar():
##	global inbeweging, activatietijd, crosstalk
##	inbeweging = False
##	crosstalk = False
##	activatietijd = 28
	
	
def bediening_op(channel):
	#via crosstalk zien of er pas een commando gegeven is, indien zo, stop de code)
	global crosstalk
	if crosstalk:
		logger.info("bediening_op - crosstalk detected")
		return 1
	
	#crosstalk op true zetten om ander ingange te blokkeren	voor 100ms
	crosstalk = True
	time.sleep(0.1)
	crosstalk = False
	
	#print('naar boven')
	logger.info("bediening_op")
	global status
	logger.info("status voor commando is " + str(status))
	
	global inbeweging
	logger.info("in beweging is " + str(inbeweging)) #probsolv
	if inbeweging:  #gordijn is al aan het bewegen, het commando dat nu volgt is een stopcommando
		inbeweging = False
		
	else:			#gordijn beweegt nog niet, dit is het eerste commando
		
		#print status
		inbeweging = True	#de controller kent de stand van de gordijn ook niet, dus voor hem is de gordijn nu in beweging
		tijdcommando = time.time()
		conn = sqlite3.connect('/home/witje/Sqlite/Woning.db')
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
		inbeweging = False
		logger.info("in beweging is " + str(inbeweging)) #probsolv
		
		conn.close()
	
	logger.info("status na commando is " + str(status))

    
def bediening_neer(channel):
	#via crosstalk zien of er pas een commando gegeven is, indien zo, stop de code)
	global crosstalk
	if crosstalk:
		return 1
	
	#crosstalk op true zetten om ander ingange te blokkeren	voor 100ms
	crosstalk = True
	time.sleep(0.1)
	crosstalk = False
	
	#print('naar beneden')
	logger.info("bediening_neer")
	global status
	logger.info("status voor commando is " + str(status))
    
	global inbeweging
	logger.info("in beweging is " + str(inbeweging)) #probsolv
	if inbeweging:  #gordijn is al aan het bewegen, het commando dat nu volgt is een stopcommando
		inbeweging = False
		
	else:			#gordijn beweegt nog niet, dit is het eerste commando
		#print status
		inbeweging = True	#de controller kent de stand van de gordijn ook niet, dus voor hem is de gordijn nu in beweging
		tijdcommando = time.time()
		conn = sqlite3.connect('/home/witje/Sqlite/Woning.db')
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
		inbeweging = False
		logger.info("in beweging is " + str(inbeweging)) #probsolv

		conn.close()
	
	logger.info("status na commando is " + str(status))

'''

'''while True:
	ik = 0
'''