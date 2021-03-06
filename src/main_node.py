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
from gs_interfaces.msg import SimpleBatteryState
#from gs_interfaces.msg import PointGPS
from geometry_msgs.msg import Point
from std_msgs.msg import Int32, Bool
from swarm_drones.msg import Array, Array_o

f_vac=0 # флаг сделанной фотографии
num_photos=0 # кол-во сделанных фото
f_reached=0 # флаг достижения точки при возврате
f_arr=0 
rospy.init_node("main_node")

coordinates = []# координаты точек

 
run = True
position_number = 0
latitude = 0.0
longitude = 0.0
all_points = 1
repeat = 0

to_home = False

def goToHome():
    global to_home
    global h
    to_home = True
    ap.goToLocalPoint(lat_home, lon_home, h)
def callback(event):#полёт по точкам
    global ap
    global run
    global coordinates
    global position_number
    global proxy_cam
    global to_home
    global num_photos
    global low_battery
    event = event.data
    if low_battery==True:
        goToHome()
    else:
        if event == CallbackEvent.ENGINES_STARTED:
            rospy.loginfo("engine started")
            ap.takeoff()
        if(repeat==0):
            if event == CallbackEvent.TAKEOFF_COMPLETE:
                rospy.loginfo("takeoff complite")
                # position_number = 0
                # ap.goToLocalPoint(coordinates[position_number][0], coordinates[position_number][1], coordinates[position_number][2])
            if event == CallbackEvent.POINT_REACHED:
                if to_home:
                    ap.landing()
                else:
                    rospy.loginfo("point {} reached".format(position_number))
                    position_number += 1
                    coordinates=coordinates[:]
                    if position_number < len(coordinates):
                        ap.goToLocalPoint(coordinates[position_number][0], coordinates[position_number][1], coordinates[position_number][2])
            elif event == CallbackEvent.COPTER_LANDED:
                rospy.loginfo("finish programm")
                run = False
        else:
            if event == CallbackEvent.TAKEOFF_COMPLETE:
                rospy.loginfo("takeoff complite")
                ap.updateYaw(0)
                # position_number = 0
                # ap.goToLocalPoint(coordinates[position_number][0], coordinates[position_number][1], coordinates[position_number][2])
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
def callback_point(coord):
    global h
    global all_points
    global ap
    global coordinates
    global position_number
    all_points=len(coord.data)
    h=coord.data[1].data[3]
    if repeat==0 and num_photos/all_points==1:
        coordinates=in_point # массив точек для доснятия
    else:
        for i in coord.data:
            coordinates.append([i[0], i[1], i[2]])
    position_number = 0
    ap.goToLocalPoint(coordinates[position_number][0], coordinates[position_number][1], coordinates[position_number][2])
def callback_state(data):
    global repeat
    repeat = data
def callback_pos(data):
    global latitude
    global longitude
    latitude = data.y
    longitude = data.x
def callback_in_point(data):
    global in_point
    in_point=data
print("board")
board = BoardManager()
ap = FlightController(callback)
sensor_manager = SensorManager()
_, charge = sensor_manager.power()
once = False

pub_photos = Publisher("swarm_drones/white/work_completed", Int32, queue_size=10)
pub_low_battery = Publisher("swarm_drones/white/low_battery", Bool, queue_size=10)
pub_out_points_low_bat = Publisher("swarm_drones/white/out_points_low_bat",Array, queue_size=10)
sub_point=Subscriber("swarm_drones/white/points", Array,callback_point)
sub_stateRep = Subscriber("swarm_drones/state_repeater", Int32, callback_state)
sub_pos = Subscriber("geoscan/navigation/local/position", Point, callback_pos)
sub_in_points_low_bat = Subscriber("swarm_drones/white/in_points_low_bat",Array,callback_in_point)
proxy_cam=ServiceProxy("swarm/take_photos", TakeScreen)

while not rospy.is_shutdown():
    if board.runStatus() and not once:
        rospy.loginfo("start programm")
        lat_home=latitude
        lon_home=longitude
        ap.preflight()
        once = True
    if charge<10.5:
        low_battery=True
        pub_out_points_low_bat.publish(coordinates[::-1])
    else:
        low_battery=False
    pub_low_battery.publish(low_battery)
    if repeat!=0:
        pub_photos.publish(int(num_photos/all_points*100)) #публикуем процент выполненной работы
