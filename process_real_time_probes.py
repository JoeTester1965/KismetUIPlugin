import csv
import time
import os
import sys 
import configparser
import ast
import paho.mqtt.client as mqtt
import logging

def filter_non_printable(str):
  return ''.join([c for c in str if ord(c) > 31 or ord(c) == 9])

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

if config.has_option("probes", "ssid_watchlist"):
    ssid_watchlist = ast.literal_eval(config.get("probes", "ssid_watchlist"))
else:
    ssid_watchlist = ""

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

    raw_ssid = row[8] # ssid in raw format
    printable_ssid = bytes.fromhex(raw_ssid).decode("latin-1")
    printable_ssid = filter_non_printable(printable_ssid)
 
    ssid_to_message=None

    if len(ssid_watchlist) > 0:
        if raw_ssid in ssid_watchlist:
            ssid_to_message = raw_ssid
    
    if len(ssid_watchlist) > 0:
        if printable_ssid in ssid_watchlist:
            ssid_to_message = printable_ssid

    if ssid_to_message:
        logging.info("%s", ssid_to_message)
        if config.has_section("mqtt"):    
            mqtt_client.publish(mqtt_topic, ssid_to_message)