# robotics_ws

Workspace de ROS2 con el paquete `basics`, que implementa nodos publicadores y suscriptores para distintos ejercicios: comunicación básica por tópicos, control de turtlesim, y control de hardware (LED y potenciómetro) conectado a un ESP32.

---

## Explicación de funcionamiento

### Publicador (`velocity_publisher.py`)

El nodo `velocity_publisher` publica valores de velocidad simulados en el tópico **`/velocity`**, usando mensajes de tipo **`std_msgs/Float32`**.

Funcionamiento:
- Se crea un publicador asociado al tópico `/velocity` con una cola (queue size) de 10.
- Un timer ejecuta la función `publish_velocity()` cada **0.5 segundos**.
- En cada llamada, se publica el valor actual de `Vel` y se incrementa en 0.1.
- Cuando `Vel` alcanza 1.5, el timer se cancela y el nodo deja de publicar.

### Suscriptor (`velocity_subscriber.py`)

El nodo `velocity_subscriber` se suscribe al mismo tópico **`/velocity`**, escuchando mensajes de tipo **`std_msgs/Float32`**.

Funcionamiento:
- Se crea una suscripción al tópico `/velocity` con una cola de 10.
- Cada vez que llega un mensaje nuevo, se ejecuta la función `listener_callback()`, que imprime el valor recibido en consola.

### Comunicación

Ambos nodos se comunican de forma indirecta a través del tópico `/velocity`, siguiendo el patrón publicador/suscriptor: el publicador no conoce al suscriptor (ni viceversa), solo comparten el nombre del tópico y el tipo de mensaje.

---

## Control de turtlesim

### Publicador (`velocity_turtle_pub.py`)

El nodo `velocity_turtle_publisher` publica comandos de velocidad traslacional al tópico **`/turtle1/cmd_vel`** (el que escucha `turtlesim` para mover la tortuga), usando mensajes de tipo **`geometry_msgs/msg/Twist`**.

Funcionamiento:
- Se crea un publicador asociado al tópico `/turtle1/cmd_vel` con una cola de 10.
- Un timer ejecuta la publicación cada **0.5 segundos**.
- La velocidad lineal en `x` inicia en 0.0 y se incrementa en 0.1 en cada ciclo, hasta llegar a **1.2 m/s**.
- Al alcanzar 1.2, se publica explícitamente un mensaje con velocidad 0.0 (para detener la tortuga, ya que turtlesim mantiene la última velocidad recibida aunque se deje de publicar) y se cancela el timer.
- La velocidad angular en `z` se mantiene en 0.0 durante todo el recorrido, por lo que la tortuga se mueve en línea recta.

### Suscriptor (`velocity_turtle_sub.py`)

El nodo `velocity_turtle_subscriber` se suscribe al mismo tópico **`/turtle1/cmd_vel`**, detectando los comandos de velocidad enviados a la tortuga (tipo **`geometry_msgs/msg/Twist`**), e imprime en consola la velocidad lineal y angular recibida en cada mensaje.

### Nodos activos durante la ejecución

```
/turtlesim
/velocity_turtle_publisher
/velocity_turtle_subscriber
/parameter_events
/rosout
```

### Tópicos activos

```
/turtle1/cmd_vel
/turtle1/color_sensor
/turtle1/pose
```

### Grafo de nodos (rqt_graph)

El grafo muestra `/velocity_turtle_publisher` enviando mensajes al tópico `/turtle1/cmd_vel`, el cual es leído tanto por `/turtlesim` (que mueve la tortuga) como por `/velocity_turtle_subscriber` (que detecta la velocidad). Esto coincide con lo reportado por `ros2 topic info`:

```
Type: geometry_msgs/msg/Twist
Publisher count: 1
Subscription count: 2
```

Es decir, un solo publicador (nuestro nodo) y dos suscriptores (turtlesim y nuestro nodo suscriptor).

### Ejemplo de salida de `ros2 topic echo /turtle1/cmd_vel`

Se observa el incremento gradual de la velocidad lineal en `x` de 0.0 a 1.2 m/s, seguido del mensaje de detención (0.0) y el reinicio del ciclo:

```yaml
linear:
  x: 0.0
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0
---
linear:
  x: 0.1
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0
---
...
---
linear:
  x: 1.2
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0
---
linear:
  x: 0.0
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0
---
```

---

## Control de LED (ESP32)

