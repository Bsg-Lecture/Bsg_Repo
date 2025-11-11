# Attack Simulator Usage Guide

Complete guide for using the Charging Profile Poisoning Attack Simulator.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Configuration](#configuration)
5. [Attack Scenarios](#attack-scenarios)
6. [Batch Execution](#batch-execution)
7. [Analysis and Visualization](#analysis-and-visualization)
8. [Advanced Usage](#advanced-usage)
9. [Troubleshooting](#troubleshooting)

## Quick Start

### 5-Minute Demo

Run a complete attack simulation in 5 steps:

```bash
# 1. Navigate to EmuOCPP directory
cd EmuOCPP

# 2. Start EmuOCPP server (Terminal 1)
python charging/server.py

# 3. Run baseline simulation (Terminal 2)
python run_baseline_simulation.py --cycles 100

# 4. Run attack simulation (Terminal 3)
python attack_simulator.py --config attack_simulation/config/attack_config.yaml --cycles 100

# 5. Compare results
python run_comparison_analysis.py
```

Results will be in `./output/` with plots and metrics.

## Installation

### Prerequisites

- Python 3.8 or higher
- EmuOCPP installed and configured
- Required Python packages (see requirements.txt)

### Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- websockets
- PyYAML
- pandas
- matplotlib
- numpy
- asyncio

### Verify Installation

```bash
python attack_simulator.py --version
python test_integration.py
```

## Basic Usage

### Command-Line Interface

```bash
python attack_simulator.py [OPTIONS]
```

#### Essential Options

- `--config FILE` - Path to attack configuration file
- `--batch FILE` - Path to batch configuration file
- `--cycles N` - Number of charging cycles to simulate
- `--output-dir DIR` - Output directory for results
- `--log-level LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

#### Examples

```bash
# Run single attack scenario
python attack_simulator.py --config attack_simulation/config/attack_config.yaml

# Run with custom cycle count
python attack_simulator.py --config attack_simulation/config/attack_config.yaml --cycles 2000

# Run with debug logging
python attack_simulator.py --config attack_simulation/config/attack_config.yaml --log-level DEBUG

# Run batch scenarios
python attack_simulator.py --batch attack_simulation/config/batch_config.yaml

# Dry run (validate config without running)
python attack_simulator.py --config attack_simulation/config/attack_config.yaml --dry-run
```

### Help and Documentation

```bash
# Show help message
python attack_simulator.py --help

# Show version
python attack_simulator.py --version
```

## Configuration

### Configuration Files

Three main configuration files:

1. **attack_config.yaml** - Single attack scenario
2. **baseline_config.yaml** - Baseline (no attack) scenario
3. **batch_config.yaml** - Multiple scenarios for comparison

Located in: `attack_simulation/config/`

### Attack Configuration Structure

```yaml
attack_config:
  enabled: true              # Enable/disable attack
  strategy: "aggressive"     # Attack strategy
  
  manipulations:
    voltage:
      enabled: true
      deviation_percent: 15  # Increase by 15%
      
    current:
      enabled: true
      deviation_percent: 25  # Increase by 25%
      
    charging_curve:
      enabled: true
      modification_type: "flatten"

battery_model:
  initial_capacity_ah: 75.0
  degradation_params:
    optimal_voltage: 3.7
    voltage_stress_coefficient: 0.5
    # ... more parameters

proxy:
  csms_host: "127.0.0.1"
  csms_port: 9000
  listen_port: 9001

simulation:
  cycles: 1000
  cycle_duration_hours: 2.0
  mode: "attack"

metrics:
  output_dir: "./output/attack"
  export_csv: true
  export_json: true
  generate_plots: true
```

### Customizing Attack Parameters

#### Voltage Manipulation

```yaml
manipulations:
  voltage:
    enabled: true
    deviation_percent: 20      # Increase voltage by 20%
    target_range: [4.2, 4.4]   # Target voltage range (V)
```

#### Current Manipulation

```yaml
manipulations:
  current:
    enabled: true
    deviation_percent: 30      # Increase current by 30%
    target_range: [60, 90]     # Target current range (A)
```

#### Charging Curve Modification

```yaml
manipulations:
  charging_curve:
    enabled: true
    modification_type: "flatten"  # Options: flatten, steepen, invert
```

### Attack Strategies

Four built-in strategies:

#### 1. Aggressive Strategy

Maximum parameter deviations for rapid degradation:

```yaml
attack_config:
  strategy: "aggressive"
  manipulations:
    voltage:
      deviation_percent: 20
    current:
      deviation_percent: 30
```

**Use case**: Demonstrate maximum attack impact

#### 2. Subtle Strategy

Minimal deviations to evade detection:

```yaml
attack_config:
  strategy: "subtle"
  manipulations:
    voltage:
      deviation_percent: 5
    current:
      deviation_percent: 10
```

**Use case**: Test detection mechanisms

#### 3. Random Strategy

Randomized manipulations within bounds:

```yaml
attack_config:
  strategy: "random"
  randomization:
    enabled: true
    seed: 42
    deviation_range: [5, 25]
```

**Use case**: Simulate unpredictable attacks

#### 4. Targeted Strategy

Target specific parameters:

```yaml
attack_config:
  strategy: "targeted"
  manipulations:
    voltage:
      enabled: true
      deviation_percent: 15
    current:
      enabled: false
    charging_curve:
      enabled: false
```

**Use case**: Isolate specific attack vectors

## Attack Scenarios

### Scenario 1: Baseline (No Attack)

Establish normal degradation baseline:

```bash
python attack_simulator.py --config attack_simulation/config/baseline_config.yaml --cycles 1000
```

**Expected result**: Normal battery degradation (~10% SoH loss over 1000 cycles)

### Scenario 2: Voltage Overstress Attack

Attack focusing on voltage manipulation:

```yaml
# Create custom config: voltage_attack.yaml
attack_config:
  enabled: true
  strategy: "aggressive"
  manipulations:
    voltage:
      enabled: true
      deviation_percent: 20
    current:
      enabled: false
    charging_curve:
      enabled: false
```

```bash
python attack_simulator.py --config voltage_attack.yaml --cycles 1000
```

**Expected result**: Accelerated degradation due to voltage stress

### Scenario 3: Current Overstress Attack

Attack focusing on current manipulation:

```yaml
# Create custom config: current_attack.yaml
attack_config:
  enabled: true
  strategy: "aggressive"
  manipulations:
    voltage:
      enabled: false
    current:
      enabled: true
      deviation_percent: 30
    charging_curve:
      enabled: false
```

```bash
python attack_simulator.py --config current_attack.yaml --cycles 1000
```

**Expected result**: Accelerated degradation due to current stress

### Scenario 4: Combined Attack

Multi-vector attack:

```bash
python attack_simulator.py --config attack_simulation/config/attack_config.yaml --cycles 1000
```

**Expected result**: Maximum degradation acceleration

### Scenario 5: Subtle Evasion Attack

Minimal manipulation to avoid detection:

```yaml
# Create custom config: subtle_attack.yaml
attack_config:
  enabled: true
  strategy: "subtle"
  manipulations:
    voltage:
      enabled: true
      deviation_percent: 5
    current:
      enabled: true
      deviation_percent: 8
```

```bash
python attack_simulator.py --config subtle_attack.yaml --cycles 1000
```

**Expected result**: Moderate degradation, harder to detect

## Batch Execution

### Running Multiple Scenarios

Use batch configuration for comparative analysis:

```bash
python attack_simulator.py --batch attack_simulation/config/batch_config.yaml
```

### Batch Configuration Example

```yaml
batch_config:
  name: "Comparative Study"
  output_dir: "./results/batch_001"
  
  scenarios:
    - name: "baseline"
      attack_enabled: false
      cycles: 1000
      
    - name: "aggressive_voltage"
      attack_enabled: true
      strategy: "aggressive"
      cycles: 1000
      manipulations:
        voltage:
          enabled: true
          deviation_percent: 20
        current:
          enabled: false
          
    - name: "aggressive_current"
      attack_enabled: true
      strategy: "aggressive"
      cycles: 1000
      manipulations:
        voltage:
          enabled: false
        current:
          enabled: true
          deviation_percent: 30
```

### Batch Results

After batch execution:

```
results/batch_001/
├── baseline/
│   ├── session_baseline_*/
│   └── plots/
├── aggressive_voltage/
│   ├── session_aggressive_voltage_*/
│   └── plots/
├── aggressive_current/
│   ├── session_aggressive_current_*/
│   └── plots/
└── comparison_report.txt
```

## Analysis and Visualization

### Automatic Analysis

Results are automatically generated:

- **CSV files**: Raw metrics data
- **JSON files**: Summary statistics
- **PNG plots**: Visualization charts
- **TXT reports**: Comparison analysis

### Manual Analysis

#### Load and Analyze Data

```python
from attack_simulation.metrics import ComparisonAnalyzer

analyzer = ComparisonAnalyzer(
    baseline_session_dir="./output/baseline/session_baseline_20241110_120000",
    attack_session_dir="./output/attack/session_attack_20241110_130000"
)

analyzer.load_simulation_data()
metrics = analyzer.generate_comparison_metrics()

print(f"Degradation acceleration: {metrics.degradation_acceleration_factor:.2f}x")
print(f"Additional degradation: {metrics.additional_degradation_percent:.2f}%")
```

#### Generate Custom Plots

```python
from attack_simulation.visualization import VisualizationEngine
from attack_simulation.metrics import MetricsCollector

metrics = MetricsCollector.load_from_session("./output/attack/session_*")
viz = VisualizationEngine(metrics)

# Generate custom plots
viz.plot_soh_timeline("./custom_plots/soh.png")
viz.plot_parameter_deviations("./custom_plots/deviations.png")
viz.plot_stress_factors("./custom_plots/stress.png")
```

### Understanding Results

#### Key Metrics

1. **SoH (State of Health)**: Battery health percentage (100% = new, 0% = dead)
2. **Degradation Rate**: SoH loss per cycle
3. **Acceleration Factor**: Attack degradation / Baseline degradation
4. **Stress Factors**: Voltage, current, and SoC stress contributions

#### Interpreting Plots

**SoH Timeline Plot**:
- X-axis: Charging cycles
- Y-axis: State of Health (%)
- Shows degradation over time

**Comparison Plot**:
- Overlays baseline and attack curves
- Shaded area shows additional degradation
- Quantifies attack impact

**Parameter Deviation Histogram**:
- Shows distribution of manipulations
- Helps understand attack patterns

## Advanced Usage

### Custom Attack Strategies

Create custom manipulation logic:

```python
from attack_simulation.core import AttackEngine

class CustomAttackEngine(AttackEngine):
    def manipulate_charging_profile(self, profile):
        # Custom manipulation logic
        if self.cycle_count % 10 == 0:
            # Attack every 10th cycle
            profile.voltage *= 1.15
        return profile
```

### Integration with Detection Systems

Test anomaly detection:

```python
from attack_simulation.detection import AnomalyDetector

detector = AnomalyDetector(config_path="attack_simulation/config/detection_config.yaml")

# During simulation
if detector.detect_anomaly(charging_profile):
    print("Attack detected!")
```

### Parallel Batch Execution

Run scenarios in parallel:

```yaml
# batch_config.yaml
execution:
  parallel: true
  max_workers: 4
```

### Custom Output Formats

Export in different formats:

```bash
python attack_simulator.py --config attack_config.yaml --export-format csv json
```

## Troubleshooting

### Common Issues

#### Issue 1: Connection Refused

**Symptom**: `Connection refused to 127.0.0.1:9000`

**Solution**:
```bash
# Verify server is running
python charging/server.py

# Check server configuration
cat charging/server_config.yaml
```

#### Issue 2: Client Cannot Connect to Proxy

**Symptom**: Client fails to connect

**Solution**:
```yaml
# Update client_config.yaml
csms_url: ws://127.0.0.1:9001/  # Use proxy port
```

#### Issue 3: No Manipulation Detected

**Symptom**: Attack runs but no manipulation occurs

**Solution**:
```yaml
# Verify attack is enabled
attack_config:
  enabled: true  # Must be true
```

#### Issue 4: Import Errors

**Symptom**: `ModuleNotFoundError`

**Solution**:
```bash
# Install dependencies
pip install -r requirements.txt

# Verify Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Issue 5: Plot Generation Fails

**Symptom**: Plots not generated

**Solution**:
```bash
# Install matplotlib backend
pip install matplotlib pillow

# Disable plots if not needed
python attack_simulator.py --config attack_config.yaml --no-plots
```

### Debug Mode

Enable detailed logging:

```bash
python attack_simulator.py --config attack_config.yaml --log-level DEBUG --log-file debug.log
```

### Validation

Test configuration before running:

```bash
python attack_simulator.py --config attack_config.yaml --dry-run
```

### Integration Test

Verify EmuOCPP integration:

```bash
python test_integration.py
```

## Best Practices

### 1. Always Run Baseline First

Establish baseline before attack simulations:

```bash
python run_baseline_simulation.py --cycles 1000
python attack_simulator.py --config attack_config.yaml --cycles 1000
```

### 2. Use Consistent Cycle Counts

Use same cycle count for fair comparison:

```bash
--cycles 1000  # Use same value for all scenarios
```

### 3. Document Experiments

Keep notes on configurations used:

```bash
# Save configuration with results
cp attack_config.yaml ./output/attack/session_*/config_used.yaml
```

### 4. Monitor Resource Usage

For long simulations, monitor resources:

```bash
# Run with resource monitoring
python attack_simulator.py --config attack_config.yaml --cycles 10000 &
top -p $!
```

### 5. Backup Results

Save important results:

```bash
# Archive results
tar -czf experiment_001.tar.gz ./output/
```

## Example Workflows

### Workflow 1: Quick Impact Assessment

```bash
# 1. Run baseline (100 cycles for quick test)
python run_baseline_simulation.py --cycles 100

# 2. Run attack
python attack_simulator.py --config attack_simulation/config/attack_config.yaml --cycles 100

# 3. Compare
python run_comparison_analysis.py

# 4. View results
cat ./output/comparison_report.txt
```

### Workflow 2: Comprehensive Study

```bash
# 1. Run batch scenarios
python attack_simulator.py --batch attack_simulation/config/batch_config.yaml

# 2. Analyze each scenario
for dir in ./results/batch_001/*/; do
    echo "Analyzing $dir"
    python -c "from attack_simulation.metrics import MetricsCollector; \
               m = MetricsCollector.load_from_session('$dir'); \
               print(m.generate_summary_report())"
done

# 3. Generate comparison report
python run_comparison_analysis.py --batch ./results/batch_001/
```

### Workflow 3: Detection Evaluation

```bash
# 1. Run with detection enabled
python attack_simulator.py --config attack_simulation/config/detection_config.yaml

# 2. Evaluate detection performance
python attack_simulation/examples/demo_detection_performance.py

# 3. Generate ROC curves
python -c "from attack_simulation.detection import PerformanceEvaluator; \
           e = PerformanceEvaluator('./output/attack/session_*/'); \
           e.generate_roc_curve('./output/roc_curve.png')"
```

## Additional Resources

- **Main Documentation**: `attack_simulation/README.md`
- **Integration Guide**: `attack_simulation/EMUOCPP_INTEGRATION.md`
- **Baseline Comparison**: `BASELINE_COMPARISON_QUICKSTART.md`
- **Scenario Manager**: `attack_simulation/SCENARIO_MANAGER_QUICKSTART.md`
- **Detection Framework**: `attack_simulation/DETECTION_QUICKSTART.md`
- **Troubleshooting**: `TROUBLESHOOTING.md`

## Support

For issues or questions:
- Check troubleshooting section above
- Review logs in `./logs/` directory
- Run integration test: `python test_integration.py`
- Visit: https://github.com/vfg27/EmuOCPP

## License

[To be determined - Research/Academic use]

## Citation

If you use this tool in your research, please cite:

```
[Citation information to be added]
```
