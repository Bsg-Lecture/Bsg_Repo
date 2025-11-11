# Baseline Comparison Mode Guide

## Overview

The Baseline Comparison Mode allows you to run simulations in transparent proxy mode (no attack manipulation) and compare the results with attack simulations to quantify the impact of charging profile poisoning attacks on battery degradation.

## Features

### 1. Baseline Simulation Capability
- **Transparent Proxy Mode**: Runs MITM proxy without manipulating charging profiles
- **Normal Degradation Tracking**: Measures battery degradation under normal charging conditions
- **Baseline Configuration**: Dedicated configuration file with attack disabled

### 2. Comparison Analysis
- **Load Baseline and Attack Data**: Automatically loads simulation results from both scenarios
- **Calculate Degradation Difference**: Computes the additional degradation caused by attacks
- **Degradation Acceleration Factor**: Measures how much faster attacks degrade batteries
- **Time to Threshold Analysis**: Compares cycles needed to reach degradation milestones
- **Comprehensive Reports**: Generates detailed comparison reports in multiple formats

## Quick Start

### Step 1: Run Baseline Simulation

Run a baseline simulation with no attack manipulation:

```bash
python run_baseline_simulation.py --config attack_simulation/config/baseline_config.yaml --cycles 1000
```

This will:
- Run 1000 charging cycles with normal (unmanipulated) charging profiles
- Track battery degradation under optimal conditions
- Save results to `./output/baseline/session_baseline_YYYYMMDD_HHMMSS/`

### Step 2: Run Attack Simulation

Run an attack simulation with charging profile manipulation:

```bash
python attack_simulator.py --config attack_simulation/config/attack_config.yaml --cycles 1000
```

This will:
- Run 1000 charging cycles with manipulated charging profiles
- Track accelerated battery degradation
- Save results to `./output/attack/session_attack_YYYYMMDD_HHMMSS/`

### Step 3: Compare Results

Compare baseline and attack simulation results:

```bash
python run_comparison_analysis.py
```

This will automatically:
- Find the latest baseline and attack sessions
- Load and analyze both datasets
- Generate comparison reports and metrics
- Save results to `./output/comparison/`

## Configuration

### Baseline Configuration

The baseline configuration (`baseline_config.yaml`) has attack mode disabled:

```yaml
attack_config:
  enabled: false  # Attack disabled for baseline
  
  manipulations:
    voltage:
      enabled: false
      deviation_percent: 0
    current:
      enabled: false
      deviation_percent: 0
    charging_curve:
      enabled: false

simulation:
  cycles: 1000
  cycle_duration_hours: 2.0
  mode: "baseline"

metrics:
  output_dir: "./output/baseline"
```

### Attack Configuration

The attack configuration (`attack_config.yaml`) has attack mode enabled:

```yaml
attack_config:
  enabled: true  # Attack enabled
  strategy: "aggressive"
  
  manipulations:
    voltage:
      enabled: true
      deviation_percent: 15
    current:
      enabled: true
      deviation_percent: 25

simulation:
  cycles: 1000
  cycle_duration_hours: 2.0
  mode: "attack"

metrics:
  output_dir: "./output/attack"
```

## Command-Line Options

### run_baseline_simulation.py

```bash
python run_baseline_simulation.py [OPTIONS]

Options:
  --config PATH       Path to baseline configuration file
                      (default: attack_simulation/config/baseline_config.yaml)
  --cycles INT        Number of charging cycles to simulate (default: 1000)
  --output-dir PATH   Output directory for results (default: from config)
```

### run_comparison_analysis.py

```bash
python run_comparison_analysis.py [OPTIONS]

Options:
  --baseline PATH       Path to specific baseline session directory
  --attack PATH         Path to specific attack session directory
  --baseline-dir PATH   Base directory for baseline simulations (default: ./output/baseline)
  --attack-dir PATH     Base directory for attack simulations (default: ./output/attack)
  --output PATH         Output directory for comparison results (default: ./output/comparison)
```

## Output Files

### Baseline Simulation Output

```
output/baseline/session_baseline_YYYYMMDD_HHMMSS/
├── config.json                    # Simulation configuration
├── summary.json                   # Summary statistics
├── charging_cycles.csv            # Cycle-by-cycle data
├── degradation_timeline.csv       # SoH over time
└── manipulations.csv              # Empty (no manipulations in baseline)
```

### Attack Simulation Output

```
output/attack/session_attack_YYYYMMDD_HHMMSS/
├── config.json                    # Simulation configuration
├── summary.json                   # Summary statistics
├── charging_cycles.csv            # Cycle-by-cycle data
├── degradation_timeline.csv       # SoH over time
└── manipulations.csv              # Manipulation events
```

### Comparison Output

```
output/comparison/
├── comparison_report.txt          # Human-readable comparison report
├── comparison_metrics.json        # Detailed metrics in JSON format
└── comparison_metrics.csv         # Metrics in CSV format
```

## Comparison Metrics

The comparison analysis generates the following metrics:

