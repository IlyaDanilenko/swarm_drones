#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from time import sleep
from rospy import Publisher
from rospy import Subscriber
from swarm_drones.msg import Telemetry
from gs_interfaces.msg import SimpleBatteryState
from gs_interfaces.msg import SatellitesGPS
from gs_interfaces.msg import PointGPS
from swarm_drones.srv import VotingResponse, VotingRequest, Voting

satel = SatellitesGPS()
position = PointGPS()
power = SimpleBatteryState()

def callback_sat(data):
    global satel
    satel = data

def callback_bat(data):
    global power
    power = data

def callback_pos(data):
    global position
    position = data
 

rospy.init_node("communication_node")
pub = Publisher("white/telemetry", Telemetry, queue_size=10)
sub_sat = Subscriber("geoscan/navigation/global/satellites", SatellitesGPS, callback_sat)
sub_bat = Subscriber("geoscan/battery_state", SimpleBatteryState, callback_bat)
sub_pos = Subscriber("geoscan/navigation/global/position", PointGPS, callback_pos)
while not rospy.is_shutdown():
    tel = Telemetry()
    tel.charg = power
    tel.position = position
    tel.sat = satel
    pub.publish(tel)
    sleep(1)