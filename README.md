# KismetUIPlugin

Pretty useful graphs for [Kismet](https://github.com/kismetwireless/kismet) like below:

<table>
  <tr>
    <td><img src="./1.JPG" width="400"</td>
    <td><img src="./2.JPG" width="400"</td>
  </tr>
  <tr>
     <td><img src="./3.JPG" width="400"</td>
     <td><img src="./4.JPG" width="400"</td>
  </tr>
</table>

# Installing

Install [Kismet](https://www.kismetwireless.net/) then:

``` console
chmod u+x start.sh

chmod u+x stop.sh

sudo apt-get install python3-pandas python3-pandas-lib libopenblas-dev tshark

python3 -m venv venv

source venv/bin/activate

pip3 install -r requirements.txt
```
By default this visualisation server runs on port 8050, change the line at the bottom of the [python code](./KismetUIPlugin.py) if needed.

# Using

**Important:** Edit /etc/kismet/kismet.conf to meet your interface needs.

**Important:** Then edit the bottom line of and [start.sh](start.sh) to capture probes if needed on your prmoiscous wlan interface/s. Default is *wlan0mon*.

Then:

``` console
./start.sh
./stop.sh
```

For kismet configuration usually best to use [kismet_site.conf](https://www.kismetwireless.net/docs/readme/configuring/configfiles/). 

For example to set capture card to wlan0 and disable all packet logging:

```
sudo touch /etc/kismet/kismet_site.conf
```

Then edit that file as root to contain:

```
source=wlan0
kis_log_packets=false
```

# User interface

You can interact with the graph (important as information may be hiding off the screen) as follows:

**Mouse** | **Feature**
----- | -------
```Wheel``` | Zoom in and out
```Left button``` | Drag whole graph or specific nodes
```Hover``` | Node and edge information

You can interact with the menu as follows:

**Label** | **Explanation**
----- | -----------
```Channel``` | Select all or a specific channel seen, this list is updated dynamically by refreshing your browser (CTRL F5)
```Graph type``` | Choose what to graph
```Kismet credentials``` | username:password e.g. me:12345
```Kismet URI``` | Kismet API URI e.g. 192.168.1.50:2501
```Rewind timeframe (s)``` | How long back you will start to look, bigger values mean bigger graphs, and too small will yield nothing
```Refresh``` | Refresh the graph based on what you have
```Reset``` | Reset the graph back to defaults

# Real time Probe alerts

You can get MQTT alerts when a probe comes in based on what is in what is in [process_real_time_probes.example.cfg](process_real_time_probes.example.cfg).

This will only work if tshark is configured for non root users (default). 

Otherwise use this and allow non-superusers to captur packets. 
```
sudo dpkg-reconfigure wireshark-common
```

Then do this to add your user to the worshar group, you may need to log out and in again for this to take effect.
```
sudo usermod -aG wireshark pi
```

# Automated periodic probed ssid visualisation 

<img src="./example-probes.jpg">

Put something like [this](crontab) in your crontab file to update visualisation images say every 24 hours but changing */home/pi/Documents/Share/wifi* to what works for you.

Enjoy


