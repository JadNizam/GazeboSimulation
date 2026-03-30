# Mars Rover Autonomous Navigation & Mapping

A comprehensive ROS 2 Jazzy and Gazebo Harmonic simulation featuring a rocker-bogie Mars rover traversing a realistic Mars-analog terrain. This project implements a complete robotics software stack, demonstrating hardware-bridged simulation, sensor fusion, SLAM-based mapping, and fully autonomous Nav2 waypoint navigation.

---

## Overview

This repository serves as a testing environment for robotics perception and planning. It features a custom rocker-bogie rover integrated with live 2D LiDAR and IMU sensors dynamically interacting with a detailed simulated world. The project demonstrates a production-grade ROS 2 workflow, capturing an environment through real-time SLAM, saving the generated occupancy grid, and localizing the rover against that map to execute complex, obstacle-avoidant pathing using the Nav2 stack.

---

## System Architecture

The robot's software stack mirrors a physical deployment, relying heavily on standard ROS 2 capabilities bridged seamlessly to Gazebo.

### Simulation Engine
- **Gazebo Harmonic**: Orchestrates physical interactions, planetary gravity constraints, multi-mesh collision handling, and sensor simulation.

### Bridge Layer
- **os_gz_bridge**: Handles bidirectional topic translation, mapping Gazebo hardware outputs (`/scan`, `/odom`, `/imu`, `/clock`) explicitly to their ROS 2 equivalents for real-time consumption.

### State Estimation
- **robot_localization**: Consumes raw wheel odometry and IMU data, routing through an Extended Kalman Filter (EKF) to produce a fused `/odometry/filtered` topic and the crucial `odom -> base_link` transform.

### Perception & Mapping
- **SLAM Toolbox**: Provides asynchronous mapping, consuming LiDAR scans to construct high-resolution trinary occupancy grids of the environment (`/map`).

### Navigation & Localization
- **Nav2 Stack**: Manages path planning (Navfn) and trajectory execution, utilizing AMCL (Adaptive Monte Carlo Localization) for fixed-map tracking over the map server.

---

## Features & Capabilities

- **Visual & Structural Simulation**: Functional rocker-bogie suspension models. Includes a detailed laboratory outcropping set against Mars-like planetary terrain capable of obstructing sensors.
- **Real-time SLAM Mapping**: Launch a dedicated pipeline that seamlessly fuses LiDAR to plot unknown spatial constraints while you drive manually.
- **Pre-computed Map Navigation (Saved-Map Workflow)**: A robust bringup sequence that loads an existing `.yaml/.pgm` occupancy grid, invokes AMCL for exact pose estimation, and executes paths while preserving accurate TF tree synchronization.
- **Autonomous Path Execution**: Configurable `controller_server` output bridged tightly to the physical differential drive interface, translating global plans into reactive rover velocities (`/cmd_vel`).

---

## Tech Stack

- **ROS 2**: Jazzy Jalisco
- **Gazebo**: Harmonic
- **Core Packages**: `nav2_bringup`, `slam_toolbox`, `robot_localization`, `os_gz_sim`, `robot_state_publisher`
- **Visualizer**: RViz2
- **OS**: WSL 2 (Ubuntu/Windows integration) leveraging software rendering or discrete UI bridging.

---

## Project Structure

```
GazeboSimulation/
├── config/       # AMCL, Nav2 tuning, EKF, and RViz viewpoints
├── launch/       # Modular Python launch sequences
├── worlds/       # Detailed SDF environment definitions
├── urdf/         # Robot description, collision geometry, and plugins
├── scripts/      # Shell execution helpers
├── my_saved_map.{pgm,yaml}  # Generated occupancy grids via map_saver_cli
```

---

## How It Works: The Navigation Workflow

The typical lifecycle to utilize the rover's autonomy involves dual phases: Mapping the location, then navigating it.

### 1. Mapping the Environment
Initiate the mapping sequence:
```bash
ros2 launch launch/slam_mapping.launch.py
```
This single command spins up Gazebo, the hardware bridge, the EKF, SLAM Toolbox, and RViz. Drive the rover manually (e.g., using a teleop publisher to `/cmd_vel`). As the rover drives, the LiDAR scans aggregate into a growing map.

### 2. Saving the Map
Once the area has been fully mapped, invoke the map saver while respecting the simulation clock:
```bash
ros2 run nav2_map_server map_saver_cli -f my_saved_map --use_sim_time
```
This isolates the grid into serialized `.pgm` and `.yaml` formats.

### 3. Saved-Map Autonomous Navigation
When returning to the project, launch the highly-tuned autonomous navigation stack. This sequence employs multi-stage timers to ensure the Gazebo clock initiates before Nav2 reads empty time states:
```bash
ros2 launch launch/saved_map_navigation.launch.py
```

#### In RViz:
- Use the **2D Pose Estimate** tool to orient the rover's spawn location against the static map.
- Use the **2D Goal Pose** tool to designate a coordinate destination.

The global planner will compute a route around established obstacles, and the controller relay automatically dictates necessary velocity commands to manipulate the rover along the path.

---

## Current Working Status

- **Gazebo Link**: Stable `/clock`, physics, and hardware plugins.
- **Telemetry**: Teleop drive, IMU generation, and Wheel Odometry active.
- **State Estimation**: EKF successfully publishing TF trees without timeline extrapolation faults.
- **Mapping Phase**: SLAM seamlessly identifies boundaries.
- **Localization Phase**: Map Server and AMCL configure pose alignments accurately.
- **Execution**: Goal generation actively bridges to the drive plugin, culminating in true physical automation.

---

## Requirements

- ROS 2 Jazzy properly sourced.
- Gazebo Harmonic installed.
- Python 3 environment capable of evaluating the nested XML/URDF parsing configurations and executing launch commands.

---

## Future Improvements

- **Enhanced Terrain Models**: Add more complex Mars-like terrains with varying slopes and obstacles.
- **Multi-Robot Coordination**: Extend the simulation to include multiple rovers working collaboratively.
- **Advanced Sensor Fusion**: Integrate additional sensors like stereo cameras or GPS for improved localization.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.
