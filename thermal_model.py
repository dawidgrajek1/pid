"""
Advanced thermal model for PCR thermocycler simulation.
Includes heating/cooling power limits, ambient heat loss, and configurable sample properties.
"""

import numpy as np


class ThermalModel:
    """
    Advanced thermal model for PCR thermocycler.
    
    Models heat transfer with:
    - Separate heating and cooling power limits
    - Ambient heat loss (proportional to temperature difference)
    - Configurable thermal mass (block + samples)
    - Sample properties (volume, density, specific heat)
    """
    
    def __init__(
        self,
        heat_capacity: float = 500.0,  # J/K
        heating_power: float = 250.0,  # W
        cooling_power: float = 150.0,  # W
        heat_loss_coef: float = 1.5,  # W/K
        ambient_temp: float = 22.0,  # °C
        sample_volume: float = 5e-6,  # m³
        sample_density: float = 1000.0,  # kg/m³
        sample_specific_heat: float = 4100.0,  # J/(kg·K)
        initial_temp: float = 22.0,  # °C
    ):
        """
        Initialize thermal model.
        
        Args:
            heat_capacity: Total heat capacity of system (J/K)
            heating_power: Maximum heating power (W)
            cooling_power: Maximum cooling power (W, positive value)
            heat_loss_coef: Heat loss coefficient to ambient (W/K)
            ambient_temp: Ambient temperature (°C)
            sample_volume: Volume of sample (m³)
            sample_density: Density of sample (kg/m³)
            sample_specific_heat: Specific heat capacity of sample (J/(kg·K))
            initial_temp: Initial temperature (°C)
        """
        self.heat_capacity = heat_capacity
        self.heating_power = heating_power
        self.cooling_power = cooling_power
        self.heat_loss_coef = heat_loss_coef
        self.ambient_temp = ambient_temp
        self.sample_volume = sample_volume
        self.sample_density = sample_density
        self.sample_specific_heat = sample_specific_heat
        self.temperature = initial_temp
        
        # Calculate sample contribution to heat capacity
        sample_mass = sample_volume * sample_density
        self.sample_heat_capacity = sample_mass * sample_specific_heat
        
        # Total effective heat capacity (block + sample)
        # Note: heat_capacity parameter includes both, but we track sample separately
        self.total_heat_capacity = heat_capacity
    
    def calculate_heat_flow(self, control_output: float) -> float:
        """
        Calculate net heat flow into the system.
        
        Args:
            control_output: Control signal from PID controller (W)
                           Positive = heating, Negative = cooling
        
        Returns:
            Net heat flow (W) after applying power limits and ambient losses
        """
        # Apply power limits
        if control_output > 0:
            # Heating mode
            applied_power = min(control_output, self.heating_power)
        else:
            # Cooling mode (control_output is negative)
            applied_power = max(control_output, -self.cooling_power)
        
        # Calculate ambient heat loss (always losing heat to ambient)
        # Positive when temp > ambient (heat loss), negative when temp < ambient (heat gain)
        heat_loss = self.heat_loss_coef * (self.temperature - self.ambient_temp)
        
        # Net heat flow = applied power - ambient losses
        net_heat_flow = applied_power - heat_loss
        
        return net_heat_flow
    
    def get_derivative(self, control_output: float) -> float:
        """
        Calculate temperature derivative (rate of change).
        
        Args:
            control_output: Control signal from PID controller (W)
        
        Returns:
            dT/dt (°C/s)
        """
        net_heat_flow = self.calculate_heat_flow(control_output)
        
        # dT/dt = Q / C
        # where Q is net heat flow (W = J/s) and C is heat capacity (J/K)
        dT_dt = net_heat_flow / self.total_heat_capacity
        
        return dT_dt
    
    def update(self, control_output: float, dt: float) -> float:
        """
        Update temperature using Euler integration.
        
        Args:
            control_output: Control signal from PID controller (W)
            dt: Time step (seconds)
        
        Returns:
            New temperature (°C)
        """
        dT_dt = self.get_derivative(control_output)
        self.temperature += dT_dt * dt
        
        return self.temperature
    
    def reset(self, initial_temp: float = None):
        """
        Reset thermal model to initial conditions.
        
        Args:
            initial_temp: Temperature to reset to (°C). If None, uses ambient temp.
        """
        if initial_temp is None:
            initial_temp = self.ambient_temp
        self.temperature = initial_temp
