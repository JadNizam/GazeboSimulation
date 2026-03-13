# GazeboSimulation — Mars Rover Test Environment

A Gazebo Harmonic / ROS 2 Jazzy simulation of a rocker-bogie Mars rover on a realistic Mars-analog terrain. Designed for testing LiDAR SLAM, perception, and autonomous navigation.

## Project Structure

```
GazeboSimulation/
├── worlds/          # Gazebo world files (.world, .sdf)
├── urdf/            # Robot description files (.urdf)
├── launch/          # ROS 2 launch files (.launch.py)
├── scripts/         # Shell launch helpers (.sh)
├── assets/          # Future: meshes, textures, models
├── config/          # Future: SLAM, nav, and sensor configs
└── docs/            # Future: documentation
```

## Launching the Simulation

Run the shell scripts from WSL. They source ROS 2 Jazzy automatically.

### Mars visual world (rocker-bogie visual rover)
```bash
bash scripts/launch_rover_mars_visual.sh
```

### Flat world (rocker-bogie final rover)
```bash
bash scripts/launch_rover_rocker_bogie_final.sh
```

### Flat world (simple rover)
```bash
bash scripts/launch_rover_simple.sh
```

## State Estimation

The rover fuses wheel odometry (`/odom`) and IMU data (`/imu/data`) through a robot_localization EKF node. It runs automatically when launching the simulation.

Verify filtered odometry is publishing:
```bash
ros2 topic list | grep filtered
ros2 topic echo /odometry/filtered
```

EKF config: `config/ekf.yaml`

## LiDAR Test Pipeline

Launches Gazebo, bridges the LiDAR scan topic, and opens RViz in one command.

```bash
bash scripts/run_lidar_test.sh
```

RViz will open with a `LaserScan` display subscribed to `/scan`, fixed frame `base_link`. Drive the rover near obstacles to see live scan data.

Verify the topic is streaming:
```bash
ros2 topic echo /scan
```

## SLAM Mapping

To build a real-time map of the environment using SLAM Toolbox, launch the mapping pipeline:

```bash
ros2 launch launch/slam_mapping.launch.py
```

This will automatically start the rover simulation, state estimation, SLAM Toolbox, and RViz configured with map and LiDAR visualization. 

Expected topics:
- `/scan`
- `/odometry/filtered`
- `/map`
- `/map_metadata`

Drive the rover around to generate the continuous occupancy grid in RViz.

## Full Autonomy Pipeline

To run the complete system including Gazebo simulation, LiDAR bridge, state estimation, SLAM mapping, and RViz in a single command:

```bash
ros2 launch launch/full_autonomy.launch.py
```

This will:
1. Start Gazebo with the visual Mars rover
2. Bridge the `/scan` LiDAR data to ROS2
3. Run the EKF state estimation (`/odometry/filtered`)
4. Start SLAM Toolbox
5. Open RViz with live LiDAR scans and the evolving map.

## Requirements

- ROS 2 Jazzy
- Gazebo Harmonic (`gz-sim`)
- `ros_gz_sim`, `ros_gz_bridge`, `robot_state_publisher`, `rviz2`
- WSL 2 (Windows) with software rendering (`LIBGL_ALWAYS_SOFTWARE=1`)
