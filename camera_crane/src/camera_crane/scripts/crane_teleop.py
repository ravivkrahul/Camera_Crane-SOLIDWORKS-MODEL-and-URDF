#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import sys, select, termios, tty

msg = """
Control Your Camera Crane!
---------------------------
Joint Selection:
1, 2, 3, 4, 5, 6

Movement:
w : Increase (+)
s : Decrease (-)

Current Joint: {0}
Step Size: {1}

CTRL-C to quit
"""

class CraneTeleop(Node):
    def __init__(self):
        super().__init__('crane_teleop')
        self.publisher_ = self.create_publisher(JointTrajectory, '/crane_controller/joint_trajectory', 10)
        self.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        self.current_positions = [0.0] * 6
        self.active_joint = 0 # Default to Joint 1
        self.step = 0.05      # Movement increment (meters or radians)
        
        self.settings = termios.tcgetattr(sys.stdin)

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        select.select([sys.stdin], [], [], 0.1)
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def run(self):
        try:
            print(msg.format(self.active_joint + 1, self.step))
            while rclpy.ok():
                key = self.get_key()
                if key in ['1', '2', '3', '4', '5', '6']:
                    self.active_joint = int(key) - 1
                    print(f"Switched to Joint {key}")
                elif key == 'w':
                    self.current_positions[self.active_joint] += self.step
                    self.send_cmd()
                elif key == 's':
                    self.current_positions[self.active_joint] -= self.step
                    self.send_cmd()
                elif key == '\x03': # CTRL-C
                    break
        except Exception as e:
            print(e)

    def send_cmd(self):
        traj = JointTrajectory()
        traj.joint_names = self.joint_names
        point = JointTrajectoryPoint()
        point.positions = self.current_positions
        point.time_from_start = Duration(sec=0, nanosec=500000000) # 0.5s move
        traj.points.append(point)
        self.publisher_.publish(traj)

def main():
    rclpy.init()
    node = CraneTeleop()
    node.run()
    rclpy.shutdown()

if __name__ == '__main__':
    main()