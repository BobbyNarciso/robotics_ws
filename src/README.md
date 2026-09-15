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
