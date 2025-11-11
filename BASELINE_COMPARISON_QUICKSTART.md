# Baseline Comparison Quick Start Guide

## What is Baseline Comparison?

Baseline comparison allows you to measure the impact of charging profile poisoning attacks by comparing battery degradation between:
- **Baseline**: Normal charging (no attack)
- **Attack**: Manipulated charging profiles

## Quick Start (3 Steps)

### Step 1: Run Baseline Simulation

```bash
python run_baseline_simulation.py --cycles 1000
```

This runs 1000 charging cycles with **normal** (unmanipulated) charging profiles.

**Output**: `./output/baseline/session_baseline_YYYYMMDD_HHMMSS/`

### Step 2: Run Attack Simulation

```bash
python attack_simulator.py --cycles 1000
```

This runs 1000 charging cycles with **manipulated** charging profiles.

**Output**: `./output/attack/session_attack_YYYYMMDD_HHMMSS/`

### Step 3: Compare Results

```bash
python run_comparison_analysis.py
```

This automatically finds the latest baseline and attack sessions and generates a comparison report.

**Output**: `./output/comparison/`

## What You Get

The comparison analysis provides:

1. **Degradation Difference**: How much more degradation the attack caused
2. **Acceleration Factor**: How much faster the attack degrades the battery
3. **Time to Thresholds**: How many cycles to reach 90% and 80% SoH
4. **Manipulation Statistics**: Average voltage and current deviations

## Example Output

```
Degradation Acceleration Factor: 2.50x
→ Attack degrades battery 2.5 times faster than normal charging

Degradation Difference: 1.5%
→ After 1000 cycles, attack caused 1.5% additional degradation

Attack reached 90% SoH 2.5x faster
→ Battery reaches end-of-life much sooner under attack
```

## Files Generated

```
output/
├── baseline/session_baseline_*/
│   ├── summary.json              # Baseline metrics
│   └── degradation_timeline.csv  # SoH over time
├── attack/session_attack_*/
│   ├── summary.json              # Attack metrics
│   ├── degradation_timeline.csv  # SoH over time
│   └── manipulations.csv         # Attack events
└── comparison/
    ├── comparison_report.txt     # Human-readable report
    ├── comparison_metrics.json   # Detailed metrics
    └── comparison_metrics.csv    # Spreadsheet format
```

## Advanced Usage

### Custom Configuration

```bash
# Use custom baseline config
python run_baseline_simulation.py --config my_baseline_config.yaml

# Use custom attack config
python attack_simulator.py --config my_attack_config.yaml
```

### Compare Specific Sessions

```bash
python run_comparison_analysis.py \
  --baseline ./output/baseline/session_baseline_20241110_120000 \
  --attack ./output/attack/session_attack_20241110_130000
```

### Different Cycle Counts

```bash
# Run 5000 cycles for more data
python run_baseline_simulation.py --cycles 5000
python attack_simulator.py --cycles 5000
python run_comparison_analysis.py
```

## Troubleshooting

**Problem**: "No baseline sessions found"
**Solution**: Run `python run_baseline_simulation.py` first

**Problem**: "No attack sessions found"
**Solution**: Run `python attack_simulator.py` first

**Problem**: No difference in results
**Solution**: Check that attack is enabled in `attack_simulation/config/attack_config.yaml`

## Next Steps

- Read the full guide: `attack_simulation/BASELINE_COMPARISON_GUIDE.md`
- View implementation details: `attack_simulation/BASELINE_COMPARISON_IMPLEMENTATION.md`
- Run the demo: `python attack_simulation/examples/demo_baseline_comparison.py`

## Requirements

```bash
pip install pandas pyyaml
```

## Support

For detailed documentation, see:
- `attack_simulation/BASELINE_COMPARISON_GUIDE.md`
- `attack_simulation/README.md`
