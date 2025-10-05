import sys
import logging
import datetime
import logging
import pandas as pd
import os

def filter_non_printable(str):
  return ''.join([c for c in str if ord(c) > 31 or ord(c) == 9])

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO)
    
if len(sys.argv) != 3:
    logging.info("Usage %s probes_csv_file time_filter e.g. %s probes.csv 5m", sys.argv[0], sys.argv[0])
    sys.exit(0)

#frame.time_epoch,wlan.ta,wlan.ra,wlan.sa,wlan.da,frame.len,wlan_radio.channel,wlan_radio.signal_dbm,wlan.ssid en
csvfile = sys.argv[1]

logging.info("Processing %s", csvfile)

probe_df = pd.read_csv(csvfile).dropna()

probe_df = pd.read_csv(csvfile, usecols=[0,6,7,8,9], names=['timestamp', 'channel', 'signal_dbm', 'ssid', 'collector'])

probe_df = probe_df.dropna()

probe_df['timestamp'] = probe_df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x))

probe_df['printable_ssid'] = probe_df['ssid'].apply(lambda x: bytes.fromhex(x).decode('latin-1'))
probe_df['printable_ssid'] = probe_df['printable_ssid'].apply(lambda x: x.replace('$','\$'))
probe_df['printable_ssid'] = probe_df['printable_ssid'].apply(lambda x: filter_non_printable(x))

probe_df['publishedAt'] = pd.to_datetime(probe_df['timestamp'])
probe_df = probe_df.set_index(['publishedAt'])
probe_df = probe_df.sort_index()

latest_time_interval = int(sys.argv[2])

created_time = datetime.datetime.now() - datetime.timedelta(minutes=latest_time_interval)
probe_df_last5m = probe_df[(probe_df['timestamp'] > created_time) & (probe_df['timestamp'] < datetime.datetime.now())]

map_filename = os.getcwd() + '/probes_latest.csv'
probes_printable = probe_df_last5m[['printable_ssid', 'ssid', 'channel','signal_dbm', 'collector']]
probes_printable.to_csv(map_filename, header=False)
