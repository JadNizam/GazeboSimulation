#!/bin/bash

source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
source install/setup.bash

export GZ_SIM_RESOURCE_PATH=${GZ_SIM_RESOURCE_PATH}:${HOME}/ros2_ws/install/rover_description/share

# Software rendering for WSL2
export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=llvmpipe
unset __GLX_VENDOR_LIBRARY_NAME
unset __NV_PRIME_RENDER_OFFLOAD

echo "Launching simple rover..."

ros2 launch /mnt/c/Users/jadni/Desktop/GazeboSimulation/launch/rover_world_simple.launch.py
