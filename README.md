# Autonomous Mars Rover Simulation: Exploration and Navigation Pipeline

A highly realistic ROS 2 and Gazebo simulation of a planetary rover capable of autonomous frontier exploration, simultaneous localization and mapping (SLAM), and multi-waypoint navigation. This project highlights a production-ready robotics software stack, transitioning from raw data acquisition in an unknown environment to reliable, mapped, and coordinated autonomous operations.

## Overview

This repository provides an end-to-end testing environment for autonomous robotics perception and planning. An equipped differential-drive rover interacts physically with a detailed simulated Mars research facility environment. The core focus is demonstrating a high-level autonomy pipeline: the rover can organically explore unknown spatial bounds utilizing frontier algorithms, generate and save high-resolution occupancy grids using LiDAR-based SLAM, and seamlessly relocalize against these maps to execute obstacle-avoidant multi-goal routes through the Nav2 architecture.

## Key Capabilities

*   **Autonomous Frontier Exploration**: The rover programmatically drives to the boundaries of known space, systematically expanding its map without human teleoperation intervention.
*   **Simultaneous Localization and Mapping (SLAM)**: Real-time asynchronous processing of LiDAR point clouds and wheel odometry into 2D trinary occupancy grids.
*   **Saved-Map Localization**: Robust usage of Adaptive Monte Carlo Localization (AMCL) to precisely place the rover within previously constrained and saved maps.
*   **Multi-Goal / Waypoint Navigation**: Integration of the Nav2 waypoint follower node and RViz UI tooling, allowing the plotting and sequential execution of comprehensive, multi-destination patrol routes.
*   **State Estimation**: Extended Kalman Filter (EKF) sensor fusion of IMU datastreams and skid-steer wheel odometry to anchor real-world tracking.
*   **Detailed Simulation Mechanics**: Configured Gazebo Harmonic world featuring custom bounding perimeters, varied scientific outposts, scattered terrain, and precise physical friction constraints.

## System Architecture

The software structure closely models a physical hardware deployment, isolating abstraction layers for ease of tuning:

*   **Simulation Engine**: Gazebo Harmonic simulating physics, rigid body collisions, and lidar/IMU outputs.
*   **Hardware Bridge**: 
os_gz_bridge facilitating zero-latency synchronization of topics (/cmd_vel, /scan, /odom, /imu, /clock) between Gazebo formats and ROS 2 standard messages.
*   **State Estimation Layer**: 
obot_localization executing an EKF to yield a polished /odometry/filtered topic and accurate odom -> base_link TF transforms.
*   **Perception Layer**: slam_toolbox handling topological spatial tracking during the exploration phase.
*   **Navigation Stack**: 
av2_bringup (Navigation 2) governing the global planner, local trajectory execution, costmap generations, and waypoint management.
*   **Exploration Controller**: explore_lite (or custom frontier scripts) directing geometric boundary testing for independent world-mapping.

## Project Structure

`	ext
GazeboSimulation/
├── archive/        # Legacy launch files, obsolete scripts, and deprecated URDFs
├── config/         # System configuration tuning (Nav2, AMCL, RViz layouts, EKF, SLAM)
├── launch/         # Core Python launch configurations for simulation and autonomy brings-ups
├── maps/           # Saved topological output grids (.yaml / .pgm) generated from SLAM
├── src/            # Custom standard ROS 2 packages and autonomy nodes
├── urdf/           # Extensible URDF macros detailing links, joints, and physical limits
└── worlds/         # 3D Gazebo Simulation Definitions (SDF) and world geometry
`

## Running the Autonomy Pipeline

The simulation can be operated sequentially through two separate launch ecosystems, showcasing the progression from mapping an unknown territory to navigating it.

### Phase 1: Autonomous Frontier Exploration

To command the rover to automatically probe and map the 3D environment:

`ash
ros2 launch launch/frontier_exploration.launch.py
`

*This spins up the simulation, SLAM Toolbox, the frontier exploration node, and RViz. The rover will autonomously identify map boundaries and drive toward them to gather complete point-cloud data until the testing perimeter is fully plotted.*

Once the environment is mapped to your satisfaction, save the map state to disk:

`ash
ros2 run nav2_map_server map_saver_cli -f maps/my_saved_map --use_sim_time
`

### Phase 2: Saved-Map Navigation & Waypoint Operation

Once a map is generated and safely stored in the maps/ directory, utilize the Navigation 2 stack to execute intelligent routing.

`ash
ros2 launch launch/saved_map_navigation.launch.py
`

**Executing Navigation via RViz:**
1.  **Initialize Localization**: Select the **2D Pose Estimate** tool from the upper toolbar and drag an arrow matching the rover's visual Gazebo spawn position to align the AMCL particle cloud.
2.  **Toggle Waypoint Mode**: In the bottom-left **Navigation 2** panel, press the **Waypoint mode** button.
3.  **Plot the Path**: Use the **Nav2 Goal** tool to place multiple destination arrows throughout the Mars laboratory map.
4.  **Execute**: Click **Start Waypoint Following** on the Nav2 panel to send the rover along the queued path. 

*For standard single-goal traversal, simply leave Waypoint mode unchecked and click any location natively on the map.*

## Current Status

*   **Frontier Exploration**: Fully operational. Reliably bounds external outcropping. 
*   **Static Mapping / SLAM**: Consistently parses dense, accurate boundary grids natively tied to the Gazebo simulation clock.
*   **Nav2 Autonomy Stack**: Highly tuned global and local route planning parameters mitigating rover drift and stall faults.
*   **Waypoint Framework**: The standard ROS 2 Nav2 toolkit is exposed to the RViz UI, completing the autonomous multi-goal patrol loop. 

## Future Improvements

*   **Terrain-Aware Costmaps**: Integrating 3D Pointcloud topography or RGB-D depth perception to influence navigation costs based on surface slope and rock clustering instead of utilizing strict 2D Lidar ray-tracing.
*   **Battery & Mission Lifecycle Management**: Expanding the waypoint server to recognize logical docking routines at the solar outposts upon depletion of simulated resources.
*   **Enhanced Dynamic Avoidance**: Injecting continuously moving physical obstacles within the test perimeter to challenge and calibrate local DWB critics.
