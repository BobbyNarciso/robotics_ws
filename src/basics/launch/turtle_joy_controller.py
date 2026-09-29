from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            output='screen'
        ),
        Node(
            package='basics',
            executable='joystick_publisher',
            output='screen'
        ),
        Node(
            package='basics',
            executable='turtle_controller',
            output='screen'
        ),
    ])
