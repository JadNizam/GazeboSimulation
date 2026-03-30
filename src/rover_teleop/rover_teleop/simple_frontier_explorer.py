import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav_msgs.msg import OccupancyGrid, Odometry
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
import numpy as np
import math
import time

class SimpleFrontierExplorer(Node):
    def __init__(self):
        super().__init__('simple_frontier_explorer')
        
        # Subscribe to map
        self.map_sub = self.create_subscription(OccupancyGrid, '/map', self.map_callback, 1)
        
        # Subscribe to odom for current position estimate
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 1)
        
        # Action client for Nav2
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        self.current_map = None
        self.current_pose = None
        self.exploring = False
        self.goal_handle = None
        
        # Timer to run exploration logic continuously at a faster rate
        self.timer = self.create_timer(1.0, self.explore_step)
    def map_callback(self, msg):
        self.current_map = msg

    def odom_callback(self, msg):
        self.current_pose = msg.pose.pose

    def explore_step(self):
        if self.current_map is None:
            self.get_logger().info("Waiting for /map...", throttle_duration_sec=5.0)
            return
            
        if self.current_pose is None:
            self.get_logger().info("Waiting for /odom...", throttle_duration_sec=5.0)
            return

        if self.exploring:
            # Currently trying to reach a goal
            return

        # Find frontiers
        width = self.current_map.info.width
        height = self.current_map.info.height
        res = self.current_map.info.resolution
        origin_x = self.current_map.info.origin.position.x
        origin_y = self.current_map.info.origin.position.y

        # Convert to numpy array
        # -1 = unknown, 0 = free, 100 = occupied
        map_data = np.array(self.current_map.data, dtype=np.int8).reshape((height, width))
        
        free_cells = (map_data == 0)
        unknown_cells = (map_data == -1)

        # Shift up, down, left, right to find edges
        up = np.roll(unknown_cells, 1, axis=0)
        down = np.roll(unknown_cells, -1, axis=0)
        left = np.roll(unknown_cells, 1, axis=1)
        right = np.roll(unknown_cells, -1, axis=1)

        # A frontier is a FREE cell that is adjacent to an UNKNOWN cell
        frontier_mask = free_cells & (up | down | left | right)
        
        y_coords, x_coords = np.where(frontier_mask)
        
        if len(x_coords) == 0:
            self.get_logger().info("No frontiers found! Exploration complete.")
            return

        # Score frontiers based on distance from current robot position
        rx = self.current_pose.position.x
        ry = self.current_pose.position.y
        
        best_x = None
        best_y = None
        min_cost = float('inf')

        # We'll sample up to 500 frontiers to save computation if the map is huge
        indices = np.random.choice(len(x_coords), min(500, len(x_coords)), replace=False)
        
        for idx in indices:
            fx = x_coords[idx] * res + origin_x
            fy = y_coords[idx] * res + origin_y
            
            # Simple euclidean distance cost
            dist = math.hypot(fx - rx, fy - ry)
            
            # Penalize frontiers that are TOO close (might have already been visited but map hasn't updated)
            if dist < 1.0:
                cost = 9999.0
            else:
                cost = dist

            if cost < min_cost:
                min_cost = cost
                best_x = fx
                best_y = fy

        if best_x is None or min_cost > 9000.0:
            self.get_logger().info("No valid distant frontiers found. Trying random one.")
            best_idx = np.random.choice(len(x_coords))
            best_x = x_coords[best_idx] * res + origin_x
            best_y = y_coords[best_idx] * res + origin_y

        self.send_goal(best_x, best_y)

    def send_goal(self, x, y):
        self.get_logger().info(f"Sending exploration target: x={x:.2f}, y={y:.2f}")
        
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0
        
        # Just face the direction of the goal lightly or just zero orientation
        goal_msg.pose.pose.orientation.w = 1.0
        
        if not self.nav_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("Nav2 Action Server not available")
            return
            
        self.exploring = True
        
        send_goal_future = self.nav_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info("Exploration goal rejected by Nav2.")
            self.exploring = False
            return

        self.get_logger().info("Exploration goal accepted.")
        self.goal_handle = goal_handle
        
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info("Reached exploration target or aborted.")
        self.exploring = False

def main(args=None):
    rclpy.init(args=args)
    node = SimpleFrontierExplorer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
