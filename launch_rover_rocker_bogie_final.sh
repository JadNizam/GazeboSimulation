#!/bin/bash

# Software rendering for WSL2
export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=llvmpipe

source /opt/ros/jazzy/setup.bash

cd /mnt/c/Users/jadni/Desktop/GazeboSimulation

ros2 launch rover_world_rocker_bogie_final.launch.py
