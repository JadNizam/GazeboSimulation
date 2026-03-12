#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

    # launch/ is one level below project root
    current_dir  = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..')
    urdf_file    = os.path.join(project_root, 'urdf', 'rocker_bogie_rover_visual.urdf')
    world_file   = os.path.join(project_root, 'worlds', 'mars_test_world.world')

    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_desc},
            {'use_sim_time': True}
        ]
    )

    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', world_file, '-r'],
        output='screen'
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'rocker_bogie_rover_visual',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.32',
        ],
        output='screen'
    )

    bridge_cmd_vel = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist'],
        output='screen'
    )

    bridge_odom = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry'],
        output='screen'
    )

    bridge_scan = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan'],
        output='screen'
    )

    bridge_imu = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/imu/data@sensor_msgs/msg/Imu@gz.msgs.IMU'],
        output='screen'
    )

    # State estimation (EKF fusing odom + IMU)
    state_estimation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(current_dir, 'state_estimation.launch.py')
        )
    )

    return LaunchDescription([
        robot_state_publisher,
        gazebo,
        spawn_robot,
        bridge_cmd_vel,
        bridge_odom,
        bridge_scan,
        bridge_imu,
        state_estimation,
    ])
