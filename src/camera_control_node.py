#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import rospy
from time import sleep
from rospy import Subscriber,Publisher, Service
from cv_bridge import CvBridge,CvBridgeError
from gs_interfaces.msg import PointGPS
from swarm_drones.srv import TakeScreen,TakeScreenResponse
from sensor_msgs.msg import Image
from PIL import Image as ImagePIL
import piexif
import math

rospy.init_node("camera_control_node")
bridge = CvBridge()
photo = np.array([])
position = PointGPS()

def callback_img(data):
    global bridge
    global photo
    try:
        photo = bridge.imgmsg_to_cv2(data,"bgr8")
    except CvBridgeError as e:
        print(str(e))

def callback_pos(data):
    import random
    global position
    position = data
    # position.latitude = random.randint(1,1000)
    # position.longitude = random.randint(1, 1000)
    # position.altitude = random.randint(1, 1000)

def pioneer2exif(data):

    d = int(math.modf(data)[1])
    md = math.modf(data)[0] * 60
    m = math.modf(md)[1]
    sd = math.modf(md)[0] * 60
    s = math.modf(sd)[1]
    return int(d), int(m), int(s)

def handle_photo(req):
    global photo
    global position
    try:
        cv2.imwrite("name.jpg",photo)
        print(position)
        lat_1, lat_2, lat_3 = pioneer2exif(position.latitude)
        lon_1, lon_2, lon_3 = pioneer2exif(position.longitude)
        gps_ifd = {
            piexif.GPSIFD.GPSLatitudeRef:"N",
            piexif.GPSIFD.GPSLatitude: ((lat_1,1), (lat_2,1), (lat_3,1)),
      
            piexif.GPSIFD.GPSLongitudeRef: "E",
            piexif.GPSIFD.GPSLongitude:((lon_1,1),(lon_2,1),(lon_3,1)),
            piexif.GPSIFD.GPSAltitudeRef: (0),
            piexif.GPSIFD.GPSAltitude: (int(position.altitude),1)
        }
        zero = {
            piexif.ImageIFD.Make: u'PiCamera v2',
            piexif.ImageIFD.Software: u'piexif'
        }

        exif_dict = {"0th":zero,"GPS":gps_ifd}
        piexif.insert(piexif.dump(exif_dict),"name.jpg")
        return TakeScreenResponse(1)
    except Exception as e:
        print(str(e))
        return TakeScreenResponse(0)

sub_pos = Subscriber("geoscan/navigation/global/position", PointGPS, callback_pos)
sub_cam=Subscriber("pioneer_max_camera/image_raw",Image,callback_img)
camera_service = Service("swarm/take_photos", TakeScreen, handle_photo)

while not rospy.is_shutdown():
    pass