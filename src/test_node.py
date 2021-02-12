#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from rospy import Subscriber, Publisher
from rospy import Res
from gs_interfaces.msg import SimpleBatteryState
from std_msgs.msg import Int32
from time import sleep

def callback_bat(date):
    global power
    power = date
rospy.init_node("ros_test_node")

power = SimpleBatteryState()
pub = Publisher("white/int_bat", Int32, queue_size=10)
sub_bat = Subscriber("geoscan/battery_state", SimpleBatteryState, callback_bat)

while not rospy.is_shutdown():
    rospy.loginfo(power)
    pub.publish(int(power.charge))
    sleep(0.5)
    pass
