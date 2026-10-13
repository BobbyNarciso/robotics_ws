#!/usr/bin/env python3
"""
joy_turtle_controller.py
Convierte los mensajes sensor_msgs/Joy de un control comercial (Xbox, PlayStation
o genérico) en comandos geometry_msgs/Twist para Turtlesim.

Mapeo por defecto (Xbox / SDL2, ver config/joy_turtle.yaml):
  - Stick izquierdo vertical   -> velocidad lineal  (linear.x)
  - Stick derecho horizontal   -> velocidad angular (angular.z)
  - LB (mantener)              -> botón de habilitación (deadman)
  - RB (mantener)              -> modo turbo
  - A                          -> subir / bajar la pluma (rastro)
  - X                          -> limpiar el fondo (/clear)
  - Y                          -> reiniciar la tortuga (/reset)
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
from std_srvs.srv import Empty
from turtlesim.srv import SetPen


class JoyTurtleController(Node):
    def __init__(self):
        super().__init__('joy_turtle_controller')

        # --- Parámetros (todos ajustables desde el YAML o la terminal) ---
        self.declare_parameter('axis_linear', 1)
        self.declare_parameter('axis_angular', 2)
        self.declare_parameter('invert_angular', False)
        self.declare_parameter('scale_linear', 2.0)
        self.declare_parameter('scale_angular', 2.0)
        self.declare_parameter('turbo_factor', 2.5)
        self.declare_parameter('deadzone', 0.10)
        self.declare_parameter('require_enable_button', True)
        self.declare_parameter('button_enable', 9)   # LB
        self.declare_parameter('button_turbo', 10)   # RB
        self.declare_parameter('button_pen', 0)      # A
        self.declare_parameter('button_clear', 2)    # X
        self.declare_parameter('button_reset', 3)    # Y
        self.declare_parameter('publish_rate', 20.0)
        self.declare_parameter('joy_timeout', 0.5)

        p = lambda name: self.get_parameter(name).value
        self.axis_lin = p('axis_linear')
        self.axis_ang = p('axis_angular')
        self.inv_ang = p('invert_angular')
        self.k_lin = p('scale_linear')
        self.k_ang = p('scale_angular')
        self.turbo = p('turbo_factor')
        self.deadzone = p('deadzone')
        self.need_enable = p('require_enable_button')
        self.b_enable = p('button_enable')
        self.b_turbo = p('button_turbo')
        self.b_pen = p('button_pen')
        self.b_clear = p('button_clear')
        self.b_reset = p('button_reset')
        self.timeout = p('joy_timeout')

        # --- Comunicación ---
        self.sub = self.create_subscription(Joy, 'joy', self.joy_callback, 10)
        self.pub = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.cli_clear = self.create_client(Empty, 'clear')
        self.cli_reset = self.create_client(Empty, 'reset')
        self.cli_pen = self.create_client(SetPen, 'turtle1/set_pen')

        self.last_joy = None
        self.last_joy_time = None
        self.prev_buttons = []
        self.pen_on = True

        # Publicamos a frecuencia fija: la tortuga se mueve aunque el stick
        # se mantenga quieto en una posición (joy solo publica en cambios).
        self.timer = self.create_timer(1.0 / p('publish_rate'), self.publish_cmd)
        self.get_logger().info(
            f'Control listo. Lineal: eje {self.axis_lin}, angular: eje {self.axis_ang}. '
            + (f'Mantén el botón {self.b_enable} (LB) para mover.' if self.need_enable else ''))

    # ---------------- utilidades ----------------
    def apply_deadzone(self, value):
        """Anula ruido cerca del centro y re-escala para que la salida sea continua."""
        if abs(value) < self.deadzone:
            return 0.0
        sign = 1.0 if value > 0 else -1.0
        return sign * (abs(value) - self.deadzone) / (1.0 - self.deadzone)

    @staticmethod
    def get(arr, idx, default=0):
        return arr[idx] if 0 <= idx < len(arr) else default

    def pressed_now(self, buttons, idx):
        """Flanco de subida: el botón se acaba de presionar (evita repetir la acción)."""
        return self.get(buttons, idx) == 1 and self.get(self.prev_buttons, idx) == 0

    # ---------------- callbacks ----------------
    def joy_callback(self, msg: Joy):
        self.last_joy = msg
        self.last_joy_time = self.get_clock().now()

        if self.pressed_now(msg.buttons, self.b_clear):
            self.call_empty(self.cli_clear, 'clear')
        if self.pressed_now(msg.buttons, self.b_reset):
            self.call_empty(self.cli_reset, 'reset')
            self.pen_on = True
        if self.pressed_now(msg.buttons, self.b_pen):
            self.toggle_pen()

        self.prev_buttons = list(msg.buttons)

    def publish_cmd(self):
        twist = Twist()
        msg = self.last_joy
        if msg is not None:
            age = (self.get_clock().now() - self.last_joy_time).nanoseconds * 1e-9
            enabled = (not self.need_enable) or self.get(msg.buttons, self.b_enable) == 1
            if age < self.timeout and enabled:
                factor = self.turbo if self.get(msg.buttons, self.b_turbo) == 1 else 1.0
                lin = self.apply_deadzone(self.get(msg.axes, self.axis_lin, 0.0))
                ang = self.apply_deadzone(self.get(msg.axes, self.axis_ang, 0.0))
                if self.inv_ang:
                    ang = -ang
                twist.linear.x = self.k_lin * factor * lin
                twist.angular.z = self.k_ang * factor * ang
        # Si no hay datos recientes o se suelta LB, se publica Twist en cero (paro seguro).
        self.pub.publish(twist)

    # ---------------- servicios de turtlesim ----------------
    def call_empty(self, client, name):
        if not client.service_is_ready():
            self.get_logger().warn(f'Servicio /{name} no disponible')
            return
        client.call_async(Empty.Request())
        self.get_logger().info(f'/{name} llamado')

    def toggle_pen(self):
        if not self.cli_pen.service_is_ready():
            self.get_logger().warn('Servicio set_pen no disponible')
            return
        self.pen_on = not self.pen_on
        req = SetPen.Request()
        req.r, req.g, req.b, req.width = 255, 255, 255, 3
        req.off = 0 if self.pen_on else 1
        self.cli_pen.call_async(req)
        self.get_logger().info(f'Pluma {"activada" if self.pen_on else "desactivada"}')


def main(args=None):
    rclpy.init(args=args)
    node = JoyTurtleController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.pub.publish(Twist())  # detener la tortuga al salir
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
