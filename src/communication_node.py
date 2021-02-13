#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from time import sleep
from rospy import Publisher, Subscriber
from rospy import Service, ServiceProxy
from swarm_drones.msg import Telemetry
from gs_interfaces.msg import SimpleBatteryState
from gs_interfaces.msg import SatellitesGPS
from gs_interfaces.msg import PointGPS
from swarm_drones.srv import VotingResponse, VotingRequest, Voting
from swarm_drones.srv import RepeaterRequest, RepeaterResponse, Repeater
from sensor_msgs.msg import Image
from std_msgs.msgs import Int32, Int16MultiArray
satel = SatellitesGPS()
position = PointGPS()
power = SimpleBatteryState()
telOrange = Telemetry()
telBlue = Telemetry()

l, w = 16, 16 # длина и ширина маршрута (длина прощади съемки) в метрах
hr, hw = 6, 4 # высота полёта ретранслятора и дронов
v = 5
batteryForHome = 10.5 #напряжение возврата домой
coord=[]#облако точек от оператора

n_s=9 # кол-во снимков на маршруте
n_route=9 # кол-во маршрутов
n=81 # кол-во снимков в облаке
coordinate=[] # массив точек для этого дрона

networksNames = ["Geoscan-White", "Geoscan-Blue", "Geoscan-Orange"]

def time(x, y, l, w, v, hr, hw):
    def gipotenuza(a, b):
        return sum(list(map(lambda x: x * x, (a, b)))) ** 0.5
    return ((gipotenuza(l, w)/2 + hr - hw)) / v, gipotenuza(x, y) / v, (gipotenuza(l-x, w-y) + hr - hw) / v # от ретрансятора до дома, от точки до дома, точки до ретранслятора
def callback_sat(data):
    global satel
    satel = data
def callback_bat(data):
    global power
    power = data
def callback_pos(data):
    global position
    position = data
def callback_stream(data):
    global bridge
    bridge = data
def callback_comp(data):
    global complet
    complet = data
def callback_orange(data):
    global telOrange
    telOrange = data
def callback_blue(data):
    global telBlue
    telBlue = data
def callback_repOran(data):
    global repOran
    repOran = data
def callback_repBlue(data):
    global repBlue
    repBlue = data
def handle_otherVoit(req):
    global otherVoit
    otherVoit = req.my_voit

    for i in range(3):
        if max(powerDrones) < batteryForHome:
            rospy.logwarn("Low_Battery")
            break
        elif max(timeNeed) == timeNeed[i]:
            voit = i
    if voit == otherVoit:
        return voit
    else:
        return 0
def callback_repWhite(data):
    global repWhite
    repWhite = data    
def callback_req(data):
    global com
    com = data

rospy.init_node("communication_node")
sub_sat = Subscriber("geoscan/navigation/global/satellites", SatellitesGPS, callback_sat)
sub_bat = Subscriber("geoscan/battery_state", SimpleBatteryState, callback_bat)
sub_pos = Subscriber("geoscan/navigation/global/position", PointGPS, callback_pos)
sub_stream = Subscriber("pioneer_max_camera/image_raw", Image, callback_stream)
pub_stream = Publisher("swarm_drones/white/stream", Image, queue_size= len(bridge)+1)
sub_comp = Subscriber("swarm_drones/white/work_completed", Int32, callback_comp)
pub_tel = Publisher("swarm_drones/white/telemetry", Telemetry, queue_size=10)
pun_repWhite = Subscriber("swarm_drones/white/repeater", Int32, callback_repWhite)
pub_points = Publisher("white/points", Int16MultiArray, queue_size=10)
sub_oran = Subscriber("swarm_drones/orange/telemetry", Telemetry, callback_orange)
sub_blue = Subscriber("swarm_drones/blue/telemetry", Telemetry, callback_blue)
sub_stateRep = Subscriber("swarm_drones/state_repeater", Int32, callback_req)
pub_stateRep = Publisher("swarm_drones/state_repeater", Int32, queue_size=4)
sub_repBlue = Subscriber("swarm_drones/repeater", Int32, callback_repBlue)
voit_orange = ServiceProxy("swarm_drones/orange/voit", Voting)
voit_blue = ServiceProxy("swarm_drones/blue/voit", Voting)
change_rep = ServiceProxy("swarm_drones/to_repeater", Repeater)

x = position.latitude
y = position.longitude
xo = telOrange.position.lagitude
yo = telOrange.position.longitude
xb = telBlue.position.latitude
yb = telBlue.position.longitude

powerDrones = []
timeNeed = []
powerDrones[0] = int(power.charge)
powerDrones[1] = int(telOrange.charg)
powerDrones[2] = int(telBlue.charg)
timeNeed[0] = time(x, y, l, w, v, hr, hw)[2]
timeNeed[1] = time(xo, yo, l, w, v, hr, hw)[2]
timeNeed[2] = time(xb, yb, l, w, v, hr, hw)[2]

for i in range(3):
    if max(powerDrones) < batteryForHome:
        rospy.logwarn("Low_Battery")
        break
    elif min(timeNeed) == timeNeed[i]:
        voit = i
if voit == 0:
    i_repeater = True

if i_repeater: # 0 для белого, 1 для голубого, 3 для оранжевого
    lat=l/2
    lon=w/2
    coordinate.append([0, 0, hr])
    coordinate.append([lat, lon, hr])
else: # берём ближнию территорию только белый
    if n_route%2==0: # чётность не чётность маршрутов
        par_route=1
    else:
        par_route=0

    if par_route==1: # выбор нужных точек из облака
        route=n_route/2+1
        dots=n_s*route
        i=0
        while i<dots:
            coordinate.append(coord[i])
            i=i+1
    elif par_route==0:
        route=round(n_route/2)
        dots=n_s*route
        i=0
        while i<dots:
            coordinate.append(coord[i])
            i=i+1

server_otherVoit = Service("white/voite", Voting, handle_otherVoit)

while not rospy.is_shutdown():
    voited = VotingRequest()
    comRep = RepeaterRequest()
    voited.my_voit = voit
    if com == -1: 
        if voit_blue(voit) == voit and voit_orange(voit) == voit and i_repeater:
            sub_stateRep.unregister()
        comRep.commande = 1
        comRep.id = voit
        change_rep(comRep)  
    tel = Telemetry()
    stream = Image() 
    tel.charg = power
    tel.position = position
    tel.sat = satel
    pub_tel.publish(tel)
    pub_stream.publish(stream)
    pub_points.publish(coordinate)
    sleep(1)