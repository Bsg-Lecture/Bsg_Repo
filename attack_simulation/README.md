# Charging Profile Poisoning Attack Simulation

This package provides tools for simulating and analyzing charging profile poisoning attacks on OCPP-based EV charging infrastructure.

## Overview

The attack simulation framework demonstrates how malicious manipulation of OCPP charging profile parameters can lead to long-term battery degradation in electric vehicles. This research-oriented implementation provides:

- Realistic charging profile manipulation attacks
- Battery degradation modeling and simulation
- Comprehensive metrics collection and analysis
- Publication-quality visualization and reporting
- Multi-scenario batch execution capabilities

## Directory Structure

```
attack_simulation/
├── core/                      # Core attack simulation components
│   ├── attack_engine.py       # Attack logic and manipulation strategies
│   ├── mitm_proxy.py          # MITM proxy for OCPP interception
│   └── scenario_manager.py    # Multi-scenario orchestration
├── models/                    # Data models
│   ├── battery_model.py       # Battery degradation simulation
│   └── ocpp_models.py         # OCPP data structures
├── metrics/                   # Metrics collection and analysis
│   └── metrics_collector.py   # Data collection and export
├── visualization/             # Visualization and reporting
│   └── visualization_engine.py # Plot generation
└── config/                    # Configuration templates
    ├── attack_config.yaml     # Single scenario configuration
    └── batch_config.yaml      # Batch execution configuration
```

## Configuration

### Attack Configuration (`attack_config.yaml`)

Configure attack parameters, battery model settings, and simulation options:

- **Attack Strategy**: aggressive, subtle, random, or targeted
- **Manipulation Types**: voltage, current, charging curve
- **Battery Model**: degradation parameters based on literature
- **Simulation Settings**: number of cycles, duration, etc.

### Batch Configuration (`batch_config.yaml`)

Define multiple scenarios for comparative analysis:

- Multiple attack scenarios with different parameters
- Baseline (no attack) scenario for comparison
- Shared battery model and proxy settings
- Output and execution options

## Quick Start

### 5-Minute Demo

```bash
# 1. Start EmuOCPP server (Terminal 1)
python charging/server.py

# 2. Run baseline simulation (Terminal 2)
python run_baseline_simulation.py --cycles 100

# 3. Run attack simulation (Terminal 3)
python attack_simulator.py --config attack_simulation/config/attack_config.yaml --cycles 100

# 4. Compare results
python run_comparison_analysis.py
```

Results will be in `./output/` with plots and metrics.

### Command-Line Interface

```bash
# Show help
python attack_simulator.py --help

# Run single scenario
python attack_simulator.py --config attack_simulation/config/attack_config.yaml

# Run batch scenarios
python attack_simulator.py --batch attack_simulation/config/batch_config.yaml

# Run with custom options
python attack_simulator.py --config attack_simulation/config/attack_config.yaml \
    --cycles 2000 --log-level DEBUG --output-dir ./results/experiment_001
```

## Documentation

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Complete usage guide with examples
- **[EMUOCPP_INTEGRATION.md](EMUOCPP_INTEGRATION.md)** - Integration with EmuOCPP
- **[TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md)** - Troubleshooting common issues
- **[BASELINE_COMPARISON_QUICKSTART.md](../BASELINE_COMPARISON_QUICKSTART.md)** - Baseline comparison workflow
- **[SCENARIO_MANAGER_QUICKSTART.md](SCENARIO_MANAGER_QUICKSTART.md)** - Batch execution guide
- **[DETECTION_QUICKSTART.md](DETECTION_QUICKSTART.md)** - Anomaly detection guide

## Usage

### Baseline Comparison (Quick Start)

The easiest way to quantify attack impact is to run baseline and attack simulations, then compare:

```bash
# Step 1: Run baseline simulation (no attack)
python run_baseline_simulation.py --cycles 1000

# Step 2: Run attack simulation
python attack_simulator.py --config attack_simulation/config/attack_config.yaml --cycles 1000

# Step 3: Compare results
python run_comparison_analysis.py
```

See [BASELINE_COMPARISON_QUICKSTART.md](../BASELINE_COMPARISON_QUICKSTART.md) for details.

### Single Scenario Execution

```python
from attack_simulation.core import AttackEngine, OCPPMITMProxy
from attack_simulation.models import BatteryDegradationModel
from attack_simulation.metrics import MetricsCollector

# Load configuration
# Initialize components
# Run simulation
```

### Batch Execution

```python
from attack_simulation.core import ScenarioManager

# Load batch configuration
manager = ScenarioManager("config/batch_config.yaml")

# Execute all scenarios
results = await manager.run_batch()

# Generate comparison report
manager.generate_comparison_report(results)
```

### Comparison Analysis

```python
from attack_simulation.metrics import ComparisonAnalyzer

# Compare baseline and attack simulations
analyzer = ComparisonAnalyzer(
    baseline_session_dir="./output/baseline/session_baseline_20241110_120000",
    attack_session_dir="./output/attack/session_attack_20241110_130000"
)

analyzer.load_simulation_data()
metrics = analyzer.generate_comparison_metrics()
report_path = analyzer.generate_comparison_report(metrics)

print(f"Acceleration factor: {metrics.degradation_acceleration_factor:.2f}x")
```

## Components

### Attack Engine

Implements intelligent manipulation of OCPP charging profiles with configurable strategies:

- **Aggressive**: Maximum parameter deviations for rapid degradation
- **Subtle**: Minimal deviations to evade detection
- **Random**: Randomized manipulations within bounds
- **Targeted**: Specific parameter targeting

### Battery Degradation Model

Simulates battery State of Health (SoH) decline based on:

- Voltage stress (exponential relationship)
- Current rate stress (quadratic relationship)
- SoC cycling range (penalty for extremes)
- Literature-based degradation parameters

### MITM Proxy

Transparent interception of OCPP WebSocket communication:

- Bidirectional message interception
- Protocol version detection (OCPP 1.6, 2.0, 2.0.1)
- Selective manipulation of SetChargingProfile messages
- Graceful connection handling

### Metrics Collector

Comprehensive data collection and export:

- Manipulation event logging
- Charging cycle metrics
- Degradation timeline tracking
- CSV and JSON export formats
- Summary statistics generation

### Comparison Analyzer

Baseline vs. attack comparison capabilities:

- Load and analyze baseline and attack simulation data
- Calculate degradation difference and acceleration factor
- Find cycles to reach degradation thresholds
- Generate comprehensive comparison reports
- Export in multiple formats (TXT, JSON, CSV)

### Visualization Engine

Publication-quality plots and reports:

- SoH degradation timeline plots
- Baseline vs. attack comparison plots
- Parameter deviation histograms
- Stress factor contribution charts
- LaTeX tables and HTML reports

## Research Applications

This framework is designed for academic research on:

- OCPP security vulnerabilities
- Battery degradation attack vectors
- Anomaly detection mechanism evaluation
- Defense strategy development
- Impact quantification and analysis

## Ethical Use

**IMPORTANT**: This tool is designed for research purposes only. Users must:

- Only use in controlled test environments
- Never deploy against production systems without authorization
- Follow responsible disclosure practices
- Comply with all applicable laws and regulations

## Requirements

- Python 3.8+
- websockets
- PyYAML
- pandas
- matplotlib
- numpy

## Installation

```bash
pip install -r requirements.txt
```

## Development Status

This is an active research project. Components are being implemented incrementally according to the implementation plan in `.kiro/specs/charging-profile-poisoning-attack/tasks.md`.

## License

[To be determined - Research/Academic use]

## Contact

[Research team contact information]
