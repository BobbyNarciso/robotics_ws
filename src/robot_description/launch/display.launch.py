"""Visualiza el Colmibot en RViz2 con sliders para mover las ruedas (sin Gazebo).

Uso:
    ros2 launch robot_description display.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command, FindExecutable
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = get_package_share_directory('robot_description')
    xacro_file = os.path.join(pkg, 'urdf', 'colmibot.urdf.xacro')
    rviz_config = os.path.join(pkg, 'rviz', 'colmibot.rviz')

    robot_description = ParameterValue(
        Command([FindExecutable(name='xacro'), ' ', xacro_file, ' use_gazebo:=false']),
        value_type=str)

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen'),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            output='screen'),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
            output='screen'),
    ])