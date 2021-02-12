#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from rospy import Subscriber, Publisher 
from gs_flight import FlightController, CallbackEvent
from gs_board import BoardManager
from time import sleep
from rospy import ServiceProxy
from swarm_drones.srv import TakeScreen, TakeScreenResponse, TakeScreenRequest
from multimaster.srv import DiscoveryMasters, MasterResponse, MasterRequest
from std_msgs.msgs import Int32

vac=0
num_photos=0
rospy.init_node("main_node")

coordinates = []# координаты точек

run = True
position_number = 0


def handle_came(event):
    event=1

def callback(event):#полёт по точкам
    global ap
    global run
    global coordinates
    global position_number

    event = event.data
    if event == CallbackEvent.ENGINES_STARTED:
        rospy.loginfo("engine started")
        ap.takeoff()
    elif event == CallbackEvent.TAKEOFF_COMPLETE:
        rospy.loginfo("takeoff complite")
        position_number = 0
        ap.goToLocalPoint(coordinates[position_number][0], coordinates[position_number][1], coordinates[position_number][2])
    elif event == CallbackEvent.POINT_REACHED:
        rospy.loginfo("point {} reached".format(position_number))
        vac=TakeScreenRequest()
        position_number += 1
        num_photos=position_number
        if position_number < len(coordinates):
            ap.goToLocalPoint(coordinates[position_number][0], coordinates[position_number][1], coordinates[position_number][2])
        else:
            ap.landing()
    elif event == CallbackEvent.COPTER_LANDED:
        rospy.loginfo("finish programm")
        run = False

board = BoardManager()
ap = FlightController(callback)
once = False

pub_photos = Publisher("white/work_completed", Int32, queue_size=10)
proxy=ServiceProxy("master_discovery/get_loggers", DiscoveryMasters, ) # ввести название сервиса
proxy_cam=ServiceProxy("swarm/take_photos", TakeScreen)

while not rospy.is_shutdown():
    if board.runStatus() and not once:
        rospy.loginfo("start programm")
        ap.preflight()
        once = True
    master=MasterRequest()
    pub_photos.publish(num_photos/len(coordinates)) #публикуем процент выполненной работы