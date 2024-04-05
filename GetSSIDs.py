import csv
import requests
import logging
import datetime
import os


logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO)

csvfile = "ssid.csv"

ssid_handle = open(csvfile, 'a', newline='')
ssid_writer = csv.writer(ssid_handle)

if os.path.getsize(csvfile) == 0:
    ssid_header = ['ssid', 'start_time', 'end_time', 'responding_devices_len', 'probing_devices_len', 'advertising_devices_len'] 
    ssid_writer.writerow(ssid_header)

kismet_api_uri =  "http://username:password@192.168.1.57:2501/phy/phy80211/ssids/views/ssids.prettyjson"

logging.info("Sending kismet_api_uri '%s'", kismet_api_uri)

try:
    response = requests.get(kismet_api_uri, verify=False, timeout=10)
except:
    logging.warn("No response received, check Kismet server and your API URI and credentials")

if response:
    try:
        ssid_dict = response.json()
        for ssid in ssid_dict:
            name = ssid['dot11.ssidgroup.ssid']
            if len(name) > 0:
                first_time =  ssid['dot11.ssidgroup.first_time']
                last_time =  ssid['dot11.ssidgroup.last_time']
                first_time_formatted = datetime.datetime.fromtimestamp(first_time).strftime('%c')
                last_time_formatted = datetime.datetime.fromtimestamp(last_time).strftime('%c')
                responding_devices_len = ssid['dot11.ssidgroup.responding_devices_len']
                probing_devices_len = ssid['dot11.ssidgroup.probing_devices_len']
                advertising_devices_len = ssid['dot11.ssidgroup.advertising_devices_len']
                ssid_writer.writerow([name, first_time_formatted, last_time_formatted, responding_devices_len, probing_devices_len, advertising_devices_len])
    except:
        pass  

ssid_handle.close()

logging.info("Written '%s'", csvfile)

