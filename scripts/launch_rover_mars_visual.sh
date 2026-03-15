#!/bin/bash

# Allow GPU acceleration
# export GALLIUM_DRIVER=llvmpipe

source /opt/ros/jazzy/setup.bash

cd /mnt/c/Users/jadni/Desktop/GazeboSimulation

ros2 launch launch/rover_world_mars_visual.launch.py
