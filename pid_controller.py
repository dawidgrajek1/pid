"""
PID controller implementation using standard form (Kp, Ti, Td).
Includes anti-windup protection and output clamping.
"""


class PIDController:
    """
    Standard-form PID controller.
    
    Control equation:
    u(t) = Kp * [e(t) + (1/Ti)*∫e(t)dt + Td*de(t)/dt]
    
    Where:
    - Kp: Proportional gain
    - Ti: Integration time (seconds)
    - Td: Derivative time (seconds)
    - e(t): Error signal (setpoint - measurement)
    """
    
    def __init__(
        self,
        kp: float = 80.0,
        ti: float = 1.0,
        td: float = 20.0,
        output_min: float = -150.0,
        output_max: float = 250.0,
    ):
        """
        Initialize PID controller.
        
        Args:
            kp: Proportional gain
            ti: Integration time (seconds)
            td: Derivative time (seconds)
            output_min: Minimum control output (typically -cooling_power)
            output_max: Maximum control output (typically +heating_power)
        """
        self.kp = kp
        self.ti = ti
        self.td = td
        self.output_min = output_min
        self.output_max = output_max
        
        # Internal state
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_derivative = 0.0
        
        # Component tracking (for visualization)
        self.p_term = 0.0
        self.i_term = 0.0
        self.d_term = 0.0
    
    def update(self, setpoint: float, measurement: float, dt: float) -> float:
        """
        Update PID controller and calculate control output.
        
        Args:
            setpoint: Desired value (°C)
            measurement: Current value (°C)
            dt: Time step (seconds)
        
        Returns:
            Control output (W)
        """
        # Calculate error
        error = setpoint - measurement
        
        # Proportional term
        self.p_term = error
        
        # Integral term with anti-windup
        # Only integrate if we're not saturated or if integration would reduce saturation
        self.integral += error * dt
        
        # Calculate I term contribution
        if self.ti > 0:
            self.i_term = self.integral / self.ti
        else:
            self.i_term = 0.0
        
        # Derivative term with filtering
        # Use filtered derivative to reduce noise sensitivity
        if dt > 0:
            derivative = (error - self.prev_error) / dt
            # Simple low-pass filter (alpha = 0.5)
            alpha = 0.5
            filtered_derivative = alpha * derivative + (1 - alpha) * self.prev_derivative
            self.d_term = self.td * filtered_derivative
            self.prev_derivative = filtered_derivative
        else:
            self.d_term = 0.0
        
        # Calculate total output
        output = self.kp * (self.p_term + self.i_term + self.d_term)
        
        # Apply output limits
        output_clamped = max(self.output_min, min(output, self.output_max))
        
        # Anti-windup: Back-calculate integral if output is saturated
        if output != output_clamped and self.ti > 0:
            # Clamp integral to prevent further windup
            # Calculate what integral should be to keep output at limit
            max_i_term = (output_clamped / self.kp) - self.p_term - self.d_term
            self.integral = max_i_term * self.ti
            self.i_term = max_i_term
        
        # Store error for next iteration
        self.prev_error = error
        
        return output_clamped
    
    def reset(self):
        """Reset controller internal state."""
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_derivative = 0.0
        self.p_term = 0.0
        self.i_term = 0.0
        self.d_term = 0.0
    
    def get_components(self) -> tuple[float, float, float]:
        """
        Get individual PID component values (for visualization).
        
        Returns:
            Tuple of (P contribution, I contribution, D contribution) in units of error/time
        """
        return (self.p_term, self.i_term, self.d_term)
    
    def set_output_limits(self, output_min: float, output_max: float):
        """
        Update output limits.
        
        Args:
            output_min: Minimum control output
            output_max: Maximum control output
        """
        self.output_min = output_min
        self.output_max = output_max
