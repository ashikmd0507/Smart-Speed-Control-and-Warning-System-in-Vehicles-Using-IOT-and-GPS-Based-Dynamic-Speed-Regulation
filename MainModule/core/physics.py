"""
Smart Speed Control System - Physics Engine Module
==================================================

Handles realistic vehicle physics simulation including:
- Acceleration and deceleration
- Friction and drag
- Speed limiting
- Steering and rotation

Author: IoT Development Team
Version: 1.0
"""

import math
import config


class VehiclePhysics:
    """
    Realistic vehicle physics engine with acceleration, friction, and speed control.
    
    Attributes:
        position (tuple): Current vehicle position (x, y, z)
        velocity (float): Current velocity in km/h
        heading (float): Current heading angle in degrees
        acceleration_input (float): Input acceleration (-1 to 1)
        steering_input (float): Input steering (-1 to 1)
        is_braking (bool): Whether brakes are applied
    """
    
    def __init__(self):
        """Initialize vehicle physics with default values."""
        self.position = list(config.VEHICLE_INITIAL_POSITION)
        self.velocity = 0.0  # km/h
        self.heading = 0.0  # degrees (0 = +X direction)
        
        self.acceleration_input = 0.0  # -1 to 1
        self.steering_input = 0.0  # -1 to 1
        self.is_braking = False
        
        self._heading_velocity = 0.0  # degrees per second
        
    def update(self, dt, max_speed_limit=None, max_acceleration=1.0):
        """
        Update physics state for dt seconds.
        
        Args:
            dt (float): Delta time in seconds
            max_speed_limit (float): Maximum allowed speed in km/h
            max_acceleration (float): Acceleration multiplier (0 to 1)
        
        Returns:
            tuple: Updated (velocity, position)
        """
        # Apply acceleration/deceleration
        if self.is_braking:
            decel = config.VEHICLE_DECELERATION_BRAKE * dt
            self.velocity = max(0, self.velocity - decel)
        elif self.acceleration_input > 0:
            accel = config.VEHICLE_ACCELERATION * self.acceleration_input * max_acceleration * dt
            self.velocity = min(config.VEHICLE_MAX_SPEED, self.velocity + accel)
        elif self.acceleration_input < 0:
            decel = config.VEHICLE_DECELERATION_NORMAL * abs(self.acceleration_input) * dt
            self.velocity = max(0, self.velocity - decel)
        else:
            # Passive friction
            friction = config.VEHICLE_FRICTION * dt
            self.velocity = max(0, self.velocity - friction)
        
        # Apply max speed limit regulation
        if max_speed_limit is not None and self.velocity > max_speed_limit:
            # Gradual deceleration
            overspeed = self.velocity - max_speed_limit
            friction_factor = min(1.0, overspeed / 10.0)  # Scale friction with overspeed
            decel = config.VEHICLE_FRICTION * 2.5 * friction_factor * dt
            self.velocity = max(max_speed_limit * 0.95, self.velocity - decel)
        
        # Update heading based on steering
        if abs(self.steering_input) > 0.01:
            self._heading_velocity = config.VEHICLE_STEERING_SPEED * self.steering_input
        else:
            self._heading_velocity *= 0.8  # Damping
        
        self.heading += self._heading_velocity * dt
        self.heading = self.heading % 360.0
        
        # Move vehicle based on velocity and heading
        # Convert heading to radians
        heading_rad = math.radians(self.heading)
        distance = (self.velocity / 3.6) * dt  # Convert km/h to m/s, then to meters per dt
        
        self.position[0] += distance * math.cos(heading_rad)
        self.position[1] += distance * math.sin(heading_rad)
        
        return self.velocity, tuple(self.position)
    
    def set_inputs(self, acceleration, steering, braking):
        """
        Set user input values.
        
        Args:
            acceleration (float): -1 (brake) to 1 (accelerate)
            steering (float): -1 (left) to 1 (right)
            braking (bool): Whether brakes are being applied
        """
        self.acceleration_input = max(-1.0, min(1.0, acceleration))
        self.steering_input = max(-1.0, min(1.0, steering))
        self.is_braking = braking
    
    def reset(self):
        """Reset vehicle to initial state."""
        self.position = list(config.VEHICLE_INITIAL_POSITION)
        self.velocity = 0.0
        self.heading = 0.0
        self.acceleration_input = 0.0
        self.steering_input = 0.0
        self.is_braking = False
        self._heading_velocity = 0.0
    
    def get_state(self):
        """
        Get current physics state.
        
        Returns:
            dict: Current state including position, velocity, heading
        """
        return {
            "position": tuple(self.position),
            "velocity": self.velocity,
            "heading": self.heading,
            "acceleration_input": self.acceleration_input,
            "steering_input": self.steering_input,
        }
