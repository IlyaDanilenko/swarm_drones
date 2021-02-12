#! /bin/bash
sudo systemctl stop NetworkManager
sudo systemctl disable NetworkManager
sudo systemctl enable config-wlan.service
sudo systemctl start config-wlan.service 
sudo systemctl enable isc-dhcp-server.service
sudo systemctl start isc-dhcp-server.service 
sudo systemctl enable hostapd.service
sudo systemctl start hostapd.service
