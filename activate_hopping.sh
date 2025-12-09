#!/bin/sh

while true; do
    sudo iwconfig wlan0mon channel 1
    sleep 1
    sudo iwconfig wlan0mon channel 6
    sleep 1
    sudo iwconfig wlan0mon channel 11
    sleep 1
done
