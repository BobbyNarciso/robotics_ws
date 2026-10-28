"""Visualiza el Colmibot en RViz2 con sliders para las ruedas (equivale a display.launch de ROS 1).

Uso:
    ros2 launch robot_description display.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('robot_description')
    urdf_file = os.path.join(pkg, 'urdf', 'CLM-EnsambleColmibot.urdf')
    rviz_config = os.path.join(pkg, 'rviz', 'urdf.rviz')

    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    return LaunchDescription([
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': robot_description}]),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config]),
    ])