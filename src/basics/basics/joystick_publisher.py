import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
import serial


class JoystickPublisher(Node):
    def __init__(self):
        super().__init__('joystick_publisher')

        self.publisher_ = self.create_publisher(Vector3, '/joystick_raw', 10)
        self.serial_ = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
        self.timer_ = self.create_timer(0.02, self.read_serial)

        self.get_logger().info('Joystick publisher iniciado')

    def read_serial(self):
        if self.serial_.in_waiting > 0:
            linea = self.serial_.readline().decode().strip()

            if ',' in linea:
                partes = linea.split(',')

                if len(partes) == 2 and partes[0].isdigit() and partes[1].isdigit():
                    x = int(partes[0])
                    y = int(partes[1])

                    msg = Vector3()
                    msg.x = float(x)
                    msg.y = float(y)
                    msg.z = 0.0

                    self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = JoystickPublisher()
    rclpy.spin(node)
    node.serial_.close()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
