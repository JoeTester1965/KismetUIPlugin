import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State
import visdcc
import pandas as pd
import sys
import time
import sys
import json
import collections
import csv
import base64
import datetime 
import requests
import dpkt
from dpkt.compat import compat_ord
import os
import logging
import binascii

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO)

external_stylesheets = [
    'https://cdnjs.cloudflare.com/ajax/libs/vis/4.20.1/vis.min.css',
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

nodes = []
edges = []

label_for_newline_in_graph = ":-:"

mac_details_cache = collections.defaultdict(dict)

channel_list = []

tmp_csvfile = "edge_df.csv"

ui_variables = {   
                    'rewind_timeframe' : 300,
                    'mac_privacy_filter' : False,
                    'mac_multicast_filter' : False,
                    'gratuitous_arp_filter' : False,
                    'kismet_credentials' : 'user:password',
                    'kismet_uri' : '127.0.0.1:2501',
                    'packet_limit' : 10000
               }

def test_if_mac_filtered_in_edge(mac_list):
    global ui_variables
    
    retval = False
    
    for mac in mac_list:
        
        if ui_variables['gratuitous_arp_filter']:
            if mac == '00:00:00:00:00:00': 
                return True    
       
        if ui_variables['mac_privacy_filter']:
            stripped_mac = mac.replace(":","")
            u_l_bit = (int(stripped_mac[1], 16) & 2) >> 1
            if u_l_bit:
               return True
        
        if ui_variables['mac_multicast_filter']:
            stripped_mac = mac.replace(":","")
            m_c_bit = (int(stripped_mac[1], 16) & 1)
            if m_c_bit:
                return True

    return False

def ieee80211_frequency_to_channel(freq_mhz):
    if (freq_mhz == 0):
        return 0
    if (freq_mhz == 2484):
        return 14
    if (freq_mhz < 2484):
        return ((freq_mhz - 2407) / 5)
    return (freq_mhz/5 - 1000) 

def get_cached_mac_details(mac):

    retval_pretty_mac_name = mac
    retval_node_details = "Device type as of yet unknown"
    retval_device_type = "Unknown" 
    retval = dict()
    
    retval['pretty_mac_name'] = retval_pretty_mac_name    
    retval['node_details'] = retval_node_details
    retval['device_type'] = retval_device_type

    if mac in mac_details_cache:
        retval['pretty_mac_name'] = mac_details_cache[mac]['pretty_mac_name']
        retval['node_details'] = mac_details_cache[mac]['node_details']
        retval['device_type'] = mac_details_cache[mac]['device_type']
        return retval

    kismet_api_uri = "http://" + ui_variables['kismet_credentials'] + "@" + ui_variables['kismet_uri'] + "/devices/by-mac/" + mac + "/devices.json"

    try:
        response = requests.get(kismet_api_uri)
    except:
        logging.warn("No API response received")
        pass

    if response.content:

        devices_dict = json.loads(response.content)

        try:
            device_dict = devices_dict[0]
        except:
            return retval

        retval_device_type = device_dict['kismet.device.base.type']

        manuf= device_dict['kismet.device.base.manuf']
        if not manuf or manuf == 'Unknown':
            stripped_mac = mac.replace(":","")
            u_l_bit = (int(stripped_mac[1], 16) & 2) >> 1
            if u_l_bit:
                manuf = "Privacy"
            else:
                manuf = ""
        retval_pretty_mac_name = manuf + label_for_newline_in_graph + mac
        
        #node details
        type_text = "Type : " + retval_device_type
        ap_name_text = ""
        if retval_device_type == 'Wi-Fi AP':
            ap_name_text = "( " + device_dict['kismet.device.base.name'] + " , channel " + device_dict['kismet.device.base.channel'] + " )"
        first_time_text = "First seen : " + datetime.datetime.fromtimestamp(device_dict['kismet.device.base.first_time']).strftime('%c')
        last_time_text = "Last seen : " + datetime.datetime.fromtimestamp(device_dict['kismet.device.base.last_time']).strftime('%c')
        retval_node_details = type_text + " " + ap_name_text + " <br/> " + first_time_text + " <br/> " + last_time_text

    mac_details_cache[mac]['pretty_mac_name'] = retval_pretty_mac_name
    mac_details_cache[mac]['node_details'] = retval_node_details
    mac_details_cache[mac]['device_type'] = retval_device_type
   
    retval['pretty_mac_name'] = retval_pretty_mac_name    
    retval['node_details'] = retval_node_details
    retval['device_type'] = retval_device_type

    return retval

def pretty_format_hex(a):
    return ':'.join([a[i:i + 2] for i in range(0, len(a), 2)])

def create_edge_df(time_window_seconds, graph_type):

    global ui_variables, channel_list, channel_options

    mac_details_cache.clear()
    
    latest_timestamp =  time.time()

    working_timestamp = latest_timestamp - float(time_window_seconds)
    
    kismet_login_uri =  "http://" + ui_variables['kismet_credentials'] + "@" + ui_variables['kismet_uri']

    logging.info("Sending login '%s'", kismet_login_uri)

    try:
        response = requests.get(kismet_login_uri)
    except:
        logging.warn("No response received, check Kismet server and your API URI and credentials")
        pass
    
    kismet_api_uri = "http://" + ui_variables['kismet_credentials'] + "@" + ui_variables['kismet_uri'] + "/logging/kismetdb/pcap/packets.pcapng?limit=" + str(ui_variables['packet_limit']) + "&timestamp_start=" + str(working_timestamp) + "&timestamp_end=" + str(latest_timestamp)

    logging.info("Sending request '%s'", kismet_api_uri)

    try:
        os.remove("packets.pcapng")
    except:
        pass

    try:
        os.remove("packets.pcap")
    except:
        pass

    f = open("packets.pcap", "wb")
    f.close()

    f = open("packets.pcapng", "wb")

    try:
        response = requests.get(kismet_api_uri)
        f.write(response.content)
        f.flush()
        f.close()
        logging.info("Received response, now processing packets ... ")
    except:
        logging.warn("No response received, check Kismet server and your API URI and credentials")
        pass

    if os.name == "nt":
        command_line = "editcap.exe -F libpcap packets.pcapng packets.pcap"
    else:
        command_line = "editcap -F libpcap packets.pcapng packets.pcap"

    os.system(command_line)
        
    frequency_list_set = set()
    data = []

    with open("packets.pcap", 'rb') as f:

        try:
            pcap = dpkt.pcap.Reader(f)
        except:
            logging.warn("Cannot process packets")
            return
        for timestamp, buf in pcap:
    
            try:
                type = buf[18]
            except:
                   pass
            if type == 0x08:
                ss_mac = pretty_format_hex(binascii.hexlify(buf[22:28]).decode('utf-8'))
                ap_mac = pretty_format_hex(binascii.hexlify(buf[28:34]).decode('utf-8'))
                ds_mac = pretty_format_hex(binascii.hexlify(buf[34:40]).decode('utf-8'))
                frequency = int.from_bytes(buf[10:12], "little")
                frequency_list_set.add(frequency)
                packet_len = len(buf)
                signal = int((128 - (buf[14] & 0b01111111)) * -1)
                
                if (graph_type == 'ssds'):
                    data_tuple_endpoint=[ss_mac, ds_mac, frequency, packet_len, signal]
                if (graph_type == 'ssap'):
                    data_tuple_endpoint=[ss_mac, ap_mac, frequency, packet_len, signal]
                if (graph_type == 'apds'):
                    data_tuple_endpoint=[ap_mac, ds_mac, frequency, packet_len, signal]

                data.append(data_tuple_endpoint)  

    graph_dict = collections.defaultdict(dict)

    for entry_tuple in data:
        from_mac = entry_tuple[0]
        to_mac = entry_tuple[1]
        key = from_mac + to_mac
        channel = int(ieee80211_frequency_to_channel(int(entry_tuple[2])))
        filtered_mac = test_if_mac_filtered_in_edge([from_mac,to_mac])
        if channel != 0 and not filtered_mac and not from_mac == to_mac:
            channel_list.append(int(channel))
            current_bytes = entry_tuple[3]
            current_signal = entry_tuple[4]
            if not key in graph_dict[channel]:
                graph_dict[channel][key] = [from_mac, to_mac, 1, current_bytes, current_signal]
            else:
                graph_dict[channel][key][2] = graph_dict[channel][key][2] + 1                       #total_packets
                graph_dict[channel][key][3] = graph_dict[channel][key][3] + current_bytes           #total_bytes
                graph_dict[channel][key][4] = int(graph_dict[channel][key][4] + current_signal)/2   #average_signal

    channel_list = list(set(channel_list))
    channel_list.sort()
    
    channel_options.clear()
    channel_options.append({'label': 'all', 'value': 'all'})
    for channel in channel_list:
        channel_options.append({'label': channel, 'value': int(channel)})

    edge_df_handle = open(tmp_csvfile, 'w', newline='')
    edge_writer = csv.writer(edge_df_handle)
    edge_header = ['from_mac', 'to_mac', 'channel', 'total_packets', 'total_bytes', 'average_signal']
    edge_writer.writerow(edge_header)

    for channel in graph_dict:
        for key in graph_dict[channel]:
            from_mac = graph_dict[channel][key][0]
            to_mac = graph_dict[channel][key][1]
            total_packets = graph_dict[channel][key][2]
            total_bytes = graph_dict[channel][key][3]
            average_signal = graph_dict[channel][key][4]
            edge_writer.writerow([from_mac,to_mac,channel,total_packets,total_bytes,average_signal])
           
    edge_df_handle.flush()

    logging.info("Packets processed")

    return

def update_graph_data(channel):
    global nodes,edges,channel_list

    try:
     df = pd.read_csv(tmp_csvfile)
    except:
        return
 
    if channel != 'all':
        df = df.loc[df['channel'] == channel, :]

    node_list = list(set(df['from_mac'].unique().tolist() + df['to_mac'].unique().tolist()))
    node_translation_dict={
                                "Wi-Fi AP":                 ['#000000',12],      #black
                                "Wi-Fi Bridged":            ['#808080',10],      #grey
                                "Wi-Fi Device":             ['#008000',10],      #green
                                "Wi-Fi Device (Inferred)":  ['#808000',10],      #olive
                                "Wi-Fi Ad-Hoc":             ['#800080',10],      #purple   
                                "Wi-Fi WDS Device":         ['#008080',10],      #teal
                                "Wi-Fi WDS AP":             ['#C0C0C0',12],      #silver
                                "Unknown":                  ['#800000',10]}      #maroon
    
    if len(node_list) == 0:
        nodes.clear()
        node_list = ['Nothing to display']
        edges.clear()
    else:
        nodes = []

    for node_name in node_list:
        node_label = "Nothing to display"
        node_title = "Nothing to display"
        node_color = '#FF0000' #red
        node_size = 12
        if node_name != 'Nothing to display':
            node_label_unfiltered = get_cached_mac_details(node_name)['pretty_mac_name']
            node_label = node_label_unfiltered.replace(label_for_newline_in_graph,"\n")
            node_title = get_cached_mac_details(node_name)['node_details'] 
            node_color = node_translation_dict[get_cached_mac_details(node_name)['device_type']][0];
            node_size = node_translation_dict[get_cached_mac_details(node_name)['device_type']][1];
        nodes.append({
            'id': node_name, 
            'label': node_label, 
            'shape': 'dot', 
            'size': 10,
            'color': node_color, 
            'title': node_title,
            'font': {'size' : node_size, 'color': "black"}
            }),
                        
    for row in df.to_dict(orient='records'):
        source, target, packets, total_bytes, average_signal = row['from_mac'] , row['to_mac'], row['total_packets'], row['total_bytes'], row['average_signal']
        label = str(packets) + " packets <br/>" + str(total_bytes) + " bytes<br/>signal strength  " + str(average_signal) 
        edges.append({
            'id': source + "__" + target,
            'from': source,
            'to': target,
            'value': total_bytes,
            'color': {'color' : '#CCCCCC'},
            'width': 1,
            'font': {'size' : 10},
            'title': label
        })

    return True

try:
    os.remove(tmp_csvfile)
except:
    pass

channel_options=[]
channel_options.append({'label': 'all', 'value': 'all'})

graph_type_options=[]
graph_type_options.append({'label': 'AP -> Dest STA', 'value': 'apds'})
graph_type_options.append({'label': 'Source STA -> Dest STA', 'value': 'ssds'})
graph_type_options.append({'label': 'Source STA -> AP', 'value': 'ssap'})

# https://visjs.github.io/vis-network/docs/network/
network_options = {
    'height'        : '900px',
    'width'         : '100%',
    'interaction'   : {'hover' : True},
    'edges'         : {'arrows' : { 'to' : {'enabled': True,  'scaleFactor': 0.5} }, 'scaling' : { 'min': 1, 'max': 5 }},
    'physics'       : {'stabilization' :{'iterations': 1000}}, 
}

gui = html.Tr([html.Tr("Channel (CTRL-F5 update)"),
                html.Tr(dcc.Dropdown(id = 'channel',
                     options=channel_options,
                     value="all",
                     clearable=False)),
                html.Tr("Graph type"),
                html.Tr(dcc.Dropdown(id = 'graph_type',
                     options=graph_type_options,
                     value="apds",
                     clearable=False)), 
               html.Tr([dcc.Checklist(id = 'mac_privacy_filter',
                     options=[
                            {'label': 'mac_privacy_filter', 'value': 'mac_privacy_filter'},
                        ],
                        value=[])]),  
               html.Tr([dcc.Checklist(id = 'mac_multicast_filter',
                     options=[
                            {'label': 'mac_multicast_filter', 'value': 'mac_multicast_filter'},
                        ],
                        value=[])]),
               html.Tr([dcc.Checklist(id = 'gratuitous_arp_filter',
                     options=[
                            {'label': 'gratuitous_arp_filter', 'value': 'gratuitous_arp_filter'},
                        ],
                        value=[])]),
                html.Tr([dbc.Button( "Get Kismet data", id="get_ksimet_data", className="mr-2", n_clicks=0),html.Span(id="example-output", style={"verticalAlign": "middle",}),],),
                html.Tr("-------------------"), 
                html.Tr("Kismet credentials"),
                html.Tr(dcc.Input(id = 'kismet_credentials', value = ui_variables['kismet_credentials'], type="password", style={'textAlign': 'center'})),
                html.Tr("Kismet URI"),
                html.Tr(dcc.Input(id = 'kismet_uri', value = ui_variables['kismet_uri'], style={'textAlign': 'center'})),
                html.Tr("Rewind timeframe (s)"),
                html.Tr(dcc.Input(id = 'rewind_timeframe',value = ui_variables['rewind_timeframe'], style={'textAlign': 'center'})),
                html.Tr("Packet limit"),
                html.Tr(dcc.Input(id = 'packet_limit', value = ui_variables['packet_limit'], style={'textAlign': 'center'})),
                html.Tr("-------------------"),
                html.Tr("Wi-Fi AP", style={'background': '#000000', 'color': '#FFFFFF', 'font-size': '10px'}),
                html.Tr("Wi-Fi Bridged", style={'background': '#808080', 'color': '#FFFFFF', 'font-size': '10px'}),
                html.Tr("Wi-Fi Device", style={'background': '#008000', 'color': '#FFFFFF', 'font-size': '10px'}),
                html.Tr("Wi-Fi Device (Inferred)", style={'background': '#808000', 'color': '#FFFFFF', 'font-size': '10px'}),
                html.Tr("Wi-Fi Ad-Hoc", style={'background': '#800080', 'color': '#FFFFFF', 'font-size': '10px'}),
                html.Tr("Wi-Fi WDS Device", style={'background': '#008080', 'color': '#FFFFFF', 'font-size': '10px'}),
                html.Tr("Wi-Fi WDS AP", style={'background': '#404040', 'color': '#FFFFFF', 'font-size': '10px'}),
                html.Tr("Unknown", style={'background': '#800000', 'color': '#FFFFFF', 'font-size': '10px'}),
            ])

network = visdcc.Network(id = 'net', options = network_options)
row1 = html.Tr([html.Td(gui), html.Td(network)])
table_body = [html.Tbody([row1])]
table = dbc.Table(table_body)

app.layout = html.Div([ 
    table,
    #row1,
    #visdcc.Network(     id = 'net', 
    #                    options = network_options)
    ], style =  {'text-align': 'center'})

#update graph for new channel and rewind_timeframe
@app.callback(
    Output('net', 'data'),
    [   Input('graph_type', 'value'), Input('channel', 'value'), Input('kismet_credentials', 'value'), Input('kismet_uri', 'value'),
        Input('rewind_timeframe', 'value'),Input('get_ksimet_data', 'n_clicks'),
        Input('mac_privacy_filter', 'value'),Input('mac_multicast_filter', 'value'),Input('gratuitous_arp_filter', 'value'),
        Input('packet_limit', 'value')])

def myfun(graph_type, channel, kismet_credentials,kismet_uri,rewind_timeframe,n_clicks,
          mac_privacy_filter,mac_multicast_filter,gratuitous_arp_filter, packet_limit):
    
    global nodes,edges,ui_variables
    
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if kismet_credentials:
        ui_variables['kismet_credentials'] = kismet_credentials
    if kismet_uri:
        ui_variables['kismet_uri'] = kismet_uri
    
    if mac_privacy_filter:
        ui_variables['mac_privacy_filter'] = True
    else:
        ui_variables['mac_privacy_filter'] = False
    
    if mac_multicast_filter:
        ui_variables['mac_multicast_filter'] = True
    else:
        ui_variables['mac_multicast_filter'] = False

    if gratuitous_arp_filter:
        ui_variables['gratuitous_arp_filter'] = True
    else:
        ui_variables['gratuitous_arp_filter'] = False
    
    ui_variables['rewind_timeframe'] = rewind_timeframe
    ui_variables['packet_limit'] = int(packet_limit)

    if 'get_ksimet_data' in changed_id:
        create_edge_df(rewind_timeframe, graph_type) 
        update_graph_data(channel)
    
    data = {'nodes':nodes, 'edges':edges} 
    
    return data

if __name__ == '__main__':
    logging.info("Starting UI:")
    app.run_server(port=8050,host='0.0.0.0',debug=False)
