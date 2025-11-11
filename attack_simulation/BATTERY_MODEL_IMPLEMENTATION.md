# Battery Degradation Model Implementation

## Overview

The Battery Degradation Model simulates battery State of Health (SoH) decline based on charging parameters. This implementation is based on literature-backed degradation models that account for voltage stress, current rate stress, and State of Charge (SoC) cycling patterns.

## Implementation Status

✅ **Task 4.1**: Battery degradation model structure created
✅ **Task 4.2**: Stress factor calculations implemented
✅ **Task 4.3**: Charging cycle simulation implemented
✅ **Task 4.4**: Degradation result tracking implemented

## Components

### 1. DegradationParameters

Dataclass containing literature-based degradation model parameters:

- **Voltage Parameters**:
  - `optimal_voltage`: 3.7V (optimal cell voltage)
  - `voltage_stress_coefficient`: 0.5 (exponential stress factor)

- **Current Parameters**:
  - `optimal_c_rate`: 0.5C (optimal charging rate)
  - `current_stress_coefficient`: 0.3 (quadratic stress factor)

- **SoC Parameters**:
  - `optimal_soc_min`: 20% (optimal minimum SoC)
  - `optimal_soc_max`: 80% (optimal maximum SoC)
  - `soc_stress_coefficient`: 0.2 (linear stress factor)

- **Base Degradation**:
  - `base_degradation_per_cycle`: 0.001 (0.1% per 100 cycles)

### 2. BatteryDegradationModel

Main class for simulating battery health degradation.

#### Key Methods

**`__init__(initial_capacity_ah, params)`**
- Initializes battery with 100% SoH
- Sets initial capacity (default: 75 Ah)
- Loads degradation parameters

**`calculate_voltage_stress_factor(voltage)`**
- Formula: `stress = exp(k * |V - V_optimal|)`
- Exponential increase with voltage deviation
- Penalizes both overvoltage and undervoltage

**`calculate_current_stress_factor(current)`**
- Formula: `stress = 1 + k * (C_rate - C_optimal)²`
- Quadratic increase with C-rate deviation
- Penalizes both fast and slow charging

**`calculate_soc_cycling_factor(soc_min, soc_max)`**
- Formula: `stress = 1 + k * (low_stress + high_stress)`
- Linear increase for SoC outside 20-80% range
- Additive penalties for low and high SoC

**`calculate_temperature_stress_factor(temperature)`**
- Placeholder for future temperature modeling
- Currently returns 1.0 (no effect)

**`simulate_charging_cycle(profile, duration_hours)`**
- Simulates one complete charging cycle
- Combines all stress factors multiplicatively
- Updates SoH based on degradation calculation
- Returns DegradationResult with detailed metrics

**`update_soh(degradation_percent)`**
- Updates State of Health
- Ensures SoH never goes below 0%
- Increments cycle counter

**`get_remaining_capacity()`**
- Calculates remaining capacity based on current SoH
- Formula: `capacity_ah * (soh / 100)`

**`reset()`**
- Resets battery to initial state (100% SoH, 0 cycles)

### 3. DegradationResult

Dataclass containing detailed degradation calculation results:

- `soh_before`: SoH before cycle
- `soh_after`: SoH after cycle
- `degradation_percent`: Degradation amount
- `voltage_stress_factor`: Voltage contribution
- `current_stress_factor`: Current contribution
- `soc_stress_factor`: SoC contribution
- `combined_stress_factor`: Total stress multiplier

## Degradation Model

### Mathematical Formulation

For each charging cycle:

1. **Calculate Individual Stress Factors**:
   - Voltage: `σ_v = exp(k_v * |V - V_opt|)`
   - Current: `σ_c = 1 + k_c * (C - C_opt)²`
   - SoC: `σ_s = 1 + k_s * (max(0, 20-SoC_min, SoC_max-80))`
   - Temperature: `σ_t = 1.0` (placeholder)

2. **Combine Stress Factors**:
   - `σ_total = σ_v * σ_c * σ_s * σ_t`

