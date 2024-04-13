from cgi import test
from re import L
import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State
import visdcc
import pandas as pd
import time
import math

import sys
import json
import collections
import csv
import datetime 
import requests
import os
import logging

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO)

external_stylesheets = [
    'https://cdnjs.cloudflare.com/ajax/libs/vis/4.20.1/vis.min.css',
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

nodes = []
edges = []

label_to_replace_in_graph = ":-:"

mac_details_cache = collections.defaultdict(dict)
undirected_probes = collections.defaultdict(dict)
directed_probes = collections.defaultdict(dict)

channels_with_edges_list = []

channel_options=[]
channel_options.append({'label': 'all', 'value': 'all'})

tmp_csvfile = "edge_df.csv"

epoch = ""

ui_variables = {   
                    'channel' : 'all',
                    'graph_type' : 'db-device-and-bridge',
                    'rewind_seconds' : 3600,
                    'kismet_credentials' : 'username:password',
                    'kismet_uri' : '192.168.1.57:2501',
               }

def ieee80211_frequency_to_channel(freq_mhz):
    if (freq_mhz == 0):
        return 0
    if (freq_mhz == 2484):
        return 14
    if (freq_mhz < 2484):
        return ((freq_mhz - 2407) / 5)
    return (freq_mhz/5 - 1000) 

def pretty_format_hex(a):
    return ':'.join([a[i:i + 2] for i in range(0, len(a), 2)])

def create_edge_df(graph_type, graphing_channel):

    global ui_variables,channels_with_edges_list,channel_options,mac_details_cache,epoch,directed_probes,undirected_probes,devices_dict

    edge_df_handle = open(tmp_csvfile, 'w', newline='')
    edge_writer = csv.writer(edge_df_handle)
    edge_header = ['from_mac', 'to_mac', 'channel', 'total_packets', 'total_bytes'] 
    edge_writer.writerow(edge_header)

    kismet_login_uri =  "http://" + ui_variables['kismet_credentials'] + "@" + ui_variables['kismet_uri']

    logging.info("Sending login '%s'", kismet_login_uri)

    try:
        response = requests.get(kismet_login_uri, verify=False, timeout=10)
    except:
        logging.warn("No response received, check Kismet server and your API URI and credentials")
        return

    kismet_api_uri = "http://" + ui_variables['kismet_credentials'] + "@" + ui_variables['kismet_uri'] + "/system/status.json"

    logging.info("Sending request '%s'", kismet_api_uri)

        
    if kismet_api_uri:
        try:
            system_dict = requests.get(kismet_api_uri, verify=False, timeout=10).json()
            epoch_seconds = system_dict['kismet.system.timestamp.start_sec']
            epoch = datetime.datetime.fromtimestamp(epoch_seconds).strftime('%d-%m-%Y %H:%M:%S')
        except:
            return

    kismet_api_uri = "http://" + ui_variables['kismet_credentials'] + "@" + ui_variables['kismet_uri'] + "/devices/views/all/devices.json"

    logging.info("Sending request '%s'", kismet_api_uri)

    if kismet_api_uri:
        try:
             devices_dict = requests.get(kismet_api_uri, verify=False, timeout=10).json()
        except:
            return

        for device in devices_dict:

            mac = device['kismet.device.base.macaddr']
            retval_device_type = device['kismet.device.base.type']
            manuf = device['kismet.device.base.manuf']
            if not manuf or manuf == 'Unknown':
                stripped_mac = mac.replace(":","")
                u_l_bit = (int(stripped_mac[1], 16) & 2) >> 1
                if u_l_bit:
                    manuf = "Privacy"
                else:
                    manuf = ""
            retval_node_name = manuf + label_to_replace_in_graph + mac

            first_time_text = "First seen : " + datetime.datetime.fromtimestamp(device['kismet.device.base.first_time']).strftime('%c')
            last_time_text = "Last seen : " + datetime.datetime.fromtimestamp(device['kismet.device.base.last_time']).strftime('%c')

            if retval_device_type == 'Wi-Fi AP':
                retval_node_name = device['kismet.device.base.manuf'] + "\n" + mac + "\n" + device['kismet.device.base.name']
                retval_node_details =  first_time_text + "<br/>" + last_time_text + "<br/>" + "channel <b>" +  device['kismet.device.base.channel'] + "</b><br/>"  + device['kismet.device.base.macaddr']
        
            else:
                retval_node_details = first_time_text + "<br/>" + last_time_text 

            signal_strength = 0
            try:
                signal_strength = device['kismet.device.base.signal']['kismet.common.signal.last_signal']
            except:
                pass
            if signal_strength < 0:
                retval_node_details = retval_node_details + "<br/> Last seen signal strength: <b>" + str(signal_strength) + "</b>" 

            retval_node_details = retval_node_details + "<br/>"
          
            mac_details_cache[mac]['node_name'] = retval_node_name
            mac_details_cache[mac]['node_details'] = retval_node_details
            mac_details_cache[mac]['device_type'] = retval_device_type
            mac_details_cache[mac]['last_time'] = device['kismet.device.base.last_time']
            mac_details_cache[mac]['channel'] = device['kismet.device.base.channel']
            mac_details_cache[mac]['packets'] = device['kismet.device.base.packets.total']
            mac_details_cache[mac]['data'] = device['kismet.device.base.datasize']
            mac_details_cache[mac]['signal'] = 0

            try:
                mac_details_cache[mac]['signal'] = device['kismet.device.base.signal']['kismet.common.signal.last_signal'] 
            except:
                pass

        # Change this to call a function testing all device types, then only write of device type selected by UI
        for device in devices_dict:
            
            channel = device['kismet.device.base.channel']

            device_mac = device['kismet.device.base.macaddr']

            try:
                client_map_dict = device['dot11.device']['dot11.device.client_map']
                for client_mac in client_map_dict:
                    valid_device = False
                    if graph_type == 'db-device':
                        if device['kismet.device.base.type'] in['Wi-Fi Device', 'Wi-Fi Device (Inferred)','Wi-Fi WDS Device','Wi-Fi Ad-Hoc']:   
                            valid_device = True
                    if graph_type == 'db-bridge':
                        if device['kismet.device.base.type'] in['Wi-Fi Bridged']:   
                            valid_device = True
                    if graph_type == 'db-device-and-bridge':
                        if device['kismet.device.base.type'] in['Wi-Fi Device', 'Wi-Fi Device (Inferred)','Wi-Fi WDS Device','Wi-Fi Ad-Hoc', 'Wi-Fi Bridged']:   
                            valid_device = True

                    if valid_device == True:
                        packets=mac_details_cache[device_mac]['packets']
                        data=mac_details_cache[device_mac]['data']

                        if (int(time.time()) - client_map_dict[client_mac]['dot11.client.last_time']) < int(ui_variables['rewind_seconds']):
                            if graphing_channel == 'all':
                                edge_writer.writerow([device_mac,client_mac,channel,packets,data])
                                if int(mac_details_cache[device_mac]['channel']) == int(mac_details_cache[client_mac]['channel']):
                                    channels_with_edges_list.append(int(mac_details_cache[device_mac]['channel']))                     
                            else:
                                if (int(mac_details_cache[device_mac]['channel']) == graphing_channel) and (int(mac_details_cache[client_mac]['channel']) == graphing_channel): 
                                    edge_writer.writerow([device_mac,client_mac,channel,packets,data])
                                    channels_with_edges_list.append(int(mac_details_cache[device_mac]['channel'])) 
            except:
                pass

    channels_with_edges_list = list(set(channels_with_edges_list))
    channels_with_edges_list.sort()

    channel_options.clear()
    channel_options.append({'label': 'all', 'value': 'all'})
    for channel in channels_with_edges_list: 
        channel_options.append({'label': channel, 'value': int(channel)})

    kismet_api_uri =  "http://username:password@192.168.1.57:2501/phy/phy80211/ssids/views/ssids.prettyjson"

    logging.info("Sending kismet_api_uri '%s'", kismet_api_uri)

    try:
        response = requests.get(kismet_api_uri, verify=False, timeout=10)
    except:
        logging.warn("No response received, check Kismet server and your API URI and credentials")

    if response:
        ssid_dict = response.json()
        for ssid in ssid_dict:
            name = ssid['dot11.ssidgroup.ssid']
            if len(name) > 0:
                responding_devices_len = ssid['dot11.ssidgroup.responding_devices_len']
                probing_devices_len = ssid['dot11.ssidgroup.probing_devices_len']
                advertising_devices_len = ssid['dot11.ssidgroup.advertising_devices_len']
                    
                if ((responding_devices_len == 0) and (advertising_devices_len == 0) and (probing_devices_len > 0)):
                    probing_device_list = ssid['dot11.ssidgroup.probing_devices']
                    client_name_list = []
                    for probing_device in probing_device_list:
                        for device in devices_dict:
                            if probing_device == device['kismet.device.base.key']:
                                client_name_list.append(device['kismet.device.base.macaddr'])
                                    
                    client_name_list.sort()
                    undirected_probes[name]=client_name_list
                    
                if (((responding_devices_len > 0) or (advertising_devices_len > 0)) and (probing_devices_len > 0)):
                    probing_device_list = ssid['dot11.ssidgroup.probing_devices']
                    client_name_list = []
                    for probing_device in probing_device_list:
                        for device in devices_dict:
                            if probing_device == device['kismet.device.base.key']:
                                client_name_list.append(device['kismet.device.base.macaddr'])

                    client_name_list.sort()    
                    directed_probes[name]=client_name_list

    if graph_type == 'directed_probes':
        for ssid in directed_probes:
            mac_details_cache[ssid]['node_name'] = ssid
            mac_details_cache[ssid]['node_details'] = ""
            mac_details_cache[ssid]['device_type'] = "Wi-Fi AP"
            for mac in directed_probes[ssid]:
                edge_writer.writerow([ssid,mac,1,1,1])      
                
    if graph_type == 'undirected_probes':
        for ssid in undirected_probes:
            mac_details_cache[ssid]['node_name'] = ssid
            mac_details_cache[ssid]['node_details'] = ""
            mac_details_cache[ssid]['device_type'] = "Wi-Fi AP"
            for mac in undirected_probes[ssid]:
                edge_writer.writerow([ssid,mac,1,1,1])

    edge_df_handle.flush()
    edge_df_handle.close()

    logging.info("Kismet DB processed")
    return

def update_graph_data(channel):
    global nodes,edges,mac_details_cache,epoch

    try:
     df = pd.read_csv(tmp_csvfile)
    except:
        return
 
    if channel != 'all':
        df = df.loc[df['channel'] == channel, :]

    node_list = list(set(df['from_mac'].unique().tolist() + df['to_mac'].unique().tolist()))
    node_translation_dict={
                                "Wi-Fi AP":                 ['#000000'],      #black
                                "Wi-Fi Bridged":            ['#808080'],      #grey
                                "Wi-Fi Device":             ['#008000'],      #green
                                "Wi-Fi Client":             ['#008000'],      #green
                                "Wi-Fi Device (Inferred)":  ['#808000'],      #olive
                                "Wi-Fi Ad-Hoc":             ['#800080'],      #purple   
                                "Wi-Fi WDS Device":         ['#008080'],      #teal
                                "Wi-Fi WDS AP":             ['#C0C0C0'],      #silver
                                "Unknown":                  ['#800000']}      #maroon
    
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
        node_size = 10
        if node_name != 'Nothing to display':
            node_label_unfiltered = mac_details_cache[node_name]['node_name']
            node_label = node_label_unfiltered.replace(label_to_replace_in_graph,"\n")
            node_title = mac_details_cache[node_name]['node_details'] 
            node_color = node_translation_dict[mac_details_cache[node_name]['device_type']][0];
        nodes.append({
            'id': node_name, 
            'label': node_label, 
            'shape': 'dot', 
            'size': node_size,
            'color': node_color, 
            'title': node_title,
            'font': {'size' : 10, 'color': "black"}
            }),
                        
    for row in df.to_dict(orient='records'):
        source, target, packets, total_bytes = row['from_mac'] , row['to_mac'], row['total_packets'], row['total_bytes']
        if packets > 0:
            label = str(packets) + " packets average " + str(round(total_bytes/packets)) + " bytes  </br>since " + epoch
        else:
            label = ""
        if(total_bytes > 0):
            edges.append({
                'id': source + "__" + target,
                'from': source,
                'to': target,
                'value': math.log10(total_bytes),
                'color': {'color' : '#CCCCCC'},
                'width': 2,
                'font': {'size' : 10},
                'title': label
            })

    return True

try:
    os.remove(tmp_csvfile)
except:
    pass

graph_type_options=[]
graph_type_options.append({'label': 'Client device traffic', 'value': 'db-device'})
graph_type_options.append({'label': 'Bridged device traffic', 'value': 'db-bridge'})
graph_type_options.append({'label': 'All device traffic', 'value': 'db-device-and-bridge'})
graph_type_options.append({'label': 'Directed probes', 'value': 'directed_probes'})
graph_type_options.append({'label': 'Undirected probes', 'value': 'undirected_probes'})

# https://visjs.github.io/vis-network/docs/network/
network_options = {
    'height'        : '900px',
    'width'         : '100%',
    'interaction'   : {'hover' : True},
    'edges'         : {'scaling' : { 'min': 0.5, 'max': 5.0 }},
    'physics'       : {'solver': 'forceAtlas2Based', 'minVelocity': 0.75}
}

gui = html.Tr([ html.Tr("Channel"),
                html.Tr(dcc.Dropdown(id = 'channel',
                     options=[{'label': 'all', 'value': 'all'}],
                     value=ui_variables['channel'],
                     clearable=False)),
                html.Tr("Graph type"),
                html.Tr(dcc.Dropdown(id = 'graph_type',
                     options=graph_type_options,
                     value=ui_variables['graph_type'],
                     clearable=False)), 
                html.Tr("Uptime rewind seconds"),
                html.Tr(dcc.Input(id = 'rewind_seconds',value = ui_variables['rewind_seconds'], style={'textAlign': 'center'})), 
                html.Tr("Kismet credentials"),
                html.Tr(dcc.Input(id = 'kismet_credentials', value = ui_variables['kismet_credentials'], type="password", style={'textAlign': 'center'})),
                html.Tr("Kismet URI"),
                html.Tr(dcc.Input(id = 'kismet_uri', value = ui_variables['kismet_uri'], style={'textAlign': 'center'})),
                html.Tr("Wi-Fi AP", style={'background': '#000000', 'color': '#FFFFFF', 'font-size': '10px'}),
                html.Tr("Wi-Fi Bridged", style={'background': '#808080', 'color': '#FFFFFF', 'font-size': '10px'}),
                html.Tr("Wi-Fi Device", style={'background': '#008000', 'color': '#FFFFFF', 'font-size': '10px'}),
                html.Tr("Wi-Fi Device (Inferred)", style={'background': '#808000', 'color': '#FFFFFF', 'font-size': '10px'}),
                html.Tr("Wi-Fi Ad-Hoc", style={'background': '#800080', 'color': '#FFFFFF', 'font-size': '10px'}),
                html.Tr("Wi-Fi WDS Device", style={'background': '#008080', 'color': '#FFFFFF', 'font-size': '10px'}),
                html.Tr("Wi-Fi WDS AP", style={'background': '#404040', 'color': '#FFFFFF', 'font-size': '10px'}),
                html.Tr("Unknown", style={'background': '#800000', 'color': '#FFFFFF', 'font-size': '10px'}),
                html.Tr([dbc.Button( "Update graph", id="update_graph", n_clicks=0),html.Span(id="button-1", style={"verticalAlign": "middle"}),],),     
                html.Tr(""),
                html.Tr(""),
                html.Tr(""),
                html.Tr(""),
                html.Tr([dbc.Button( "Daily stats download", id="stats", n_clicks=0, download="stats.zip", external_link=True,),html.Span(id="button-2", style={"verticalAlign": "middle",}),],),
                dcc.Download(id="download-dataframe"),
            ])

network = visdcc.Network(id = 'net', options = network_options)
row1 = html.Tr([html.Td(gui), html.Td(network)])
table_body = [html.Tbody([row1])]
table = dbc.Table(table_body)

app.layout = html.Div([table], style =  {'text-align': 'center'})

@app.callback(
    Output('channel', 'options'),
    [State('channel', 'options'), Input('graph_type', 'value'), Input('channel', 'value'), 
        Input('kismet_credentials', 'value'), Input('kismet_uri', 'value'), Input('rewind_seconds', 'value')])
def myfun1(existing_options, graph_type, channel, kismet_credentials, kismet_uri, rewind_seconds): 

    global channels_with_edges_list

    existing_options.clear()
    existing_options.append({'label': 'all', 'value': 'all'})
    for channel_seen in channels_with_edges_list: 
        existing_options.append({'label': channel_seen, 'value': int(channel_seen)})

    ui_variables['graph_type'] = graph_type
    ui_variables['channel'] = channel
    ui_variables['rewind_seconds'] = rewind_seconds
    ui_variables['kismet_credentials'] = kismet_credentials
    ui_variables['kismet_uri']= kismet_uri

    return existing_options

@app.callback(
       Output('net', 'data'),
        [Input('update_graph', 'n_clicks')])
def myfun3(n_clicks):
    
    global nodes,edges,ui_variables
    
    nodes.clear()
    edges.clear()
    mac_details_cache.clear()
    create_edge_df(ui_variables['graph_type'], ui_variables['channel']) 
    update_graph_data(ui_variables['channel'])

    data = {'nodes':nodes, 'edges':edges} 
    
    return data

@app.callback(
    Output('download-dataframe', 'data'),
    [Input('stats', 'n_clicks')],
    prevent_initial_call=True)
def myfun4(n_clicks):
      
    return dcc.send_file("stats.zip")

if __name__ == '__main__':
    create_edge_df('db-device', 'all') # set channel list 
    logging.info("Starting UI:")
    app.run_server(port=8050,host='0.0.0.0',debug=False)
