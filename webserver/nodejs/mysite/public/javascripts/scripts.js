var color1 = 'rgba(57,129,142,1)';	//Petrol
var color2 = 'rgba(120,24,55,1)';    //'rgba(255,0,0,0.5)';	//fuchia
var color3 = 'rgba(86,86,86,1)';
var color4 = 'rgba(31,100,137,1)';  //blue
//var solar_chart;
var solar_end = 0;
var solar_number = 1;
var solar_type="Detail";
var solar_chart_exist=false;
var forecast_chart_exist=false;
var x = new Date();
//var currentTimeZoneOffsetInSeconds = x.getTimezoneOffset() * 60;   //.getTimezoneOffset()//in minuten .. onze tijd + offset = UTC tijd
//console.log (currentTimeZoneOffsetInSeconds);

var topic_weather_now = 'weather/now';
var topic_weather_forecast = 'weather/forecast';
var topic_solar = 'power/solar/energy';


function set_visibility(hide, show) {
// 	hides the id in the first tabel; shows the divs in the second table
	for (i = 0; i < hide.length; i++) { 
	    var e = document.getElementById(hide[i]);
	    e.style.display = 'none';
	}
	for (i = 0; i < show.length; i++) { 
	    var e = document.getElementById(show[i]);
	    e.style.display = 'block';
	}
}	


/*

var e = document.getElementById(id);
if(e.style.display == 'block')
e.style.display = 'none';
else
e.style.display = 'block';
}
*/
function change_solar_end(i) {
	solar_end = solar_end + i;
	if (solar_end > 0) {
		solar_end = 0;
	} else {
		console.log(solar_end);
		get_solar_chart();
	}
	
	}

function change_solar_number(i) {
	solar_number = solar_number + i;
	if (solar_number < 1) {
		solar_number = 1;
	} else {
		console.log(solar_number);
		get_solar_chart();
	}
}

function change_solar_type(type, optional_end, optional_number) {
	solar_type = type;
	get_solar_chart(optional_end, optional_number);
}

function get_solar_chart(optional_end, optional_number) {
	if (!(typeof optional_end === 'undefined')) { solar_end = optional_end; }
	if (!(typeof optional_number === 'undefined')) { solar_number = optional_number; }
	if (solar_type=="Detail") {	//detail info
		parameter={einde:solar_end,aantal:solar_number};
		//console.log(parameter);
		$.get( '/solar_detail', parameter, function(data){
		//$('#test').html("dit is een test");
			//console.log(data);
			
			var_labels = [];
			var_dataset1 = [];
			var_dataset2 = [];
			for(i in data) {
				var_labels.push(1000*(data[i].time));//   -currentTimeZoneOffsetInSeconds));  //charts houd hiermee al rekening!!
				var_dataset1.push(data[i].ACPower);
				var_dataset2.push(data[i].efficiency/10);	
			}
			
		
			var ctx1 = document.getElementById("pvchart_today");
			if (solar_chart_exist) {
				console.log("test");
				solar_chart.destroy();
			}
			solar_chart_exist=true;
			window.solar_chart = new Chart(ctx1, {
			    type: 'line',
			    data: {
			        labels : var_labels,
			        datasets: [{
			            label: 'vermogen',
			            yAxisID:'y-axis-1',
			            data: var_dataset1,
			            borderColor: color1, //'rgba(0,255,0,0.5)',
			            borderWidth: 2,
			            pointRadius: 0,
			            },{
				        label: 'rendement',
			            yAxisID: 'y-axis-2',
				        data: var_dataset2,
				        borderColor: color2, //'rgba(255,0,0,0.5)',
				        borderWidth: 1,
				        pointRadius: 0,
				        hidden: true,
			        }]
			    },
			    options: {
			        scales: {
			            yAxes: [{
				                scaleLabel: {display: true, labelString: 'Vermogen in W', fontColor: color1},
				                type: "linear",
				                position: "left",
				                id: "y-axis-1",
				                ticks : {max : 1600, min : 0, stepSize : 200, fontColor: color1},
				                gridLines: {color: color3, drawOnChartArea: true ,drawTicks: true},
				            }, {
				                scaleLabel: {display: true, labelString: 'Omvormer-rendement in %', fontColor: color2},
				                type: "linear",
				                position: "right",
				                id: "y-axis-2",
				                ticks : {max : 100, min : 68, stepSize : 4, fontColor: color2},
				                gridLines: {drawOnChartArea: false, color: color3, drawTicks: true},
				            }],
						xAxes : [{
							type: 'time',
							time: {
								displayFormats: {
									'millisecond': 'MMM DD H:mm',
									'second': 'MMM DD H:mm',
									'minute': 'MMM DD H:mm',
									'hour': 'MMM DD H:mm',
									'day': 'MMM DD H:mm',
									'week': 'MMM DD H:mm',
									'month': 'MMM DD H:mm',
									'quarter': 'MMM DD H:mm',
									'year': 'MMM DD H:mm',
								},
								tooltipFormat: 'HH:mm',
							},
							gridLines: {drawOnChartArea: false, color: color3, drawTicks: true}
						}],
						
						tooltips: {    
			                mode: 'index',
				            intersect: false,
				            callbacks: {
				                label: function (t, d) {
				                    if (t.datasetIndex === 0) {
				                        return t.yLabel + 'W';
				                    } else if (t.datasetIndex === 1) {
				                        return t.yLabel + '%';
				                    }
				                }
				            }
				        },						
						
			        }
			    }
			});
		});
	}
	if (solar_type=="Daily") {if (solar_chart_exist) {solar_chart.destroy();}
		parameter={einde:solar_end,aantal:solar_number};
		//console.log(parameter);
		$.get( '/solar_daily', parameter, function(data){
		//$('#test').html("dit is een test");
			//console.log(data);
			
			var_labels = [];
			var_dataset1 = [];
			//var_dataset2 = [];
			for(i in data) {
				var_labels.push(1000*(data[i].time));//   -currentTimeZoneOffsetInSeconds));  //charts houd hiermee al rekening!!
				var_dataset1.push(data[i].ACPower);
				//var_dataset2.push(data[i].efficiency/10);	
			}
		
		//de grafiek nog bouwen natuurlijk
		
		});
	}
	
	if (solar_type=="Monthly") {if (solar_chart_exist) {solar_chart.destroy();}
	
	}
}



