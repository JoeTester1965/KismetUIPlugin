import sys
import logging
import datetime
import logging
import numpy as np
import pandas as pd
from plotnine import *
from mizani.formatters import date_format
import os

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO)
    
if len(sys.argv) != 2:
    logging.info("Usage %s probes_csv_file", sys.argv[0])
    sys.exit(0)

#frame.time_epoch,wlan.ta,wlan.ra,wlan.sa,wlan.da,frame.len,wlan_radio.channel,wlan_radio.signal_dbm,wlan.ssid en
csvfile = sys.argv[1]

logging.info("Processing %s", csvfile)

probe_df = pd.read_csv(csvfile).dropna()

probe_df = pd.read_csv(csvfile, usecols=[0,6,7,8], names=['timestamp', 'channel', 'signal_dbm', 'ssid'])

probe_df['timestamp'] = probe_df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x))

#Use this if kave the latest version of tshark which outputs hex not ascii for wlan.ssid
#probe_df['ssid'] = probe_df['ssid'].apply(lambda x: bytes.fromhex(x).decode('utf-8'))

title = "Probed SSIDs"

graph = ggplot(probe_df) 

graph = ggplot(probe_df, aes(y = 'timestamp', x = 'ssid')) + geom_point(aes(size='signal_dbm'), alpha=0.2) + \
        ylab("Hour") + theme(axis_text_x=element_text(rotation=90, size=6)) + \
        scale_y_datetime(date_breaks = "1 hour", labels = date_format("%H")) + \
        theme(axis_text_y=element_text(size=6)) + theme(figure_size=(8, 4)) + \
        ggtitle(title)

plot_filename = os.getcwd() + '\probes.jpg'
logging.info("Saving %s", plot_filename)
graph.save(filename = plot_filename, dpi = 600)





