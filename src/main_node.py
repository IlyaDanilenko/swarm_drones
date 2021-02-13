#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from rospy import Subscriber, Publisher 
from gs_flight import FlightController, CallbackEvent
from gs_board import BoardManager
from gs_sensors import SensorManager
from time import sleep
from rospy import ServiceProxy
from swarm_drones.srv import TakeScreen, TakeScreenResponse
from multimaster.srv import DiscoveryMasters, DiscoveryMastersResponse, DiscoveryMastersRequest
from gs_interfaces.msg import SimpleBatteryState
from std_msgs.msgs import Int32, Int16MultiArray

rospy.init_node("main_node")
sensor_manager = SensorManager()
_, charge = sensor_manager.power()

f_vac=0 # флаг сделанной фотографии
num_photos=0 # кол-во сделанных фото
f_reached=0 # флаг достижения точки при возврате
f_arr=0
rospy.init_node("main_node")

coordinates = []# координаты точек

 
run = True
position_number = 0

to_home = False

def goToHome():
    global to_home
    global h
    to_home = True
    ap.goToLocalPoint(0, 0, h)

def callback(event):#полёт по точкам
    global ap
    global run
    global coordinates
    global position_number
    global proxy_cam
    global to_home
    global num_photos

    event = event.data
    if charge<=10.5:
        goToHome()
    else:
        if event == CallbackEvent.ENGINES_STARTED:
            rospy.loginfo("engine started")
            ap.takeoff()
        if(repeat==0):
            if event == CallbackEvent.TAKEOFF_COMPLETE:
                rospy.loginfo("takeoff complite")
                position_number = 0
                ap.goToLocalPoint(coordinates[position_number][0], coordinates[position_number][1], coordinates[position_number][2])
            if event == CallbackEvent.POINT_REACHED:
                if to_home:
                    ap.landing()
                else:
                    rospy.loginfo("point {} reached".format(position_number))
                    position_number += 1
                    if position_number < len(coordinates):
                        ap.goToLocalPoint(coordinates[position_number][0], coordinates[position_number][1], coordinates[position_number][2])
            elif event == CallbackEvent.COPTER_LANDED:
                rospy.loginfo("finish programm")
                run = False
        else:
            if event == CallbackEvent.TAKEOFF_COMPLETE:
                rospy.loginfo("takeoff complite")
                ap.updateYaw(0)
                position_number = 0
                ap.goToLocalPoint(coordinates[position_number][0], coordinates[position_number][1], coordinates[position_number][2])
            if event == CallbackEvent.POINT_REACHED:
                if to_home:
                    ap.landing()
                else:
                    rospy.loginfo("point {} reached".format(position_number))
                    f_vac=proxy_cam()
                    if f_vac.stait_img == 1:
                        num_photos=position_number
                        position_number += 1
                    else:
                        goToHome()
                        rospy.logwarn("Camera-truble")
                    if position_number < len(coordinates):
                        ap.goToLocalPoint(coordinates[position_number][0], coordinates[position_number][1], coordinates[position_number][2])
                    else:
                        goToHome()
            elif event == CallbackEvent.COPTER_LANDED:
                rospy.loginfo("finish programm")
                run = False

def callback_point(data):
    global h
    global coordinates
    coordinates=data
    h=coordinates[1][3]
def callback_state(data):
    global repeat
    repeat = data
board = BoardManager()
ap = FlightController(callback)
once = False

pub_photos = Publisher("white/work_completed", Int32, queue_size=10)
sub_point=Subscriber("white/points", Int16MultiArray,callback_point)
sub_stateRep = Subscriber("swarm_drones/state_repeater", Int32, callback_state)
#proxy=ServiceProxy("master_discovery/get_loggers", DiscoveryMasters, )
proxy_cam=ServiceProxy("swarm/take_photos", TakeScreen,)

while not rospy.is_shutdown():
    if board.runStatus() and not once:
        rospy.loginfo("start programm")
        ap.preflight()
        once = True
    #master = DiscoveryMastersRequest()
    pub_photos.publish(num_photos/len(coordinates)*100) #публикуем процент выполненной работы