import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # 1. Specify the name of your package and the path to the URDF
    pkg_name = 'camera_crane'
    urdf_file = 'camera_crane.urdf' # Make sure this matches your filename
    
    pkg_path = os.path.join(get_package_share_directory(pkg_name))
    urdf_path = os.path.join(pkg_path, 'urdf', urdf_file)

    # 2. Process the URDF file
    # (Using xacro even if it's a plain URDF is good practice for ROS 2)
    robot_description_config = xacro.process_file(urdf_path)
    params = {'robot_description': robot_description_config.toxml()}

    # 3. Node: Robot State Publisher
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )

    # 4. Action: Include the Gazebo launch file (provided by gazebo_ros)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py'
        )]),
    )

    # 5. Node: Spawn Entity (The "Spawner")
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description',
                   '-entity', 'camera_crane'],
        output='screen'
    )

    # 6. Launch Description
    return LaunchDescription([
        node_robot_state_publisher,
        gazebo,
        spawn_entity,
    ])