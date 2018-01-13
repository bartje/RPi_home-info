# RPi_home-info

Code voor het uitlezen
- van het telwerk van een watermeter  (TODO)
- van het telwerk van een gasmeter    (TODO)
- ven het telwerk van een elek-teller van de zonnepanelen (TODO)

Code voor het uitlezen:
- van de zonneomvormer (SMA SB-1600-TL) (python, reference to https://github.com/TD22057/T-Home)
- van de verwarmingsinstallatie (Viessmann)  (TODO)

Code nodig voor het uitlezen van de zonnewering (inlezen commando's en state-estimater van de stand)

Code nodig voor het inlezen van het weer (openweather)

Elke deel wordt gebouwd als een sensor en is modulair, de verschillende modules kunnen onderling data uitwisselen via MQTT

module voor wegschrijven van de info naar SQlite DB

Webserver gebasseerd op nodejs en Express.js die de verschillende inforamtie visualiseerd



Watermeter: kent V100
https://flukso.net/content/water-probe

Gasmeter (eandis)
https://flukso.net/content/gas-probe
