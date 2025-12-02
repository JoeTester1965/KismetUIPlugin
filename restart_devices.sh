#!/bin/sh
sudo airmon-ng stop wlan0mon
sudo airmon-ng stop wlan1mon
sudo ifconfig wlan0 down
sudo ifconfig wlan1 down
sudo usbreset 001/003
sudo usbreset 001/004
sudo ifconfig wlan0 up
sudo ifconfig wlan1 up
sudo airmon-ng check kill
sudo airmon-ng start wlan0
sudo airmon-ng start wlan1

