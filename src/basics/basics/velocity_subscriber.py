import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

#Definicion de la clase del nodo suscriptor
class VelocitySubscriber(Node):

    def __init__(self):
        #Inicio del nodo con el nombre
        super().__init__('velocity_subscriber')
        #Suscripcion con el nombre del tópico velocity y se ejecuta cada que llega un mensaje
        self.subscription_ = self.create_subscription(Float32,'/velocity',self.velocity_callback,10)

    def velocity_callback(self, msg):
        #SE ejecuta de manera automatica cada vez que llega mensaje al topico
        Velocity = msg.data
        self.get_logger().info(f'Vel = {Velocity:.1f} m/s')


def main(args = None):
    #Com con ros2
    rclpy.init(args=args)
    #Creacion dde una instancia del nodo suscriptor
    node = VelocitySubscriber()
    #EL nodo se mantiene activo esperando mensajes
    rclpy.spin(node)
    # Se destruye el nodo y se cierra la comunicacion
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
