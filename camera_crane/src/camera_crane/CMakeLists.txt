cmake_minimum_required(VERSION 3.8)
project(camera_crane)

# 1. Find the ament_cmake build tool
find_package(ament_cmake REQUIRED)

# 2. Install directories (ROS 2 uses a slightly different destination syntax)
install(DIRECTORY
  config
  launch
  meshes
  urdf
  worlds
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/crane_teleop_lpf.py
  scripts/crane_spline_planner.py
  scripts/crane_teleop.py
  scripts/crane_moveit_track.py
  DESTINATION lib/${PROJECT_NAME}
)

# 3. Export dependencies and register the package
ament_package()