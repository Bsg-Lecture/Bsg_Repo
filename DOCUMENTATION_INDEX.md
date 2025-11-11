# Documentation Index

Complete index of all documentation for the EmuOCPP Charging Profile Poisoning Attack Simulation Framework.

## Quick Start

**New to the framework?** Start here:
1. [ATTACK_SIMULATION_README.md](ATTACK_SIMULATION_README.md) - Main overview and quick start
2. [attack_simulation/USAGE_GUIDE.md](attack_simulation/USAGE_GUIDE.md) - Complete usage guide
3. [BASELINE_COMPARISON_QUICKSTART.md](BASELINE_COMPARISON_QUICKSTART.md) - 5-minute demo

## Core Documentation

### Main Documentation

| Document | Description |
|----------|-------------|
| [ATTACK_SIMULATION_README.md](ATTACK_SIMULATION_README.md) | Main framework overview, installation, and quick start |
| [README.md](README.md) | EmuOCPP base framework documentation |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Quick reference for common tasks |

### Usage Guides

| Document | Description |
|----------|-------------|
| [attack_simulation/USAGE_GUIDE.md](attack_simulation/USAGE_GUIDE.md) | Complete usage guide with examples |
| [BASELINE_COMPARISON_QUICKSTART.md](BASELINE_COMPARISON_QUICKSTART.md) | Baseline comparison workflow |
| [attack_simulation/SCENARIO_MANAGER_QUICKSTART.md](attack_simulation/SCENARIO_MANAGER_QUICKSTART.md) | Batch execution guide |
| [attack_simulation/DETECTION_QUICKSTART.md](attack_simulation/DETECTION_QUICKSTART.md) | Anomaly detection guide |
| [VALIDATION_QUICKSTART.md](VALIDATION_QUICKSTART.md) | Validation scenarios |

### API and Technical Reference

| Document | Description |
|----------|-------------|
| [attack_simulation/API_REFERENCE.md](attack_simulation/API_REFERENCE.md) | Complete API documentation |
| [attack_simulation/RESEARCH_METHODOLOGY.md](attack_simulation/RESEARCH_METHODOLOGY.md) | Research methodology and formulas |

### Integration and Setup

| Document | Description |
|----------|-------------|
| [attack_simulation/EMUOCPP_INTEGRATION.md](attack_simulation/EMUOCPP_INTEGRATION.md) | Integration with EmuOCPP |
| [CLIENT_SETUP_LOG.md](CLIENT_SETUP_LOG.md) | Client setup instructions |
| [SERVER_STARTUP_LOG.md](SERVER_STARTUP_LOG.md) | Server startup instructions |

### Troubleshooting

| Document | Description |
|----------|-------------|
| [attack_simulation/TROUBLESHOOTING_GUIDE.md](attack_simulation/TROUBLESHOOTING_GUIDE.md) | Common issues and solutions |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | EmuOCPP troubleshooting |

## Implementation Documentation

### Component Implementation

| Document | Description |
|----------|-------------|
| [attack_simulation/ATTACK_ENGINE_IMPLEMENTATION.md](attack_simulation/ATTACK_ENGINE_IMPLEMENTATION.md) | Attack engine implementation details |
| [attack_simulation/BATTERY_MODEL_IMPLEMENTATION.md](attack_simulation/BATTERY_MODEL_IMPLEMENTATION.md) | Battery degradation model implementation |
| [attack_simulation/METRICS_COLLECTOR_IMPLEMENTATION.md](attack_simulation/METRICS_COLLECTOR_IMPLEMENTATION.md) | Metrics collection implementation |
| [attack_simulation/VISUALIZATION_IMPLEMENTATION.md](attack_simulation/VISUALIZATION_IMPLEMENTATION.md) | Visualization engine implementation |
| [attack_simulation/DETECTION_FRAMEWORK_IMPLEMENTATION.md](attack_simulation/DETECTION_FRAMEWORK_IMPLEMENTATION.md) | Detection framework implementation |
| [attack_simulation/SCENARIO_MANAGER_IMPLEMENTATION.md](attack_simulation/SCENARIO_MANAGER_IMPLEMENTATION.md) | Scenario manager implementation |
| [attack_simulation/BASELINE_COMPARISON_IMPLEMENTATION.md](attack_simulation/BASELINE_COMPARISON_IMPLEMENTATION.md) | Baseline comparison implementation |
| [attack_simulation/CLI_IMPLEMENTATION_SUMMARY.md](attack_simulation/CLI_IMPLEMENTATION_SUMMARY.md) | CLI implementation summary |

### Testing and Validation

| Document | Description |
|----------|-------------|
| [tests/README.md](tests/README.md) | Test suite documentation |
| [tests/TEST_SUITE_SUMMARY.md](tests/TEST_SUITE_SUMMARY.md) | Test suite summary |

## Research and Ethics

### Research Documentation

| Document | Description |
|----------|-------------|
| [attack_simulation/RESEARCH_METHODOLOGY.md](attack_simulation/RESEARCH_METHODOLOGY.md) | Research methodology, formulas, and literature |
| [attack_simulation/BASELINE_COMPARISON_GUIDE.md](attack_simulation/BASELINE_COMPARISON_GUIDE.md) | Baseline comparison methodology |

### Ethical Guidelines

| Document | Description |
|----------|-------------|
| [attack_simulation/ETHICAL_USE_GUIDELINES.md](attack_simulation/ETHICAL_USE_GUIDELINES.md) | Ethical use guidelines and responsible disclosure |

