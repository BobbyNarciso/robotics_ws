"""
Lanza el sistema completo: driver del joystick + Turtlesim + nodo de control.

Uso:
  ros2 launch basics joy_turtle.launch.py
  ros2 launch basics joy_turtle.launch.py device_id:=1 enable_button:=false
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('basics'), 'config', 'joy_turtle.yaml')

    device_id = LaunchConfiguration('device_id')
    enable_button = LaunchConfiguration('enable_button')

    return LaunchDescription([
        DeclareLaunchArgument('device_id', default_value='0',
                              description='Índice del control (0 = primero conectado)'),
        DeclareLaunchArgument('enable_button', default_value='false'),

        # 1) Driver: lee el control vía SDL2 y publica sensor_msgs/Joy en /joy
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            parameters=[config, {'device_id': device_id}],
            output='screen',
        ),

        # 2) Simulador
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen',
        ),

        # 3) Nodo propio: /joy -> /turtle1/cmd_vel + servicios de turtlesim
        Node(
            package='basics',
            executable='joy_turtle_controller',
            name='joy_turtle_controller',
            parameters=[config, {'require_enable_button': enable_button}],
            output='screen',
        ),
    ])
