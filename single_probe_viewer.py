import sys
import logging
import datetime
import logging
import pandas as pd
from plotnine import *
from mizani.formatters import date_format
import os
import string

def filter_non_printable(str):
  return ''.join([c for c in str if ord(c) > 31 or ord(c) == 9])

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO)
    
if len(sys.argv) != 3:
    logging.info("Usage %s probes_csv_file ssid_name e.g. %s probes.csv TPLINK", sys.argv[0], sys.argv[0])
    sys.exit(0)

#frame.time_epoch,wlan.ta,wlan.ra,wlan.sa,wlan.da,frame.len,wlan_radio.channel,wlan_radio.signal_dbm,wlan.ssid en
csvfile = sys.argv[1]

logging.info("Processing %s", csvfile)

probe_df = pd.read_csv(csvfile).dropna()

probe_df = pd.read_csv(csvfile, usecols=[0,6,7,8], names=['timestamp', 'channel', 'signal_dbm', 'ssid'])

probe_df['timestamp'] = probe_df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x))

#Use this line only if have the latest version of tshark which outputs hex not ascii for wlan.ssid
probe_df['ssid'] = probe_df['ssid'].apply(lambda x: bytes.fromhex(x).decode('latin-1'))

probe_df = probe_df[probe_df['ssid'] == sys.argv[2]]

#Have to escape $ for matplotlib
probe_df['ssid'] = probe_df['ssid'].apply(lambda x: x.replace('$','\$'))

#tshark gving non printable characters sometimes, why they use hex!
probe_df['ssid'] = probe_df['ssid'].apply(lambda x: filter_non_printable(x))

title = "Probed SSIDs"

#graph = ggplot(probe_df, aes(y = 'timestamp', x = 'ssid')) + geom_point(aes(size='signal_dbm'), alpha=0.2) + \
#        ylab("Hour") + theme(axis_text_x=element_text(rotation=90, size=6)) + \
#        scale_y_datetime(date_breaks = "1 hour", labels = date_format("%H")) + \
#        theme(axis_text_y=element_text(size=6)) + theme(figure_size=(16, 8)) + \
#        ggtitle(title)

probe_df['timestamp-utc-copy'] = probe_df['timestamp']
probe_df['timestamp-utc-copy'] = probe_df['timestamp-utc-copy'].apply(lambda dt: dt.replace(hour=0,minute=0,second=0))
probe_df['timestamp'] = probe_df['timestamp'].apply(lambda dt: dt.replace(day=1,month=1,year=2000))

graph = ggplot(probe_df, aes(y = 'timestamp', x = 'timestamp-utc-copy')) + geom_point(aes(size=5), alpha=0.05) + \
        ylab("Hour") + theme(axis_text_x=element_text(rotation=90, size=6)) + \
        xlab("Day") + theme(axis_text_x=element_text(size=6)) + \
        scale_y_datetime(date_breaks = "1 hour", labels = date_format("%H")) + \
        scale_x_datetime(date_breaks = "1 day", labels = date_format("%d/%m/%Y")) + \
        theme(axis_text_y=element_text(size=6)) + theme(figure_size=(16, 8)) + \
        ggtitle(title)

plot_filename = os.getcwd() + "/" + sys.argv[2] + '.jpg'
logging.info("Saving %s", plot_filename)
graph.save(filename = plot_filename, dpi = 600)








