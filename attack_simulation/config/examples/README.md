# Example Attack Configurations

This directory contains example attack scenario configurations demonstrating different attack strategies.

## Available Examples

### 1. Voltage Overstress Attack (`voltage_attack.yaml`)

Focuses exclusively on voltage manipulation to demonstrate voltage-induced battery degradation.

**Configuration**:
- Voltage deviation: 20% increase
- Current manipulation: Disabled
- Charging curve: Disabled

**Use Case**: Isolate and quantify voltage stress effects

**Expected Results**:
- Accelerated degradation due to high voltage stress
- Voltage stress factor dominates in degradation analysis
- Useful for studying voltage-specific attack vectors

**Run**:
```bash
python attack_simulator.py --config attack_simulation/config/examples/voltage_attack.yaml --cycles 1000
```

### 2. Current Overstress Attack (`current_attack.yaml`)

Focuses exclusively on current manipulation to demonstrate current-induced battery degradation.

**Configuration**:
- Voltage manipulation: Disabled
- Current deviation: 30% increase
- Charging curve: Disabled

**Use Case**: Isolate and quantify current stress effects

**Expected Results**:
- Accelerated degradation due to high current rates
- Current stress factor dominates in degradation analysis
- Useful for studying current-specific attack vectors

**Run**:
```bash
python attack_simulator.py --config attack_simulation/config/examples/current_attack.yaml --cycles 1000
```

### 3. Subtle Attack (`subtle_attack.yaml`)

Minimal parameter deviations designed to evade detection while still causing degradation.

**Configuration**:
- Voltage deviation: 5% increase (minimal)
- Current deviation: 8% increase (minimal)
- Charging curve: Disabled (too obvious)

**Use Case**: Test anomaly detection mechanisms and demonstrate stealthy attacks

**Expected Results**:
- Moderate degradation acceleration (1.5-2x baseline)
- Harder to detect with statistical methods
- Useful for evaluating detection thresholds

**Run**:
```bash
python attack_simulator.py --config attack_simulation/config/examples/subtle_attack.yaml --cycles 1000
```

## Comparison Study

Run all examples together for comparative analysis:

```bash
# 1. Run baseline
python run_baseline_simulation.py --cycles 1000

# 2. Run voltage attack
python attack_simulator.py --config attack_simulation/config/examples/voltage_attack.yaml --cycles 1000

# 3. Run current attack
python attack_simulator.py --config attack_simulation/config/examples/current_attack.yaml --cycles 1000

# 4. Run subtle attack
python attack_simulator.py --config attack_simulation/config/examples/subtle_attack.yaml --cycles 1000

# 5. Compare all results
python run_comparison_analysis.py --baseline ./output/baseline/session_* \
    --attack ./output/voltage_attack/session_* \
    --output ./results/voltage_comparison.txt

python run_comparison_analysis.py --baseline ./output/baseline/session_* \
    --attack ./output/current_attack/session_* \
    --output ./results/current_comparison.txt

python run_comparison_analysis.py --baseline ./output/baseline/session_* \
    --attack ./output/subtle_attack/session_* \
    --output ./results/subtle_comparison.txt
```

## Creating Custom Configurations

### Template

Use these examples as templates for custom attack scenarios:

```yaml
# custom_attack.yaml
attack_config:
  enabled: true
  strategy: "aggressive"  # or "subtle", "random", "targeted"
  
  manipulations:
    voltage:
      enabled: true
      deviation_percent: 15  # Customize this
      target_range: [4.2, 4.35]
      
    current:
      enabled: true
      deviation_percent: 25  # Customize this
      target_range: [50, 80]
      
    charging_curve:
      enabled: false
      modification_type: "flatten"

# ... rest of configuration
```

### Customization Guidelines

**Voltage Manipulation**:
- Conservative: 5-10% deviation
- Moderate: 10-15% deviation
- Aggressive: 15-25% deviation
- Extreme: >25% deviation (may be unrealistic)

