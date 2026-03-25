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
    world_file   = os.path.join(project_root, 'worlds', 'mars_world_full.sdf')

    gui_config   = os.path.join(project_root, 'config', 'gui.config')

    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True,
            'publish_frequency': 100.0
        }]
    )

    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', world_file, '-r', '--gui-config', gui_config],
        output='screen'
    )

    # Automatically delete any lingering instance of the rover before spawning a new one
    delete_robot = ExecuteProcess(
        cmd=[
            'gz', 'service', '-s', '/world/mars_test_world/remove',
            '--reqtype', 'gz.msgs.Entity',
            '--reptype', 'gz.msgs.Boolean',
            '--timeout', '1000',
            '--req', 'name: "rocker_bogie_rover_visual", type: 2'
        ],
        output='log'
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'rocker_bogie_rover_visual',
            '-string', robot_desc,
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.32',
            '-Y', '0.0'
        ],
        output='screen'
    )


    bridge_all = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'use_sim_time': True}],
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/world/mars_test_world/model/rocker_bogie_rover_visual/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model'
        ],
        remappings=[
            ('/world/mars_test_world/model/rocker_bogie_rover_visual/joint_state', '/joint_states')
        ],
        output='screen'
    )

    bridge_clock = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'use_sim_time': True}],
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher,
        gazebo,
        delete_robot,
        spawn_robot,
        bridge_all,
        bridge_clock,
    ])
