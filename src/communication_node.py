#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from time import sleep
from rospy import Publisher, Subscriber
from rospy import Service, ServiceProxy
from swarm_drones.msg import Telemetry
from swarm_drones.msg import Array, Array_o
from gs_interfaces.msg import SimpleBatteryState
from gs_interfaces.msg import SatellitesGPS
#from gs_interfaces.msg import PointGPS
from geometry_msgs.msg import Point
from swarm_drones.srv import VotingResponse, VotingRequest, Voting
from swarm_drones.srv import VotiResponse, VotiRequest, Voti
from swarm_drones.srv import RepeaterRequest, RepeaterResponse, Repeater
from swarm_drones.srv import PointCloudRequest, PointCloudResponse, PointCloud
from sensor_msgs.msg import Image
from std_msgs.msg import Int32

satel = SatellitesGPS()
#position = PointGPS()
position = Point()
power = SimpleBatteryState()
telOrange = Telemetry()
telBlue = Telemetry()

batteryForHome = 10.5 #напряжение возврата домой
coord=[]#облако точек от оператора

n_s=0 # кол-во снимков на маршруте
n_route=0 # кол-во маршрутов
n=0 # кол-во снимков в облаке
# coordinate= Array() # массив точек для этого дрона

networksNames = ["Geoscan-White", "Geoscan-Blue", "Geoscan-Orange"]

altitude=0#убрать если gps
complet=0
in_coordb=[]
in_coordo=[]
start_point=0
h=0
lat=0
lon=0

def callback_sat(data):
    global satel
    satel = data
def callback_bat(data):
    global power
    power = data
def callback_pos(data):
    global position
    global altitude
    position = data
    #if f_start==False:
    #    altitude=data.altitude
    #    f_start=1
def callback_stream(data):
    global bridge
    bridge = data
def callback_comp(data):
    global complet
    complet = data
def handler_take_points(req):
    global start_point
    global coord
    global n_s
    global n_route
    global n
    global latit
    global longit
    global h
    global ly
    global lx
    coordinate = []
    start_point=req.numStart
    coord=req.points
    n_route=req.num_route  # кол-во маршрутов
    ly=req.ly
    lx=req.lx
    latit=coord.data[0].data[1]
    longit=coord.data[0].data[2]
    h=coord.data[0].data[2] #+altitude убрать если gps
    n=len(coord.data) # кол-во снимков всего
    n_s=n/n_route # кол-во снимков на маршруте

    for i in range(len(coord.data)):# замена на абсолютную высоту
        coord[i].data[2].data=h
        i+=1
    if voit.num==0 and len(coord.data)>0: # 0 для белого, 1 для голубого, 3 для оранжевого
        if start_point==1:
            lat=latit+ly/2
            lon=longit+lx/2
        elif start_point==2:
            lat=latit-ly/2
            lon=longit+lx/2
        elif start_point==3:
            lat=latit+ly/2
            lon=longit-lx/2
        elif start_point==4:
            lat=latit-ly/2
            lon=longit-lx/2
        coordinate.append([coord[0].data[0].data, coord.data[0].data[1], h+2])
        coordinate.append([lat, lon, h+2])
    elif (voit.num==1 or voit.num==2) and len(coord)>0: # берём ближнию территорию здесь только белый
        if n_route%2==0: # чётность не чётность маршрутов
            par_route=1
        else:
            par_route=0

        if par_route==1: # выбор нужных точек из облака
            route=n_route/2+1
            dots=n_s*route
            i=0
            while i<dots:
                coordinate.append(coord.data[i])
                i=i+1
        elif par_route==0:
            route=round(n_route/2)
            dots=n_s*route
            i=0
            while i<dots:
                coordinate.append(coord.data[i])
                i=i+1
    pub_points.publish(coordinate)
def callback_out_points_low_bat(data):
    global points_low_bat
    points_low_bat=data
def callback_in_points_blue(data):
    global in_coordb
    if charg_blue<10.5 and coordi!=data:
        coordi=data
        in_coordb=data
    elif coordi!=data:
        coordi=data
        in_coordb=data
        in_coordb=in_coordb[:len(in_coordb)-(len(in_coordb)%n_s)]
def callback_in_points_orange(data):
    global in_coordo
    #если он разряжен, то полностью, иначе навстречу но убирая точки которые
    if charg_orange<10.5 and coordi!=data:
        coordi=data
        in_coordo=data
    elif coordi!=data:
        coordi=data
        in_coordo=data
        in_coordo=in_coordo[:len(in_coordo)-(len(in_coordo)%n_s)]
def callback_orange(data):
    global charg_orange
    charg_orange=data.charge
def callback_blue(data):
    global charg_blue
    charg_blue=data.charge

rospy.init_node("communication_node")

sub_sat = Subscriber("geoscan/navigation/global/satellites", SatellitesGPS, callback_sat)
sub_bat = Subscriber("geoscan/battery_state", SimpleBatteryState, callback_bat)
sub_pos = Subscriber("geoscan/navigation/local/position", Point, callback_pos)

sub_stream = Subscriber("pioneer_max_camera/image_raw", Image, callback_stream)
sub_out_points_low_bat = Subscriber("swarm_drones/white/out_points_low_bat",Array, callback_out_points_low_bat)
sub_in_points_low_bat_blue = Subscriber("swarm_drones/blue/in_points", Array, callback_in_points_blue)
sub_in_points_low_bat_oran = Subscriber("swarm_drones/orange/in_points", Array, callback_in_points_orange)

pub_stream = Publisher("swarm_drones/white/stream", Image, queue_size= 85)
sub_comp = Subscriber("swarm_drones/white/work_completed", Int32, callback_comp)
sub_oran = Subscriber("swarm_drones/orange/telemetry", Telemetry, callback_orange)
sub_blue = Subscriber("swarm_drones/blue/telemetry", Telemetry, callback_blue)
pub_tel = Publisher("swarm_drones/white/telemetry", Telemetry, queue_size=10)

pub_points = Publisher("swarm_drones/white/points", Array, queue_size=85)
pub_in_points_low_bat = Publisher("swarm_drones/white/in_points_low_bat",Array,queue_size=85)
proxy_voit_res = ServiceProxy("swarm_drones/white/voit_res", Voti)
service = Service("swarm_drones/take_points", PointCloud, handler_take_points)


while not rospy.is_shutdown():
    voit=proxy_voit_res()
    tel = Telemetry()
    stream = Image() 
    tel.completed=complet
    tel.charge = power
    tel.position = position
    tel.sat = satel
    pub_tel.publish(tel)
    if len(in_coordb)>0:
        pub_in_points_low_bat.publish(in_coordb)
    elif len(in_coordo)>0:
        pub_in_points_low_bat.publish(in_coordo)
    pub_stream.publish(stream)
    sleep(1)