**Current Manipulation**:
- Conservative: 5-10% deviation
- Moderate: 10-20% deviation
- Aggressive: 20-35% deviation
- Extreme: >35% deviation (may be unrealistic)

**Strategy Selection**:
- `aggressive`: Maximum deviations, obvious attack
- `subtle`: Minimal deviations, stealthy attack
- `random`: Randomized deviations, unpredictable
- `targeted`: Specific parameter focus

## Expected Degradation Rates

Based on literature and simulation results:

| Scenario | Cycles to 80% SoH | Acceleration Factor |
|----------|-------------------|---------------------|
| Baseline | 1500-2000 | 1.0x |
| Subtle Attack | 1000-1500 | 1.5-2.0x |
| Voltage Attack | 800-1200 | 2.0-3.0x |
| Current Attack | 700-1100 | 2.5-3.5x |
| Combined Attack | 500-800 | 3.0-5.0x |

*Note: Actual results depend on battery model parameters*

## Integration with EmuOCPP

All examples are compatible with EmuOCPP server/client:

1. **Start EmuOCPP server**:
   ```bash
   python charging/server.py
   ```

2. **Configure client to use proxy**:
   ```yaml
   # charging/client_config.yaml
   csms_url: ws://127.0.0.1:9001/  # Proxy port
   ```

3. **Run attack simulator**:
   ```bash
   python attack_simulator.py --config attack_simulation/config/examples/voltage_attack.yaml
   ```

4. **Start client**:
   ```bash
   python charging/client.py
   ```

See [EMUOCPP_INTEGRATION.md](../../EMUOCPP_INTEGRATION.md) for details.

## Batch Execution

Create a batch configuration to run all examples:

```yaml
# examples_batch.yaml
batch_config:
  name: "Example Scenarios Comparison"
  output_dir: "./results/examples_batch"
  
  scenarios:
    - name: "baseline"
      attack_enabled: false
      cycles: 1000
      
    - name: "voltage_attack"
      attack_enabled: true
      strategy: "aggressive"
      cycles: 1000
      manipulations:
        voltage:
          enabled: true
          deviation_percent: 20
        current:
          enabled: false
          
    - name: "current_attack"
      attack_enabled: true
      strategy: "aggressive"
      cycles: 1000
      manipulations:
        voltage:
          enabled: false
        current:
          enabled: true
          deviation_percent: 30
          
    - name: "subtle_attack"
      attack_enabled: true
      strategy: "subtle"
      cycles: 1000
      manipulations:
        voltage:
          enabled: true
          deviation_percent: 5
        current:
          enabled: true
          deviation_percent: 8
```

Run batch:
```bash
python attack_simulator.py --batch examples_batch.yaml
```

## Troubleshooting

If you encounter issues with these examples:

1. **Verify EmuOCPP is running**:
   ```bash
   python test_integration.py
   ```

2. **Check configuration syntax**:
   ```bash
   python attack_simulator.py --config attack_simulation/config/examples/voltage_attack.yaml --dry-run
   ```

3. **Enable debug logging**:
   ```bash
   python attack_simulator.py --config attack_simulation/config/examples/voltage_attack.yaml --log-level DEBUG
   ```

4. **See troubleshooting guide**:
   - [TROUBLESHOOTING_GUIDE.md](../../TROUBLESHOOTING_GUIDE.md)

## Additional Resources

- **Usage Guide**: [USAGE_GUIDE.md](../../USAGE_GUIDE.md)
- **Integration Guide**: [EMUOCPP_INTEGRATION.md](../../EMUOCPP_INTEGRATION.md)
- **Main README**: [README.md](../../README.md)

## Contributing

To add new example configurations:

1. Create new YAML file in this directory
2. Follow existing naming convention
3. Document expected results
4. Test with `--dry-run` first
5. Update this README with new example

## License

[To be determined - Research/Academic use]
