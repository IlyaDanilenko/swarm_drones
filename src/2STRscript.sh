#! /bin/bash

export ROS_MASTER_URI=http://10.0.0.31:11311
export ROS_HOSTNAME=10.0.0.31
roslaunch swarm_drones swarm_global.launch --screen