3. **Calculate Degradation**:
   - `Δ_SoH = base_degradation * σ_total * duration`

4. **Update State**:
   - `SoH_new = SoH_old - Δ_SoH`
   - `cycles = cycles + 1`

### Example Stress Factors

**Voltage Stress** (V_opt = 3.7V):
- 3.2V: 1.28x
- 3.7V: 1.00x (optimal)
- 4.2V: 1.28x
- 4.4V: 1.42x

**Current Stress** (C_opt = 0.5C):
- 0.2C: 1.03x
- 0.5C: 1.00x (optimal)
- 1.0C: 1.08x
- 1.5C: 1.30x
- 2.0C: 1.68x

**SoC Stress**:
- 20-80%: 1.00x (optimal)
- 10-90%: 1.04x
- 5-95%: 1.06x
- 0-100%: 1.08x

## Usage Example

```python
from attack_simulation.models.battery_model import BatteryDegradationModel

# Initialize battery
battery = BatteryDegradationModel(initial_capacity_ah=75.0)

# Define charging profile
profile = {
    'voltage': 4.2,      # Cell voltage (V)
    'current': 1.0,      # C-rate
    'soc_min': 20.0,     # Minimum SoC (%)
    'soc_max': 80.0      # Maximum SoC (%)
}

# Simulate charging cycle
result = battery.simulate_charging_cycle(profile, duration_hours=1.0)

print(f"SoH: {result.soh_after:.4f}%")
print(f"Degradation: {result.degradation_percent:.6f}%")
print(f"Voltage Stress: {result.voltage_stress_factor:.4f}x")
print(f"Current Stress: {result.current_stress_factor:.4f}x")
print(f"Combined Stress: {result.combined_stress_factor:.4f}x")
```

## Demonstration Results

### Optimal Charging (100 cycles)
- Initial SoH: 100.00%
- Final SoH: 99.90%
- Total Degradation: 0.10%
- Degradation per cycle: 0.001%

### Aggressive Charging (100 cycles)
- Initial SoH: 100.00%
- Final SoH: 99.81%
- Total Degradation: 0.19%
- Degradation per cycle: 0.0019%
- Stress Factor: 1.86x

### Comparison (200 cycles)
- Baseline Final SoH: 99.80%
- Attack Final SoH: 99.63%
- Additional Degradation: 0.17%
- **Acceleration Factor: 1.86x**

## Testing

Comprehensive unit tests cover:
- ✅ Model initialization and state management
- ✅ Individual stress factor calculations
- ✅ Charging cycle simulation
- ✅ Multiple cycle degradation
- ✅ Duration scaling effects
- ✅ Boundary conditions (SoH = 0%)
- ✅ DegradationResult dataclass

**Test Results**: 23/23 tests passed

Run tests with:
```bash
python -m unittest tests.test_battery_model -v
```

## Integration Points

The battery model integrates with:

1. **Attack Engine**: Receives manipulated charging profiles
2. **Metrics Collector**: Provides degradation data for logging
3. **Scenario Manager**: Supports batch simulations with reset capability
4. **Visualization Engine**: Supplies data for SoH timeline plots

## Future Enhancements

1. **Temperature Modeling**: Implement temperature-dependent degradation
2. **Calendar Aging**: Add time-based degradation (storage effects)
3. **Cell Heterogeneity**: Model cell-to-cell variations
4. **Advanced Models**: Integrate electrochemical models (e.g., SEI growth)
5. **Validation**: Calibrate against real battery degradation data

## References

The degradation model is based on established battery aging research:
- Voltage stress: Exponential relationship with cell voltage
- Current stress: Quadratic relationship with C-rate
- SoC cycling: Linear penalties for extreme SoC ranges
- Base degradation: Typical Li-ion degradation rates (0.1% per 100 cycles)

## Files

- `attack_simulation/models/battery_model.py` - Main implementation
- `tests/test_battery_model.py` - Unit tests
- `attack_simulation/examples/demo_battery_model.py` - Demonstration script
