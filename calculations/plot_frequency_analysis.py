#!/usr/bin/env python3
"""
Frequency and Point Density Analysis with Matplotlib
Shows how update frequency affects number of plotted points
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

def calculate_points(frequency, velocity, distance):
    """
    Calculate number of points for given parameters
    
    Args:
        frequency: Update rate in Hz
        velocity: Speed in m/s
        distance: Total distance in meters
    
    Returns:
        num_points: Number of (x,y) points
        time_taken: Time to travel distance
    """
    time_taken = distance / velocity
    num_points = int(frequency * time_taken)
    return num_points, time_taken

def generate_path(frequency, velocity, distance, heading=0):
    """Generate path points"""
    time_taken = distance / velocity
    dt = 1.0 / frequency
    num_points = int(frequency * time_taken)
    
    times = np.arange(0, time_taken, dt)[:num_points]
    x = velocity * times * np.cos(heading)
    y = velocity * times * np.sin(heading)
    
    return x, y, times

def plot_scenario_1():
    """
    Scenario 1: User enters frequency and velocity
    Shows how points decrease when velocity increases (for fixed time)
    """
    print("\n" + "="*60)
    print("SCENARIO 1: Frequency and Velocity Analysis")
    print("="*60)
    
    frequency = float(input("Enter update frequency (Hz): "))
    velocity = float(input("Enter velocity (m/s): "))
    time_duration = float(input("Enter time duration (seconds): "))
    
    distance = velocity * time_duration
    num_points = int(frequency * time_duration)
    
    print(f"\nCalculated:")
    print(f"  Distance traveled: {distance:.2f} m")
    print(f"  Number of points: {num_points}")
    print(f"  Points per meter: {num_points/distance:.2f}")
    
    # Generate path
    x, y, times = generate_path(frequency, velocity, distance)
    
    # Create figure
    fig = plt.figure(figsize=(14, 10))
    gs = GridSpec(3, 2, figure=fig)
    
    # Plot 1: Path visualization
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(x, y, 'o-', markersize=4, linewidth=1, color='blue')
    ax1.plot(x[0], y[0], 'go', markersize=10, label='Start')
    ax1.plot(x[-1], y[-1], 'ro', markersize=10, label='End')
    ax1.set_xlabel('X Position (m)', fontsize=12)
    ax1.set_ylabel('Y Position (m)', fontsize=12)
    ax1.set_title(f'Path: {frequency:.0f} Hz, {velocity:.1f} m/s, {num_points} points', 
                  fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.axis('equal')
    
    # Plot 2: Compare different velocities at same frequency
    ax2 = fig.add_subplot(gs[1, 0])
    velocities = [velocity * 0.5, velocity, velocity * 2]
    colors = ['green', 'blue', 'red']
    
    for v, c in zip(velocities, colors):
        x_v, y_v, _ = generate_path(frequency, v, distance)
        ax2.plot(x_v, y_v, 'o-', markersize=3, color=c, 
                label=f'{v:.1f} m/s ({len(x_v)} pts)')
    
    ax2.set_xlabel('X Position (m)', fontsize=10)
    ax2.set_ylabel('Y Position (m)', fontsize=10)
    ax2.set_title(f'Same Distance, Different Velocities\n({frequency:.0f} Hz)', 
                  fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.axis('equal')
    
    # Plot 3: Points vs Velocity
    ax3 = fig.add_subplot(gs[1, 1])
    vel_range = np.linspace(1, velocity * 3, 50)
    points_range = [int(frequency * (distance / v)) for v in vel_range]
    
    ax3.plot(vel_range, points_range, 'b-', linewidth=2)
    ax3.plot(velocity, num_points, 'ro', markersize=10, label='Your input')
    ax3.set_xlabel('Velocity (m/s)', fontsize=10)
    ax3.set_ylabel('Number of Points', fontsize=10)
    ax3.set_title(f'Points vs Velocity\n(Fixed: {frequency:.0f} Hz, {distance:.0f}m)', 
                  fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # Plot 4: Time series
    ax4 = fig.add_subplot(gs[2, :])
    ax4.plot(times, x, 'b-', linewidth=2, label='X position')
    ax4.plot(times, y, 'r-', linewidth=2, label='Y position')
    ax4.scatter(times, x, c='blue', s=20, alpha=0.5)
    ax4.scatter(times, y, c='red', s=20, alpha=0.5)
    ax4.set_xlabel('Time (s)', fontsize=12)
    ax4.set_ylabel('Position (m)', fontsize=12)
    ax4.set_title(f'Position vs Time ({len(times)} data points)', 
                  fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('scenario1_frequency_velocity.png', dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: scenario1_frequency_velocity.png")
    plt.show()


def plot_scenario_2():
    """
    Scenario 2: User enters distance
    Shows how points increase with distance at different frequencies
    """
    print("\n" + "="*60)
    print("SCENARIO 2: Distance and Frequency Analysis")
    print("="*60)
    
    distance = float(input("Enter distance to travel (meters): "))
    velocity = float(input("Enter velocity (m/s): "))
    
    frequencies = [10, 100, 1000, 10000]
    
    print(f"\nAnalysis for {distance:.0f}m at {velocity:.1f} m/s:")
    print(f"Time to travel: {distance/velocity:.2f} seconds\n")
    
    print("┌────────────┬──────────────┬─────────────────┐")
    print("│ Frequency  │ Num Points   │ Points per Meter│")
    print("├────────────┼──────────────┼─────────────────┤")
    
    results = []
    for freq in frequencies:
        num_pts, time_taken = calculate_points(freq, velocity, distance)
        pts_per_meter = num_pts / distance
        results.append((freq, num_pts, pts_per_meter))
        print(f"│ {freq:6.0f} Hz  │ {num_pts:10d}   │ {pts_per_meter:13.2f}    │")
    
    print("└────────────┴──────────────┴─────────────────┘")
    
    # Create comprehensive figure
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(3, 3, figure=fig)
    
    # Plot paths for each frequency
    colors = ['red', 'orange', 'green', 'blue']
    
    for idx, (freq, color) in enumerate(zip(frequencies, colors)):
        row = idx // 2
        col = idx % 2
        ax = fig.add_subplot(gs[row, col])
        
        x, y, times = generate_path(freq, velocity, distance)
        ax.plot(x, y, 'o-', markersize=2, linewidth=1, color=color, alpha=0.7)
        ax.plot(x[0], y[0], 'go', markersize=8)
        ax.plot(x[-1], y[-1], 'ro', markersize=8)
        
        ax.set_xlabel('X Position (m)', fontsize=10)
        ax.set_ylabel('Y Position (m)', fontsize=10)
        ax.set_title(f'{freq} Hz: {len(x)} points', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
    
    # Plot: Number of points comparison
    ax_bar = fig.add_subplot(gs[2, 0])
    freqs_labels = [f'{f} Hz' for f in frequencies]
    num_points_list = [r[1] for r in results]
    
    bars = ax_bar.bar(freqs_labels, num_points_list, color=colors, alpha=0.7, edgecolor='black')
    ax_bar.set_ylabel('Number of Points', fontsize=12)
    ax_bar.set_title('Total Points by Frequency', fontsize=12, fontweight='bold')
    ax_bar.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, val in zip(bars, num_points_list):
        height = bar.get_height()
        ax_bar.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:,}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Plot: Points per meter
    ax_ppm = fig.add_subplot(gs[2, 1])
    pts_per_meter_list = [r[2] for r in results]
    
    ax_ppm.plot(frequencies, pts_per_meter_list, 'o-', linewidth=2, markersize=8, color='purple')
    ax_ppm.set_xlabel('Frequency (Hz)', fontsize=12)
    ax_ppm.set_ylabel('Points per Meter', fontsize=12)
    ax_ppm.set_title('Point Density vs Frequency', fontsize=12, fontweight='bold')
    ax_ppm.set_xscale('log')
    ax_ppm.set_yscale('log')
    ax_ppm.grid(True, alpha=0.3, which='both')
    
    # Add annotations
    for freq, ppm in zip(frequencies, pts_per_meter_list):
        ax_ppm.annotate(f'{ppm:.1f}', xy=(freq, ppm), 
                       xytext=(10, 10), textcoords='offset points',
                       fontsize=9, fontweight='bold')
    
    # Summary text
    ax_text = fig.add_subplot(gs[2, 2])
    ax_text.axis('off')
    
    summary_text = f"""
