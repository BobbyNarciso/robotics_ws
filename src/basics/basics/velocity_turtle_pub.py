import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

# Nodo publicador que envía comandos de velocidad traslacional a la tortuga de turtlesim
class VelocityTurtlePublisher(Node):
    def __init__(self):
        super().__init__('velocity_turtle_publisher')

        # Publicador al tópico que turtlesim escucha para moverse
        # Tipo de mensaje: geometry_msgs/Twist
        self.publisher_ = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # Velocidad inicial en 0.0 m/s
        self.Vel = 0.0

        # Timer que llama a publish_velocity cada 0.5 segundos
        self.timer_ = self.create_timer(
            0.5,
            self.publish_velocity
        )

    def publish_velocity(self):
        msg = Twist()

        # Velocidad lineal en x (traslación hacia adelante)
        msg.linear.x = self.Vel

        # Sin giro
        msg.angular.z = 0.0

        self.publisher_.publish(msg)

        self.get_logger().info(
            f'Publicando: Vel = {self.Vel:.1f} m/s'
        )

        # Incrementamos 0.1 mientras no lleguemos a 1.2
        if self.Vel < 1.2:
            self.Vel = round(self.Vel + 0.1, 1)
        else:
            # Al llegar a 1.2, detenemos la tortuga publicando velocidad 0
            stop_msg = Twist()
            stop_msg.linear.x = 0.0
            stop_msg.angular.z = 0.0
            self.publisher_.publish(stop_msg)

            self.get_logger().info('Velocidad máxima alcanzada. Deteniendo tortuga.')

            # Cancelamos el timer para dejar de publicar
            self.timer_.cancel()

def main(args=None):
    rclpy.init(args=args)
    node = VelocityTurtlePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
