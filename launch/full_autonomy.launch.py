import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = os.path.join(os.getcwd())

    # 1. Launch Gazebo simulation with Mars visual world
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_dir, 'launch', 'rover_world_mars_visual.launch.py')
        )
    )

    # 2. Launch SLAM Toolbox
    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            os.path.join(pkg_dir, 'config', 'slam_toolbox.yaml'),
            {'use_sim_time': True}
        ]
    )

    # 3. Launch RViz
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', os.path.join(pkg_dir, 'config', 'slam_view.rviz')],
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        sim_launch,
        slam_toolbox_node,
        rviz_node
    ])
