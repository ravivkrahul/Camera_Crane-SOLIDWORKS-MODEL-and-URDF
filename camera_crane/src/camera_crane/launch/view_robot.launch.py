import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'camera_crane'
    urdf_file = 'camera_crane.urdf' # Confirm this matches your actual filename

    # Path to the URDF
    pkg_share = get_package_share_directory(pkg_name)
    urdf_path = os.path.join(pkg_share, 'urdf', urdf_file)

    # Read the URDF file
    with open(urdf_path, 'r') as infp:
        robot_desc = infp.read()

    # 1. Robot State Publisher
    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )

    # 2. Joint State Publisher GUI (Sliding bars to move joints)
    jsp_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen'
    )

    # 3. RViz2
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        rsp,
        jsp_gui,
        rviz
    ])