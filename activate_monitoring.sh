#!/bin/sh
sudo airmon-ng stop wlan0mon  2>/dev/null
#sudo usbreset 001/004
sudo airmon-ng check kill 2>/dev/null
sudo airmon-ng start wlan0 2>/dev/null

while true; do
    sudo iwconfig wlan0mon channel 1
    sleep 1
    sudo iwconfig wlan0mon channel 6
    sleep 1
    sudo iwconfig wlan0mon channel 11
    sleep 1
done
