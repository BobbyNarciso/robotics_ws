import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

# Definimos la clase del nodo publicador, heredando de NOde
class VelocityPublisher(Node):

    def __init__(self):
        super().__init__('velocity_publisher')
        #Iniciamos el nodo con el nombre 'velocity_publisher'
        self.publisher_ = self.create_publisher(
            Float32,
            '/velocity',
            10
        #Se cre el publicador con el topico velocity y una cola de 10
        )
        #Variable que guarda el valor de la velocidad del publicador
        self.Vel = 0.0
        #Este es un timer que llama a publish_velocity cada 0.5 segs
        self.timer_ = self.create_timer(
            0.5,
            self.publish_velocity
        )

    def publish_velocity(self):
        # Mensaje que se manda
        msg = Float32()

        msg.data = self.Vel
        # Aquí se publica el msg con el topico
        self.publisher_.publish(msg)
        # Se muestre el valor en la consola
        self.get_logger().info(
            f'Publicando: Vel = {self.Vel:.1f} m/s'
        )
        # Incremento de la velocidad fijado entre 1.5 y 0.1
        if self.Vel < 1.5:
            self.Vel = round(self.Vel + 0.1, 1)
        else:
        # Si se llega al limite se detiene
            self.timer_.cancel()


def main(args=None):
#Comunicacion con ros2
    rclpy.init(args=args)

    node = VelocityPublisher()
#Nodo publicador
    rclpy.spin(node)
#Se mantiene el nodo activo
    node.destroy_node()
#Se destruye el nodo al terminar
    rclpy.shutdown()
# COmunicacion se cierra

if __name__ == '__main__':
    main()
