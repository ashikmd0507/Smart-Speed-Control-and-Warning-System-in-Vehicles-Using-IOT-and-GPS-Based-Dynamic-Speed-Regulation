"""
Smart Speed Control System - Vehicle Module
==========================================

Encapsulates vehicle representation in the 3D environment.
Manages vehicle position, rotation, speed display, and 3D model updates.
Bridges physics engine with 3D rendering.

Author: IoT Development Team
Version: 1.0
"""

import config


class Vehicle:
    """
    Represents the vehicle in the simulation.
    
    Attributes:
        position (tuple): Current vehicle position (x, y, z)
        velocity (float): Current velocity in km/h
        heading (float): Current heading in degrees
        physics_engine (VehiclePhysics): Physics simulation engine
        node (NodePath): Panda3D node representing the vehicle
    """
    
    def __init__(self, physics_engine):
        """
        Initialize vehicle instance.
        
        Args:
            physics_engine (VehiclePhysics): Physics simulation engine
        """
        self.physics_engine = physics_engine
        self.node = None  # Will be set by 3D engine
        self.position = (0, 0, 0)
        self.velocity = 0.0
        self.heading = 0.0
    
    def update(self, dt, acceleration, steering, braking, speed_regulation_factor=1.0):
        """
        Update vehicle state based on physics.
        
        Args:
            dt (float): Delta time in seconds
            acceleration (float): Input acceleration (-1 to 1)
            steering (float): Input steering (-1 to 1)
            braking (bool): Braking state
            speed_regulation_factor (float): Speed regulation multiplier
        
        Returns:
            tuple: Updated (velocity, position)
        """
        # Set inputs
        self.physics_engine.set_inputs(acceleration, steering, braking)
        
        # Update physics with speed regulation
        max_speed = getattr(self, '_max_speed_limit', config.VEHICLE_MAX_SPEED)
        velocity, position = self.physics_engine.update(
            dt,
            max_speed_limit=max_speed,
            max_acceleration=speed_regulation_factor
        )
        
        # Update vehicle state
        self.velocity = velocity
        self.position = position
        self.heading = self.physics_engine.heading
        
        return velocity, position
    
    def set_position(self, x, y, z=0):
        """
        Set vehicle position.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            z (float): Z coordinate (optional)
        """
        self.position = (x, y, z)
        self.physics_engine.position[0] = x
        self.physics_engine.position[1] = y
        self.physics_engine.position[2] = z
    
    def get_position(self):
        """
        Get current vehicle position.
        
        Returns:
            tuple: (x, y, z) coordinates
        """
        return self.position
    
    def get_velocity(self):
        """
        Get current vehicle velocity.
        
        Returns:
            float: Velocity in km/h
        """
        return self.velocity
    
    def get_heading(self):
        """
        Get current vehicle heading.
        
        Returns:
            float: Heading in degrees
        """
        return self.heading
    
    def set_speed_limit(self, limit):
        """
        Set current speed limit for regulation.
        
        Args:
            limit (float): Speed limit in km/h
        """
        self._max_speed_limit = limit
    
    def reset(self):
        """Reset vehicle to initial state."""
        self.physics_engine.reset()
        self.position = (0, 0, 0)
        self.velocity = 0.0
        self.heading = 0.0
    
    def get_state(self):
        """
        Get complete vehicle state.
        
        Returns:
            dict: Vehicle state information
        """
        return {
            "position": self.position,
            "velocity": self.velocity,
            "heading": self.heading,
            "physics_state": self.physics_engine.get_state()
        }
    
    def set_3d_node(self, node):
        """
        Set the Panda3D node representing this vehicle.
        
        Args:
            node (NodePath): Panda3D node
        """
        self.node = node
    
    def update_3d_representation(self):
        """Update 3D node position and rotation to match vehicle state."""
        if self.node:
            x, y, z = self.position
            self.node.setX(x)
            self.node.setY(y)
            self.node.setZ(z)
            
            # Set heading rotation (rotate around Z-axis)
            self.node.setH(self.heading)
