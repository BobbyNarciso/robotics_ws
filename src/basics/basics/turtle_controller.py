import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3, Twist


class TurtleController(Node):
    def __init__(self):
        super().__init__('turtle_controller')

        # --- Calibración del joystick (segun mediciones) ---
        self.centro_x = 1968
        self.centro_y = 1952
        self.max_adc = 4095  # rango completo del ADC de 12 bits

        # Zona muerta: ±5% del rango total del ADC alrededor del centro.
        # Se eligió 5% porque en reposo el ADC varía de forma natural
        # unos ±20 conteos (ruido normal del sensor), y 5% de 4095 (~205)
        # da margen suficiente para absorber ese ruido sin sacrificar
        # sensibilidad real de movimiento.
        self.zona_muerta = int(0.5 * self.max_adc)  # ~205

        # Límites de velocidad, elegidos tras pruebas en Turtlesim:
        # valores más altos hacen que la tortuga se salga rápido de
        # la ventana de simulación; estos permiten control fino y
        # visible sin perder el control del movimiento.
        self.max_vel_lineal = 5.0   # m/s
        self.max_vel_angular = 5.0  # rad/s

        self.subscription_ = self.create_subscription(
            Vector3,
            '/joystick_raw',
            self.joystick_callback,
            10
        )

        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self.get_logger().info('Controlador de tortuga iniciado')

    def aplicar_zona_muerta_y_mapear(self, valor, centro, vel_max):
        """
        Convierte una lectura cruda del ADC (0-4095) en una velocidad
        proporcional dentro de [-vel_max, vel_max], aplicando zona muerta
        alrededor del centro.
        """
        delta = valor - centro

        if abs(delta) < self.zona_muerta:
            return 0.0

        # Rango disponible hacia cada lado del centro, descontando
        # la zona muerta, para mapear de forma proporcional.
        if delta > 0:
            rango_disponible = (self.max_adc - centro) - self.zona_muerta
            delta_ajustado = delta - self.zona_muerta
            proporcion = delta_ajustado / rango_disponible
        else:
            rango_disponible = centro - self.zona_muerta
            delta_ajustado = delta + self.zona_muerta
            proporcion = delta_ajustado / rango_disponible

        proporcion = max(-1.0, min(1.0, proporcion))  # constrain
        return proporcion * vel_max

    def joystick_callback(self, msg):
        # Eje Y del joystick -> velocidad lineal (adelante/atrás)
        vel_lineal = self.aplicar_zona_muerta_y_mapear(
            msg.y, self.centro_y, self.max_vel_lineal
        )

        # Eje X del joystick -> velocidad angular (giro)
        vel_angular = self.aplicar_zona_muerta_y_mapear(
            msg.x, self.centro_x, self.max_vel_angular
        )

        twist = Twist()
        twist.linear.x = vel_lineal
        twist.angular.z = -vel_angular  # invertido para que sea intuitivo

        self.publisher_.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
