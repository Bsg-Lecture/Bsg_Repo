# Attack Simulator Quick Reference

Quick reference card for the Charging Profile Poisoning Attack Simulator.

## Essential Commands

### Get Help
```bash
python attack_simulator.py --help
python attack_simulator.py --version
```

### Run Simulations
```bash
# Single attack scenario
python attack_simulator.py --config attack_simulation/config/attack_config.yaml

# Baseline (no attack)
python attack_simulator.py --config attack_simulation/config/baseline_config.yaml

# Batch scenarios
python attack_simulator.py --batch attack_simulation/config/batch_config.yaml

# With custom cycle count
python attack_simulator.py --config attack_config.yaml --cycles 2000
```

### Validate Configuration
```bash
# Dry run (no execution)
python attack_simulator.py --config attack_config.yaml --dry-run

# Test integration
python test_integration.py
```

### Quick Comparison Workflow
```bash
# 1. Baseline
python run_baseline_simulation.py --cycles 1000

# 2. Attack
python attack_simulator.py --config attack_simulation/config/attack_config.yaml --cycles 1000

# 3. Compare
python run_comparison_analysis.py
```

## Configuration Files

| File | Purpose |
|------|---------|
| `attack_simulation/config/attack_config.yaml` | Default attack scenario |
| `attack_simulation/config/baseline_config.yaml` | Baseline (no attack) |
| `attack_simulation/config/batch_config.yaml` | Multiple scenarios |
| `attack_simulation/config/examples/voltage_attack.yaml` | Voltage-only attack |
| `attack_simulation/config/examples/current_attack.yaml` | Current-only attack |
| `attack_simulation/config/examples/subtle_attack.yaml` | Minimal deviations |

## Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--config FILE` | Single scenario config | `--config attack_config.yaml` |
| `--batch FILE` | Batch config | `--batch batch_config.yaml` |
| `--cycles N` | Override cycle count | `--cycles 2000` |
| `--output-dir DIR` | Output directory | `--output-dir ./results` |
| `--log-level LEVEL` | Logging level | `--log-level DEBUG` |
| `--log-file FILE` | Log file path | `--log-file debug.log` |
| `--quiet` | Suppress console | `--quiet` |
| `--no-plots` | Skip plots | `--no-plots` |
| `--dry-run` | Validate only | `--dry-run` |

## Output Structure

```
output/
├── baseline/
│   └── session_baseline_YYYYMMDD_HHMMSS/
│       ├── config.yaml
│       ├── manipulations.csv
│       ├── charging_cycles.csv
│       ├── degradation_timeline.csv
│       ├── summary.json
│       └── plots/
│           ├── soh_timeline.png
│           └── parameter_deviations.png
│
└── attack/
    └── session_attack_YYYYMMDD_HHMMSS/
        └── [same structure]
```

## Key Metrics

| Metric | Description | Good Value |
|--------|-------------|------------|
| **SoH** | State of Health (%) | 100% = new, 80% = end of life |
| **Degradation Rate** | SoH loss per cycle | ~0.01-0.02% per cycle (baseline) |
| **Acceleration Factor** | Attack / Baseline | 1.0x = no effect, 3.0x = 3x faster |
| **Voltage Stress** | Voltage contribution | Lower is better |
| **Current Stress** | Current contribution | Lower is better |

## Attack Strategies

| Strategy | Deviation | Use Case |
|----------|-----------|----------|
| **Aggressive** | 15-30% | Maximum impact demonstration |
| **Subtle** | 5-10% | Evasion testing |
| **Random** | Variable | Unpredictable attacks |
| **Targeted** | Specific | Isolate attack vectors |

## Integration Setup

### 1. Configure Server
```yaml
# charging/server_config.yaml
server_host: 127.0.0.1
server_port: 9000
ocpp_version: 2.0.1
```

### 2. Configure Proxy
```yaml
# attack_simulation/config/attack_config.yaml
proxy:
  csms_host: "127.0.0.1"  # Match server_host
  csms_port: 9000         # Match server_port
  listen_port: 9001       # Proxy port
```

### 3. Configure Client
```yaml
# charging/client_config.yaml
csms_url: ws://127.0.0.1:9001/  # Proxy port!
```

### 4. Start Components
```bash
# Terminal 1: Server
python charging/server.py

# Terminal 2: Attack Simulator
python attack_simulator.py --config attack_config.yaml

# Terminal 3: Client
python charging/client.py
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | Start EmuOCPP server first |
| Client can't connect | Update `csms_url` to proxy port (9001) |
| No manipulation | Check `attack_config.enabled: true` |
| Import errors | `pip install -r requirements.txt` |
| Config not found | Use full path: `attack_simulation/config/...` |
| SSL errors | Check security_profile matches ssl_enabled |

## Documentation

| Document | Purpose |
|----------|---------|
| `attack_simulation/README.md` | Main documentation |
| `attack_simulation/USAGE_GUIDE.md` | Complete usage guide |
| `attack_simulation/EMUOCPP_INTEGRATION.md` | Integration guide |
| `attack_simulation/TROUBLESHOOTING_GUIDE.md` | Troubleshooting |
| `BASELINE_COMPARISON_QUICKSTART.md` | Quick start guide |

## Example Workflows

### Workflow 1: Quick Test (5 min)
```bash
python run_baseline_simulation.py --cycles 100
python attack_simulator.py --config attack_simulation/config/attack_config.yaml --cycles 100
python run_comparison_analysis.py
```

### Workflow 2: Full Study (1 hour)
```bash
python run_baseline_simulation.py --cycles 1000
python attack_simulator.py --config attack_simulation/config/attack_config.yaml --cycles 1000
python run_comparison_analysis.py
```

### Workflow 3: Batch Comparison
```bash
python attack_simulator.py --batch attack_simulation/config/batch_config.yaml
# Results in ./results/batch_001/comparison_report.txt
```

### Workflow 4: Custom Attack
```bash
# 1. Copy example
cp attack_simulation/config/examples/voltage_attack.yaml my_attack.yaml

# 2. Edit
nano my_attack.yaml

# 3. Validate
python attack_simulator.py --config my_attack.yaml --dry-run

# 4. Run
python attack_simulator.py --config my_attack.yaml --cycles 1000
```

## Tips

- ✅ Always run `test_integration.py` first
- ✅ Start with small cycle counts (10-100) for testing
- ✅ Use `--dry-run` to validate configurations
- ✅ Enable `--log-level DEBUG` for troubleshooting
- ✅ Run baseline before attack for comparison
- ✅ Use consistent cycle counts for fair comparison
- ✅ Save configurations with results for reproducibility

## Support

- **Help**: `python attack_simulator.py --help`
- **Test**: `python test_integration.py`
- **Docs**: `attack_simulation/USAGE_GUIDE.md`
- **Issues**: Check `attack_simulation/TROUBLESHOOTING_GUIDE.md`
- **GitHub**: https://github.com/vfg27/EmuOCPP

---

**For detailed information, see the complete documentation in `attack_simulation/`**