Este ejercicio controla un LED físico conectado a un ESP32 desde ROS2, usando dos nodos y comunicación serial.

### Publicador (`led_blink.py`)

El nodo `led_blink` publica un valor entero (1 o 0) en el tópico **`/led_command`**, usando mensajes de tipo **`std_msgs/Int32`**.

Funcionamiento:
- Se crea un publicador asociado al tópico `/led_command` con una cola de 10.
- Un timer ejecuta la publicación cada **1 segundo**.
- El valor publicado alterna entre 1 y 0 en cada ciclo, generando el efecto de parpadeo.

### Puente serial (`serial_bridge.py`)

El nodo `serial_bridge` se suscribe al tópico `/led_command` y traduce cada mensaje recibido en un comando serial hacia el ESP32.

Funcionamiento:
- Se abre una conexión serial al puerto `/dev/ttyUSB0` a 115200 baudios.
- Al recibir un mensaje con valor `1`, envía el carácter `'1'` por serial.
- Al recibir un mensaje con valor `0`, envía el carácter `'0'` por serial.

### Firmware del ESP32 (`LED_Serial.ino`)

El sketch configura el pin del LED como salida y permanece escuchando el puerto serial. Al recibir el carácter `'1'` enciende el LED (`digitalWrite(LED, HIGH)`), y al recibir `'0'` lo apaga (`digitalWrite(LED, LOW)`).

### Nodos activos durante la ejecución

```
/led_blink
/serial_bridge
/parameter_events
/rosout
```

### Detalle del nodo `led_blink` (`ros2 node info /led_blink`)

```
/led_blink
  Subscribers:

  Publishers:
    /led_command: std_msgs/msg/Int32
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
  Service Servers:
    /led_blink/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /led_blink/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /led_blink/get_parameters: rcl_interfaces/srv/GetParameters
    /led_blink/get_type_description: type_description_interfaces/srv/GetTypeDescription
    /led_blink/list_parameters: rcl_interfaces/srv/ListParameters
    /led_blink/set_parameters: rcl_interfaces/srv/SetParameters
    /led_blink/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
  Service Clients:

  Action Servers:

  Action Clients:

```

Se confirma que `led_blink` únicamente publica en `/led_command` (además de los tópicos internos de ROS2 `/parameter_events` y `/rosout`), sin ninguna suscripción — es un nodo puramente publicador.

### Tópicos activos

```
/led_command
/parameter_events
/rosout
```

### Grafo de nodos (rqt_graph)

El grafo muestra `/led_blink` publicando hacia `/led_command`, y `/serial_bridge` suscrito a ese mismo tópico, actuando como puente hacia el hardware físico.

```
Type: std_msgs/msg/Int32
Publisher count: 1
Subscription count: 1
```

### Video de demostración — LED

