from time import sleep
from datetime import datetime
from json import load
from pymongo import MongoClient
from Adafruit_DHT import read_retry, DHT22
from RPi import GPIO


with open('config.json') as config:
    config_data = load(config)

MEASURE_INTERVAL = config_data[u"MEASURE_INTERVAL"]
SAMPLE_INTERVAL = config_data[u"SAMPLE_INTERVAL"]
SENSOR_PINS = config_data[u"SENSOR_PINS"]
SWITCH_PIN = config_data[u"SWITCH_PIN"]
HUMID_UPPER = config_data[u"HUMID_UPPER"]
HUMID_LOWER = config_data[u"HUMID_LOWER"]
SENSOR_COUNT = len(SENSOR_PINS)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SWITCH_PIN, GPIO.OUT)
switch_on = False
sleep_time = SAMPLE_INTERVAL

db = MongoClient().local

while True:
    data = {"dt": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    avg_humid = 0

    for pin in SENSOR_PINS:
        humid, temp = read_retry(DHT22, pin)
        avg_humid += humid
        data[str(pin)] = {"h": round(humid, 3), "t": round(temp, 3)}
    
    avg_humid /= SENSOR_COUNT

    if switch_on:
        if avg_humid > HUMID_UPPER:
            GPIO.output(SWITCH_PIN, GPIO.LOW)
            sleep_time = SAMPLE_INTERVAL
            data['on'] = 0
            switch_on = False
    else:
        if avg_humid < HUMID_LOWER:
            GPIO.output(SWITCH_PIN, GPIO.HIGH)
            sleep_time = MEASURE_INTERVAL
            data['on'] = 1
            switch_on = True

    db.temp_humid.insert_one(data)
    sleep(sleep_time)
