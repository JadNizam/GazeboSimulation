import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = os.path.join(os.getcwd())

    # 1. Launch Gazebo simulation with Mars visual world
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_dir, 'launch', 'rover_world_mars_visual.launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true'
        }.items()
    )

    # 2. Launch State Estimation (EKF)
    state_estimation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_dir, 'launch', 'state_estimation.launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true'
        }.items()
    )

    # 3. Launch SLAM Toolbox properly managed
    slam_toolbox_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'slam_params_file': os.path.join(pkg_dir, 'config', 'slam_toolbox.yaml'),
            'params_file': os.path.join(pkg_dir, 'config', 'slam_toolbox.yaml')
        }.items()
    )

    # 3. Launch RViz (with new Nav2 specific config)
    rviz_node = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                arguments=['-d', os.path.join(pkg_dir, 'config', 'nav2_view.rviz')],
                output='screen',
                parameters=[{'use_sim_time': True}]
            )
        ]
    )

    # 4. Launch Nav2 Stack
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_dir, 'launch', 'nav2.launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'params_file': os.path.join(pkg_dir, 'config', 'nav2_params.yaml')
        }.items()
    )

    return LaunchDescription([
        sim_launch,
        state_estimation_launch,
        slam_toolbox_launch,
        nav2_launch,
        rviz_node
    ])
