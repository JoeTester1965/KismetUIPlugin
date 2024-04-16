import csv
import time
import os
import sys 
import configparser
import ast
import paho.mqtt.client as mqtt
  
def rolling_reader(filename, poll_period=.1, encoding="utf-8"):
    pos = 0
    while True:
        while True:
            try:
                if os.stat(filename).st_size > pos:
                    break
            except FileNotFoundError:
                pass
            time.sleep(poll_period)
        fp = open(filename, "rb")
        fp.seek(pos)
        for line in fp:
            if line.strip():
                yield line.decode("utf-8")
        pos = fp.tell()


config = configparser.ConfigParser()
config.read(sys.argv[1])

ssid_list = ast.literal_eval(config.get("probes", "ssid_matchlist")) 

if config.has_section("mqtt"):
    mqtt_ip_address = config["mqtt"]["mqtt_ip_address"] 
    mqtt_username = config["mqtt"]["mqtt_username"]
    mqtt_password = config["mqtt"]["mqtt_password"]
    mqtt_topic = config["mqtt"]["mqtt_topic"]
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    mqtt_client.username_pw_set(mqtt_username, mqtt_password)
    try:
        mqtt_client.connect(mqtt_ip_address, 1883)
    except:
        print("Cannot connect to MQTT, check config and server")
    mqtt_client.loop_start()

reader = csv.reader(rolling_reader("probes.csv"))
for row in reader:
    if  row[8] in ssid_list:
        print(row)
        if config.has_section("mqtt"):
            mqtt_client.publish(mqtt_topic, row[8]) 