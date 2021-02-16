#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import rospy
from rospy import Publisher, Subscriber
from rospy import Service
from swarm_drones.srv import Repeater, RepeaterResponse, RepeaterRequest
from gs_interfaces.msg import SimpleBatteryState
from std_msgs.msg import Int32, Bool

rospy.init_node("repeater_node")

networksNames = ["Geoscan-White", "Geoscan-Blue", "Geoscan-Orange"]
# subprocess.call("echo connect", shell=True)

low_battery=False
def connectToWifi(networkId):
    global networksNames
    print("connecting to ", networkId)
    subprocess.Popen(["sh","/home/ubuntu/geoscan_ws/src/swarm_drones/bash/enableNetworkManager.sh"],stdout=subprocess.PIPE).communicate()
    subprocess.Popen("nmcli device wifi connect \"{}\" password geoscan123 name \"{}\"".format(networksNames[networkId],networksNames[networkId]), shell=True).communicate()

def enableHotspot():
    subprocess.Popen("sh /home/ubuntu/geoscan_ws/src/swarm_drones/bash/enableNetworkManagerHotspot.sh", stdout=subprocess.PIPE).communicate()

def wifiConnect(req):
    if req.command == 1:
        connectToWifi(req.id)
    elif req.command == 2:
        enableHotspot()
    return 1
    # return 192 when complited
def callback_low_battery(data):
    global low_battery
    low_battery=data
"""def callback_req(data):
    global com
    com = data"""



pub_stateRep = Publisher("swarm_drones/state_repeater", Int32, queue_size=4)
proxy = Service("swarm_drones/to_repeater", Repeater, wifiConnect)
sub_low_battery = Subscriber("swarm_drones/white/low_battery", Bool, callback_low_battery)

while not rospy.is_shutdown():
    if low_battery==True:
        pub_stateRep.publish(-1)
    pub_stateRep.publish(0)
    pass
