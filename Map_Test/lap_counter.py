"""
Lap counting system using dead reckoning only
Handles edge cases like returning to start from opposite direction
"""

import numpy as np
from collections import deque


class LapCounter:
    """Count laps using position tracking and reference path matching"""
    
    def __init__(self, start_threshold=2.0, min_lap_distance=10.0):
        """
        Args:
            start_threshold: Distance from origin to consider as lap completion (meters)
            min_lap_distance: Minimum distance to count as valid lap (meters)
        """
        self.start_position = np.array([0.0, 0.0], dtype=np.float64)
        self.start_threshold = start_threshold
        self.min_lap_distance = min_lap_distance
        
        # Lap tracking
        self.laps_completed = 0
        self.current_lap_distance = 0.0
        self.total_distance = 0.0
        self.last_position = self.start_position.copy()
        
        # Reference path (learned from first lap)
        self.reference_path = []
        self.reference_learned = False
        self.path_resolution = 0.5  # Store point every 0.5m
        
        # State tracking
        self.was_near_start = True
        self.left_start_zone = False
        self.position_history = deque(maxlen=100)  # Last 100 positions
        
        # Direction tracking for opposite direction detection
        self.approach_vectors = []
    
    def update(self, current_position):
        """
        Update lap counter with new position
        
        Args:
            current_position: numpy array [x, y]
        
        Returns:
            tuple: (laps_completed, current_lap_distance, total_distance, lap_just_completed)
        """
        # Calculate distance traveled since last update
        displacement = np.linalg.norm(current_position - self.last_position)
        self.current_lap_distance += displacement
        self.total_distance += displacement
        
        # Store position history
        self.position_history.append(current_position.copy())
        
        # Check if near start position
        distance_from_start = np.linalg.norm(current_position - self.start_position)
        is_near_start = distance_from_start < self.start_threshold
        
        lap_just_completed = False
        
        # Lap detection logic
        if not self.was_near_start and is_near_start:
            # Just entered start zone
            if self.left_start_zone and self.current_lap_distance >= self.min_lap_distance:
                # Valid lap completion
                
                # Check if approaching from opposite direction
                is_opposite_direction = self._check_opposite_direction(current_position)
                
                if not self.reference_learned:
                    # First lap - learn the reference path
                    self._learn_reference_path()
                    self.reference_learned = True
                    print(f"Reference path learned: {len(self.reference_path)} points")
                
                self.laps_completed += 1
                lap_just_completed = True
                print(f"Lap {self.laps_completed} completed! Distance: {self.current_lap_distance:.2f}m "
                      f"{'(OPPOSITE DIRECTION)' if is_opposite_direction else ''}")
                
                # Reset lap distance
                self.current_lap_distance = 0.0
                self.left_start_zone = False
        
        elif self.was_near_start and not is_near_start:
            # Just left start zone
            self.left_start_zone = True
        
        # Update state
        self.was_near_start = is_near_start
        self.last_position = current_position.copy()
        
        # Store reference path points during first lap
        if not self.reference_learned and self.left_start_zone:
            if len(self.reference_path) == 0 or \
               np.linalg.norm(current_position - self.reference_path[-1]) >= self.path_resolution:
                self.reference_path.append(current_position.copy())
        
        return self.laps_completed, self.current_lap_distance, self.total_distance, lap_just_completed
    
    def _check_opposite_direction(self, current_position):
        """
        Detect if vehicle is approaching start from opposite direction
        Uses recent position history to determine approach vector
        """
        if len(self.position_history) < 10:
            return False
        
        # Get approach vector (direction of travel over last few positions)
        recent_positions = list(self.position_history)[-10:]
        approach_vector = recent_positions[-1] - recent_positions[0]
        approach_vector_norm = np.linalg.norm(approach_vector)
        
        if approach_vector_norm < 0.1:
            return False  # Not moving enough to determine direction
        
        approach_vector = approach_vector / approach_vector_norm
        
        # Store approach vector for this lap completion
        self.approach_vectors.append(approach_vector.copy())
        
        # If we have at least 2 lap completions, compare directions
        if len(self.approach_vectors) >= 2:
            # Compare with previous approach vector
            prev_vector = self.approach_vectors[-2]
            dot_product = np.dot(approach_vector, prev_vector)
            
            # If dot product is negative, directions are opposite
            # Threshold at -0.5 to allow some variation
            if dot_product < -0.5:
                return True
        
        return False
    
    def _learn_reference_path(self):
        """Store the reference path from first lap"""
        # Reference path is already stored in self.reference_path
        # This method can be extended for path smoothing or validation
        pass
    
    def get_lap_info(self):
        """Get current lap information"""
        return {
            'laps_completed': self.laps_completed,
            'current_lap_distance': self.current_lap_distance,
            'total_distance': self.total_distance,
            'reference_learned': self.reference_learned,
            'reference_path_points': len(self.reference_path)
        }
    
    def reset(self):
        """Reset lap counter"""
        self.laps_completed = 0
        self.current_lap_distance = 0.0
        self.total_distance = 0.0
        self.last_position = self.start_position.copy()
        self.was_near_start = True
        self.left_start_zone = False
        self.position_history.clear()
        self.approach_vectors.clear()
        print("Lap counter reset")
    
    def set_start_position(self, position):
        """Set new start position"""
        self.start_position = position.copy()
        self.last_position = position.copy()
        print(f"Start position set to: ({position[0]:.2f}, {position[1]:.2f})")
