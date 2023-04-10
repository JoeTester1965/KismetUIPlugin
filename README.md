# KismetUIPlugin

Pretty useful graphs for [Kismet](https://github.com/kismetwireless/kismet) like below:

![!](./UI.JPG "")

# Installing

Python script developed and tested with python 3.9.2

Install [Kismet](https://www.kismetwireless.net/) then:

``` console
sudo apt-get install python3-pandas and python3-pandas-lib

pip install -r requirements.txt

chmod u+x start.sh

chmod u+x stop.sh
```
By default this visualisation server runs on port 8050, change the line at the bottom of the [python code](./KismetUIPlugin.py) if needed.

# Using

``` console
./start.sh
./stop.sh
```
Put something like this in your cron file to restart every 24 hours and manage database growth:

``` console
0 0 * * * (cd /home/pi/Documents/KismetUIPlugin; bash ./stop.sh; bash ./start.sh)
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

Enjoy


