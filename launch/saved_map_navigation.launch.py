import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = os.path.join(os.getcwd())

    # 1. Launch Gazebo simulation with Mars visual world & robot_state_publisher
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_dir, 'launch', 'rover_world_mars_visual.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

# 2. Launch State Estimation (EKF) for odom -> base_link (Wait 2s for Gazebo clock)
    state_estimation_launch = TimerAction(
        period=2.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_dir, 'launch', 'state_estimation.launch.py')
                ),
                launch_arguments={'use_sim_time': 'true'}.items()
            )
        ]
    )

    # 3. Launch Nav2 with map_server and AMCL (Wait 5s for Gazebo clock & EKF to stabilize to avoid TF back-jumps)
    nav2_saved_map_launch = TimerAction(
        period=5.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_dir, 'launch', 'nav2_saved_map.launch.py')
                ),
                launch_arguments={'use_sim_time': 'true'}.items()
            )
        ]
    )

    # 4. Launch RViz config for Nav2 workflow (Wait 10 seconds to ensure AMCL and Map Server are fully active)
    rviz_node = TimerAction(
        period=10.0,
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

    return LaunchDescription([
        sim_launch,
        state_estimation_launch,
        nav2_saved_map_launch,
        rviz_node
    ])
