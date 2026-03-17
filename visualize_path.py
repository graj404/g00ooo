#!/usr/bin/env python3
"""
Visualize the recorded path from dead reckoning
"""

import numpy as np
import matplotlib.pyplot as plt
from config import LOG_FILE


def plot_path(log_file=LOG_FILE):
    """Plot the vehicle path from log file"""
    try:
        data = np.loadtxt(log_file, delimiter=',', skiprows=1)
        
        if len(data) == 0:
            print("No data to plot")
            return
        
        timestamps = data[:, 0]
        x = data[:, 1]
        y = data[:, 2]
        heading = data[:, 3]
        velocity = data[:, 4]
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Path plot
        axes[0, 0].plot(x, y, 'b-', linewidth=2)
        axes[0, 0].plot(x[0], y[0], 'go', markersize=10, label='Start')
        axes[0, 0].plot(x[-1], y[-1], 'ro', markersize=10, label='End')
        axes[0, 0].set_xlabel('X Position (m)')
        axes[0, 0].set_ylabel('Y Position (m)')
        axes[0, 0].set_title('Vehicle Path')
        axes[0, 0].grid(True)
        axes[0, 0].legend()
        axes[0, 0].axis('equal')
        
        # Velocity over time
        axes[0, 1].plot(timestamps - timestamps[0], velocity, 'r-')
        axes[0, 1].set_xlabel('Time (s)')
        axes[0, 1].set_ylabel('Velocity (m/s)')
        axes[0, 1].set_title('Velocity Profile')
        axes[0, 1].grid(True)
        
        # Heading over time
        axes[1, 0].plot(timestamps - timestamps[0], np.degrees(heading), 'g-')
        axes[1, 0].set_xlabel('Time (s)')
        axes[1, 0].set_ylabel('Heading (degrees)')
        axes[1, 0].set_title('Heading Profile')
        axes[1, 0].grid(True)
        
        # Distance traveled
        distances = np.sqrt(np.diff(x)**2 + np.diff(y)**2)
        cumulative_distance = np.concatenate(([0], np.cumsum(distances)))
        axes[1, 1].plot(timestamps - timestamps[0], cumulative_distance, 'm-')
        axes[1, 1].set_xlabel('Time (s)')
        axes[1, 1].set_ylabel('Distance (m)')
        axes[1, 1].set_title('Cumulative Distance')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig('path_visualization.png', dpi=150)
        print(f"Path visualization saved to: path_visualization.png")
        plt.show()
        
    except FileNotFoundError:
        print(f"Log file not found: {log_file}")
    except Exception as e:
        print(f"Error plotting path: {e}")


if __name__ == "__main__":
    plot_path()
