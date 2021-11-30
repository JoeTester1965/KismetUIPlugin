import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State
import visdcc
import pandas as pd
import time
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

channel_list = []

tmp_csvfile = "edge_df.csv"

ui_variables = {   
                    'channel' : 'all',
                    'graph_type' : 'db',
                    'rewind_seconds' : 60,
                    'kismet_credentials' : 'user:password',
                    'kismet_uri' : '192.168.1.50:2501',
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

def create_edge_df_from_db(graphing_channel):

    global ui_variables, channel_list, channel_options, mac_details_cache

    kismet_api_uri = "http://" + ui_variables['kismet_credentials'] + "@" + ui_variables['kismet_uri'] + "/devices/views/all/devices.json"

    logging.info("Sending request '%s'", kismet_api_uri)

    edge_df_handle = open(tmp_csvfile, 'w', newline='')
    edge_writer = csv.writer(edge_df_handle)
    edge_header = ['from_mac', 'to_mac', 'channel', 'total_packets', 'total_bytes', 'average_signal'] 
    edge_writer.writerow(edge_header)

    kismet_login_uri =  "http://" + ui_variables['kismet_credentials'] + "@" + ui_variables['kismet_uri']

    logging.info("Sending login '%s'", kismet_login_uri)

    try:
        response = requests.get(kismet_login_uri)
    except:
        logging.warn("No response received, check Kismet server and your API URI and credentials")
        return
        pass

    try:
        response = requests.get(kismet_api_uri)
    except:
        logging.warn("No API response received, check Kismet server and your API URI and credentials")
        pass

    if response.content:
        try:
             devices_dict = json.loads(response.content)
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

            type_text = "Type : " + retval_device_type
            ap_name_text = ""

            first_time_text = "First seen : " + datetime.datetime.fromtimestamp(device['kismet.device.base.first_time']).strftime('%c')
            last_time_text = "Last seen : " + datetime.datetime.fromtimestamp(device['kismet.device.base.last_time']).strftime('%c')

            if retval_device_type == 'Wi-Fi AP':
                if device['kismet.device.base.name'] == "":
                    retval_node_name = mac
                else:
                    retval_node_name = device['kismet.device.base.name']

                retval_node_details = "channel " +  device['kismet.device.base.channel'] + "<br/>" + device['kismet.device.base.manuf'] + "<br/>" + device['kismet.device.base.macaddr'] + "<br/>" + first_time_text + "<br/>" + last_time_text
        
            else:
                retval_node_details = first_time_text + "<br/>" + last_time_text

            mac_details_cache[mac]['node_name'] = retval_node_name
            mac_details_cache[mac]['node_details'] = retval_node_details
            mac_details_cache[mac]['device_type'] = retval_device_type
            mac_details_cache[mac]['last_time'] = device['kismet.device.base.last_time']
            mac_details_cache[mac]['channel'] = device['kismet.device.base.channel']
        
        for device in devices_dict:
            if device['kismet.device.base.type'] == 'Wi-Fi AP':
                channel = device['kismet.device.base.channel']
                channel_list.append(int(channel))
                ap_mac = device['kismet.device.base.macaddr']

                try:
                    client_map_dict = device['dot11.device']['dot11.device.associated_client_map']
                    for client_mac in client_map_dict:
                        if mac_details_cache[client_mac]:
                            if (int(time.time()) - mac_details_cache[client_mac]['last_time']) < int(ui_variables['rewind_seconds']):
                                if graphing_channel == 'all':
                                    edge_writer.writerow([ap_mac,client_mac,channel,0,0,0])       
                                else:
                                    if (int(mac_details_cache[ap_mac]['channel']) == graphing_channel):
                                        edge_writer.writerow([ap_mac,client_mac,channel,0,0,0])
                except:
                    pass
           
    edge_df_handle.flush()
    edge_df_handle.close()

    channel_list = list(set(channel_list))
    channel_list.sort()
    
    channel_options.clear()
    channel_options.append({'label': 'all', 'value': 'all'})
    for channel in channel_list:
        channel_options.append({'label': channel, 'value': int(channel)})

    logging.info("Kismet DB processed")
    return

def create_edge_df(graph_type, channel):

    mac_details_cache.clear()

    if graph_type == 'db':
        create_edge_df_from_db(channel)
        return

    return

def update_graph_data(channel):
    global nodes,edges,channel_list,mac_details_cache

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
        node_size = 12
        if node_name != 'Nothing to display':
            node_label_unfiltered = mac_details_cache[node_name]['node_name']
            node_label = node_label_unfiltered.replace(label_to_replace_in_graph,"\n")
            node_title = mac_details_cache[node_name]['node_details'] 
            node_color = node_translation_dict[mac_details_cache[node_name]['device_type']][0];
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
        if packets > 0:
            label = str(packets) + " packets <br/>" + str(total_bytes) + " bytes<br/>signal strength  " + str(average_signal) 
        else:
            label = ""
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
graph_type_options.append({'label': 'Kismet DB', 'value': 'db'})

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
                     options=channel_options,
                     value=ui_variables['channel'],
                     clearable=False)),
                html.Tr("Graph type"),
                html.Tr(dcc.Dropdown(id = 'graph_type',
                     options=graph_type_options,
                     value=ui_variables['graph_type'],
                     clearable=False)), 
                html.Tr("Rewind seconds"),
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
                html.Tr([dbc.Button( "Refresh", id="get_ksimet_data", className="mr-2", n_clicks=0),html.Span(id="example-output", style={"verticalAlign": "middle",}),],),
                html.A(html.Button('Reset'),href='/'),
            ])

network = visdcc.Network(id = 'net', options = network_options)
row1 = html.Tr([html.Td(gui), html.Td(network)])
table_body = [html.Tbody([row1])]
table = dbc.Table(table_body)

app.layout = html.Div([table], style =  {'text-align': 'center'})

#update graph for new channel and rewind_seconds
@app.callback(
    Output('net', 'data'),
    [   Input('graph_type', 'value'), Input('channel', 'value'), Input('kismet_credentials', 'value'), Input('kismet_uri', 'value'),
        Input('rewind_seconds', 'value'),Input('get_ksimet_data', 'n_clicks')])

def myfun(graph_type, channel, kismet_credentials,kismet_uri,rewind_seconds,n_clicks):
    
    global nodes,edges,ui_variables

    refresh = False
    
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if graph_type:
         ui_variables['graph_type'] = graph_type
         refresh = True

    if channel:
         ui_variables['channel'] = channel
         refresh = True

    if kismet_credentials:
        ui_variables['kismet_credentials'] = kismet_credentials
        refresh = True
    
    if kismet_uri:
        ui_variables['kismet_uri'] = kismet_uri
        refresh = True

    if rewind_seconds:
        ui_variables['rewind_seconds'] = rewind_seconds
        refresh = True

    if 'get_ksimet_data' in changed_id:
        refresh = True

    if refresh == True:
        nodes.clear()
        edges.clear()
        mac_details_cache.clear()
        create_edge_df(graph_type, channel) 
        update_graph_data(channel)
    
    data = {'nodes':nodes, 'edges':edges} 
    
    return data

if __name__ == '__main__':
    create_edge_df('db', 'all') # set channel list 
    logging.info("Starting UI:")
    app.run_server(port=8050,host='0.0.0.0',debug=False)
