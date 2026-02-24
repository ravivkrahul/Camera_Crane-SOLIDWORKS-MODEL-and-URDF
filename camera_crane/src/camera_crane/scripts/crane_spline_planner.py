#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class CraneSplinePlanner(Node):
    def __init__(self):
        super().__init__('crane_spline_planner')
        self.publisher_ = self.create_publisher(JointTrajectory, '/crane_controller/joint_trajectory', 10)
        
        # CONFIGURATION
        self.duration = 8.0 # Move takes 8 seconds
        self.hz = 50.0      # Resolution of the trajectory
        
        # Define your Start and End poses (all 6 joints)
        self.start_p = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.end_p = [0.4, 1.57, 0.7, -1.0, 0.0, 1.57] 

    def get_quintic_pos(self, q0, qf, tf, t):
        # Coefficients for a quintic polynomial with v0=vf=a0=af=0
        a0 = q0
        a3 = (10 * (qf - q0)) / (tf**3)
        a4 = (-15 * (qf - q0)) / (tf**4)
        a5 = (6 * (qf - q0)) / (tf**5)
        return a0 + a3*(t**3) + a4*(t**4) + a5*(t**5)

    def execute_move(self):
        msg = JointTrajectory()
        msg.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        
        total_steps = int(self.duration * self.hz)
        for i in range(total_steps + 1):
            t = i / self.hz
            point = JointTrajectoryPoint()
            
            for j in range(6):
                pos = self.get_quintic_pos(self.start_p[j], self.end_p[j], self.duration, t)
                point.positions.append(pos)
            
            point.time_from_start = Duration(sec=int(t), nanosec=int((t % 1) * 1e9))
            msg.points.append(point)
        
        print(f"Publishing Quintic Spline Move ({self.duration}s)...")
        self.publisher_.publish(msg)

def main():
    rclpy.init()
    node = CraneSplinePlanner()
    node.execute_move()
    rclpy.spin_once(node) # Send once and exit
    rclpy.shutdown()

if __name__ == '__main__':
    main()