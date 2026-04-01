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
        
        # Goal state tracking for timeouts and stuck detection
        self.goal_start_time = None
        self.last_pose = None
        self.last_pose_time = None
        self.current_goal_x = None
        self.current_goal_y = None
        
        # Blacklist to temporarily remember and avoid stuck or unreachable areas
        self.blacklist = []
        
        # Safe margin to push frontier goals away from lethal obstacles (8 * 0.05m res = 0.40m)
        self.margin_cells = 8
        
        # Timer to run exploration logic continuously at a faster rate
        self.timer = self.create_timer(1.0, self.explore_step)
    def map_callback(self, msg):
        self.current_map = msg

    def odom_callback(self, msg):
        self.current_pose = msg.pose.pose

    def cancel_current_goal(self):
        """Safely handle goal cancellation and blacklisting for stuck/unreachable areas."""
        if self.goal_handle is not None:
            # Temporarily add current goal to blacklist
            if self.current_goal_x is not None and self.current_goal_y is not None:
                self.blacklist.append((self.current_goal_x, self.current_goal_y))
                # Prevent blacklist from growing indefinitely memory-wise
                if len(self.blacklist) > 20:
                    self.blacklist.pop(0)

            self.get_logger().info("Canceling current Nav2 goal...")
            self.goal_handle.cancel_goal_async()
            
        self.exploring = False
        self.goal_handle = None
        self.goal_start_time = None

    def explore_step(self):
        if self.current_map is None:
            self.get_logger().info("Waiting for /map...", throttle_duration_sec=5.0)
            return
            
        if self.current_pose is None:
            self.get_logger().info("Waiting for /odom...", throttle_duration_sec=5.0)
            return

        if self.exploring:
            # Instead of just waiting forever if the rover is stuck, check goal time & progress
            try:
                now_sec = self.get_clock().now().nanoseconds / 1e9
                if self.goal_start_time is not None:
                    # Cancel goal if it's taking extremely long (120s max for exploration)
                    if (now_sec - self.goal_start_time) > 120.0:
                        self.get_logger().warn("Goal timeout reached. Canceling and blacklisting area.")
                        self.cancel_current_goal()
                        return

                    # Safely check if we are stuck (moved less than 0.2m in 20 seconds)
                    if self.last_pose is not None and self.last_pose_time is not None:
                        dt = now_sec - self.last_pose_time
                        if dt > 20.0:
                            dx = self.current_pose.position.x - self.last_pose.position.x
                            dy = self.current_pose.position.y - self.last_pose.position.y
                            dist_moved = math.hypot(dx, dy)
                            if dist_moved < 0.2:
                                self.get_logger().warn("Rover seems stuck (no progress). Canceling and blacklisting area.")
                                self.cancel_current_goal()
                                return
                            else:
                                # Updated last pose check as we are still moving
                                self.last_pose = self.current_pose
                                self.last_pose_time = now_sec
                    else:
                        self.last_pose = self.current_pose
                        self.last_pose_time = now_sec
            except Exception as e:
                self.get_logger().error(f"Error in tracking progress: {e}")
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
            fx_idx = x_coords[idx]
            fy_idx = y_coords[idx]
            fx = fx_idx * res + origin_x
            fy = fy_idx * res + origin_y
            
            # Simple euclidean distance cost
            dist = math.hypot(fx - rx, fy - ry)
            
            # Penalize frontiers that are TOO close (might have already been visited but map hasn't updated)
            if dist < 1.0:
                cost = 9999.0
            else:
                cost = dist

            # 1. Penalize areas on our temporary blacklist (stuck regions)
            for bx, by in self.blacklist:
                if math.hypot(fx - bx, fy - by) < 1.5:
                    cost += 5000.0  # Encourage finding other frontiers safely

            # 2. Obstacle clearance check (Margin Filtering)
            # Only do the heavy matrix check if it's already a good candidate to save CPU
            if cost < min_cost:
                y_min = max(0, fy_idx - self.margin_cells)
                y_max = min(height, fy_idx + self.margin_cells + 1)
                x_min = max(0, fx_idx - self.margin_cells)
                x_max = min(width, fx_idx + self.margin_cells + 1)
                
                # If there's an obstacle (100) exactly around this frontier, severely penalize it
                if np.any(map_data[y_min:y_max, x_min:x_max] == 100):
                    cost += 3000.0

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
        
        # Track current destination to blacklist if we fail or get stuck
        self.current_goal_x = x
        self.current_goal_y = y
        
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
        
        # Initialize tracking for progress and timeout
        now_sec = self.get_clock().now().nanoseconds / 1e9
        self.goal_start_time = now_sec
        self.last_pose = self.current_pose
        self.last_pose_time = now_sec
        
        send_goal_future = self.nav_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info("Exploration goal rejected by Nav2. Blacklisting area.")
            # Blacklist this unreachable goal
            if self.current_goal_x is not None and self.current_goal_y is not None:
                self.blacklist.append((self.current_goal_x, self.current_goal_y))
                if len(self.blacklist) > 20:
                    self.blacklist.pop(0)

            self.exploring = False
            self.goal_start_time = None
            return

        self.get_logger().info("Exploration goal accepted.")
        self.goal_handle = goal_handle
        
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info("Reached exploration target or aborted.")
        self.exploring = False
        self.goal_handle = None
        self.goal_start_time = None

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
