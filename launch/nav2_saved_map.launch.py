import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, GroupAction, ExecuteProcess
from launch_ros.actions import SetRemap
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_dir = os.path.join(os.getcwd())
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    map_yaml_file = LaunchConfiguration('map')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    declare_params_file = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(pkg_dir, 'config', 'nav2_params.yaml'),
        description='Full path to the ROS2 parameters file to use')

    declare_map_yaml = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(pkg_dir, 'maps', 'my_saved_map.yaml'),
        description='Full path to map yaml file to load')

    # Launch Nav2 in Full Bringup Mode (Map Server + AMCL Localization + Navigation)
    nav2_launch = GroupAction(
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')),
                launch_arguments={
                    'use_sim_time': use_sim_time,
                    'params_file': params_file,
                    'map': map_yaml_file,
                    'autostart': 'True',
                    'use_collision_monitor': 'false',
                    'use_velocity_smoother': 'false'
                }.items()
            )
        ]
    )

    # Relay node to forward /cmd_vel_nav to /cmd_vel so the robot drives
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

    return LaunchDescription([
        declare_use_sim_time,
        declare_params_file,
        declare_map_yaml,
        nav2_launch,
        relay_cmd_vel
    ])
