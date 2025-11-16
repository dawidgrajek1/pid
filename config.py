"""
Default configuration values for PCR thermocycler simulation.
"""

# Thermal System Parameters
THERMAL_HEAT_CAPACITY = 500  # J/K - Combined heat capacity of PCR block and samples
HEATING_POWER = 250  # W - Maximum heating power
COOLING_POWER = 150  # W - Maximum cooling power (negative in simulation)
HEAT_LOSS_COEF = 1.5  # W/K - Heat loss coefficient to ambient
AMBIENT_TEMP = 22  # °C - Ambient temperature

# Sample Properties
SAMPLE_VOLUME = 1.8e-6  # m³ - 1.8 mL total sample volume
SAMPLE_DENSITY = 1000  # kg/m³ - Water-based PCR mix
SAMPLE_SPECIFIC_HEAT = 4100  # J/(kg·K) - Specific heat capacity of aqueous solution

# PID Controller Parameters (Standard Form)
PID_KP = 80  # Proportional gain
PID_TI = 1.0  # seconds - Integration time
PID_TD = 20  # seconds - Derivative time

# Standard PCR Protocol
# Stage format: (temperature °C, duration seconds)
PCR_INITIAL_DENATURATION = (95, 180)  # Initial denaturation: 95°C for 3 minutes
PCR_CYCLES = 35  # Number of amplification cycles
PCR_DENATURATION = (95, 30)  # Cycling denaturation: 95°C for 30 seconds
PCR_ANNEALING = (58, 30)  # Annealing: 58°C for 30 seconds
PCR_EXTENSION = (72, 60)  # Extension: 72°C for 60 seconds
PCR_FINAL_EXTENSION = (72, 300)  # Final extension: 72°C for 5 minutes
PCR_HOLD = (10, 60)  # Hold at 10°C for 1 minute (for simulation)

# Simulation Parameters
TIME_STEP = 0.1  # seconds - Simulation time step
DOWNSAMPLE_THRESHOLD = 5000  # Maximum points to display on graph

# Input Validation Ranges
TEMP_MIN = 0  # °C
TEMP_MAX = 100  # °C
DURATION_MIN = 1  # seconds
DURATION_MAX = 3600  # seconds (1 hour)
CYCLES_MIN = 1
CYCLES_MAX = 100
HEAT_CAPACITY_MIN = 100  # J/K
HEAT_CAPACITY_MAX = 2000  # J/K
POWER_MIN = 10  # W
POWER_MAX = 1000  # W
HEAT_LOSS_MIN = 0.1  # W/K
HEAT_LOSS_MAX = 10  # W/K
VOLUME_MIN = 0.1e-6  # m³ (0.1 mL)
VOLUME_MAX = 50e-6  # m³ (50 mL)
PID_KP_MIN = 0
PID_KP_MAX = 1000
PID_TI_MIN = 0.01  # seconds
PID_TI_MAX = 100  # seconds
PID_TD_MIN = 0
PID_TD_MAX = 500  # seconds
