"""
Battery Degradation Model for simulating battery health decline
"""

from dataclasses import dataclass
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class DegradationParameters:
    """Literature-based degradation model parameters"""
    
    # Voltage stress parameters
    optimal_voltage: float = 3.7  # Optimal cell voltage (V)
    voltage_stress_coefficient: float = 0.5
    
    # Current stress parameters
    optimal_c_rate: float = 0.5  # Optimal charging rate (C)
    current_stress_coefficient: float = 0.3
    
    # SoC cycling parameters
    optimal_soc_min: float = 20.0  # Optimal minimum SoC (%)
    optimal_soc_max: float = 80.0  # Optimal maximum SoC (%)
    soc_stress_coefficient: float = 0.2
    
    # Base degradation per cycle
    base_degradation_per_cycle: float = 0.001  # 0.1% per 100 cycles
    
    # Temperature effects (future enhancement)
    temperature_coefficient: float = 0.1


@dataclass
class DegradationResult:
    """Result of degradation calculation"""
    soh_before: float
    soh_after: float
    degradation_percent: float
    voltage_stress_factor: float
    current_stress_factor: float
    soc_stress_factor: float
    combined_stress_factor: float


class BatteryDegradationModel:
    """
    Simulates battery State of Health (SoH) degradation
    Based on literature: voltage stress, current rate, SoC cycling
    """
    
    def __init__(self, initial_capacity_ah: float = 75.0, 
                 params: DegradationParameters = None):
        """
        Initialize battery model with capacity
        
        Args:
            initial_capacity_ah: Initial battery capacity in Ah
            params: Degradation parameters (uses defaults if None)
        """
        self.soh: float = 100.0  # State of Health percentage
        self.cycle_count: int = 0
        self.capacity_ah: float = initial_capacity_ah
        self.params = params or DegradationParameters()
        logger.info(f"BatteryDegradationModel initialized: {initial_capacity_ah} Ah, SoH: {self.soh}%")
    
    def simulate_charging_cycle(self, profile: Dict[str, Any], 
                                duration_hours: float) -> DegradationResult:
        """
        Simulate one charging cycle and calculate degradation
        
        Args:
            profile: Charging profile parameters (dict with voltage, current, soc_min, soc_max)
            duration_hours: Charging duration
            
        Returns:
            DegradationResult with SoH change and contributing factors
        """
        logger.debug(f"Simulating charging cycle {self.cycle_count + 1}")
        
        soh_before = self.soh
        
        # Extract charging parameters from profile
        # Profile can contain: voltage (V), current (C-rate), soc_min (%), soc_max (%)
        voltage = profile.get('voltage', self.params.optimal_voltage)
        current = profile.get('current', self.params.optimal_c_rate)
        soc_min = profile.get('soc_min', self.params.optimal_soc_min)
        soc_max = profile.get('soc_max', self.params.optimal_soc_max)
        temperature = profile.get('temperature', 25.0)
        
        # Calculate individual stress factors
        voltage_stress = self.calculate_voltage_stress_factor(voltage)
        current_stress = self.calculate_current_stress_factor(current)
        soc_stress = self.calculate_soc_cycling_factor(soc_min, soc_max)
        temperature_stress = self.calculate_temperature_stress_factor(temperature)
        
        # Combine stress factors (multiplicative model)
        combined_stress = voltage_stress * current_stress * soc_stress * temperature_stress
        
        # Calculate degradation for this cycle
        # Base degradation scaled by combined stress and duration
        degradation = self.params.base_degradation_per_cycle * combined_stress * duration_hours
        
        logger.info(
            f"Cycle {self.cycle_count + 1}: V={voltage:.2f}V, I={current:.2f}C, "
            f"SoC=[{soc_min:.1f}%, {soc_max:.1f}%], duration={duration_hours:.2f}h, "
            f"combined_stress={combined_stress:.4f}, degradation={degradation:.4f}%"
        )
        
        # Update battery state
        self.update_soh(degradation)
        
        return DegradationResult(
            soh_before=soh_before,
            soh_after=self.soh,
            degradation_percent=degradation,
            voltage_stress_factor=voltage_stress,
            current_stress_factor=current_stress,
            soc_stress_factor=soc_stress,
            combined_stress_factor=combined_stress
        )
    
    def calculate_voltage_stress_factor(self, voltage: float) -> float:
        """
        Calculate degradation factor from voltage stress
        Based on: Higher voltage = exponential degradation increase
        
        Formula: stress_factor = exp(k * (V - V_optimal))
        
        Args:
            voltage: Cell voltage in V
            
        Returns:
            Voltage stress factor
        """
        import math
        
        # Calculate voltage deviation from optimal
        voltage_deviation = voltage - self.params.optimal_voltage
        
        # Apply exponential stress model
        # Positive deviation (overvoltage) increases stress exponentially
        # Negative deviation (undervoltage) also increases stress but less severely
        stress_factor = math.exp(
            self.params.voltage_stress_coefficient * abs(voltage_deviation)
        )
        
        logger.debug(
            f"Voltage stress: V={voltage:.2f}V, V_opt={self.params.optimal_voltage:.2f}V, "
            f"deviation={voltage_deviation:.2f}V, stress_factor={stress_factor:.4f}"
        )
        
        return stress_factor
    
    def calculate_current_stress_factor(self, current: float) -> float:
        """
        Calculate degradation factor from current rate
        Based on: Higher C-rate = increased degradation
        
        Formula: stress_factor = 1 + k * (C_rate - C_optimal)^2
        
        Args:
            current: Charging current (C-rate)
            
        Returns:
            Current stress factor
        """
        # Calculate C-rate deviation from optimal
        c_rate_deviation = current - self.params.optimal_c_rate
        
        # Apply quadratic stress model
        # Deviation from optimal C-rate increases stress quadratically
        # This penalizes both too-fast and too-slow charging
        stress_factor = 1.0 + self.params.current_stress_coefficient * (c_rate_deviation ** 2)
        
        logger.debug(
            f"Current stress: C_rate={current:.2f}C, C_opt={self.params.optimal_c_rate:.2f}C, "
            f"deviation={c_rate_deviation:.2f}C, stress_factor={stress_factor:.4f}"
        )
        
        return stress_factor
    
    def calculate_soc_cycling_factor(self, soc_min: float, 
                                     soc_max: float) -> float:
        """
        Calculate degradation factor from SoC cycling range
        Based on: Cycling outside 20-80% increases degradation
        
        Args:
            soc_min: Minimum SoC in cycle (%)
            soc_max: Maximum SoC in cycle (%)
            
        Returns:
            SoC cycling stress factor
        """
        # Calculate stress from operating outside optimal SoC range
        # Penalize both low SoC (< 20%) and high SoC (> 80%)
        
        low_soc_stress = 0.0
        if soc_min < self.params.optimal_soc_min:
            low_soc_stress = self.params.optimal_soc_min - soc_min
        
        high_soc_stress = 0.0
        if soc_max > self.params.optimal_soc_max:
            high_soc_stress = soc_max - self.params.optimal_soc_max
        
        # Combined SoC stress (additive)
        total_soc_stress = low_soc_stress + high_soc_stress
        
        # Apply stress coefficient
        stress_factor = 1.0 + self.params.soc_stress_coefficient * (total_soc_stress / 100.0)
        
        logger.debug(
            f"SoC stress: range=[{soc_min:.1f}%, {soc_max:.1f}%], "
            f"optimal=[{self.params.optimal_soc_min:.1f}%, {self.params.optimal_soc_max:.1f}%], "
            f"low_stress={low_soc_stress:.1f}, high_stress={high_soc_stress:.1f}, "
            f"stress_factor={stress_factor:.4f}"
        )
        
        return stress_factor
    
    def calculate_temperature_stress_factor(self, temperature: float = 25.0) -> float:
        """
        Calculate degradation factor from temperature
        Placeholder for future enhancement
        
        Args:
            temperature: Battery temperature in Celsius (default: 25°C)
            
        Returns:
            Temperature stress factor (currently always 1.0)
        """
        # Placeholder implementation for future temperature modeling
        # Currently returns neutral factor (no temperature effect)
        logger.debug(f"Temperature stress: T={temperature:.1f}°C (placeholder, factor=1.0)")
        return 1.0
    
    def update_soh(self, degradation_percent: float) -> None:
        """
        Update State of Health after degradation calculation
        
        Args:
            degradation_percent: Degradation amount in percent
        """
        self.soh = max(0.0, self.soh - degradation_percent)
        self.cycle_count += 1
        logger.debug(f"SoH updated: {self.soh:.2f}% (cycle {self.cycle_count})")
    
    def get_remaining_capacity(self) -> float:
        """
        Calculate remaining capacity based on current SoH
        
        Returns:
            Remaining capacity in Ah
        """
        return self.capacity_ah * (self.soh / 100.0)
    
    def reset(self) -> None:
        """
        Reset battery model to initial state
        """
        self.soh = 100.0
        self.cycle_count = 0
        logger.info("Battery model reset to initial state")
