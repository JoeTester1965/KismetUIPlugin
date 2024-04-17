import sys
import os
import requests
import logging
import datetime
import logging
import numpy as np
import pandas as pd
from plotnine import *
from mizani.formatters import date_format

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


#
# Change below!
#

probe_df[0] = probe_df[0].apply(lambda x: datetime.fromtimestamp(x).strftime("%I:%M:%S"))

probe_df_temp = probe_df.loc[((probe_df['advertising_devices_len'] == 0) & (probe_df['responding_devices_len'] == 0)),:]

frequency_ssid = probe_df_temp['ssid'].value_counts()
frequency_indexes = frequency_ssid[frequency_ssid >= times_seen_threshold].index 
probe_df_temp_filtered = probe_df_temp[probe_df_temp['ssid'].isin(frequency_indexes)]

for index,row in probe_df_temp_filtered.iterrows():
    #row['start_time'].replace(year=2000, month=1, day=1)
    probe_df_temp_filtered.at[index, 'start_time_datetime'] = pd.to_datetime(row['start_time'][11:16])
    probe_df_temp_filtered.at[index, 'end_time_datetime'] = pd.to_datetime(row['end_time'][11:16])
    pass

title = "Probed SSIDs not advertising or responding, seen at least " + str(times_seen_threshold) + " times and wrapped every 24 hours."

graph = ggplot(probe_df_temp_filtered) + geom_errorbar(aes(x = 'ssid', ymax = 'start_time_datetime', ymin = 'end_time_datetime' ), size = 2, color = "black", alpha=0.1) + \
        ylab("Hour") + theme(axis_text_x=element_text(rotation=90, size=6)) + \
        scale_y_datetime(date_breaks = "1 hour", labels = date_format("%H")) + \
        theme(axis_text_y=element_text(size=6)) + theme(figure_size=(12, 12)) + \
      ggtitle(title)

plot_filename = os.getcwd() + '/probes.png'

logging.info("Saving %s", plot_filename)

graph.save(filename = plot_filename)





