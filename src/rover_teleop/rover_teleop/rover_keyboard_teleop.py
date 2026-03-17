import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import select
import termios
import tty
import threading

def get_terminal_settings():
    if sys.stdin.isatty():
        return termios.tcgetattr(sys.stdin)
    return None

settings = get_terminal_settings()

msg = """
Rover Keyboard Teleop
---------------------------
Controls:
   w
a  s  d
SPACE: stop

w: forward
s: backward
a: turn left
d: turn right
space/any other key: stop

CTRL-C to quit
"""

key_bindings = {
    'w': (1.0, 0.0),
    's': (-1.0, 0.0),
    'a': (0.0, 1.0),
    'd': (0.0, -1.0),
}


class KeyboardTeleopNode(Node):
    def __init__(self):
        super().__init__('rover_keyboard_teleop')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Publish at 30 Hz for smooth control
        self.timer = self.create_timer(1.0 / 30.0, self.timer_callback)
        
        self.target_linear = 0.0
        self.target_angular = 0.0
        self.running = True

        self.get_logger().info(msg)

        # Thread for non-blocking key capture
        self.key_thread = threading.Thread(target=self.key_capture_thread)
        self.key_thread.daemon = True
        self.key_thread.start()

    def get_key(self):
        key = ''
        if settings is None:
            return key
            
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
        if rlist:
            key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        return key

    def key_capture_thread(self):
        while self.running:
            key = self.get_key()
            if key:
                if key in key_bindings:
                    self.target_linear = key_bindings[key][0]
                    self.target_angular = key_bindings[key][1]
                elif key == '\x03':  # CTRL-C
                    self.running = False
                    self.target_linear = 0.0
                    self.target_angular = 0.0
                    break
                else:  # Space or any other key = stop
                    self.target_linear = 0.0
                    self.target_angular = 0.0
            else:
                # If no key is actively held/pressed, auto-stop
                self.target_linear = 0.0
                self.target_angular = 0.0

    def timer_callback(self):
        twist = Twist()
        twist.linear.x = self.target_linear
        twist.linear.y = 0.0
        twist.linear.z = 0.0
        twist.angular.x = 0.0
        twist.angular.y = 0.0
        twist.angular.z = self.target_angular
        self.publisher_.publish(twist)

        # If we got ctrl-c, shutdown
        if not self.running:
            sys.exit(0)


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardTeleopNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.target_linear = 0.0
        node.target_angular = 0.0
        node.timer_callback() # stop rover
        if settings is not None:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
