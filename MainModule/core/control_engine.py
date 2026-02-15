"""
Smart Speed Control System - Control Engine Module
=================================================

Implements speed state management and control logic:
- NORMAL: Speed within limit
- WARNING: Speed slightly above limit (within tolerance)
- REGULATING: Speed significantly above limit (active deceleration)

Manages state transitions and notifies listeners of state changes.

Author: IoT Development Team
Version: 1.0
"""

import config


class ControlEngine:
    """
    Smart speed control engine managing vehicle speed state and regulation.
    
    Attributes:
        current_speed (float): Current vehicle speed in km/h
        speed_limit (float): Current speed limit in km/h
        current_state (str): Current control state (NORMAL/WARNING/REGULATING)
        state_callbacks (list): List of callbacks to notify on state changes
        regulation_factor (float): Acceleration reduction factor during regulation
    """
    
    def __init__(self):
        """Initialize control engine with default values."""
        self.current_speed = 0.0
        self.speed_limit = config.VEHICLE_MAX_SPEED
        self.current_state = config.SPEED_STATE_NORMAL
        self.state_callbacks = []
        self.regulation_factor = 1.0
        
        self._previous_state = None
        self._warning_triggered = False
        self._regulation_triggered = False
    
    def add_state_callback(self, callback):
        """
        Register a callback function to be called when state changes.
        
        Args:
            callback (callable): Function to call with state change info
                                 signature: callback(old_state, new_state, speed, limit)
        """
        self.state_callbacks.append(callback)
    
    def update(self, speed, speed_limit):
        """
        Update control state based on current speed and limit.
        Triggers state change callbacks if state changes.
        
        Args:
            speed (float): Current vehicle speed in km/h
            speed_limit (float): Current speed limit in km/h
        """
        self.current_speed = speed
        self.speed_limit = speed_limit
        
        # Determine state
        new_state = self._calculate_state(speed, speed_limit)
        
        # Trigger callbacks if state changed
        if new_state != self._previous_state:
            old_state = self._previous_state or config.SPEED_STATE_NORMAL
            self._notify_state_change(old_state, new_state)
            self._previous_state = new_state
        
        # Update regulation factor
        self._update_regulation_factor()
    
    def _calculate_state(self, speed, speed_limit):
        """
        Calculate current speed state.
        
        Args:
            speed (float): Current speed in km/h
            speed_limit (float): Speed limit in km/h
        
        Returns:
            str: State (NORMAL, WARNING, or REGULATING)
        """
        speed_over_limit = speed - speed_limit
        
        # Check regulating condition first (highest priority)
        if speed_over_limit > config.SPEED_WARNING_TOLERANCE:
            self.current_state = config.SPEED_STATE_REGULATING
            return config.SPEED_STATE_REGULATING
        
        # Check warning condition
        elif 0 < speed_over_limit <= config.SPEED_WARNING_TOLERANCE:
            self.current_state = config.SPEED_STATE_WARNING
            return config.SPEED_STATE_WARNING
        
        # Normal state
        else:
            self.current_state = config.SPEED_STATE_NORMAL
            return config.SPEED_STATE_NORMAL
    
    def _update_regulation_factor(self):
        """
        Update acceleration regulation factor based on current state.
        Used to gradually reduce acceleration during regulation.
        """
        if self.current_state == config.SPEED_STATE_REGULATING:
            # Calculate how much over the limit we are
            overspeed = self.current_speed - self.speed_limit
            max_overspeed = config.SPEED_WARNING_TOLERANCE * 2
            
            # Linear interpolation: at max overspeed, factor = 0 (no acceleration)
            self.regulation_factor = max(0.0, 1.0 - (overspeed / max_overspeed))
        
        elif self.current_state == config.SPEED_STATE_WARNING:
            self.regulation_factor = 0.5  # 50% acceleration allowed
        
        else:  # NORMAL
            self.regulation_factor = 1.0
    
    def _notify_state_change(self, old_state, new_state):
        """
        Notify all registered callbacks of state change.
        
        Args:
            old_state (str): Previous state
            new_state (str): New state
        """
        for callback in self.state_callbacks:
            try:
                callback(old_state, new_state, self.current_speed, self.speed_limit)
            except Exception as e:
                print(f"Error in state change callback: {e}")
    
    def get_acceleration_multiplier(self):
        """
        Get the acceleration multiplier to apply to user input.
        During regulation, this reduces available acceleration.
        
        Returns:
            float: Multiplier 0.0 to 1.0
        """
        return self.regulation_factor
    
    def get_current_state(self):
        """
        Get current control state information.
        
        Returns:
            dict: State information including state name, color, and regulation factor
        """
        state_colors = {
            config.SPEED_STATE_NORMAL: (0.0, 1.0, 0.0),      # Green
            config.SPEED_STATE_WARNING: (1.0, 1.0, 0.0),     # Yellow
            config.SPEED_STATE_REGULATING: (1.0, 0.0, 0.0)   # Red
        }
        
        return {
            "state": self.current_state,
            "color": state_colors.get(self.current_state, (1.0, 1.0, 1.0)),
            "speed": self.current_speed,
            "limit": self.speed_limit,
            "overspeed": max(0, self.current_speed - self.speed_limit),
            "regulation_factor": self.regulation_factor
        }
    
    def is_warning(self):
        """Check if system is in warning state."""
        return self.current_state == config.SPEED_STATE_WARNING
    
    def is_regulating(self):
        """Check if system is in regulating state."""
        return self.current_state == config.SPEED_STATE_REGULATING
    
    def is_normal(self):
        """Check if system is in normal state."""
        return self.current_state == config.SPEED_STATE_NORMAL
    
    def reset(self):
        """Reset control engine to initial state."""
        self.current_speed = 0.0
        self.speed_limit = config.VEHICLE_MAX_SPEED
        self.current_state = config.SPEED_STATE_NORMAL
        self.regulation_factor = 1.0
        self._previous_state = None
        self._warning_triggered = False
        self._regulation_triggered = False
