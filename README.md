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

Tested on Kali Linux release 2023.2 (ARM, Pi4)

Install [Kismet](https://www.kismetwireless.net/) then:

``` console
sudo apt-get install python3-pandas python3-pandas-lib libopenblas-dev tshark

pip3 install -r requirements.txt

chmod u+x start.sh

chmod u+x stop.sh
```
You may want to follow the instructions [here](https://github.com/kismetwireless/kismet/blob/master/packaging/systemd/README) to install kismet as a managed service (note that you may need to set the user and group of the modified system service to your usual username and group, not kismet!). If you do this, remove the respective lines for **kismet** in [start.sh](start.sh) and [stop.sh](stop.sh). 

I found that using the remote capture tool *kismet_cap_linux_wifi* was more reliable for running over extended periods than adding local capture interfaces to the kismet GUI. See [start.sh](start.sh) which includes an example that you will need to edit to meet your needs.


By default this visualisation server runs on port 8050, change the line at the bottom of the [python code](./KismetUIPlugin.py) if needed.

# Using

Edit [start.sh](start.sh) to meet your interface needs then:

``` console
./start.sh
./stop.sh
```
Put something like [this](crontab) in your crontab file to autostart on boot then also restart every 24 hours and manage database growth.

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

# Brucie Bonus, real time Probe alerts and better visibility

You can run [start_realtime.sh](start_realtime.sh) as root and then get MQTT alerts when a probe comes in based on what is in what is in [process_real_time_probes.example.cfg](process_real_time_probes.example.cfg).

Also The 'Probes as CSV' button on the UI can be used to dowload a file, which when processed with [probe_viewer.py](probe_viewer.py) gives you this:

<img src="./example-probes.jpg">

Enjoy


