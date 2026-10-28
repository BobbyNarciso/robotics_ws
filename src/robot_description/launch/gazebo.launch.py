"""Simula el Colmibot en Gazebo Harmonic (equivale a gazebo.launch de ROS 1).

Uso:
    ros2 launch robot_description gazebo.launch.py
    ros2 launch robot_description gazebo.launch.py rviz:=false
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            SetEnvironmentVariable)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('robot_description')
    ros_gz_sim = get_package_share_directory('ros_gz_sim')
    urdf_file = os.path.join(pkg, 'urdf', 'CLM-EnsambleColmibot.urdf')
    rviz_config = os.path.join(pkg, 'rviz', 'gazebo.rviz')

    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    # Para que Gazebo resuelva package://robot_description/meshes/...
    resource_path = os.path.dirname(pkg)
    if os.environ.get('GZ_SIM_RESOURCE_PATH'):
        resource_path += os.pathsep + os.environ['GZ_SIM_RESOURCE_PATH']

    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true',
                              description='Abrir RViz junto con Gazebo'),

        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', resource_path),

        # Mundo vacio de Gazebo (-r: iniciar la simulacion de una vez)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')),
            launch_arguments={'gz_args': '-r empty.sdf'}.items()),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description,
                         'use_sim_time': True}],
            output='screen'),

        # Equivale a spawn_model de ROS 1
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-topic', 'robot_description', '-name', 'CLM-EnsambleColmibot',
                       '-x', '0', '-y', '0', '-z', '0.03'],
            output='screen'),

        # Puente Gazebo <-> ROS 2
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
                '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            ],
            parameters=[{'use_sim_time': True}],
            output='screen'),

        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': True}],
            condition=IfCondition(LaunchConfiguration('rviz')),
            output='screen'),
    ])