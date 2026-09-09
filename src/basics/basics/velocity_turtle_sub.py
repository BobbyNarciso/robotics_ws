import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

# Nodo suscriptor que detecta/lee la velocidad enviada a la tortuga
class VelocityTurtleSubscriber(Node):
    def __init__(self):
        super().__init__('velocity_turtle_subscriber')

        # Suscripción al mismo tópico que usa turtlesim: /turtle1/cmd_vel
        self.subscription = self.create_subscription(
            Twist,
            '/turtle1/cmd_vel',
            self.listener_callback,
            10
        )

    def listener_callback(self, msg):
        self.get_logger().info(
            f'Detectado: Vel lineal = {msg.linear.x:.1f} m/s | '
            f'Vel angular = {msg.angular.z:.1f} rad/s'
        )

def main(args=None):
    rclpy.init(args=args)
    node = VelocityTurtleSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
