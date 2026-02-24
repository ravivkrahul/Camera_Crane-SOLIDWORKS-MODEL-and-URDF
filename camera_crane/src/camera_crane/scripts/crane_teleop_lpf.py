#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import sys, select, termios, tty

class CraneLPFTeleop(Node):
    def __init__(self):
        super().__init__('crane_lpf_teleop')
        self.publisher_ = self.create_publisher(JointTrajectory, '/crane_controller/joint_trajectory', 10)
        
        self.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        self.target_positions = [0.0] * 6
        self.smoothed_positions = [0.0] * 6
        
        self.alpha = 0.90 # 0.90 for heavy cinematic feel
        self.active_joint = 0
        self.step = 0.1 

        # Timer runs at 50Hz
        self.timer = self.create_timer(0.02, self.timer_callback)
        self.settings = termios.tcgetattr(sys.stdin)

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        # Non-blocking key read
        rlist, _, _ = select.select([sys.stdin], [], [], 0.02)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = None
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def timer_callback(self):
        # Apply Low Pass Filter
        for i in range(6):
            self.smoothed_positions[i] = (self.smoothed_positions[i] * self.alpha) + \
                                         (self.target_positions[i] * (1.0 - self.alpha))
        
        # Build and Publish Message
        msg = JointTrajectory()
        msg.joint_names = self.joint_names
        point = JointTrajectoryPoint()
        point.positions = self.smoothed_positions
        # Very short time_from_start for real-time tracking
        point.time_from_start = Duration(sec=0, nanosec=40000000) 
        msg.points.append(point)
        self.publisher_.publish(msg)

    def run(self):
        print("--- CINEMATIC TELEOP ACTIVE ---")
        print("1-6: Select Joint | W/S: Move | CTRL+C: Exit")
        try:
            while rclpy.ok():
                # This line is CRITICAL - it allows the timer to fire!
                rclpy.spin_once(self, timeout_sec=0.01)
                
                key = self.get_key()
                if key:
                    if key in ['1', '2', '3', '4', '5', '6']:
                        self.active_joint = int(key) - 1
                        print(f"Selected Joint {key}")
                    elif key == 'w':
                        self.target_positions[self.active_joint] += self.step
                    elif key == 's':
                        self.target_positions[self.active_joint] -= self.step
        except Exception as e:
            print(e)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)

def main():
    rclpy.init()
    node = CraneLPFTeleop()
    node.run()
    rclpy.shutdown()

if __name__ == '__main__':
    main()