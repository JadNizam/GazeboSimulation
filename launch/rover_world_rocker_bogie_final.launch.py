#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    
    # launch/ is one level below project root
    current_dir  = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..')

    # Path to URDF and world files
    urdf_file  = os.path.join(project_root, 'urdf', 'rocker_bogie_rover_final.urdf')
    world_file = os.path.join(project_root, 'worlds', 'flat.sdf')
    
    # Read URDF file
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
            '-name', 'rocker_bogie_rover_final',
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
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist'
        ],
        output='screen'
    )
    
    bridge_odom = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry'
        ],
        output='screen'
    )
    
    return LaunchDescription([
        robot_state_publisher,
        gazebo,
        spawn_robot,
        bridge_cmd_vel,
        bridge_odom,
    ])
