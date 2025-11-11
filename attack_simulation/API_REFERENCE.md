# API Reference

Complete API documentation for the Charging Profile Poisoning Attack Simulation Framework.

## Overview

This document provides detailed API documentation for all public classes and methods in the attack simulation framework. All code examples use Python 3.8+ syntax.

## Quick Reference

| Component | Module | Purpose |
|-----------|--------|---------|
| AttackEngine | `attack_simulation.core.attack_engine` | Manipulate charging profiles |
| BatteryDegradationModel | `attack_simulation.models.battery_model` | Simulate battery degradation |
| MetricsCollector | `attack_simulation.metrics.metrics_collector` | Collect and export metrics |
| VisualizationEngine | `attack_simulation.visualization.visualization_engine` | Generate plots |
| AnomalyDetector | `attack_simulation.detection.anomaly_detector` | Detect anomalies |
| ComparisonAnalyzer | `attack_simulation.metrics.comparison_analyzer` | Compare simulations |
| ScenarioManager | `attack_simulation.core.scenario_manager` | Batch execution |
| OCPPMITMProxy | `attack_simulation.core.mitm_proxy` | MITM proxy |

## Installation

```python
# Import core components
from attack_simulation.core import AttackEngine, ScenarioManager
from attack_simulation.models import BatteryDegradationModel
from attack_simulation.metrics import MetricsCollector, ComparisonAnalyzer
from attack_simulation.visualization import VisualizationEngine
from attack_simulation.detection import AnomalyDetector
```

---

## Core Components

### AttackEngine

**Module:** `attack_simulation.core.attack_engine`

Implements intelligent manipulation of OCPP charging profiles with configurable strategies.

#### Constructor

```python
AttackEngine(config: AttackConfig, metrics_collector: MetricsCollector = None)
```

**Parameters:**
- `config` (AttackConfig): Attack configuration object
- `metrics_collector` (MetricsCollector, optional): Metrics collector for logging

**Example:**
```python
from attack_simulation.core import AttackEngine, AttackConfig

config = AttackConfig.from_yaml("attack_simulation/config/attack_config.yaml")
engine = AttackEngine(config, metrics_collector)
```

#### Key Methods

**`manipulate_charging_profile(profile: Dict) -> Dict`**

Apply attack manipulations to charging profile.

```python
modified_profile = engine.manipulate_charging_profile(original_profile)
```

**`should_manipulate(message: Dict) -> bool`**

Determine if message should be manipulated.

```python
if engine.should_manipulate(ocpp_message):
    # Apply manipulation
```

**`apply_voltage_manipulation(profile: Dict) -> None`**

Modify voltage limits (in-place modification).

**`apply_current_manipulation(profile: Dict) -> None`**

Modify current limits (in-place modification).

**`apply_curve_manipulation(profile: Dict) -> None`**

Modify charging curve parameters (in-place modification).

**`get_manipulation_summary() -> Dict`**

Get summary of manipulations performed.

```python
summary = engine.get_manipulation_summary()
print(f"Strategy: {summary['strategy']}")
```

### BatteryDegradationModel

**Module:** `attack_simulation.models.battery_model`

Simulates battery State of Health (SoH) decline based on charging parameters.

#### Constructor

```python
BatteryDegradationModel(
    initial_capacity_ah: float = 75.0,
    params: DegradationParameters = None
)
```

**Parameters:**
- `initial_capacity_ah` (float): Initial battery capacity in Ah (default: 75.0)
- `params` (DegradationParameters, optional): Degradation parameters

**Example:**
```python
from attack_simulation.models import BatteryDegradationModel, DegradationParameters

# Use default parameters
battery = BatteryDegradationModel(initial_capacity_ah=75.0)

# Use custom parameters
params = DegradationParameters(
    optimal_voltage=3.7,
    voltage_stress_coefficient=0.5
)
battery = BatteryDegradationModel(initial_capacity_ah=75.0, params=params)
```

#### Key Methods

**`simulate_charging_cycle(profile: Dict, duration_hours: float) -> DegradationResult`**

Simulate one charging cycle and calculate degradation.

```python
profile = {
    'voltage': 4.2,  # V
    'current': 0.8,  # C-rate
    'soc_min': 20.0,  # %
    'soc_max': 80.0   # %
}
result = battery.simulate_charging_cycle(profile, duration_hours=2.0)
print(f"SoH: {result.soh_after:.2f}%")
print(f"Degradation: {result.degradation_percent:.4f}%")
```

**`calculate_voltage_stress_factor(voltage: float) -> float`**

Calculate voltage stress factor using exponential model.

```python
stress = battery.calculate_voltage_stress_factor(4.3)  # High voltage
```

**`calculate_current_stress_factor(current: float) -> float`**

Calculate current stress factor using quadratic model.

```python
stress = battery.calculate_current_stress_factor(1.0)  # 1C charging
```

**`calculate_soc_cycling_factor(soc_min: float, soc_max: float) -> float`**

Calculate SoC cycling stress factor.

```python
stress = battery.calculate_soc_cycling_factor(10.0, 95.0)  # Wide range
```

