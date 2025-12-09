import sys
import logging
import datetime
import logging
import pandas as pd
from plotnine import *
from mizani.formatters import date_format
import os

def filter_non_printable(str):
  return ''.join([c for c in str if ord(c) > 31 or ord(c) == 9])

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO)
    
if len(sys.argv) != 2:
    logging.info("Usage %s probes_csv_file time_filter e.g. %s probes.csv", sys.argv[0], sys.argv[0])
    sys.exit(0)

#frame.time_epoch,wlan.ta,wlan.ra,wlan.sa,wlan.da,frame.len,wlan_radio.channel,wlan_radio.signal_dbm,wlan.ssid en
csvfile = sys.argv[1]

logging.info("Processing %s", csvfile)

probe_df = pd.read_csv(csvfile).dropna()

probe_df = pd.read_csv(csvfile, usecols=[0,6,7,8], names=['timestamp', 'channel', 'signal_dbm', 'ssid'])

probe_df = probe_df.dropna()

probe_df['timestamp'] = probe_df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x))

probe_df['printable_ssid'] = probe_df['ssid'].apply(lambda x: bytes.fromhex(x).decode('latin-1'))
probe_df['printable_ssid'] = probe_df['printable_ssid'].apply(lambda x: x.replace('$','\$'))
probe_df['printable_ssid'] = probe_df['printable_ssid'].apply(lambda x: filter_non_printable(x))

probe_df['publishedAt'] = pd.to_datetime(probe_df['timestamp'])
probe_df = probe_df.set_index(['publishedAt'])
probe_df = probe_df.sort_index()

title = "Probed SSIDs in a hex format"

graph = ggplot(probe_df, aes(y = 'timestamp', x = 'ssid')) + geom_point(aes(size='signal_dbm'), alpha=0.2) + \
        ylab("Hour:Minute") + theme(axis_text_x=element_text(rotation=90, size=6)) + \
        scale_y_datetime(date_breaks = "10 minutes", labels = date_format("%H:%M")) + \
        theme(axis_text_y=element_text(size=6)) + theme(figure_size=(16, 8)) + \
        ggtitle(title)

plot_filename = os.getcwd() + '/probes-raw.jpg'
logging.info("Saving %s", plot_filename)
graph.save(filename = plot_filename, dpi = 600)

title = "Probed SSIDs in a printable format"

graph = ggplot(probe_df, aes(y = 'timestamp', x = 'printable_ssid')) + geom_point(aes(size='signal_dbm'), alpha=0.2) + \
       ylab("Hour:Minute") + theme(axis_text_x=element_text(rotation=90, size=6)) + \
        scale_y_datetime(date_breaks = "10 minutes", labels = date_format("%H:%M")) + \
        theme(axis_text_y=element_text(size=6)) + theme(figure_size=(16, 8)) + \
        ggtitle(title)

plot_filename = os.getcwd() + '/probes.jpg'
logging.info("Saving %s", plot_filename)
graph.save(filename = plot_filename, dpi = 600)

map_filename = os.getcwd() + '/probes_printable.csv'
probes_printable = probe_df[['printable_ssid', 'channel','signal_dbm']]
probes_printable.to_csv(map_filename, header=False)




