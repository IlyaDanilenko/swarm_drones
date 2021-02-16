#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from rospy import Service, ServiceProxy
from swarm_drones.srv import VotiResponse, VotiRequest, Voti

def handle_voti_res(req):
    global voit
    voit=1
    return voit # вставить id коптера

rospy.init_node("samopal_node")

service_voit_res = Service("swarm_drones/voit_res", Voti, handle_voti_res)

while not rospy.is_shutdown():
    pass