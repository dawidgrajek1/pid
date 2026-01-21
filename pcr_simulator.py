"""
PCR simulator combining thermal model and PID controller.
Simulates complete PCR protocol with simplified interface.
"""

import numpy as np
from typing import Optional

from thermal_model import ThermalModel
from pid_controller import PIDController
from config import TIME_STEP, DOWNSAMPLE_THRESHOLD


class PCRSimulator:
    """
    PCR thermocycler simulator with simplified protocol interface.
    
    Protocol structure:
    1. Initial denaturation
    2. Cycling (denaturation -> annealing -> extension) * N cycles
    3. Final extension
    4. Hold
    """
    
    def __init__(
        self,
        thermal_model: ThermalModel,
        pid_controller: PIDController,
        time_step: float = TIME_STEP,
    ):
        """
        Initialize PCR simulator.
        
        Args:
            thermal_model: ThermalModel instance
            pid_controller: PIDController instance
            time_step: Simulation time step (seconds)
        """
        self.thermal_model = thermal_model
        self.pid_controller = pid_controller
        self.time_step = time_step
    
    def _build_protocol(
        self,
        initial_temp: float,
        initial_duration: float,
        denat_temp: float,
        denat_duration: float,
        anneal_temp: float,
        anneal_duration: float,
        extension_temp: float,
        extension_duration: float,
        num_cycles: int,
        final_temp: float,
        final_duration: float,
        hold_temp: float = 10.0,
        hold_duration: float = 60.0,
    ) -> list[tuple[float, float]]:
        """
        Build complete PCR protocol from parameters.
        
        Returns:
            List of (temperature, duration) tuples
        """
        protocol = []
        
        # Initial denaturation
        protocol.append((initial_temp, initial_duration))
        
        # Cycling stages (repeated num_cycles times)
        for _ in range(num_cycles):
            protocol.append((denat_temp, denat_duration))
            protocol.append((anneal_temp, anneal_duration))
            protocol.append((extension_temp, extension_duration))
        
        # Final extension
        protocol.append((final_temp, final_duration))
        
        # Hold
        protocol.append((hold_temp, hold_duration))
        
        return protocol
    
    def _downsample(self, data: np.ndarray, max_points: int = DOWNSAMPLE_THRESHOLD) -> np.ndarray:
        """
        Downsample data for visualization if it exceeds max_points.
        
        Args:
            data: Input array
            max_points: Maximum number of points to keep
        
        Returns:
            Downsampled array
        """
        if len(data) <= max_points:
            return data
        
        # Use linear interpolation downsampling
        indices = np.linspace(0, len(data) - 1, max_points, dtype=int)
        return data[indices]
    
    def simulate(
        self,
        initial_temp: float,
        initial_duration: float,
        denat_temp: float,
        denat_duration: float,
        anneal_temp: float,
        anneal_duration: float,
        extension_temp: float,
        extension_duration: float,
        num_cycles: int,
        final_temp: float,
        final_duration: float,
        hold_temp: float = 10.0,
        hold_duration: float = 60.0,
    ) -> dict:
        """
        Run complete PCR simulation.
        
        Args:
            initial_temp: Initial denaturation temperature (°C)
            initial_duration: Initial denaturation duration (s)
            denat_temp: Cycling denaturation temperature (°C)
            denat_duration: Cycling denaturation duration (s)
            anneal_temp: Annealing temperature (°C)
            anneal_duration: Annealing duration (s)
            extension_temp: Extension temperature (°C)
            extension_duration: Extension duration (s)
            num_cycles: Number of cycles
            final_temp: Final extension temperature (°C)
            final_duration: Final extension duration (s)
            hold_temp: Hold temperature (°C)
            hold_duration: Hold duration (s)
        
        Returns:
            Dictionary containing:
                - time: Time array (s)
                - temperature: Actual temperature array (°C)
                - setpoint: Setpoint temperature array (°C)
                - control: Control output array (W)
                - error: Error signal array (°C)
                - p_term: P component array
                - i_term: I component array
                - d_term: D component array
        """
        # Build protocol
        protocol = self._build_protocol(
            initial_temp, initial_duration,
            denat_temp, denat_duration,
            anneal_temp, anneal_duration,
            extension_temp, extension_duration,
            num_cycles,
            final_temp, final_duration,
            hold_temp, hold_duration,
        )
        
        # Calculate total simulation time
        total_time = sum(duration for _, duration in protocol)
        num_steps = int(total_time / self.time_step) + 1
        
        # Initialize arrays
        time_array = np.zeros(num_steps)
        temp_array = np.zeros(num_steps)
        setpoint_array = np.zeros(num_steps)
        control_array = np.zeros(num_steps)
        error_array = np.zeros(num_steps)
        p_array = np.zeros(num_steps)
        i_array = np.zeros(num_steps)
        d_array = np.zeros(num_steps)
        
        # Reset controllers
        self.thermal_model.reset()
        self.pid_controller.reset()
        
        # Initial conditions
        current_time = 0.0
        step = 0
        
        # Simulate each stage
        for stage_temp, stage_duration in protocol:
            stage_end_time = current_time + stage_duration
            
            while current_time < stage_end_time and step < num_steps:
                # Get current state
                current_temp = self.thermal_model.temperature
                
                # Calculate control output
                control_output = self.pid_controller.update(
                    stage_temp, current_temp, self.time_step
                )
                
                # Update thermal model
                new_temp = self.thermal_model.update(control_output, self.time_step)
                
                # Store data
                time_array[step] = current_time
                temp_array[step] = current_temp
                setpoint_array[step] = stage_temp
                control_array[step] = control_output
                error_array[step] = stage_temp - current_temp
                p_term, i_term, d_term = self.pid_controller.get_components()
                p_array[step] = p_term
                i_array[step] = i_term
                d_array[step] = d_term
                
                # Advance time
                current_time += self.time_step
                step += 1
        
        # Trim arrays to actual length
        time_array = time_array[:step]
        temp_array = temp_array[:step]
        setpoint_array = setpoint_array[:step]
        control_array = control_array[:step]
        error_array = error_array[:step]
        p_array = p_array[:step]
        i_array = i_array[:step]
        d_array = d_array[:step]
        
        # Downsample for visualization
        if len(time_array) > DOWNSAMPLE_THRESHOLD:
            time_array = self._downsample(time_array)
            temp_array = self._downsample(temp_array)
            setpoint_array = self._downsample(setpoint_array)
            control_array = self._downsample(control_array)
            error_array = self._downsample(error_array)
            p_array = self._downsample(p_array)
            i_array = self._downsample(i_array)
            d_array = self._downsample(d_array)
        
        return {
            'time': time_array,
            'temperature': temp_array,
            'setpoint': setpoint_array,
            'control': control_array,
            'error': error_array,
            'p_term': p_array,
            'i_term': i_array,
            'd_term': d_array,
        }
