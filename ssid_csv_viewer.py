import sys
import logging
import numpy as np
import pandas as pd
from plotnine import *
from mizani.formatters import date_format

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO)
    
#ssid,start_time,end_time,responding_devices_len,probing_devices_len,advertising_devices_len
csvfile = sys.argv[1]

logging.info("Processing '%s'", csvfile)

ssid_df = pd.read_csv(csvfile).dropna()

ssid_df['start_time'] = pd.to_datetime(ssid_df['start_time'])
ssid_df['end_time'] = pd.to_datetime(ssid_df['end_time'])

graph = ggplot(ssid_df) + geom_errorbar(aes(x = 'ssid', ymax = 'start_time', ymin = 'end_time' ), size = 2, color = "grey") + \
        ylab("date") + theme(axis_text_x=element_text(rotation=90, size=8)) + \
        scale_y_datetime(date_breaks = "1 hour", labels = date_format("%d-%m-%Y %H")) + \
        theme(axis_text_y=element_text(size=6)) + coord_flip()  + theme(figure_size=(16, 16))

print(graph)

pass




