from time import sleep
from datetime import datetime
from json import load
from pymongo import MongoClient
from Adafruit_DHT import read_retry, DHT22


with open('config.json') as config:
    config_data = load(config)

client = MongoClient()
db = client.local


while True:
    data = {"date_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S') }
    for sensor in config_data[u"sensors"]:
        humid, temp = read_retry(DHT22, sensor)
        data[str(sensor)] = {"humid": humid, "temp": temp}

    db.temp_humid.insert_one(data)

    sleep(config_data[u"sleep_sec"])
