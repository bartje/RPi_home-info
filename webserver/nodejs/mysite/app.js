var express = require('express');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');

var index = require('./routes/index');
var users = require('./routes/users');


var app = express();
var io = require('./io');
var sqlite3 = require('sqlite3').verbose();

//var server = require('http').Server(app);
//var io = require('socket.io')(server);
// zit in bin/www gedeelte!

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

// uncomment after placing your favicon in /public
//app.use(favicon(path.join(__dirname, 'public', 'favicon.ico')));
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', index);
app.use('/users', users);

// antwoord op detailinfo van de zonnencellen
app.get('/solar_detail',function(req, res){
	
	//res.send("wee");
	var endday = req.query.einde; //req.....  // 0 is vandaag, -1 is gisteren, -2 is eergisteren, ...
	var totalday = req.query.aantal; //req....  //1 is één dat zien, 2 is twee dagen zien,...
	//console.log("einde = " + endday);
	//console.log("aantal dagen = " + totalday);
	// een dag stopt om 23u en begint om 2u
	
	//eindtijd = einde van de endday
	var myDate = new Date();  //is de tijd nu!

	myDate.setHours(24 + myDate.getTimezoneOffset()/60, 00, 00); //vandaag om 24u00  
	endtime = myDate.setHours(myDate.getHours() + endday*24)/1000;
	console.log(myDate.getTimezoneOffset()); 
	//.getTimezoneOffset()//in minuten .. onze tijd + offset = UTC tijd
		
	//begintijd = begin van [endday - (totalday-1)]
	//var myDate = new Date(); 
	starttime = myDate.setHours(myDate.getHours() - totalday*24)/1000;  // de originele myDate is eindtijd op 24u
	//console.log("starttijd = " + starttime);
	//console.log("eindtijd = " + endtime);

	
		
	let db = new sqlite3.Database(path.join(__dirname, 'db/Sqlite/Solar.db'), sqlite3.OPEN_READONLY, (err) => {
		if (err) {
			console.error(err.message);
		} else {
			console.log('Connected to the Solar database.');
		}
	});
	
	db.serialize(() => {
		//db.each(`SELECT time as time, frequency as freq FROM data WHERE id<100 and id>90`, (err, row) => {
		db.all('SELECT time, ACPower, efficiency FROM data WHERE time<' + endtime + ' and time>' + starttime, (err, result) => {
			if (err) {
				console.error(err.message);
			}
			//console.log(row.time + " " + row.freq);
			res.send(result);
			//res.send(endtime);
		});
	});
	
	
	
	db.close()
	
	
});

// antwoord op daily infor
app.get('/solar_daily',function(req, res){
	
	//res.send("wee");
	var endweek = req.query.einde; //req.....  // 0 is deze week, -1 is vorige week, ...
	var totalweek = req.query.aantal; //req....  //1 is één week, 2 is twee weken zien,...
	console.log("einde = " + endday);
	console.log("aantal weken = " + totalday);
	// een week start op maandag en stop op zondagavond
	
/*
	//eindtijd = einde van de endday
	var myDate = new Date();  //is de tijd nu!

	myDate.setHours(24 + myDate.getTimezoneOffset()/60, 00, 00); //vandaag om 24u00  
	endtime = myDate.setHours(myDate.getHours() + endday*24)/1000;
	console.log(myDate.getTimezoneOffset()); 
	//.getTimezoneOffset()//in minuten .. onze tijd + offset = UTC tijd
		
	//begintijd = begin van [endday - (totalday-1)]
	//var myDate = new Date(); 
	starttime = myDate.setHours(myDate.getHours() - totalday*24)/1000;  // de originele myDate is eindtijd op 24u
	console.log("starttijd = " + starttime);
	console.log("eindtijd = " + endtime);
*/

	
		
	let db = new sqlite3.Database(path.join(__dirname, 'db/Sqlite/Solar.db'), sqlite3.OPEN_READONLY, (err) => {
		if (err) {
			console.error(err.message);
		} else {
			console.log('Connected to the Solar database.');
		}
	});
	
	db.serialize(() => {
		//db.each(`SELECT time as time, frequency as freq FROM data WHERE id<100 and id>90`, (err, row) => {
		db.all('SELECT time, ACPower, efficiency FROM data WHERE time<' + endtime + ' and time>' + starttime, (err, result) => {
			if (err) {
				console.error(err.message);
			}
			//console.log(row.time + " " + row.freq);
			res.send(result);
			//res.send(endtime);
		});
	});
	
	
	
	db.close()
	
	
});



//MQTT-variabelen gedeelte

var mqtt_host = 'mqtt://woezel.local';
var mqtt = require('mqtt');
var mqtt_client = mqtt.connect(mqtt_host);
var topic_weather_now = 'weather/now';
var topic_solar = 'power/solar/energy';
var topic_weather_forecast = 'weather/forecast';

//MQTT connecteren met de broker en subcribe topics
mqtt_client.on('connect', function () {
	//setTimeout(function(){
    //	mqtt_client.subscribe(topic_weather_now,{port: 1883, qos:2})  //
	//	mqtt_client.subscribe(topic_solar,{port: 1883})
	//}, 2000);
	//mqtt_client.subscribe(topic_weather_now,{port: 1883, qos:2})  //
	//mqtt_client.subscribe(topic_solar,{port: 1883})
});
//socket.io gedeelte //het MQTT gedeelte zie hiermee in
io.on('connection', function(client){   //--> dit wordt gerund wanneer een client zich connecteerd
	
	
	console.log('a user connected');
	//setTimeout(function(){
    //	mqtt_client.subscribe(topic_weather_now,{port: 1883, qos:2})  //
	//	mqtt_client.subscribe(topic_solar,{port: 1883})
	//}, 2000);

	client.on('join', function(data) {
		console.log(data);
		client.emit('messages', 'hello world from server');
		mqtt_client.unsubscribe(topic_weather_now);
		mqtt_client.unsubscribe(topic_solar);
		mqtt_client.unsubscribe(topic_weather_forecast);
		console.log("disconnect & unsubscribe")

		setTimeout(function(){
			mqtt_client.subscribe(topic_weather_now,{port: 1883, qos:2})  //
			mqtt_client.subscribe(topic_solar,{port: 1883})
			mqtt_client.subscribe(topic_weather_forecast,{port: 1883})
		}, 500);
	});
	
	// we weten dat er een (of meerdere) users geconnecteerd zijn, nu moeten we dus ook naar MQTT berichten luisteren
	mqtt_client.on('message', function (topic, message) {
		// message is Buffer
		//console.log(message.toString())	
		if (topic == topic_weather_now) {
			io.emit(topic_weather_now, message.toString());	
		}
		if (topic == topic_weather_forecast) {
			io.emit(topic_weather_forecast, message.toString());	
		}
	});	
		
	client.on('disconnect', function() {
		mqtt_client.unsubscribe(topic_weather_now);
		mqtt_client.unsubscribe(topic_solar);
		mqtt_client.unsubscribe(topic_weather_forecast);
		console.log("disconnect & unsubscribe")
			
	});
});



//io.sockets.on('connection', function (socket) {  
//  socket.on('subscribe', function (data) {
//    console.log('Subscribing to '+data.topic);
//    client.subscribe(data.topic);
//  });
//});









// catch 404 and forward to error handler
app.use(function(req, res, next) {
  var err = new Error('Not Found');
  err.status = 404;
  next(err);
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
