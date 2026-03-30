import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = os.path.join(os.getcwd())

    # 1. Include the full autonomy stack
    # This brings up Gazebo, the rover spawn, EKF, SLAM Toolbox, Nav2, and RViz.
    full_autonomy_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_dir, 'launch', 'full_autonomy.launch.py')
        )
    )

    # 2. Add cmd_vel_relay to map Nav2's output to Gazebo's input 
    relay_cmd_vel = ExecuteProcess(
        cmd=['python3', '-c',
             "import rclpy; from geometry_msgs.msg import Twist; "
             "rclpy.init(); "
             "node = rclpy.create_node('cmd_vel_relay'); "
             "pub = node.create_publisher(Twist, '/cmd_vel', 10); "
             "sub = node.create_subscription(Twist, '/cmd_vel_nav', pub.publish, 10); "
             "rclpy.spin(node)"],
        output='screen'
    )

    # 3. Add the frontier exploration logic on top, delayed slightly to let SLAM stabilize
    explorer_node = TimerAction(
        period=10.0,
        actions=[
            ExecuteProcess(
                cmd=['python3', os.path.join(pkg_dir, 'src', 'rover_teleop', 'rover_teleop', 'simple_frontier_explorer.py')],
                output='screen'
            )
        ]
    )

    return LaunchDescription([
        full_autonomy_launch,
        relay_cmd_vel,
        explorer_node
    ])
