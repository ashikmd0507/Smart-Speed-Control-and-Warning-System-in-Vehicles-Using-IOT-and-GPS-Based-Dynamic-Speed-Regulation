"""
Smart Speed Control System - Zone Management Module
===================================================

Manages speed control zones and dynamically determines current zone based on vehicle position.
Handles zone detection, speed limit retrieval, and zone visualization data.

Author: IoT Development Team
Version: 1.0
"""

import config


class Zone:
    """
    Represents a speed control zone with boundaries and limits.
    
    Attributes:
        zone_id (str): Unique zone identifier
        name (str): Display name of the zone
        speed_limit (float): Speed limit in km/h
        color (tuple): RGB color for zone visualization
        x_range (tuple): (min_x, max_x) boundaries
        y_range (tuple): (min_y, max_y) boundaries
    """
    
    def __init__(self, zone_id, name, speed_limit, color, x_range, y_range):
        """
        Initialize a speed control zone.
        
        Args:
            zone_id (str): Unique zone identifier
            name (str): Display name
            speed_limit (float): Speed limit in km/h
            color (tuple): RGB color (0-1 range)
            x_range (tuple): (min_x, max_x)
            y_range (tuple): (min_y, max_y)
        """
        self.zone_id = zone_id
        self.name = name
        self.speed_limit = speed_limit
        self.color = color
        self.x_range = x_range
        self.y_range = y_range
    
    def contains_point(self, x, y):
        """
        Check if a point is within this zone.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
        
        Returns:
            bool: True if point is within zone boundaries
        """
        x_min, x_max = self.x_range
        y_min, y_max = self.y_range
        return x_min <= x <= x_max and y_min <= y <= y_max
    
    def get_boundary_distance(self, x, y):
        """
        Calculate minimum distance to zone boundary.
        
        Args:
            x (float): Current x position
            y (float): Current y position
        
        Returns:
            float: Minimum distance to any boundary
        """
        if self.contains_point(x, y):
            x_min, x_max = self.x_range
            y_min, y_max = self.y_range
            
            dist_x_min = abs(x - x_min)
            dist_x_max = abs(x - x_max)
            dist_y_min = abs(y - y_min)
            dist_y_max = abs(y - y_max)
            
            return min(dist_x_min, dist_x_max, dist_y_min, dist_y_max)
        return float('inf')


class ZoneManager:
    """
    Manages all speed control zones and determines current zone based on vehicle position.
    
    Attributes:
        zones (dict): Dictionary of Zone objects keyed by zone_id
        current_zone (Zone): Currently active zone
    """
    
    def __init__(self):
        """Initialize zone manager with predefined zones from config."""
        self.zones = {}
        self.current_zone = None
        self._initialize_zones()
    
    def _initialize_zones(self):
        """Initialize zones from configuration."""
        for zone_id, zone_config in config.ZONES.items():
            zone = Zone(
                zone_id=zone_id,
                name=zone_config["name"],
                speed_limit=zone_config["speed_limit"],
                color=zone_config["color"],
                x_range=zone_config["x_range"],
                y_range=zone_config["y_range"]
            )
            self.zones[zone_id] = zone
        
        # Set initial zone
        if self.zones:
            self.current_zone = next(iter(self.zones.values()))
    
    def update_position(self, x, y):
        """
        Update current zone based on vehicle position.
        Returns the zone that the vehicle is currently in.
        
        Args:
            x (float): Vehicle X coordinate
            y (float): Vehicle Y coordinate
        
        Returns:
            Zone: Current zone object
        """
        for zone in self.zones.values():
            if zone.contains_point(x, y):
                self.current_zone = zone
                return zone
        
        # If no zone contains position, keep current zone
        return self.current_zone
    
    def get_speed_limit(self, x, y):
        """
        Get the speed limit for a given position.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
        
        Returns:
            float: Speed limit in km/h
        """
        zone = self.update_position(x, y)
        if zone:
            return zone.speed_limit
        return config.VEHICLE_MAX_SPEED
    
    def get_current_zone_name(self):
        """
        Get current zone display name.
        
        Returns:
            str: Zone name
        """
        if self.current_zone:
            return self.current_zone.name
        return "Unknown Zone"
    
    def get_current_zone_color(self):
        """
        Get current zone color for HUD display.
        
        Returns:
            tuple: RGB color (0-1 range)
        """
        if self.current_zone:
            return self.current_zone.color
        return (1.0, 1.0, 1.0)  # White as default
    
    def get_all_zones_info(self):
        """
        Get information about all zones.
        
        Returns:
            list: List of zone information dictionaries
        """
        zones_info = []
        for zone_id, zone in self.zones.items():
            zones_info.append({
                "id": zone_id,
                "name": zone.name,
                "speed_limit": zone.speed_limit,
                "color": zone.color,
                "position": {
                    "x_range": zone.x_range,
                    "y_range": zone.y_range
                }
            })
        return zones_info
    
    def get_current_state(self):
        """
        Get current zone state.
        
        Returns:
            dict: Current zone information
        """
        if self.current_zone:
            return {
                "zone_id": self.current_zone.zone_id,
                "zone_name": self.current_zone.name,
                "speed_limit": self.current_zone.speed_limit,
                "color": self.current_zone.color
            }
        return {
            "zone_id": "unknown",
            "zone_name": "Unknown",
            "speed_limit": config.VEHICLE_MAX_SPEED,
            "color": (1.0, 1.0, 1.0)
        }
