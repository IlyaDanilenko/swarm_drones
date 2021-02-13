#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import rospy
from rospy import ServiceProxy
from swarm_drones.srv import Repeater, RepeaterResponse, RepeaterRequest


rospy.init_node("repeater_node")

networksNames = ["Geoscan-Orange", "Geoscan-White", "Geoscan-Blue"]
# subprocess.call("echo connect", shell=True)

def connectToWifi(networkId):
    global networksNames
    print("connecting to ", networkId)
    subprocess.Popen(["sh","bashscrpt/enableNetworkManager.sh"],stdout=subprocess.PIPE).communicate()
    subprocess.Popen("nmcli device wifi connect \"{}\" password geoscan123 name \"{}\"".format(networksNames[networkId],networksNames[networkId]), shell=True).communicate()


def enableHotspot():
    subprocess.Popen("sh bashscrpt/enableNetworkManagerHotspot.sh", stdout=subprocess.PIPE).communicate()

def wifiConnect(req):
    if req.command == 1:
        connectToWifi(req.id)
    elif req.command == 2:
        enableHotspot()
    return 1
    # return 192 when complited


proxy = Service("Repeater", Repeater, wifiConnect)
