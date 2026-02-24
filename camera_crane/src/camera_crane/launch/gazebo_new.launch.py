import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # 1. Specify the name of your package and paths
    pkg_name = 'camera_crane'
    urdf_file = 'camera_crane.urdf' 
    # CHANGE THIS: Match your downloaded file name exactly
    world_file_name = 'office_cpr.world' 
    
    pkg_path = os.path.join(get_package_share_directory(pkg_name))
    urdf_path = os.path.join(pkg_path, 'urdf', urdf_file)
    
    # Path to your downloaded world file
    # Ensure you have put the .sdf file in your package's 'worlds' folder
    world_path = os.path.join(pkg_path, 'worlds', world_file_name)

    # 2. Process the URDF file
    robot_description_config = xacro.process_file(urdf_path)
    params = {'robot_description': robot_description_config.toxml(), 'use_sim_time': True}

    # 3. Node: Robot State Publisher
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )

    # 4. Action: Include Gazebo and LOAD THE WORLD
    # Note: We use gazebo.launch.py which includes both gzserver and gzclient
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py'
        )]),
        launch_arguments={'world': world_path}.items()
    )

    # 5. Node: Spawn Entity
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description',
                   '-entity', 'camera_crane',
                   '-x', '0.0', '-y', '0.0', '-z', '0.1'], # Lift slightly if floor is thick
        output='screen'
    )

    # 6. Launch Description
    return LaunchDescription([
        node_robot_state_publisher,
        gazebo,
        spawn_entity,
    ])