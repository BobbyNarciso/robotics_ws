Juan Daniel Rosales Salazar
Se elaboro una prectica sobre publishers en ros2 con dos programas de python que se comunican entre si

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

---

## Problemas encontrados y solución

1. **Error al compilar con colcon: `'distutils.core.setup()' was never called`**
   - Causa: el archivo `setup.py` tenía líneas de `entry_points` mezclando tabs y espacios para la indentación, además de que faltaban comas entre los elementos de `console_scripts`.
   - Solución: se reescribió el bloque `entry_points` usando únicamente espacios para la indentación y agregando las comas faltantes entre cada entrada.

2. **Error de autenticación al hacer `git push`: `Invalid username or token. Password authentication is not supported`**
   - Causa: GitHub ya no permite autenticación con usuario/contraseña para operaciones de Git.
   - Solución: se generó un token de acceso personal (Personal Access Token) desde la configuración de GitHub y se usó como contraseña al hacer push.

3. **Rechazo del push: `Updates were rejected because the remote contains work that you do not have locally`**
   - Causa: el repositorio remoto ya tenía contenido (creado desde la interfaz web de GitHub) que no existía en el historial local.
   - Solución: se usó `git pull origin main --allow-unrelated-histories` para fusionar los historiales antes de volver a hacer push.

4. **Historial de commits no cumplía con el formato pedido (publisher, subscriber, README por separado)**
   - Causa: inicialmente se hizo un solo commit con todos los archivos juntos.
   - Solución: se usó `git reset --soft HEAD~1` para deshacer el commit sin perder los archivos, y se volvieron a confirmar en tres commits separados, subiendo el resultado final con `git push --force`.
