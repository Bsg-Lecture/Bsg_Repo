# Getting Started with EmuOCPP Attack Simulation

Quick guide to get started after cloning the repository.

## Prerequisites

- Python 3.8 or higher
- Git
- pip (Python package manager)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/vfg27/EmuOCPP
cd EmuOCPP
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
# Run integration tests
python test_integration.py

# Validate configuration
python validate_config.py
```

## Quick Start

### Run a 5-Minute Demo

```bash
# Terminal 1: Start EmuOCPP server
python charging/server.py

# Terminal 2: Run baseline simulation
python run_baseline_simulation.py --cycles 100

# Terminal 3: Run attack simulation
python attack_simulator.py --config attack_simulation/config/attack_config.yaml --cycles 100

# Terminal 4: Compare results
python run_comparison_analysis.py
```

Results will be in `./output/` directory.

## Documentation

- **Main README**: [ATTACK_SIMULATION_README.md](ATTACK_SIMULATION_README.md)
- **Documentation Index**: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- **Usage Guide**: [attack_simulation/USAGE_GUIDE.md](attack_simulation/USAGE_GUIDE.md)
- **API Reference**: [attack_simulation/API_REFERENCE.md](attack_simulation/API_REFERENCE.md)
- **Ethical Guidelines**: [attack_simulation/ETHICAL_USE_GUIDELINES.md](attack_simulation/ETHICAL_USE_GUIDELINES.md)

## Directory Structure

```
EmuOCPP/
├── attack_simulation/       # Attack simulation framework
│   ├── core/               # Core components
│   ├── models/             # Data models
│   ├── metrics/            # Metrics and analysis
│   ├── visualization/      # Visualization
│   ├── detection/          # Anomaly detection
│   ├── config/             # Configuration files
│   └── examples/           # Example scripts
├── charging/               # EmuOCPP base (server/client)
├── tests/                  # Test suite
├── docs/                   # Additional documentation
└── *.py                    # Main scripts
```

## Next Steps

1. Read [ATTACK_SIMULATION_README.md](ATTACK_SIMULATION_README.md) for complete overview
2. Review [attack_simulation/ETHICAL_USE_GUIDELINES.md](attack_simulation/ETHICAL_USE_GUIDELINES.md)
3. Try examples in `attack_simulation/examples/`
4. Explore configuration options in `attack_simulation/config/`

## Troubleshooting

If you encounter issues:
1. Check [attack_simulation/TROUBLESHOOTING_GUIDE.md](attack_simulation/TROUBLESHOOTING_GUIDE.md)
2. Verify Python version: `python --version`
3. Ensure all dependencies installed: `pip list`
4. Check logs in `logs/` directory (created at runtime)

## Support

- GitHub Issues: https://github.com/vfg27/EmuOCPP/issues
- Documentation: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

## License

See LICENSE file for details.
