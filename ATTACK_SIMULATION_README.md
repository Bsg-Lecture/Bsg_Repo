# Charging Profile Poisoning Attack Simulation Framework

## Overview

This framework extends EmuOCPP with comprehensive tools for simulating, analyzing, and defending against charging profile poisoning attacks on OCPP-based electric vehicle charging infrastructure. The system demonstrates how malicious manipulation of OCPP charging profile parameters can lead to accelerated battery degradation in electric vehicles.

**Key Capabilities:**
- Realistic MITM attack simulation on OCPP communication
- Battery degradation modeling based on peer-reviewed research
- Comprehensive metrics collection and analysis
- Publication-quality visualization and reporting
- Anomaly detection and defense evaluation
- Multi-scenario batch execution for comparative studies

**Research Applications:**
- OCPP security vulnerability assessment
- Battery degradation attack vector analysis
- Anomaly detection mechanism evaluation
- Defense strategy development and testing
- Impact quantification for academic publications

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Components](#components)
7. [Documentation](#documentation)
8. [Troubleshooting](#troubleshooting)
9. [Ethical Use](#ethical-use)
10. [Contributing](#contributing)
11. [License](#license)

## Installation

### Prerequisites

- Python 3.8 or higher
- EmuOCPP base installation (see main README.md)
- Git (for cloning repository)

### Step 1: Clone Repository

```bash
git clone https://github.com/vfg27/EmuOCPP
cd EmuOCPP
```

### Step 2: Install Dependencies

```bash
# Install base EmuOCPP dependencies
pip install -r requirements.txt

# Verify installation
python attack_simulator.py --version
```

### Step 3: Verify Installation

```bash
# Run integration tests
python test_integration.py

# Run configuration validation
python validate_config.py
```

### Step 4: Configure EmuOCPP

Ensure EmuOCPP server and client are properly configured:

```bash
# Edit server configuration
nano charging/server_config.yaml

# Edit client configuration
nano charging/client_config.yaml
```

See [EMUOCPP_INTEGRATION.md](attack_simulation/EMUOCPP_INTEGRATION.md) for detailed integration instructions.

## Quick Start

### 5-Minute Demo

Run a complete attack simulation and comparison in 5 steps:

```bash
# Terminal 1: Start EmuOCPP server
python charging/server.py

# Terminal 2: Run baseline simulation (no attack)
python run_baseline_simulation.py --cycles 100

# Terminal 3: Run attack simulation
python attack_simulator.py --config attack_simulation/config/attack_config.yaml --cycles 100

# Terminal 4: Compare results
python run_comparison_analysis.py
```

**Expected Output:**
- Baseline degradation: ~1% SoH loss over 100 cycles
- Attack degradation: ~3-5% SoH loss over 100 cycles
- Acceleration factor: 3-5x faster degradation
- Plots and reports in `./output/` directory

### View Results

```bash
# View comparison report
cat output/comparison_report.txt

# View plots
ls output/plots/
# - soh_comparison.png
# - parameter_deviations.png
# - stress_factors.png
```

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     Scenario Manager                             │
│         (Batch execution, orchestration, reporting)              │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   CSMS      │  │    MITM     │  │  Charge     │
│  (Server)   │◄─┤   Proxy     │◄─┤   Point     │
│             │  │             │  │  (Client)   │
└─────────────┘  └──────┬──────┘  └─────────────┘
                        │
                        │ Intercept & Manipulate
                        │
         ┌──────────────┼──────────────┐
         │              │              │
         ▼              ▼              ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Attack    │  │  Battery    │  │  Metrics    │
│   Engine    │─►│ Degradation │─►│ Collector   │
│             │  │  Simulator  │  │             │
└─────────────┘  └─────────────┘  └──────┬──────┘
                                          │
                                          ▼
                                  ┌─────────────┐
                                  │Visualization│
                                  │  & Reports  │
                                  └─────────────┘
```

### Directory Structure

```
EmuOCPP/
├── attack_simulation/              # Attack simulation framework
│   ├── core/                       # Core components
│   │   ├── attack_engine.py        # Attack logic and strategies
│   │   ├── mitm_proxy.py           # MITM proxy for interception
│   │   ├── ocpp_parser.py          # OCPP message parsing
│   │   └── scenario_manager.py     # Multi-scenario orchestration
│   ├── models/                     # Data models
│   │   ├── battery_model.py        # Battery degradation simulation
│   │   └── ocpp_models.py          # OCPP data structures
│   ├── metrics/                    # Metrics and analysis
│   │   ├── metrics_collector.py    # Data collection and export
│   │   └── comparison_analyzer.py  # Baseline comparison
│   ├── visualization/              # Visualization and reporting
│   │   └── visualization_engine.py # Plot generation
│   ├── detection/                  # Anomaly detection
│   │   ├── anomaly_detector.py     # Detection algorithms
│   │   └── performance_evaluator.py # Detection evaluation
│   ├── config/                     # Configuration templates
│   │   ├── attack_config.yaml      # Single scenario config
│   │   ├── baseline_config.yaml    # Baseline config
│   │   ├── batch_config.yaml       # Batch execution config
│   │   └── detection_config.yaml   # Detection config
│   └── examples/                   # Example scripts and demos
│       ├── demo_*.py               # Component demonstrations
│       ├── validation_*.py         # Validation scenarios
│       └── generate_publication_materials.py
├── attack_simulator.py             # Main CLI entry point
├── run_baseline_simulation.py      # Baseline simulation script
├── run_comparison_analysis.py      # Comparison analysis script
├── test_integration.py             # Integration tests
└── validate_config.py              # Configuration validation
```

## Configuration

### Configuration Files

Three main configuration types:

1. **Attack Configuration** (`attack_config.yaml`) - Single attack scenario
2. **Baseline Configuration** (`baseline_config.yaml`) - No-attack baseline
3. **Batch Configuration** (`batch_config.yaml`) - Multiple scenarios

Located in: `attack_simulation/config/`

### Basic Attack Configuration

```yaml
attack_config:
  enabled: true
  strategy: "aggressive"  # Options: aggressive, subtle, random, targeted
  
  manipulations:
    voltage:
      enabled: true
      deviation_percent: 15  # Increase voltage by 15%
      target_range: [4.2, 4.35]
      
    current:
      enabled: true
      deviation_percent: 25  # Increase current by 25%
      target_range: [50, 80]
      
    charging_curve:
      enabled: true
      modification_type: "flatten"  # Options: flatten, steepen, invert

battery_model:
  initial_capacity_ah: 75.0
  degradation_params:
    optimal_voltage: 3.7
    voltage_stress_coefficient: 0.5
    optimal_c_rate: 0.5
    current_stress_coefficient: 0.3

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

### Attack Strategies

#### 1. Aggressive Strategy
Maximum parameter deviations for rapid degradation demonstration:
- Voltage deviation: 15-20%
- Current deviation: 25-30%
- Use case: Demonstrate maximum attack impact

#### 2. Subtle Strategy
Minimal deviations to evade detection:
- Voltage deviation: 3-5%
- Current deviation: 5-10%
- Use case: Test detection mechanisms

#### 3. Random Strategy
Randomized manipulations within bounds:
- Random deviations between configured ranges
- Reproducible with seed
- Use case: Simulate unpredictable attacks

#### 4. Targeted Strategy
Focus on specific parameters:
- Enable only selected manipulation types
- Use case: Isolate specific attack vectors

## Usage Examples

### Example 1: Basic Attack Simulation

```bash
# Run single attack scenario
python attack_simulator.py \
    --config attack_simulation/config/attack_config.yaml \
    --cycles 1000 \
    --output-dir ./results/experiment_001
```

### Example 2: Baseline Comparison

```bash
# Step 1: Run baseline
python run_baseline_simulation.py --cycles 1000

# Step 2: Run attack
python attack_simulator.py \
    --config attack_simulation/config/attack_config.yaml \
    --cycles 1000

# Step 3: Compare
python run_comparison_analysis.py

# Step 4: View results
cat output/comparison_report.txt
```

### Example 3: Batch Execution

```bash
# Run multiple scenarios for comparison
python attack_simulator.py \
    --batch attack_simulation/config/batch_config.yaml

# Results in: ./output/batch_*/
```

### Example 4: Custom Attack Strategy

Create custom configuration:

```yaml
# custom_attack.yaml
attack_config:
  enabled: true
  strategy: "targeted"
  manipulations:
    voltage:
      enabled: true
      deviation_percent: 12
    current:
      enabled: false
    charging_curve:
      enabled: false
```

Run custom attack:

```bash
python attack_simulator.py --config custom_attack.yaml --cycles 1000
```

### Example 5: Detection Evaluation

```bash
# Run with detection enabled
python attack_simulator.py \
    --config attack_simulation/config/detection_config.yaml \
    --cycles 1000

# Evaluate detection performance
python attack_simulation/examples/demo_detection_performance.py
```

### Example 6: Publication Materials

```bash
# Generate all publication materials
python attack_simulation/examples/generate_publication_materials.py

# Outputs:
# - High-resolution plots (PNG, PDF)
# - LaTeX tables
# - Summary statistics
# - Comparison reports
```

## Components

### 1. MITM Proxy

Transparent interception of OCPP WebSocket communication:

**Features:**
- Bidirectional message interception
- Protocol version detection (OCPP 1.6, 2.0, 2.0.1)
- Selective manipulation of SetChargingProfile messages
- Graceful connection handling and cleanup

**Usage:**
```python
from attack_simulation.core import OCPPMITMProxy

proxy = OCPPMITMProxy(
    csms_host="127.0.0.1",
    csms_port=9000,
    listen_port=9001,
    attack_engine=attack_engine
)

await proxy.start()
```

### 2. Attack Engine

Intelligent manipulation of charging profile parameters:

**Strategies:**
- Aggressive: Maximum deviations
- Subtle: Minimal deviations
- Random: Randomized manipulations
- Targeted: Specific parameter focus

**Usage:**
```python
from attack_simulation.core import AttackEngine

engine = AttackEngine(config_path="attack_simulation/config/attack_config.yaml")
modified_profile = engine.manipulate_charging_profile(original_profile)
```

### 3. Battery Degradation Model

Simulates battery State of Health (SoH) decline:

**Stress Factors:**
- Voltage stress (exponential relationship)
- Current rate stress (quadratic relationship)
- SoC cycling range (penalty for extremes)

**Usage:**
```python
from attack_simulation.models import BatteryDegradationModel

battery = BatteryDegradationModel(initial_capacity_ah=75.0)
result = battery.simulate_charging_cycle(profile, duration_hours=2.0)
print(f"SoH: {battery.soh:.2f}%")
```

### 4. Metrics Collector

Comprehensive data collection and export:

**Collected Metrics:**
- Manipulation events (original vs. modified parameters)
- Charging cycle data (voltage, current, SoC, duration)
- Degradation timeline (SoH over time)
- Stress factor contributions

**Export Formats:**
- CSV (for data analysis)
- JSON (for summary statistics)
- TXT (for reports)

**Usage:**
```python
from attack_simulation.metrics import MetricsCollector

metrics = MetricsCollector(output_dir="./output/attack", session_id="session_001")
metrics.log_manipulation(timestamp, original_profile, modified_profile)
metrics.export_to_csv()
```

### 5. Comparison Analyzer

Baseline vs. attack comparison:

**Capabilities:**
- Load and analyze simulation data
- Calculate degradation acceleration factor
- Find cycles to reach degradation thresholds
- Generate comprehensive comparison reports

**Usage:**
```python
from attack_simulation.metrics import ComparisonAnalyzer

analyzer = ComparisonAnalyzer(
    baseline_session_dir="./output/baseline/session_*",
    attack_session_dir="./output/attack/session_*"
)

analyzer.load_simulation_data()
metrics = analyzer.generate_comparison_metrics()
print(f"Acceleration: {metrics.degradation_acceleration_factor:.2f}x")
```

### 6. Visualization Engine

Publication-quality plots and reports:

**Plot Types:**
- SoH degradation timeline
- Baseline vs. attack comparison
- Parameter deviation histograms
- Stress factor contributions
- Detection performance (ROC curves)

**Export Formats:**
- PNG (high resolution)
- PDF (vector graphics)
- LaTeX tables
- HTML reports

**Usage:**
```python
from attack_simulation.visualization import VisualizationEngine

viz = VisualizationEngine(metrics_collector)
viz.plot_soh_timeline("./output/plots/soh.png")
viz.plot_baseline_comparison(baseline_data, attack_data, "./output/plots/comparison.png")
```

### 7. Anomaly Detector

Statistical anomaly detection for attack identification:

**Detection Methods:**
- Statistical threshold-based detection
- Z-score anomaly detection
- Moving average deviation detection

**Usage:**
```python
from attack_simulation.detection import AnomalyDetector

detector = AnomalyDetector(config_path="attack_simulation/config/detection_config.yaml")
is_anomaly = detector.detect_anomaly(charging_profile)
```

### 8. Scenario Manager

Multi-scenario batch execution and orchestration:

**Features:**
- Sequential or parallel execution
- Battery model reset between scenarios
- Consolidated comparison reports
- Progress tracking and logging

**Usage:**
```python
from attack_simulation.core import ScenarioManager

manager = ScenarioManager("attack_simulation/config/batch_config.yaml")
results = await manager.run_batch()
manager.generate_comparison_report(results)
```

## Documentation

### Core Documentation

- **[USAGE_GUIDE.md](attack_simulation/USAGE_GUIDE.md)** - Complete usage guide with examples
- **[EMUOCPP_INTEGRATION.md](attack_simulation/EMUOCPP_INTEGRATION.md)** - Integration with EmuOCPP
- **[TROUBLESHOOTING_GUIDE.md](attack_simulation/TROUBLESHOOTING_GUIDE.md)** - Common issues and solutions
- **[API_REFERENCE.md](attack_simulation/API_REFERENCE.md)** - Complete API documentation
- **[RESEARCH_METHODOLOGY.md](attack_simulation/RESEARCH_METHODOLOGY.md)** - Research methodology and formulas

### Quick Start Guides

- **[BASELINE_COMPARISON_QUICKSTART.md](BASELINE_COMPARISON_QUICKSTART.md)** - Baseline comparison workflow
- **[SCENARIO_MANAGER_QUICKSTART.md](attack_simulation/SCENARIO_MANAGER_QUICKSTART.md)** - Batch execution guide
- **[DETECTION_QUICKSTART.md](attack_simulation/DETECTION_QUICKSTART.md)** - Anomaly detection guide
- **[VALIDATION_QUICKSTART.md](VALIDATION_QUICKSTART.md)** - Validation scenarios

### Implementation Details

- **[ATTACK_ENGINE_IMPLEMENTATION.md](attack_simulation/ATTACK_ENGINE_IMPLEMENTATION.md)**
- **[BATTERY_MODEL_IMPLEMENTATION.md](attack_simulation/BATTERY_MODEL_IMPLEMENTATION.md)**
- **[METRICS_COLLECTOR_IMPLEMENTATION.md](attack_simulation/METRICS_COLLECTOR_IMPLEMENTATION.md)**
- **[VISUALIZATION_IMPLEMENTATION.md](attack_simulation/VISUALIZATION_IMPLEMENTATION.md)**
- **[DETECTION_FRAMEWORK_IMPLEMENTATION.md](attack_simulation/DETECTION_FRAMEWORK_IMPLEMENTATION.md)**
- **[SCENARIO_MANAGER_IMPLEMENTATION.md](attack_simulation/SCENARIO_MANAGER_IMPLEMENTATION.md)**

### Example Scripts

Located in `attack_simulation/examples/`:

- `demo_attack_engine.py` - Attack engine demonstration
- `demo_battery_model.py` - Battery model demonstration
- `demo_metrics_collector.py` - Metrics collection demonstration
- `demo_visualization.py` - Visualization demonstration
- `demo_baseline_comparison.py` - Baseline comparison demonstration
- `demo_anomaly_detection.py` - Anomaly detection demonstration
- `demo_detection_performance.py` - Detection performance evaluation
- `demo_scenario_manager.py` - Scenario manager demonstration
- `validation_baseline.py` - Baseline validation scenario
- `validation_aggressive.py` - Aggressive attack validation
- `validation_subtle.py` - Subtle attack validation
- `run_full_validation.py` - Complete validation suite
- `generate_publication_materials.py` - Publication materials generation

## Troubleshooting

### Common Issues

#### Issue 1: Connection Refused

**Symptom:** `Connection refused to 127.0.0.1:9000`

**Solution:**
```bash
# Verify server is running
python charging/server.py

# Check server configuration
cat charging/server_config.yaml
```

#### Issue 2: Client Cannot Connect to Proxy

**Symptom:** Client fails to connect to proxy

**Solution:**
```yaml
# Update client_config.yaml
csms_url: ws://127.0.0.1:9001/  # Use proxy port, not server port
```

#### Issue 3: No Manipulation Detected

**Symptom:** Attack runs but no manipulation occurs

**Solution:**
```yaml
# Verify attack is enabled in config
attack_config:
  enabled: true  # Must be true
```

#### Issue 4: Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'attack_simulation'`

**Solution:**
```bash
# Ensure you're in the EmuOCPP directory
cd EmuOCPP

# Install dependencies
pip install -r requirements.txt

# Set PYTHONPATH if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Issue 5: Plot Generation Fails

**Symptom:** Plots not generated or matplotlib errors

**Solution:**
```bash
# Install matplotlib with backend support
pip install matplotlib pillow

# Or disable plots
python attack_simulator.py --config attack_config.yaml --no-plots
```

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
python attack_simulator.py \
    --config attack_simulation/config/attack_config.yaml \
    --log-level DEBUG \
    --log-file debug.log
```

### Validation

Test configuration before running:

```bash
# Dry run (validate without executing)
python attack_simulator.py --config attack_config.yaml --dry-run

# Run configuration validation
python validate_config.py --config attack_config.yaml
```

### Integration Test

Verify EmuOCPP integration:

```bash
python test_integration.py
```

For more troubleshooting help, see [TROUBLESHOOTING_GUIDE.md](attack_simulation/TROUBLESHOOTING_GUIDE.md).

## Ethical Use

### ⚠️ IMPORTANT: Research Use Only

This framework is designed **exclusively for research and educational purposes**. Users must:

✅ **DO:**
- Use only in controlled test environments
- Obtain proper authorization before testing
- Follow responsible disclosure practices
- Comply with all applicable laws and regulations
- Document and report findings ethically
- Contribute to improving OCPP security

❌ **DO NOT:**
- Deploy against production systems without authorization
- Use for malicious purposes
- Cause harm to real infrastructure
- Violate laws or regulations
- Disclose vulnerabilities without responsible disclosure

### Responsible Disclosure

If you discover vulnerabilities using this framework:

1. **Do not** publicly disclose without coordination
2. **Contact** the affected vendor privately
3. **Allow** reasonable time for patching (typically 90 days)
4. **Coordinate** public disclosure with vendor
5. **Document** findings for research community

### Legal Compliance

Users are responsible for:
- Obtaining necessary permissions
- Complying with local and international laws
- Following institutional ethics guidelines
- Respecting intellectual property rights

### Academic Integrity

When using this framework for research:
- Cite this work appropriately
- Share findings with the community
- Contribute improvements back to the project
- Follow academic ethics guidelines

For complete ethical guidelines, see [ETHICAL_USE_GUIDELINES.md](attack_simulation/ETHICAL_USE_GUIDELINES.md).

## Contributing

We welcome contributions from the research community!

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Contribution Areas

- New attack strategies
- Improved battery degradation models
- Additional detection algorithms
- Enhanced visualization capabilities
- Documentation improvements
- Bug fixes and optimizations
- Test coverage improvements

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all public methods
- Include unit tests for new features
- Update documentation as needed
- Ensure backward compatibility

### Testing

Before submitting:

```bash
# Run all tests
python -m pytest tests/

# Run integration tests
python test_integration.py

# Check code style
flake8 attack_simulation/
```

## License

This project is licensed under [LICENSE TYPE] - see LICENSE file for details.

**Academic Use:** Free for research and educational purposes with proper citation.

**Commercial Use:** Contact authors for licensing information.

## Citation

If you use this framework in your research, please cite:

```bibtex
@software{emuocpp_attack_simulation,
  title={Charging Profile Poisoning Attack Simulation Framework},
  author={[Authors]},
  year={2024},
  url={https://github.com/vfg27/EmuOCPP},
  note={Research framework for OCPP security analysis}
}
```

## Acknowledgments

- EmuOCPP base framework by [vfg27](https://github.com/vfg27)
- Battery degradation models based on peer-reviewed literature
- OCPP specifications by Open Charge Alliance
- Research community contributions

## Support

### Getting Help

- **Documentation**: Check documentation files listed above
- **Issues**: Open an issue on GitHub
- **Discussions**: Join GitHub Discussions
- **Email**: [Contact information]

### Reporting Bugs

When reporting bugs, include:
- Python version
- Operating system
- Configuration files (sanitized)
- Error messages and logs
- Steps to reproduce

### Feature Requests

We welcome feature requests! Please:
- Check existing issues first
- Describe the use case
- Explain expected behavior
- Provide examples if possible

## Roadmap

### Current Version (v1.0)

- ✅ MITM proxy implementation
- ✅ Attack engine with multiple strategies
- ✅ Battery degradation modeling
- ✅ Metrics collection and analysis
- ✅ Visualization and reporting
- ✅ Baseline comparison
- ✅ Anomaly detection framework
- ✅ Batch execution capabilities

### Future Enhancements (v2.0)

- [ ] Advanced battery models (temperature effects, calendar aging)
- [ ] Machine learning-based detection
- [ ] Real-time monitoring dashboard
- [ ] Cloud-based CSMS integration
- [ ] Additional attack vectors (firmware, certificates)
- [ ] Multi-vehicle simulation
- [ ] Performance optimizations

## Related Projects

- **[CheckOCPP](https://github.com/vfg27/CheckOCPP)** - Wireshark dissector for OCPP traffic
- **[EmuOCPP](https://github.com/vfg27/EmuOCPP)** - Base OCPP emulator framework

## Contact

- **GitHub**: https://github.com/vfg27/EmuOCPP
- **Issues**: https://github.com/vfg27/EmuOCPP/issues
- **Email**: [Contact email]

---

**Last Updated**: November 2024

**Version**: 1.0.0

**Status**: Active Development
