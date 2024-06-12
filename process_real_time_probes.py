import csv
import time
import os
import sys 
import configparser
import ast
import paho.mqtt.client as mqtt
import logging

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO)
  
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


if len(sys.argv) != 3:
    logging.critical("Usage: %s config_filename csv_filename", sys.argv[0])
    sys.exit(0)

config = configparser.ConfigParser()
config.read(sys.argv[1])

if config.has_section("probes"):
    ssid_blacklist = ast.literal_eval(config.get("probes", "ssid_blacklist")) 
else:
    ssid_blacklist = ""

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
        logging.warning("Cannot connect to MQTT check config file and server")
    mqtt_client.loop_start()

reader = csv.reader(rolling_reader(sys.argv[2]))
for row in reader:
    ssid = row[8] 
    #Use this line only if have the latest version of tshark which outputs hex not ascii for wlan.ssid
    ssid = bytes.fromhex(ssid).decode("latin-1")     
    if  ssid not in ssid_blacklist:
        if config.has_section("mqtt"):
            logging.info("Hit: %s", ssid)
            mqtt_client.publish(mqtt_topic, ssid) 