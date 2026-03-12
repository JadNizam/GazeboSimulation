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

## Requirements

- ROS 2 Jazzy
- Gazebo Harmonic (`gz-sim`)
- `ros_gz_sim`, `ros_gz_bridge`, `robot_state_publisher`, `rviz2`
- WSL 2 (Windows) with software rendering (`LIBGL_ALWAYS_SOFTWARE=1`)
