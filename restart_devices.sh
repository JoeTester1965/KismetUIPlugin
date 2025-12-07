#!/bin/sh
sudo airmon-ng stop wlan0mon
#sudo usbreset 001/004
sudo airmon-ng check kill
sudo airmon-ng start wlan0

