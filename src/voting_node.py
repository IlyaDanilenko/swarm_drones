#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from rospy import Publisher, Subscriber
from rospy import Service, ServiceProxy
from gs_interfaces.msg import PointGPS
from gs_interfaces.msg import SimpleBatteryState
from swarm_drones.msg import Telemetry
from swarm_drones.srv import VotingResponse, VotingRequest, Voting
from swarm_drones.srv import VotiResponse, VotiRequest, Voti
from swarm_drones.srv import RepeaterRequest, RepeaterResponse, Repeater
from std_msgs.msg import Int32


v = 5
batteryForHome=10.5

def time(x, y, l, w, v, hr, hw):
    def gipotenuza(a, b):
        return sum(list(map(lambda x: x * x, (a, b)))) ** 0.5
    return ((gipotenuza(l, w)/2 + hr - hw)) / v, gipotenuza(x, y) / v, (gipotenuza(l-x, w-y) + hr - hw) / v # от ретрансятора до дома, от точки до дома, точки до ретранслятора
def callback_orange(data):
    global telOrange
    telOrange = data
def callback_blue(data):
    global telBlue
    telBlue = data
def callback_pos(data):
    global position
    position = data
def callback_bat(data):
    global power
    power = data
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
def handle_voti_res(req):
    global voit
    return VotingResponse(voit) # вставить id коптера
def callback_req(data):
    global com
    com = data
def callback_repWhite(data):
    global repWhite
    repWhite = data
def callback_repBlue(data):
    global repBlue
    repBlue = data
def handler_take_points(req):
    global hw
    global hr
    global l
    global w
    global coord
    coord=req.points
    l=req.ly
    w=req.lx
    hw=coord[0][3]
    hr=hw+2

rospy.init_node("voting_node")
sub_pos = Subscriber("geoscan/navigation/global/position", PointGPS, callback_pos)
sub_bat = Subscriber("geoscan/battery_state", SimpleBatteryState, callback_bat)
sub_oran = Subscriber("swarm_drones/orange/telemetry", Telemetry, callback_orange)
sub_blue = Subscriber("swarm_drones/blue/telemetry", Telemetry, callback_blue)
sub_stateRep = Subscriber("swarm_drones/state_repeater", Int32, callback_req)
pub_stateRep = Publisher("swarm_drones/state_repeater", Int32, queue_size=4)
pun_repWhite = Subscriber("swarm_drones/white/repeater", Int32, callback_repWhite)
sub_repBlue = Subscriber("swarm_drones/repeater", Int32, callback_repBlue)
sub_repBlue = Subscriber("swarm_drones/repeater", Int32, callback_repBlue)

service_voit_res = Service("swarm_drones/voit_res", Voti, handle_voti_res)
server_otherVoit = Service("swarm_drones/white/voite", Voting, handle_otherVoit)

voit_orange = ServiceProxy("swarm_drones/orange/voit", Voting)
voit_blue = ServiceProxy("swarm_drones/blue/voit", Voting)
change_rep = ServiceProxy("swarm_drones/to_repeater", Repeater)

while not rospy.is_shutdown():
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
    if com == -1:
        for i in range(3):
            if max(powerDrones) < batteryForHome:
                rospy.logwarn("Low Battery all drones")
                break
            elif min(timeNeed) == timeNeed[i]:
                voit = i
        if voit == 0:
            i_repeater = True 
        if (voit_blue() == voit) and (voit_orange() == voit) and i_repeater:
            sub_stateRep.unregister()
        '''        comRep.commande = 1
        comRep.id = voit
        change_rep(comRep) '''
    if i_repeater:
        pub_stateRep(0)