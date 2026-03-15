import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    teleop_node = Node(
        package='rover_teleop',
        executable='rover_keyboard_teleop',
        name='rover_keyboard_teleop',
        output='screen',
        emulate_tty=True
    )

    return LaunchDescription([
        teleop_node
    ])