### Degradation Comparison
- **Baseline Final SoH**: Final State of Health after baseline simulation
- **Attack Final SoH**: Final State of Health after attack simulation
- **Degradation Difference**: Additional degradation caused by attack (attack - baseline)
- **Degradation Acceleration Factor**: How much faster attack degrades battery (attack_rate / baseline_rate)

### Cycle Comparison
- **Degradation Rate per Cycle**: Percentage degradation per charging cycle
- **Cycles to 90% SoH**: Number of cycles to reach 90% State of Health
- **Cycles to 80% SoH**: Number of cycles to reach 80% State of Health

### Attack Statistics
- **Mean Voltage Deviation**: Average voltage manipulation percentage
- **Mean Current Deviation**: Average current manipulation percentage

## Example Comparison Report

```
================================================================================
BASELINE VS ATTACK SIMULATION COMPARISON REPORT
================================================================================

Baseline Session: baseline_20241110_120000
Attack Session: attack_20241110_130000

--------------------------------------------------------------------------------
DEGRADATION COMPARISON
--------------------------------------------------------------------------------

Baseline Final SoH: 99.00%
Attack Final SoH: 97.50%

Baseline Total Degradation: 1.0000%
Attack Total Degradation: 2.5000%
Degradation Difference: 1.5000%

Degradation Acceleration Factor: 2.50x

--------------------------------------------------------------------------------
CYCLE COMPARISON
--------------------------------------------------------------------------------

Baseline Cycles: 1000
Attack Cycles: 1000

Baseline Degradation Rate: 0.001000% per cycle
Attack Degradation Rate: 0.002500% per cycle

--------------------------------------------------------------------------------
TIME TO DEGRADATION THRESHOLDS
--------------------------------------------------------------------------------

Baseline Cycles to 90% SoH: Not reached
Attack Cycles to 90% SoH: 4000
  → Attack reached 90% SoH 2.50x faster

--------------------------------------------------------------------------------
ATTACK MANIPULATION STATISTICS
--------------------------------------------------------------------------------

Mean Voltage Deviation: 15.00%
Mean Current Deviation: 25.00%

================================================================================
```

## Programmatic Usage

You can also use the comparison analyzer programmatically:

```python
from attack_simulation.metrics.comparison_analyzer import ComparisonAnalyzer

# Initialize analyzer
analyzer = ComparisonAnalyzer(
    baseline_session_dir="./output/baseline/session_baseline_20241110_120000",
    attack_session_dir="./output/attack/session_attack_20241110_130000",
    output_dir="./output/comparison"
)

# Load data
analyzer.load_simulation_data()

# Calculate metrics
degradation_diff = analyzer.calculate_degradation_difference()
acceleration_factor = analyzer.compute_degradation_acceleration_factor()

# Generate comprehensive metrics
metrics = analyzer.generate_comparison_metrics()

# Generate reports
report_path = analyzer.generate_comparison_report(metrics)
csv_path = analyzer.export_comparison_csv(metrics)

print(f"Degradation acceleration: {acceleration_factor:.2f}x")
print(f"Report saved to: {report_path}")
```

## Use Cases

### 1. Research Publications
- Quantify attack impact with statistical rigor
- Generate publication-quality comparison data
- Support claims about attack effectiveness

### 2. Defense Evaluation
- Establish baseline degradation rates
- Measure effectiveness of detection mechanisms
- Compare different attack strategies

### 3. Risk Assessment
- Estimate real-world impact of attacks
- Calculate time to battery failure under attack
- Support security risk analysis

## Best Practices

1. **Use Same Configuration**: Keep battery model parameters identical between baseline and attack simulations for fair comparison

2. **Run Multiple Trials**: Run multiple baseline and attack simulations to account for randomness

3. **Match Cycle Counts**: Use the same number of cycles for both baseline and attack simulations

4. **Document Scenarios**: Save configuration files with descriptive names for different attack scenarios

5. **Version Control**: Track configuration changes to ensure reproducibility

## Troubleshooting

### Issue: "No baseline sessions found"
**Solution**: Run a baseline simulation first using `run_baseline_simulation.py`

### Issue: "Failed to load simulation data"
**Solution**: Ensure both baseline and attack simulations completed successfully and generated summary.json files

### Issue: "Degradation acceleration factor is 1.0"
**Solution**: Check that attack is enabled in attack configuration and manipulations are being applied

### Issue: Comparison shows no difference
**Solution**: Verify attack configuration has non-zero deviation percentages and attack is enabled

## Requirements

The baseline comparison functionality requires:
- Python 3.7+
- pandas (for data analysis)
- PyYAML (for configuration)
- All EmuOCPP dependencies

Install with:
```bash
pip install pandas pyyaml
```

## Related Documentation

- [Attack Engine Implementation](ATTACK_ENGINE_IMPLEMENTATION.md)
- [Battery Model Implementation](BATTERY_MODEL_IMPLEMENTATION.md)
- [Metrics Collector Implementation](METRICS_COLLECTOR_IMPLEMENTATION.md)
- [Main README](README.md)
