#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from rospy import Subscriber, Publisher 
from gs_flight import FlightController, CallbackEvent
from gs_board import BoardManager
from time import sleep
from rospy import ServiceProxy
from swarm_drones.srv import TakeScreen, TakeScreenResponse
from multimaster.srv import DiscoveryMasters, DiscoveryMastersResponse, DiscoveryMastersRequest
from gs_interfaces.msg import SimpleBatteryState
from std_msgs.msgs import Int32, Int16MultiArray

f_vac=0 # флаг сделанной фотографии
num_photos=0 # кол-во сделанных фото
rospy.init_node("main_node")

coordinates = []# координаты точек

coord_0=coordinates[1]
h=coord_0[3]
 
run = True
position_number = 0


def handle_came(event):
    event=1
def gotohome():
    ap.goToLocalPoint(0, 0, h)
    ap.landing()
def callback(event):#полёт по точкам
    global ap
    global run
    global coordinates
    global position_number
    global proxy_cam

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
        f_vac=proxy_cam()
        if f_vac.stait_img == 1:
            num_photos=position_number
        else:
            gotohome()  
        position_number += 1
        if position_number < len(coordinates):
            ap.goToLocalPoint(coordinates[position_number][0], coordinates[position_number][1], coordinates[position_number][2])
        else:
            gotohome()
    elif event == CallbackEvent.COPTER_LANDED:
        rospy.loginfo("finish programm")
        run = False

def callback_point(data):
    coordinates=data
    coord_0=coordinates[1]
    h=coord_0[3]
def callback_bat(data):
    global bat
    bat=data
    if bat<10.5:
        gotohome()
board = BoardManager()
ap = FlightController(callback)
once = False

pub_photos = Publisher("white/work_completed", Int32, queue_size=10)
sub_point=Subscriber("points", Int16MultiArray,callback_point)
sub_bat=Subscriber("geoscan/battery_state", SimpleBatteryState, callback_bat)
proxy=ServiceProxy("master_discovery/get_loggers", DiscoveryMasters, )
proxy_cam=ServiceProxy("swarm/take_photos", TakeScreen,)

while not rospy.is_shutdown():
    if board.runStatus() and not once:
        rospy.loginfo("start programm")
        ap.preflight()
        once = True
    master = DiscoveryMastersRequest()
    pub_photos.publish(num_photos/len(coordinates)) #публикуем процент выполненной работы