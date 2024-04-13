import sys
import os
import logging
import numpy as np
import pandas as pd
from plotnine import *
from mizani.formatters import date_format

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO)
    
if len(sys.argv) != 3:
    logging.info("Usage %s csv_filename minumum_times_probe_seen", sys.argv[0])
    sys.exit(0)

#ssid,start_time,end_time,responding_devices_len,probing_devices_len,advertising_devices_len
csvfile = sys.argv[1]

times_seen_threshold = int(sys.argv[2])

logging.info("Processing %s with times_seen_threshold %d", csvfile, times_seen_threshold)

ssid_df = pd.read_csv(csvfile).dropna()

ssid_df['start_time_datetime'] = pd.to_datetime(ssid_df['start_time'])
ssid_df['end_time_datetime'] = pd.to_datetime(ssid_df['end_time'])

ssid_df_temp = ssid_df.loc[((ssid_df['advertising_devices_len'] == 0) & (ssid_df['responding_devices_len'] == 0)),:]

frequency_ssid = ssid_df_temp['ssid'].value_counts()
frequency_indexes = frequency_ssid[frequency_ssid >= times_seen_threshold].index 
ssid_df_temp_filtered = ssid_df_temp[ssid_df_temp['ssid'].isin(frequency_indexes)]

for index,row in ssid_df_temp_filtered.iterrows():
    #row['start_time'].replace(year=2000, month=1, day=1)
    ssid_df_temp_filtered.at[index, 'start_time_datetime'] = pd.to_datetime(row['start_time'][11:16])
    ssid_df_temp_filtered.at[index, 'end_time_datetime'] = pd.to_datetime(row['end_time'][11:16])
    pass

title = "Probed SSIDs not advertising or responding, seen at least " + str(times_seen_threshold) + " times and wrapped every 24 hours."

graph = ggplot(ssid_df_temp_filtered) + geom_errorbar(aes(x = 'ssid', ymax = 'start_time_datetime', ymin = 'end_time_datetime' ), size = 2, color = "black", alpha=0.1) + \
        ylab("Hour") + theme(axis_text_x=element_text(rotation=90, size=6)) + \
        scale_y_datetime(date_breaks = "1 hour", labels = date_format("%H")) + \
        theme(axis_text_y=element_text(size=6)) + theme(figure_size=(12, 12)) + \
      ggtitle(title)

plot_filename = os.getcwd() + '/probes.png'

logging.info("Saving %s", plot_filename)

graph.save(filename = plot_filename)






