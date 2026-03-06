from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
import os

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    
    if os.path.exists('/mnt/c/Users'):
        world_file_path = '/mnt/c/Users/jadni/Desktop/GazeboSimulation/worlds/flat.sdf'
        robot_file_path = '/mnt/c/Users/jadni/Desktop/GazeboSimulation/simple_rover.urdf'
    else:
        home_dir = os.path.expanduser('~')
        world_file_path = os.path.join(home_dir, 'Desktop', 'GazeboSimulation', 'worlds', 'flat.sdf')
        robot_file_path = os.path.join(home_dir, 'Desktop', 'GazeboSimulation', 'simple_rover.urdf')
    
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=world_file_path,
        description='Path to world file'
    )
    
    world_file = LaunchConfiguration('world')

    robot_description_content = ParameterValue(
        Command(['cat ', robot_file_path]),
        value_type=str
    )

    robot_description = {'robot_description': robot_description_content}

    gz_sim = IncludeLaunchDescription(
        PathJoinSubstitution([
            FindPackageShare('ros_gz_sim'),
            'launch',
            'gz_sim.launch.py'
        ]),
        launch_arguments={
            'gz_args': [world_file, ' -r -v 1']
        }.items()
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            robot_description,
            {'use_sim_time': use_sim_time}
        ]
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='clock_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    cmd_vel_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='cmd_vel_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
        ],
        output='screen'
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', '/robot_description',
            '-name', 'simple_rover',
            '-z', '0.5'
        ],
        output='screen'
    )

    delayed_spawn = TimerAction(
        period=0.5,
        actions=[spawn_entity]
    )

    return LaunchDescription([
        world_arg,
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time'
        ),
        gz_sim,
        robot_state_publisher_node,
        clock_bridge,
        cmd_vel_bridge,
        delayed_spawn
    ])
