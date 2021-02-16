#! /bin/bash

export ROS_MASTER_URI=http://localhost:11311
export ROS_HOSTNAME=10.0.0.31
roslaunch fkie_master_discovery multimaster.launch --screen