## Configuration

### Configuration Files

Located in `attack_simulation/config/`:
- `attack_config.yaml` - Single attack scenario configuration
- `baseline_config.yaml` - Baseline (no attack) configuration
- `batch_config.yaml` - Batch execution configuration
- `detection_config.yaml` - Anomaly detection configuration

### Configuration Examples

Located in `attack_simulation/config/examples/`:
- Example configurations for various attack scenarios
- See [attack_simulation/config/examples/README.md](attack_simulation/config/examples/README.md)

## Examples and Demos

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

### Validation Scenarios

Located in `attack_simulation/examples/`:
- `validation_baseline.py` - Baseline validation scenario
- `validation_aggressive.py` - Aggressive attack validation
- `validation_subtle.py` - Subtle attack validation
- `run_full_validation.py` - Complete validation suite
- `generate_publication_materials.py` - Publication materials generation

See [attack_simulation/examples/VALIDATION_SCENARIOS_README.md](attack_simulation/examples/VALIDATION_SCENARIOS_README.md)

## Logs and Output

### Log Files

- `validation_log.md` - Validation execution log
- `logs/` - Runtime logs directory

### Output Structure

```
output/
├── baseline/
│   └── session_baseline_*/
│       ├── manipulations.csv
│       ├── charging_cycles.csv
│       ├── degradation_timeline.csv
│       ├── summary.json
│       └── plots/
├── attack/
│   └── session_attack_*/
│       ├── manipulations.csv
│       ├── charging_cycles.csv
│       ├── degradation_timeline.csv
│       ├── summary.json
│       └── plots/
└── comparison_report.txt
```

## Documentation by User Type

### For Researchers

1. Start: [ATTACK_SIMULATION_README.md](ATTACK_SIMULATION_README.md)
2. Methodology: [attack_simulation/RESEARCH_METHODOLOGY.md](attack_simulation/RESEARCH_METHODOLOGY.md)
3. Ethics: [attack_simulation/ETHICAL_USE_GUIDELINES.md](attack_simulation/ETHICAL_USE_GUIDELINES.md)
4. Usage: [attack_simulation/USAGE_GUIDE.md](attack_simulation/USAGE_GUIDE.md)
5. API: [attack_simulation/API_REFERENCE.md](attack_simulation/API_REFERENCE.md)

### For Developers

1. Start: [ATTACK_SIMULATION_README.md](ATTACK_SIMULATION_README.md)
2. API: [attack_simulation/API_REFERENCE.md](attack_simulation/API_REFERENCE.md)
3. Implementation: Component implementation docs (see above)
4. Testing: [tests/README.md](tests/README.md)
5. Integration: [attack_simulation/EMUOCPP_INTEGRATION.md](attack_simulation/EMUOCPP_INTEGRATION.md)

### For Security Professionals

1. Start: [ATTACK_SIMULATION_README.md](ATTACK_SIMULATION_README.md)
2. Ethics: [attack_simulation/ETHICAL_USE_GUIDELINES.md](attack_simulation/ETHICAL_USE_GUIDELINES.md)
3. Usage: [attack_simulation/USAGE_GUIDE.md](attack_simulation/USAGE_GUIDE.md)
4. Detection: [attack_simulation/DETECTION_QUICKSTART.md](attack_simulation/DETECTION_QUICKSTART.md)
5. Troubleshooting: [attack_simulation/TROUBLESHOOTING_GUIDE.md](attack_simulation/TROUBLESHOOTING_GUIDE.md)

### For Students

1. Start: [ATTACK_SIMULATION_README.md](ATTACK_SIMULATION_README.md)
2. Quick Start: [BASELINE_COMPARISON_QUICKSTART.md](BASELINE_COMPARISON_QUICKSTART.md)
3. Usage: [attack_simulation/USAGE_GUIDE.md](attack_simulation/USAGE_GUIDE.md)
4. Examples: Scripts in `attack_simulation/examples/`
5. Ethics: [attack_simulation/ETHICAL_USE_GUIDELINES.md](attack_simulation/ETHICAL_USE_GUIDELINES.md)

## Documentation Standards

All documentation follows these standards:
- Markdown format for readability
- Code examples with syntax highlighting
- Clear section organization
- Cross-references between documents
- Practical examples and use cases
- Troubleshooting sections where applicable

## Contributing to Documentation

To improve documentation:
1. Follow existing formatting and style
2. Add examples for complex concepts
3. Update cross-references when adding new docs
4. Test all code examples
5. Submit pull requests with clear descriptions

## Getting Help

If you can't find what you need:
1. Check [attack_simulation/TROUBLESHOOTING_GUIDE.md](attack_simulation/TROUBLESHOOTING_GUIDE.md)
2. Review [attack_simulation/USAGE_GUIDE.md](attack_simulation/USAGE_GUIDE.md)
3. Search existing documentation
4. Open an issue on GitHub
5. Contact the maintainers

## Version Information

- **Documentation Version:** 1.0.0
- **Last Updated:** November 2024
- **Framework Version:** 1.0.0

## License

See LICENSE file for licensing information.

---

**Quick Links:**
- [Main README](ATTACK_SIMULATION_README.md)
- [Usage Guide](attack_simulation/USAGE_GUIDE.md)
- [API Reference](attack_simulation/API_REFERENCE.md)
- [Ethical Guidelines](attack_simulation/ETHICAL_USE_GUIDELINES.md)
- [Research Methodology](attack_simulation/RESEARCH_METHODOLOGY.md)