/*
functie voor het aanroepen van een plek??
function getPersons() {
    var xmlHttpReqeust = new XMLHttpRequest();

    xmlHttpRequest.onreadystatechange = function() {
        if ( xmlHttpRequest.readyState == XMLHttpRequest.DONE && xmlHttpRequest.status == 200 ) {
            document.getElementById("persons").innerHTML = xmlHttpRequest.responseText;
        }
    };
    xmlHttpRequest.open('GET', 'http://localhost/test', true);
    xmlHttpRequest.send();
}

in de HTML
Elementutton type='button' onclick='getPersons()'>Get persons!</button>
*/

//gedeelte voor socket.io


$(function(){
	var socket = io();
	socket.on('connect',function(data){
		socket.emit('join', 'hello world from client'); 
	});
	socket.on('messages', function(data) {  //wanneer er een bericht binnenkomt met topic messages
		//alert(data);
		console.log(data);
	});
	
	socket.on(topic_weather_now, function(data) {  //wanneer er een bericht binnenkomt met topic messages
		console.log("iets ontvangen");
		weather = JSON.parse(data);
		//console.log(weather["icon"]);
				
		//$("#weather_now_icon").html(function(i,origText){
		//	icon = "http://openweathermap.org/img/w/" + weather["icon"] + ".png";
		//	return "<img src=" + icon + " width ='50', height ='50'>";
		//});
		$("#weather_now_temp").html(function(i,origText){
			icon = "http://openweathermap.org/img/w/" + weather["icon"] + ".png";
			temp = weather["temp"];
			temp = (Math.round(2*Number(temp))/2).toFixed(1);
			temp = temp.toString();
			temp = temp.replace(".",",") +" °C";
			return "<img src=" + icon + " width ='50', height ='50'>" + temp;
		});
		$("#weather-widget-wind").html(function(i,origText){
			speed = weather['wind_speed'];
			//speed = round(number(speed));
			speed = speed.toString();
			speed = speed.replace(".",",") + "m/s"
			return speed + " - " + weather['wind_deg_name'];
		});
		$("#weather-widget-pressure").html(function(i,origText){
			pres = weather['pressure'] + " hpa";
			return pres;
		});
		$("#weather-widget-humidity").html(function(i,origText){
			hum = weather['humidity'] + " %";
			return hum;
		});
		$("#weather-widget-sunrise").html(function(i,origText){
			sun = weather['sunrise'];
			//console.log(sun);
			var t = moment.unix(sun);
			//console.log(t);
			var r = t.format("H:mm");
			//console.log(r);
			return r;
		});
		$("#weather-widget-sunset").html(function(i,origText){
			sun = weather['sunset'];
			var t = moment.unix(sun);
			var r = t.format("H:mm");
			return r;
		});

		//weather-widget-wind
	});
	
	
	socket.on(topic_weather_forecast, function(data) {
		forecast = JSON.parse(data);
		var_labels = [];
		var_dataset1 = []; //temp
		var_dataset2 = []; //neerslag
		var_icon = [];
		var_wolken = [];
		var_windsnelheid = [];
		//console.log('forecast');
		//console.log(forecast['list'][0]);
		
		for (i=0; i<10; i++) {
			var_labels.push(1000*forecast['list'][i]['time']);
			var_dataset1.push(Math.round(forecast['list'][i]['temp']*10)/10);  //temperatuur
			var_dataset2.push(Math.round((forecast['list'][i]['rain_3h']+forecast['list'][i]['snow_3h'])*10)/10);	//regenval
			var_icon.push(forecast['list'][i]['icon']);
			var_wolken.push(forecast['list'][i]['description']);
			var_windsnelheid.push(Math.round(forecast['list'][i]['wind_speed']*10)/10);
				
		}
		//console.log(var_labels);
		//console.log(var_dataset1);
		//console.log(var_dataset2);
		
		//grafiek maken
		var ctx2 = document.getElementById("forecast_chart");
		if (forecast_chart_exist) {
			console.log("test");
			forecast_chart.destroy();
		}
		forecast_chart_exist=true;
		window.forecast_chart = new Chart(ctx2, {
		    type: 'bar',
		    data: {
		        labels : var_labels,
		        datasets: [{
		            label: 'temparatuur',
		            yAxisID:'y-axis-1',
		            data: var_dataset1,
		            borderColor: color2,
		            //backgroundColor: color2,
		            borderWidth: 2,
		            pointRadius: 2,
		            type: 'line',
		            },{
			        label: 'regenval',
		            yAxisID: 'y-axis-2',
			        data: var_dataset2,
			        borderColor: color4,
			        backgroundColor: color4,
			        //borderWidth: 1,
			        //pointRadius: 0,
			        //type: 'bar',
		        }]
		    },
		    options: {
			    legend: {display: false},
		        scales: {
		            yAxes: [{
			                scaleLabel: {display: true, labelString: 'temperatuur in °C', fontColor: color2},
			                type: "linear",
			                position: "left",
			                id: "y-axis-1",
			                ticks : {fontColor: color2},
			                gridLines: {color: color2, drawOnChartArea: false ,drawTicks: true},
			            }, {
			                scaleLabel: {display: true, labelString: 'neerslag in mm', fontColor: color4},
			                type: "linear",
			                position: "right",
			                id: "y-axis-2",
			                ticks : {fontColor: color4},
			                gridLines: {drawOnChartArea: false, color: color4, drawTicks: true},
			            }],
					xAxes : [{
						type: 'time',
						time: {
							displayFormats: {
								'millisecond': 'H:mm',
								'second': 'H:mm',
								'minute': 'H:mm',
								'hour': 'H:mm',
								'day': 'H:mm',
								'week': 'H:mm',
								'month': 'H:mm',
								'quarter': 'H:mm',
								'year': 'H:mm',
							},
							tooltipFormat: 'HH:mm',
							unit: 'hour',
							stepSize: 3,
						},
						gridLines: {drawOnChartArea: false, color: color3, drawTicks: true}
					}],
					
					tooltips: {    
		                mode: 'index',
			            intersect: false,
			            callbacks: {
			                label: function (t, d) {
			                    if (t.datasetIndex === 0) {
			                        return t.yLabel + 'W';
			                    } else if (t.datasetIndex === 1) {
			                        return t.yLabel + '%';
			                    }
			                }
			            }
			        },						
					
		        }
		    }
		});
		
		//einde grafiek maken
		
		// html code aanpassen --> forecast info (symbolen invoegen)
		
		$("#forecast_icons").html(function(j,origText){
			//var_icon
			//var_wolken
			//var_windsnelheid
			htmlcode1 = "<div class='weather-forecast-icons__item'><img src=";
			htmlcode2 = "><br>";
			htmlcode3 = " °C<br>";
			htmlcode4 = "<br>";
			htmlcode5 = "m/s</div>";
			data_html = "";
			for (i=0; i<10; i++) {
				icon = "http://openweathermap.org/img/w/" + var_icon[i] + ".png";
				wolken = var_wolken[i];
				wind = var_windsnelheid[i];
				data_t = htmlcode1 + icon + htmlcode2 + var_dataset1[i] + htmlcode3 + wolken + htmlcode4 + wind + htmlcode5;
				data_html = data_html + data_t;
			}
			
			
			//temp = weather["temp"];
			//temp = (Math.round(2*Number(temp))/2).toFixed(1);
			//temp = temp.toString();
			//temp = temp.replace(".",",") +" °C";
			
			return data_html;
		});

		
	});	
		
		
});



/*
$(function () {
	var socket = io();
	$('form').submit(function(){
		socket.emit('chat message', $('#m').val());
		$('#m').val('');
		return false;
	});
	socket.on('chat message', function(msg){
		//$('#messages').append($('<li>').text(msg));
		console.log('ok');
	});
});
*/