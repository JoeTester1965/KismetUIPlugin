#!/bin/sh
sudo airmon-ng stop wlan0mon
sudo airmon-ng stop wlan1mon
sudo usbreset 001/003
sleep 1
sudo usbreset 001/004
sleep 1
sudo airmon-ng check kill
sudo airmon-ng start wlan0
sudo airmon-ng start wlan1

