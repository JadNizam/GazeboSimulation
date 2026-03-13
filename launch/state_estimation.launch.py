#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    current_dir  = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..')
    ekf_config   = os.path.join(project_root, 'config', 'ekf.yaml')

    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            ekf_config,
            {'use_sim_time': True}
        ],
        remappings=[
            ('/odometry/filtered', '/odom')
        ]
    )

    return LaunchDescription([
        ekf_node,
    ])
