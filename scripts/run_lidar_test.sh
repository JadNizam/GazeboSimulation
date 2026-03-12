#!/bin/bash

export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=llvmpipe

source /opt/ros/jazzy/setup.bash

cd /mnt/c/Users/jadni/Desktop/GazeboSimulation

ros2 launch launch/lidar_test.launch.py