**`get_remaining_capacity() -> float`**

Get remaining capacity based on current SoH.

```python
capacity_ah = battery.get_remaining_capacity()
```

**`reset() -> None`**

Reset battery model to initial state.

```python
battery.reset()  # SoH back to 100%
```

#### Properties

- `soh` (float): Current State of Health (%)
- `cycle_count` (int): Number of cycles completed
- `capacity_ah` (float): Initial capacity in Ah
### MetricsCollector

**Module:** `attack_simulation.metrics.metrics_collector`

Collects and persists simulation metrics with CSV and JSON export.

#### Constructor

```python
MetricsCollector(output_dir: str, session_id: str)
```

**Parameters:**
- `output_dir` (str): Base output directory
- `session_id` (str): Unique session identifier

**Example:**
```python
from attack_simulation.metrics import MetricsCollector
from datetime import datetime

session_id = f"attack_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
metrics = MetricsCollector(output_dir="./output/attack", session_id=session_id)
```

#### Key Methods

**`log_manipulation(timestamp, original, modified, parameter_name, original_value, modified_value, deviation_percent)`**

Record charging profile manipulation event.

```python
from datetime import datetime

metrics.log_manipulation(
    timestamp=datetime.now(),
    original=original_profile,
    modified=modified_profile,
    parameter_name="voltage_limit",
    original_value=4.2,
    modified_value=4.8,
    deviation_percent=14.3
)
```

**`log_charging_cycle(cycle_num, profile, duration, energy_kwh, soh_before, soh_after)`**

Record completed charging cycle metrics.

```python
metrics.log_charging_cycle(
    cycle_num=1,
    profile={'voltage': 4.2, 'current': 0.5},
    duration=2.0,
    energy_kwh=50.0,
    soh_before=100.0,
    soh_after=99.99
)
```

**`log_degradation_event(degradation_result, cycle_num)`**

Record detailed degradation calculation.

```python
result = battery.simulate_charging_cycle(profile, 2.0)
metrics.log_degradation_event(result, cycle_num=1)
```

**`export_to_csv() -> None`**

Export all metrics to CSV files.

```python
metrics.export_to_csv()
# Creates: manipulations.csv, charging_cycles.csv, degradation_timeline.csv
```

**`generate_summary_report() -> SimulationSummary`**

Generate statistical summary of simulation.

```python
summary = metrics.generate_summary_report()
print(f"Total cycles: {summary.total_cycles}")
print(f"Final SoH: {summary.final_soh:.2f}%")
print(f"Degradation rate: {summary.degradation_rate_per_cycle:.4f}%/cycle")
```

**`save_config(config: Dict) -> None`**

Save simulation configuration to file.

```python
metrics.save_config(config_dict)
```

#### Output Files

- `manipulations.csv`: Manipulation events
- `charging_cycles.csv`: Charging cycle data
- `degradation_timeline.csv`: SoH over time
- `summary.json`: Summary statistics
- `config.json`: Simulation configuration
- `errors.csv`: Error log
- `detection_events.csv`: Detection events
### ComparisonAnalyzer

**Module:** `attack_simulation.metrics.comparison_analyzer`

Compare baseline and attack simulations to quantify attack impact.

#### Constructor

```python
ComparisonAnalyzer(baseline_session_dir: str, attack_session_dir: str)
```

**Example:**
```python
from attack_simulation.metrics import ComparisonAnalyzer

analyzer = ComparisonAnalyzer(
    baseline_session_dir="./output/baseline/session_baseline_20241110_120000",
    attack_session_dir="./output/attack/session_attack_20241110_130000"
)
```

#### Key Methods

**`load_simulation_data() -> None`**

Load data from both simulation sessions.

```python
analyzer.load_simulation_data()
```

**`generate_comparison_metrics() -> ComparisonMetrics`**

Calculate comparison metrics.

```python
metrics = analyzer.generate_comparison_metrics()
print(f"Acceleration factor: {metrics.degradation_acceleration_factor:.2f}x")
print(f"Additional degradation: {metrics.additional_degradation_percent:.2f}%")
```

**`generate_comparison_report(metrics, output_path) -> str`**

Generate comprehensive comparison report.

```python
report_path = analyzer.generate_comparison_report(metrics, "./output/comparison_report.txt")
```

### VisualizationEngine

**Module:** `attack_simulation.visualization.visualization_engine`

Generate publication-quality plots and reports.

#### Constructor

```python
VisualizationEngine(metrics_collector: MetricsCollector)
```

#### Key Methods

**`plot_soh_timeline(output_path: str) -> None`**

Generate SoH degradation timeline plot.

```python
viz = VisualizationEngine(metrics)
viz.plot_soh_timeline("./output/plots/soh_timeline.png")
```

**`plot_baseline_comparison(baseline_data, attack_data, output_path) -> None`**

Generate baseline vs. attack comparison plot.

```python
viz.plot_baseline_comparison(baseline_df, attack_df, "./output/plots/comparison.png")
```

**`plot_parameter_deviations(output_path: str) -> None`**

Generate parameter deviation histograms.