[Ver video de demostración del LED](https://drive.google.com/file/d/1pD3X1YMTJuz6i_ikDJdskwFVyLnRWLJH/view?usp=sharing)

---

## Lectura de potenciómetro (ESP32)

Este ejercicio lee un potenciómetro conectado a un ESP32 y transmite su valor a ROS2 mediante comunicación serial.

### Publicador (`analog_serial_pub.py`)

El nodo `analog_serial_pub` publica el valor leído del ADC en el tópico **`/analog`**, usando mensajes de tipo **`std_msgs/Int32`**.

Funcionamiento:
- Se abre una conexión serial al puerto `/dev/ttyUSB0` a 115200 baudios.
- Un timer revisa el puerto serial cada 0.01 segundos en busca de datos nuevos.
- Cada línea recibida se valida como número y se publica como `Int32` en el tópico `/analog`.

### Suscriptor (`analog_subs.py`)

El nodo `analog_subscriber` se suscribe al tópico `/analog` y, cada vez que llega un mensaje nuevo, imprime en consola el valor del ADC recibido.

### Firmware del ESP32 (`ADC_Pot.ino`)

El sketch lee continuamente el valor analógico del potenciómetro conectado al pin 15 con `analogRead()`, y lo envía por serial cada 100 milisegundos con `Serial.println()`.

### Nodos activos durante la ejecución

```
/analog_serial_pub
/analog_subscriber
```

### Tópicos activos

```
/analog
/parameter_events
/rosout
```

### Comunicación

`analog_serial_pub` publica hacia `/analog`, y `analog_subscriber` está suscrito a ese mismo tópico, recibiendo en tiempo real el valor del potenciómetro conforme se mueve físicamente.

### Video de demostración — Potenciómetro

[Ver video de demostración del potenciómetro](https://drive.google.com/file/d/1DqhsjX0LgjlAFKG0LxICFzLTJ_06_MQT/view?usp=sharing)

---

## Comandos utilizados

### Compilación

```bash
cd ~/robotics_ws
colcon build --packages-select basics --symlink-install
```

### Sourcear el workspace

```bash
source install/setup.bash
```

### Ejecución (en terminales separadas)

```bash
ros2 run basics velocity_publisher
```

```bash
ros2 run basics velocity_subscriber
```

### Comprobación del funcionamiento

```bash
ros2 node list
ros2 node info /velocity_publisher

ros2 topic list
ros2 topic info /velocity
ros2 topic echo /velocity
ros2 topic hz /velocity
```

### Grafo de nodos

```bash
rqt_graph
```

### Ejecución con turtlesim (en terminales separadas)

```bash
ros2 run turtlesim turtlesim_node
```

```bash
ros2 run basics velocity_turtle_pub
```

```bash
ros2 run basics velocity_turtle_sub
```

### Comprobación del funcionamiento con turtlesim

```bash
ros2 node list
ros2 topic list
ros2 topic info /turtle1/cmd_vel
ros2 topic echo /turtle1/cmd_vel
ros2 topic hz /turtle1/cmd_vel
rqt_graph
```

### Ejecución del control de LED (en terminales separadas)

```bash
ros2 run basics serial_bridge
```

```bash
ros2 run basics led_blink
```

### Comprobación del funcionamiento del LED

```bash
ros2 node list
ros2 node info /led_blink

ros2 topic list
ros2 topic info /led_command
ros2 topic echo /led_command
ros2 topic hz /led_command
rqt_graph
```

### Ejecución de la lectura del potenciómetro (en terminales separadas)

```bash
ros2 run basics analog_serial_pub
```

```bash
ros2 run basics analog_subs
```

### Comprobación del funcionamiento del potenciómetro

```bash
ros2 node list
ros2 node info /analog_serial_pub
ros2 node info /analog_subscriber

ros2 topic list
ros2 topic info /analog
ros2 topic echo /analog
ros2 topic hz /analog
rqt_graph
```

---

## Control de Turtlesim con Joystick (ESP32)

Este sistema lee un joystick analógico de dos ejes conectado a un ESP32 y lo usa para controlar el movimiento de la tortuga en Turtlesim, con control proporcional continuo.

### Adquisición de datos (`joystick.ino`)

El sketch lee dos pines analógicos del ESP32 correspondientes a los ejes X y Y del joystick, y envía ambos valores por serial en formato CSV (`x,y`) cada 20 ms.

**Pines utilizados:**
- **VRX → GPIO34**
- **VRY → GPIO35**

**Razón de elección:** se probaron inicialmente los pines GPIO26/GPIO27 (ADC2), pero presentaban lecturas erráticas (saturación repentina en 0 o 4095, sin relación con el movimiento físico del joystick). Esto se debe a que los pines ADC2 del ESP32 comparten hardware internamente con el radio WiFi/Bluetooth, lo que puede causar interferencia incluso sin usar esas funciones explícitamente. Se migró a **GPIO34 y GPIO35**, pertenecientes al **ADC1** (sin este conflicto), confirmando mediante pruebas en reposo que las lecturas se mantienen estables (variación de solo ±20 conteos sobre un valor de referencia de ~1968/1952).

### Nodo publicador (`joystick_publisher.py`)

Lee el puerto serial del ESP32 y publica los valores crudos del ADC (sin ningún procesamiento) en el tópico **`/joystick_raw`**, usando mensajes de tipo **`geometry_msgs/msg/Vector3`** (`x` e `y` para los dos ejes; `z` sin uso).

Este nodo no tiene ninguna dependencia de Turtlesim ni realiza cálculos de velocidad — únicamente transporta el dato crudo del hardware a ROS2, cumpliendo con el requisito de separación de responsabilidades del enunciado.

### Nodo de control (`turtle_controller.py`)

Se suscribe a `/joystick_raw`, convierte los valores crudos del ADC en velocidades lineal y angular, y publica el resultado como mensaje **`geometry_msgs/msg/Twist`** en el tópico `/turtle1/cmd_vel`.

#### Zona muerta

Se definió una zona muerta del **5% del rango total del ADC** (±205 unidades alrededor del centro medido) en ambos ejes.

**Razón de elección:** se midió el comportamiento del joystick en reposo (sin tocarlo) y se observó una variación natural de solo ±20 conteos sobre el valor central (ruido propio del ADC). Un margen del 5% (~205 conteos) es más de 10 veces ese ruido medido, garantizando que la tortuga permanezca completamente detenida en la posición neutral, sin sacrificar sensibilidad real de movimiento — se verificó que sigue existiendo suficiente rango fuera de la zona muerta para un control proporcional fino.

#### Control proporcional

La velocidad no es un valor fijo (On/Off): se calcula de forma continua como una función lineal de la distancia entre la lectura actual del ADC y el centro, fuera de la zona muerta. Mientras más inclinado esté el joystick, mayor es la velocidad resultante, hasta el límite máximo configurado.

#### Límites de velocidad

```python
self.max_vel_lineal = 5.0   # m/s
self.max_vel_angular = 5.0  # rad/s
```

**Razón de elección:** se probó inicialmente con 2.0 m/s y 2.0 rad/s, pero el movimiento de la tortuga resultaba poco perceptible, dificultando distinguir visualmente los distintos niveles de velocidad durante las pruebas. Se incrementó a 5.0, donde el movimiento de la tortuga es claramente visible y responde de forma ágil a la inclinación del joystick, sin perder controlabilidad ni salirse de forma descontrolada de la ventana de simulación de Turtlesim.

#### Movimiento combinado

Como los ejes X (velocidad angular) y Y (velocidad lineal) se procesan de forma independiente pero se publican juntos en el mismo mensaje `Twist`, una inclinación simultánea en diagonal produce automáticamente avance/retroceso y giro al mismo tiempo, generando un movimiento en curva.

### Nodos activos durante la ejecución

[Ver video de demostración del joystick](https://drive.google.com/file/d/1vsc9A6z8amgkDKcvC5yYFQy7jjU9OD6J/view?usp=sharing)

---

## Archivo de Launch (`velocity_system.launch.py`)

### ¿Qué es un archivo de launch?

Un archivo de launch en ROS2 permite iniciar **múltiples nodos con un solo comando**, en lugar de tener que abrir una terminal distinta y ejecutar `ros2 run` para cada nodo por separado. Esto es especialmente útil cuando un sistema depende de que varios nodos trabajen en conjunto (como un publicador y un suscriptor), ya que evita el proceso manual de abrir terminales, sourcear el workspace en cada una, y lanzar cada nodo en el orden correcto.

### Qué hace `velocity_system.launch.py`

Este archivo de launch inicia simultáneamente los dos nodos del ejercicio de velocidad básica:

- **`velocity_publisher`** — el nodo que publica los valores de velocidad simulados.
- **`velocity_subscriber`** — el nodo que se suscribe y muestra esos valores en consola.

Ambos nodos se lanzan con `output='screen'`, lo que hace que su salida (los mensajes de `get_logger().info()`) se imprima directamente en la misma terminal donde se ejecuta el launch, en lugar de quedar oculta en los archivos de log.

### Estructura del archivo

```python
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
```

Cada bloque `Node(...)` especifica:
- `package`: el paquete de ROS2 donde vive el ejecutable (`basics`).
- `executable`: el nombre del ejecutable tal como está registrado en `entry_points` dentro de `setup.py`.
- `output='screen'`: redirige la salida del nodo a la terminal en vez de solo al log.

La función `generate_launch_description()` es el punto de entrada que ROS2 busca automáticamente al ejecutar `ros2 launch` — debe retornar un objeto `LaunchDescription` que contenga la lista de acciones (en este caso, los dos nodos) a ejecutar.

### Registro del archivo en `setup.py`

Para que `colcon build` instale este archivo y `ros2 launch` pueda encontrarlo, se agregó la siguiente línea dentro de `data_files`:

```python
('share/' + package_name + '/launch', ['launch/velocity_system.launch.py']),
```

Esto copia el archivo desde `launch/` (dentro del paquete fuente) hacia `share/basics/launch/` (dentro del workspace instalado), que es donde `ros2 launch` busca los archivos de launch de un paquete.

### Ejecución

```bash
ros2 launch basics velocity_system.launch.py
```

Este único comando reemplaza la necesidad de correr manualmente:

```bash
ros2 run basics velocity_publisher
```
```bash
ros2 run basics velocity_subscriber
```
en dos terminales separadas.

[Ver video de demostracion del uso de lauch](https://drive.google.com/file/d/12w8EGk1gz-YxVVqBTSso2tALWJloiyQ9/view?usp=sharing)

---

## Archivo de Launch (`turtle_joy_controller.py`)

### ¿Qué es un archivo de launch?

Un archivo de launch en ROS2 permite iniciar **múltiples nodos con un solo comando**, en lugar de tener que abrir una terminal distinta y ejecutar `ros2 run` para cada nodo por separado. Esto es especialmente útil cuando un sistema depende de que varios nodos trabajen en conjunto (como en este caso, la simulación y dos nodos propios), ya que evita el proceso manual de abrir terminales, sourcear el workspace en cada una, y lanzar cada nodo en el orden correcto.

### Qué hace `turtle_joy_controller.py`

Este archivo de launch inicia simultáneamente los tres nodos del sistema de control por joystick:

- **`turtlesim_node`** — la simulación de la tortuga (del paquete `turtlesim`).
- **`joystick_publisher`** — lee el joystick desde el ESP32 por serial y publica los valores crudos.
- **`turtle_controller`** — convierte esos valores en velocidades y mueve la tortuga.

Los tres nodos se lanzan con `output='screen'`, lo que hace que su salida (los mensajes de `get_logger().info()`) se imprima directamente en la misma terminal donde se ejecuta el launch, en lugar de quedar oculta en los archivos de log.

### Estructura del archivo

```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            output='screen'
        ),
        Node(
            package='basics',
            executable='joystick_publisher',
            output='screen'
        ),
        Node(
            package='basics',
            executable='turtle_controller',
            output='screen'
        ),
    ])
```

Cada bloque `Node(...)` especifica:
- `package`: el paquete de ROS2 donde vive el ejecutable (`turtlesim` para el primero, `basics` para los otros dos).
- `executable`: el nombre del ejecutable tal como está registrado en `entry_points` dentro de `setup.py`.
- `output='screen'`: redirige la salida del nodo a la terminal en vez de solo al log.

La función `generate_launch_description()` es el punto de entrada que ROS2 busca automáticamente al ejecutar `ros2 launch` — debe retornar un objeto `LaunchDescription` que contenga la lista de acciones (en este caso, los tres nodos) a ejecutar.

### Registro del archivo en `setup.py`

Para que `colcon build` instale este archivo y `ros2 launch` pueda encontrarlo, se agregó a la lista existente dentro de `data_files`:

```python
('share/' + package_name + '/launch', ['launch/velocity_system.launch.py', 'launch/turtle_joy_controller.py']),
```

Esto copia ambos archivos desde `launch/` (dentro del paquete fuente) hacia `share/basics/launch/` (dentro del workspace instalado), que es donde `ros2 launch` busca los archivos de launch de un paquete.

### Ejecución

```bash
ros2 launch basics turtle_joy_controller.py
```

Este único comando reemplaza la necesidad de correr manualmente:

```bash
ros2 run turtlesim turtlesim_node
```
```bash
ros2 run basics joystick_publisher
```
```bash
ros2 run basics turtle_controller
```
en tres terminales separadas.

[Ver video de demostración del uso de launch](https://drive.google.com/file/d/1fr7DSQNxwyJ3zriAlLHhBGjmQ8UhiDNw/view?usp=sharing)

---

## Control de Turtlesim con joystick comercial (Xbox Series S)

### Descripción

Un control Xbox Series S conectado por **USB** controla la tortuga de Turtlesim. Se eligió el cable y no Bluetooth para evitar problemas de emparejamiento y latencia. Un archivo de launch levanta todo el sistema con un solo comando.

### Arquitectura

```
Control Xbox → joy_node → /joy (sensor_msgs/Joy) → joy_turtle_controller → /turtle1/cmd_vel (Twist) → turtlesim
```

- **`joy_node`** (paquete `joy`): lee el control con SDL2 y publica en `/joy` los ejes (`axes`) y botones (`buttons`).
- **`joy_turtle_controller`** (nodo propio): convierte `/joy` en velocidades `Twist` y llama servicios de Turtlesim con los botones.
- **`turtlesim_node`**: la simulación.

Los índices de ejes y botones se identificaron con `ros2 topic echo /joy`, moviendo cada stick y presionando cada botón.

### Mapeo de entradas

| Entrada | Índice | Función |
|---|---|---|
| Stick derecho vertical | `axes[3]` | Velocidad lineal |
| Stick izquierdo horizontal | `axes[0]` | Velocidad angular |
| RB | `buttons[10]` | Turbo (×2.5) |
| A | `buttons[0]` | Pluma |
| X | `buttons[2]` | Limpiar |
| Y | `buttons[3]` | Reiniciar |

### Decisiones tomadas

- **Ejes:** giro con el stick izquierdo y avance con el derecho, para separar los dos movimientos en cada mano.
- **Zona muerta:** doble filtro, 0.05 en el driver (`joy_node`) y 0.10 en el nodo, para que el drift de los sticks no mueva la tortuga en reposo.
- **Velocidades:** escala de 2.0 m/s y 2.0 rad/s con el stick al tope (el eje va de -1.0 a 1.0), con turbo en RB.
- **Botón de habilitación:** el nodo lo soporta (`require_enable_button`), pero se desactivó por defecto para mover la tortuga solo con los sticks. Se reactiva con `enable_button:=true`.
- **Seguridad:** si `/joy` deja de llegar por más de 0.5 s (`joy_timeout`), el nodo deja de publicar velocidad.
- **Parámetros en yaml:** todo se configura en `config/joy_turtle.yaml`, sin editar código.

### Archivo de launch (`joy_turtle.launch.py`)

Inicia `joy_node`, `turtlesim_node` y `joy_turtle_controller`, cargando el yaml en los nodos que lo necesitan. Acepta dos argumentos:

- `device_id` (default `0`): índice del control.
- `enable_button` (default `false`): exigir mantener un botón para mover la tortuga.

Los archivos de `launch/` y `config/` se instalan automáticamente con `glob` en `data_files` de `setup.py`:

```python
(os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
(os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
```

### Comandos

```bash
sudo apt install ros-jazzy-joy
cd ~/robotics_ws
colcon build --packages-select basics --symlink-install
source install/setup.bash
ros2 launch basics joy_turtle.launch.py
```

Opciones:

```bash
ros2 launch basics joy_turtle.launch.py enable_button:=true
ros2 launch basics joy_turtle.launch.py device_id:=1
```

Comprobación:

```bash
ros2 node list
ros2 topic echo /joy
ros2 topic echo /turtle1/cmd_vel
ros2 param get /joy_turtle_controller require_enable_button
rqt_graph
```

### Video de demostración

[Ver video del control con joystick comercial](https://drive.google.com/file/d/1-EGEmsaDxPpm8P_m8D1LftnVc1ZBcBmX/view?usp=sharing)

---

# robot_description — Colmibot

Paquete de ROS 2 Jazzy con la representación virtual del **Colmibot**, un robot móvil diferencial (dos ruedas motrices y dos ruedas locas). Contiene el modelo URDF/Xacro, los meshes generados desde el CAD de SolidWorks y los archivos de lanzamiento para visualizarlo en RViz2.

**Equipo:** [nombres de los integrantes]

---

## Herramientas y recursos empleados

| Herramienta | Uso |
|---|---|
| SolidWorks | Modelado del ensamble del robot |
| SW URDF Exporter (`sw_urdf_exporter`) | Exportar el ensamble a URDF y STL |
| ROS 2 Jazzy (Ubuntu 24.04) | Sistema base |
| `xacro` | URDF parametrizado con propiedades |
| `robot_state_publisher` | Publica el árbol TF a partir del URDF |
| `joint_state_publisher_gui` | Sliders para mover las ruedas |
| `rviz2` | Visualización del modelo |
| `check_urdf` (`liburdfdom-tools`) | Validar el URDF |
| Python: `trimesh`, `fast-simplification`, `numpy` | Script que corrige y aligera los meshes |
| VS Code y Git/GitHub | Desarrollo y control de versiones |

---

## Procedimiento para generar la representación virtual

1. **Modelo CAD.** Se modeló el ensamble completo en SolidWorks (chasis, motorreductores, electrónica, baterías, ruedas motrices y ruedas locas).
2. **Sistemas de coordenadas y ejes.** Con `sw_urdf_exporter` se definió el origen del robot, un eje de giro para cada rueda motriz (`RJoin`, `Ljoin`) y se agruparon los componentes en tres links: `Cuerpo`, `RuedaDER` y `RuedaIzq`. Las ruedas locas quedaron dentro del cuerpo, porque no tienen movimiento.
3. **Exportación.** El exportador generó un paquete de ROS 1 (`catkin`, launch en XML) con el `.urdf`, los STL y el CSV de propiedades.
4. **Revisión del export.** Se encontraron varios problemas (ver sección *Problemas encontrados*) y se volvió a exportar el ensamble con los STL corregidos.
5. **Preparación de meshes.** Un script de Python separa, reorienta y aligera los STL para que se vean bien en RViz sin pesar decenas de megas.
6. **Migración a ROS 2.** Se creó un paquete `ament_cmake` nuevo, y el URDF se reescribió como Xacro con las rutas `package://robot_description/...`.
7. **Validación.** Se comprobó con `check_urdf` y se visualizó en RViz moviendo las ruedas con los sliders.

---

## Decisiones de diseño y simplificaciones

| Decisión | Razón |
|---|---|
| **Marco `base_link` con x adelante, y izquierda, z arriba** (REP-103) | Es la convención de ROS. El marco de SolidWorks tenía el frente en +Y, así que los meshes se giraron −90° en z |
| **Link raíz `base_footprint` con un joint fijo a `base_link`** | Permite girar todo el robot de una vez cambiando una sola propiedad (`body_yaw`) |
| **Ruedas locas fijas, dentro del cuerpo** | No participan en el movimiento. Son esferas sin fricción solo en la colisión |
| **Ruedas motrices como joints `continuous` con el mismo eje `(0 1 0)`** | Un giro positivo en ambas ruedas hace avanzar el robot |
| **Colisiones con primitivas** (cilindro para el chasis, cilindros para ruedas, esferas para ruedas locas) | La malla visual tiene más de 160 mil caras y no sirve para física |
| **Cuerpo aligerado de ~447 mil a ~163 mil caras** | Menos peso en RViz. La simplificación se hace pieza por pieza para no perder componentes pequeños |
| **Masa e inercia tomadas del CAD**, rotadas a `base_link` | Conserva los valores reales del ensamble |
| **Dimensiones medidas del CAD** | Radio de rueda 0.03 m, separación entre ruedas 0.174 m, altura de eje 0.0165 m |

**Simplificaciones:** el cuerpo es un solo link rígido (motores, baterías y placas no se modelan por separado) y no se incluyen sensores (cámara, IMU, ToF) como links.

---

## Estructura del paquete

```
robot_description/
├── CMakeLists.txt
├── package.xml
├── README.md
├── launch/
│   └── display.launch.py       # robot_state_publisher + sliders + RViz
├── meshes/
│   ├── base_link.stl           # cuerpo (aligerado)
│   ├── wheel_left.stl
│   └── wheel_right.stl
├── rviz/
│   └── colmibot.rviz           # configuración de RViz
└── urdf/
    └── colmibot.urdf.xacro     # modelo del robot
```
[Si en tu paquete hay otros archivos (por ejemplo `gazebo.launch.py`), agrégalos aquí o bórralos del repo si no los usaste.]

**Árbol del robot:**
```
base_footprint
└── base_link            (cuerpo + ruedas locas)
    ├── wheel_left       (wheel_left_joint, continuous)
    └── wheel_right      (wheel_right_joint, continuous)
```

---

## Comandos para ejecutar y visualizar el modelo

**Dependencias:**
```bash
sudo apt install ros-jazzy-xacro ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher-gui ros-jazzy-rviz2 liburdfdom-tools
```

**Compilar:**
```bash
cd ~/robotics_ws
colcon build --packages-select robot_description --symlink-install
source install/setup.bash
```

**Validar el URDF:**
```bash
xacro src/robot_description/urdf/colmibot.urdf.xacro use_gazebo:=false > /tmp/colmibot.urdf
check_urdf /tmp/colmibot.urdf
```

**Visualizar en RViz con sliders:**
```bash
ros2 launch robot_description display.launch.py
```
Al mover los sliders `wheel_left_joint` y `wheel_right_joint`, cada rueda gira sobre su eje.

**Inspeccionar:**
```bash
ros2 topic echo /joint_states
ros2 run tf2_tools view_frames
```

**Girar todo el robot:** edita `body_yaw` en `urdf/colmibot.urdf.xacro` (en radianes; `1.5708` = 90°) y vuelve a lanzar.

---

## Video de demostración

[Ver video del modelo funcionando en RViz](https://drive.google.com/file/d/1ARrVsrTXGCGZD2KZFuEFYmJLc9jiqunQ/view?usp=sharing)

---
## Problemas encontrados y solución

1. **Error al compilar con colcon: `'distutils.core.setup()' was never called`**
   - Causa: el archivo `setup.py` tenía líneas de `entry_points` mezclando tabs y espacios para la indentación, además de que faltaban comas entre los elementos de `console_scripts`.
   - Solución: se reescribió el bloque `entry_points` usando únicamente espacios para la indentación y agregando las comas faltantes entre cada entrada.

2. **La tortuga seguía moviéndose después de cancelar el timer al llegar a 1.2 m/s**
   - Causa: turtlesim mantiene la última velocidad recibida en `/turtle1/cmd_vel` de forma indefinida; cancelar el timer solo detiene la publicación, no el movimiento.
   - Solución: antes de cancelar el timer, se publica explícitamente un último mensaje `Twist` con `linear.x = 0.0` para detener la tortuga.

3. **Error `ModuleNotFoundError: No module named 'basics.velocity_turlte_pub'` al ejecutar con `ros2 run`**
   - Causa: error de dedo en el nombre del módulo dentro de `entry_points` en `setup.py` (`turlte` en vez de `turtle`, y un guion en vez de punto entre el paquete y el archivo).
   - Solución: se corrigieron los nombres en `entry_points` para que coincidieran exactamente con los nombres reales de los archivos (`basics.velocity_turtle_pub:main`), y se recompiló el paquete.

4. **`PermissionError: [Errno 13] Permission denied: '/dev/ttyUSB0'` al correr `serial_bridge`**
   - Causa: el usuario no pertenecía al grupo `dialout`, necesario para acceder a puertos seriales sin privilegios de superusuario.
   - Solución: se agregó el usuario al grupo con `sudo usermod -a -G dialout $USER`, y se usó `sudo chmod 666 /dev/ttyUSB0` como solución temporal mientras se aplicaba el cambio de grupo (que requiere cerrar sesión y volver a entrar).

5. **Solo un proceso puede usar el puerto serial `/dev/ttyUSB0` a la vez**
   - Causa: tanto el ejemplo del LED como el del potenciómetro usan el mismo ESP32 y puerto serial, por lo que no se pueden correr ambos sistemas simultáneamente.
   - Solución: se cargó el sketch correspondiente a cada ejercicio (`LED_Serial.ino` o `ADC_Pot.ino`) desde el IDE de Arduino antes de correr los nodos de ROS2 asociados a ese ejercicio.

6. **El export de SolidWorks era de ROS 1** (`catkin`, `.launch` en XML, dependencia de `gazebo` clásico).
   - Solución: se creó un paquete `ament_cmake` nuevo, con launch en Python, y se reescribió el URDF como Xacro.

7. **Los tres STL contenían el robot completo.** En RViz habrían aparecido tres robots encimados.
   - Causa: el exportador guardó el ensamble entero en cada STL.
   - Solución: se volvió a exportar el ensamble con cada STL conteniendo solo su pieza (ruedas de ~7 mil caras cada una).

8. **Los meshes pesaban 69 MB.**
   - Solución: un script de Python (`trimesh` y `fast-simplification`) simplifica el cuerpo pieza por pieza (de 447k a 163k caras) y usa primitivas para la colisión.

9. **Joints mal exportados:** las ruedas salieron como `revolute` con límite 0 (no podían girar), la rueda izquierda con 1° de inclinación y los ejes en sentidos opuestos.
   - Solución: se redefinieron como `continuous`, sin inclinación y con el mismo eje, para que un giro positivo avance en las dos ruedas.

10. **Centro de masa incorrecto en el primer export** (a 4.8 cm de lado y 0.5 cm de altura, poco realista).
   - Solución: se volvió a exportar y se usaron los valores corregidos (centro de masa casi centrado y a 4.8 cm de altura), rotados al marco `base_link`.

11. **Nombre del paquete inválido:** `CLM-EnsambleColmibot` tiene mayúsculas y guiones, y ROS 2 solo acepta minúsculas y guiones bajos.
   - Solución: se creó el paquete con el nombre `robot_description`.

12. **Al girar el cuerpo, las ruedas no lo seguían.** Cambiar el `rpy` del `<visual>` solo gira el dibujo, no los joints de las ruedas.
   - Solución: se agregó un link raíz `base_footprint` con un joint fijo cuyo `rpy` gira todo lo que cuelga de `base_link`.

