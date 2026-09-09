# robotics_ws

Workspace de ROS2 con el paquete `basics`, que implementa un nodo publicador y un nodo suscriptor comunicados mediante un tópico.

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

---

## Problemas encontrados y solución

1. **Error al compilar con colcon: `'distutils.core.setup()' was never called`**
   - Causa: el archivo `setup.py` tenía líneas de `entry_points` mezclando tabs y espacios para la indentación, además de que faltaban comas entre los elementos de `console_scripts`.
   - Solución: se reescribió el bloque `entry_points` usando únicamente espacios para la indentación y agregando las comas faltantes entre cada entrada.

2. **Error de autenticación al hacer `git push`: `Invalid username or token. Password authentication is not supported`**
   - Causa: turtlesim mantiene la última velocidad recibida en `/turtle1/cmd_vel` de forma indefinida; cancelar el timer solo detiene la publicación, no el movimiento.
   - Solución: antes de cancelar el timer, se publica explícitamente un último mensaje `Twist` con `linear.x = 0.0` para detener la tortuga.

3. **Error `ModuleNotFoundError: No module named 'basics.velocity_turlte_pub'` al ejecutar con `ros2 run`**
   - Causa: error de dedo en el nombre del módulo dentro de `entry_points` en `setup.py` (`turlte` en vez de `turtle`, y un guion en vez de punto entre el paquete y el archivo).
   - Solución: se corrigieron los nombres en `entry_points` para que coincidieran exactamente con los nombres reales de los archivos (`basics.velocity_turtle_pub:main`), y se recompiló el paquete.
