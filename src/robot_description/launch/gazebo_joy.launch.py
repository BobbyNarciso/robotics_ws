import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('robot_description')
    teleop_config = os.path.join(pkg, 'config', 'joy_teleop.yaml')

    rviz_arg = DeclareLaunchArgument(
        'rviz', default_value='false',
        description='Abrir RViz junto con Gazebo')

    # 1) Gazebo + robot + bridge (el launch que ya funciona)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg, 'launch', 'gazebo.launch.py')),
        launch_arguments={'rviz': LaunchConfiguration('rviz')}.items())

    # 2) Lee el control y publica /joy
    joy_node = Node(
        package='joy', executable='joy_node', name='joy_node',
        parameters=[{'device_id': 0, 'deadzone': 0.1,
                     'autorepeat_rate': 20.0}])

    # 3) Convierte /joy en geometry_msgs/Twist en /cmd_vel
    teleop = Node(
        package='teleop_twist_joy', executable='teleop_node',
        name='teleop_twist_joy_node',
        parameters=[teleop_config])

    return LaunchDescription([rviz_arg, gazebo, joy_node, teleop])