SUMMARY
{'='*30}

Distance: {distance:.0f} m
Velocity: {velocity:.1f} m/s
Time: {distance/velocity:.2f} s

POINTS GENERATED:
"""
    
    for freq, num_pts, ppm in results:
        summary_text += f"\n{freq:>6.0f} Hz: {num_pts:>8,} pts"
        summary_text += f"\n         ({ppm:.1f} pts/m)"
    
    summary_text += f"""

KEY INSIGHT:
Higher frequency = 
More points = 
Smoother path
"""
    
    ax_text.text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
                verticalalignment='center', bbox=dict(boxstyle='round', 
                facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('scenario2_distance_frequency.png', dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: scenario2_distance_frequency.png")
    plt.show()


def main():
    """Main menu"""
    print("╔════════════════════════════════════════════════════════╗")
    print("║   FREQUENCY AND POINT DENSITY ANALYSIS WITH PLOTS     ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    print("\nChoose scenario:")
    print("1. Enter frequency and velocity (shows effect on points)")
    print("2. Enter distance (compare frequencies: 10, 100, 1000, 10000 Hz)")
    print("3. Both scenarios")
    
    choice = input("\nYour choice (1/2/3): ")
    
    if choice == '1':
        plot_scenario_1()
    elif choice == '2':
        plot_scenario_2()
    elif choice == '3':
        plot_scenario_1()
        plot_scenario_2()
    else:
        print("Invalid choice!")
        return
    
    print("\n" + "="*60)
    print("Analysis complete! Check the generated PNG files.")
    print("="*60)

if __name__ == "__main__":
    main()
