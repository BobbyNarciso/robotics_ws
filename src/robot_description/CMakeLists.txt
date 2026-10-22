cmake_minimum_required(VERSION 3.8)
project(robot_description)

find_package(ament_cmake REQUIRED)

# Carpetas del paquete (URDF, meshes, launch, rviz)
install(DIRECTORY urdf meshes launch rviz
  DESTINATION share/${PROJECT_NAME}
)

# Nodo de odometria por ruedas
install(PROGRAMS scripts/wheel_odometry.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()