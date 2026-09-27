from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='basics',
            executable='velocity_publisher',
            output='screen'
        ),
        Node(
            package='basics',
            executable='velocity_subscriber',
            output='screen'
        ),
    ])
