#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point, Pose
from moveit_msgs.action import MoveGroup
from rclpy.action import ActionClient
from moveit_msgs.msg import Constraints, PositionConstraint, BoundingVolume, WorkspaceParameters
from shape_msgs.msg import SolidPrimitive

class CraneMoveItTracker(Node):
    def __init__(self):
        super().__init__('crane_moveit_tracker')
        
        # Action Client for the MoveGroup action server
        self.client = ActionClient(self, MoveGroup, '/move_action')
        
        # Subscriber for the target coordinates
        self.sub = self.create_subscription(Point, '/target_object_pos', self.point_callback, 10)
        
        self.get_logger().info("Crane MoveIt Tracker Initialized.")
        if self.client.wait_for_server(timeout_sec=10.0):
            self.get_logger().info("MoveGroup Action Server Found!")
        else:
            self.get_logger().error("MoveGroup NOT FOUND. Check your MoveGroup terminal!")

    def point_callback(self, msg):
        self.get_logger().info(f"Target Received: x={msg.x}, y={msg.y}, z={msg.z}")
        
        goal = MoveGroup.Goal()
        goal.request.group_name = "crane_arm"
        
        # --- FIX 1: Expand the Planning Workspace (The Blue Box) ---
        # This expands the box to a 10m cube so the arm can reach its full extent
        ws = WorkspaceParameters()
        ws.header.frame_id = "world"
        ws.min_corner.x, ws.min_corner.y, ws.min_corner.z = -5.0, -5.0, -0.1
        ws.max_corner.x, ws.max_corner.y, ws.max_corner.z = 5.0, 5.0, 5.0
        goal.request.workspace_parameters = ws

        # --- FIX 2: Planning Settings ---
        goal.request.allowed_planning_time = 10.0
        goal.request.num_planning_attempts = 10
        goal.request.max_velocity_scaling_factor = 0.5
        goal.request.max_acceleration_scaling_factor = 0.5

        # Define Position Constraints
        c = Constraints()
        pc = PositionConstraint()
        pc.header.frame_id = "world"
        pc.link_name = "camera_link_optical"
        
        # Define the target region (20cm sphere)
        s = SolidPrimitive()
        s.type = SolidPrimitive.SPHERE
        s.dimensions = [0.2] 
        
        bv = BoundingVolume()
        bv.primitives.append(s)
        
        p = Pose()
        p.position.x = msg.x
        p.position.y = msg.y
        p.position.z = msg.z
        bv.primitive_poses.append(p)
        
        pc.constraint_region = bv
        pc.weight = 1.0
        c.position_constraints.append(pc)
        goal.request.goal_constraints.append(c)
        
        self.get_logger().info("Sending planning request to MoveIt...")
        self.client.send_goal_async(goal)

def main():
    rclpy.init()
    node = CraneMoveItTracker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()