```python
viz.plot_parameter_deviations("./output/plots/deviations.png")
```

### AnomalyDetector

**Module:** `attack_simulation.detection.anomaly_detector`

Statistical anomaly detection for attack identification.

#### Constructor

```python
AnomalyDetector(config_path: str)
```

#### Key Methods

**`detect_anomaly(charging_profile: Dict) -> bool`**

Detect if charging profile is anomalous.

```python
detector = AnomalyDetector("attack_simulation/config/detection_config.yaml")
is_anomaly = detector.detect_anomaly(profile)
```

**`calculate_confidence_score(profile: Dict) -> float`**

Calculate confidence score for detection.

```python
confidence = detector.calculate_confidence_score(profile)
```

### ScenarioManager

**Module:** `attack_simulation.core.scenario_manager`

Orchestrate multi-scenario batch execution.

#### Constructor

```python
ScenarioManager(batch_config_path: str)
```

#### Key Methods

**`run_batch() -> List[SimulationSummary]`**

Execute all scenarios in batch configuration.

```python
manager = ScenarioManager("attack_simulation/config/batch_config.yaml")
results = await manager.run_batch()
```

**`generate_comparison_report(results: List) -> None`**

Generate cross-scenario comparison report.

```python
manager.generate_comparison_report(results)
```

## Data Structures

### AttackConfig

Configuration for attack engine.

```python
@dataclass
class AttackConfig:
    enabled: bool = True
    strategy: AttackStrategy = AttackStrategy.AGGRESSIVE
    voltage_enabled: bool = True
    voltage_deviation_percent: float = 15.0
    current_enabled: bool = True
    current_deviation_percent: float = 25.0
    curve_enabled: bool = True
```

### DegradationResult

Result of degradation calculation.

```python
@dataclass
class DegradationResult:
    soh_before: float
    soh_after: float
    degradation_percent: float
    voltage_stress_factor: float
    current_stress_factor: float
    soc_stress_factor: float
    combined_stress_factor: float
```

### SimulationSummary

Summary statistics for simulation run.

```python
@dataclass
class SimulationSummary:
    session_id: str
    total_cycles: int
    total_duration_hours: float
    initial_soh: float
    final_soh: float
    total_degradation: float
    degradation_rate_per_cycle: float
```

## Configuration Files

### attack_config.yaml

```yaml
attack_config:
  enabled: true
  strategy: "aggressive"
  manipulations:
    voltage:
      enabled: true
      deviation_percent: 15
    current:
      enabled: true
      deviation_percent: 25
```

### batch_config.yaml

```yaml
batch_config:
  name: "Comparative Study"
  scenarios:
    - name: "baseline"
      attack_enabled: false
    - name: "aggressive"
      attack_enabled: true
      strategy: "aggressive"
```

## Complete Example

```python
from attack_simulation.core import AttackEngine, AttackConfig
from attack_simulation.models import BatteryDegradationModel
from attack_simulation.metrics import MetricsCollector
from attack_simulation.visualization import VisualizationEngine
from datetime import datetime

# Initialize components
config = AttackConfig.from_yaml("attack_simulation/config/attack_config.yaml")
engine = AttackEngine(config)
battery = BatteryDegradationModel(initial_capacity_ah=75.0)
metrics = MetricsCollector("./output/attack", f"attack_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

# Simulate charging cycles
for cycle in range(1000):
    # Create charging profile
    profile = {
        'voltage': 4.2,
        'current': 0.5,
        'soc_min': 20.0,
        'soc_max': 80.0
    }
    
    # Apply attack manipulation
    if engine.should_manipulate({'type': 'SetChargingProfile'}):
        profile = engine.manipulate_charging_profile(profile)
    
    # Simulate battery degradation
    result = battery.simulate_charging_cycle(profile, duration_hours=2.0)
    
    # Log metrics
    metrics.log_charging_cycle(
        cycle_num=cycle,
        profile=profile,
        duration=2.0,
        energy_kwh=50.0,
        soh_before=result.soh_before,
        soh_after=result.soh_after
    )
    metrics.log_degradation_event(result, cycle_num=cycle)

# Export results
metrics.export_to_csv()
summary = metrics.generate_summary_report()

# Generate visualizations
viz = VisualizationEngine(metrics)
viz.plot_soh_timeline("./output/plots/soh_timeline.png")

print(f"Simulation complete: {summary.total_cycles} cycles")
print(f"Final SoH: {summary.final_soh:.2f}%")
```

## Error Handling

All components raise appropriate exceptions:

```python
from attack_simulation.core import AttackSimulationError

try:
    engine.manipulate_charging_profile(profile)
except AttackSimulationError as e:
    logger.error(f"Attack failed: {e}")
```

## Logging

Configure logging for detailed output:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Testing

Run unit tests:

```bash
python -m pytest tests/test_attack_engine.py
python -m pytest tests/test_battery_model.py
python -m pytest tests/test_metrics_collector.py
```

## Support

For API questions:
- Check docstrings: `help(AttackEngine)`
- Review examples: `attack_simulation/examples/`
- Read implementation docs: `attack_simulation/*_IMPLEMENTATION.md`
