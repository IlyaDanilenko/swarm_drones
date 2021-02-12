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
from sensor_msgs.msg import Image
from std_msgs.msgs import Int32 
satel = SatellitesGPS()
position = PointGPS()
power = SimpleBatteryState()
telOrange = Telemetry()
telBlue = Telemetry()

l, w = 16, 16
hr, hw = 6, 4
v = 5
batteryForHome = 10.5 ########################

def time(x, y, l, w, v, hr, hw):
    def gipotenuza(a, b):
        return sum(list(map(lambda x: x * x, (a, b)))) ** 0.5
    return ((gipotenuza(l, w)/2 + hr - hw)) / v, gipotenuza(x, y) / v, (gipotenuza(l-x1, w-y1) + hr - hw) / v # от ретрансятора до дома, от точки до дома, точки до ретранслятора
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



rospy.init_node("communication_node")
sub_sat = Subscriber("geoscan/navigation/global/satellites", SatellitesGPS, callback_sat)
sub_bat = Subscriber("geoscan/battery_state", SimpleBatteryState, callback_bat)
sub_pos = Subscriber("geoscan/navigation/global/position", PointGPS, callback_pos)
sub_stream = Subscriber("pioneer_max_camera/image_raw", Image, callback_stream)
sub_comp = Subscriber("white/work_completed", Int32, callback_comp)
pub_stream = Publisher("white/stream", Image, queue_size= len(bridge)+1)
pub_tel = Publisher("white/telemetry", Telemetry, queue_size=10)
sub_oran = Subscriber("orange/telemetry", Telemetry, callback_orange)
sub_blue = Subscriber("blue/telemetry", Telemetry, callback_blue)
voit_orange = ServiceProxy("orange/voit", Voting)
voit_blue = ServiceProxy("blue/voit", Voting)

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
    elif max(timeNeed) == timeNeed[i]:
        voit = i
if voit == 0:
    i_repeater = True
               
server_otherVoit = Service("white/voite", Voting, handle_otherVoit)

while not rospy.is_shutdown():
    voited = VotingRequest()
    voited.my_voit = voit
    if voit_blue(voit) == voit and voit_orange(voit) == voit and i_repeater:
        
    tel = Telemetry()
    stream = Image() 
    tel.charg = power
    tel.position = position
    tel.sat = satel
    pub_tel.publish(tel)
    pub_stream.publish(stream)
    sleep(1)