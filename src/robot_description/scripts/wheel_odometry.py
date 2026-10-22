#!/usr/bin/env python3
"""Odometria por ruedas: mueve base_link en RViz segun el giro de las ruedas."""

import math

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster


class WheelOdometry(Node):
    def __init__(self):
        super().__init__('wheel_odometry')
        self.declare_parameter('wheel_radius', 0.03)
        self.declare_parameter('wheel_separation', 0.174)
        self.declare_parameter('left_joint', 'wheel_left_joint')
        self.declare_parameter('right_joint', 'wheel_right_joint')
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')

        self.radius = self.get_parameter('wheel_radius').value
        self.separation = self.get_parameter('wheel_separation').value
        self.left_joint = self.get_parameter('left_joint').value
        self.right_joint = self.get_parameter('right_joint').value
        self.odom_frame = self.get_parameter('odom_frame').value
        self.base_frame = self.get_parameter('base_frame').value

        # Pose del robot en el marco odom
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.prev = None  # (pos_izq, pos_der) anteriores

        self.tf_broadcaster = TransformBroadcaster(self)
        self.create_subscription(JointState, 'joint_states', self.joint_callback, 10)
        # Publica el TF de forma continua para que RViz siempre tenga el marco odom
        self.create_timer(1.0 / 30.0, self.publish_tf)

        self.get_logger().info('wheel_odometry listo: mueve las ruedas para mover el robot')

    def joint_callback(self, msg):
        try:
            left = msg.position[msg.name.index(self.left_joint)]
            right = msg.position[msg.name.index(self.right_joint)]
        except ValueError:
            return  # este mensaje no trae las ruedas

        if self.prev is None:
            self.prev = (left, right)
            return

        d_left = (left - self.prev[0]) * self.radius
        d_right = (right - self.prev[1]) * self.radius
        self.prev = (left, right)

        ds = (d_right + d_left) / 2.0
        dyaw = (d_right - d_left) / self.separation

        # Integracion en el punto medio del giro
        self.x += ds * math.cos(self.yaw + dyaw / 2.0)
        self.y += ds * math.sin(self.yaw + dyaw / 2.0)
        self.yaw += dyaw

    def publish_tf(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = self.odom_frame
        t.child_frame_id = self.base_frame
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        t.transform.rotation.z = math.sin(self.yaw / 2.0)
        t.transform.rotation.w = math.cos(self.yaw / 2.0)
        self.tf_broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = WheelOdometry()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()