# Scenario Manager Quick Start Guide

## What is the Scenario Manager?

The Scenario Manager allows you to run multiple attack scenarios in a batch, compare results, and generate comprehensive reports. It's perfect for:

- Comparing baseline vs attack scenarios
- Testing different attack strategies
- Generating research data for publications
- Evaluating attack detection mechanisms

## Quick Start

### 1. Run a Batch Simulation

```bash
cd EmuOCPP
python attack_simulator.py --batch attack_simulation/config/batch_config.yaml
```

### 2. View Results

Results are saved to the output directory specified in your batch configuration (default: `./results/batch_001/`):

```
results/batch_001/
├── session_baseline_*/          # Baseline scenario results
├── session_aggressive_*/         # Attack scenario results
└── comparison/                   # Cross-scenario comparison
    ├── consolidated_report.txt   # Main comparison report
    ├── comparative_statistics.csv
    └── plots/                    # Comparison visualizations
```

### 3. Read the Comparison Report

Open `comparison/consolidated_report.txt` to see:
- Summary of all scenarios
- Degradation comparison
- Acceleration factors
- Statistical analysis

## Example Batch Configuration

Create a file `my_batch.yaml`:

```yaml
batch_config:
  name: "My Attack Study"
  output_dir: "./my_results"
  
  scenarios:
    # Baseline (no attack)
    - name: "baseline"
      attack_enabled: false
      cycles: 100
      
    # Aggressive attack
    - name: "aggressive"
      attack_enabled: true
      strategy: "aggressive"
      cycles: 100
      manipulations:
        voltage:
          enabled: true
          deviation_percent: 20

battery_model:
  initial_capacity_ah: 75.0
  reset_between_scenarios: true

output:
  generate_comparison_report: true
  generate_plots: true

execution:
  continue_on_error: true
```

Run it:

```bash
python attack_simulator.py --batch my_batch.yaml
```

## Understanding the Output

### Consolidated Report

The consolidated report shows:

```
SCENARIO SUMMARY
Scenario                  Cycles     Final SoH (%)   Total Deg (%)   Rate/Cycle
--------------------------------------------------------------------------------
baseline                  100        99.90           0.1000          0.001000
aggressive                100        99.50           0.5000          0.005000

DEGRADATION COMPARISON
Baseline Scenario: baseline
Baseline Final SoH: 99.90%
Baseline Degradation: 0.1000%

Attack Scenarios vs Baseline:

aggressive:
  Final SoH: 99.50%
  Total Degradation: 0.5000%
  Degradation Difference: 0.4000% (400.0% increase)
  Acceleration Factor: 5.00x
```

This shows that the aggressive attack caused 5x faster degradation than baseline!

### Comparison Plots

Three main plots are generated:

1. **final_soh_comparison.png**: Bar chart of final SoH across scenarios
2. **degradation_rate_comparison.png**: Bar chart of degradation rates
3. **soh_timeline_all_scenarios.png**: Line plot showing SoH over time for all scenarios

### Pairwise Comparisons

For each attack scenario, a detailed comparison with baseline is generated in `comparison/pairwise/`:

- Detailed metrics (JSON and CSV)
- Statistical analysis
- Threshold analysis (cycles to reach 90% and 80% SoH)

## Common Scenarios

### Scenario 1: Compare Attack Strategies

```yaml
scenarios:
  - name: "baseline"
    attack_enabled: false
    cycles: 1000
    
  - name: "aggressive"
    attack_enabled: true
    strategy: "aggressive"
    cycles: 1000
    
  - name: "subtle"
    attack_enabled: true
    strategy: "subtle"
    cycles: 1000
    
  - name: "random"
    attack_enabled: true
    strategy: "random"
    cycles: 1000
```

### Scenario 2: Test Different Manipulation Types

```yaml
scenarios:
  - name: "baseline"
    attack_enabled: false
    cycles: 1000
    
  - name: "voltage_only"
    attack_enabled: true
    manipulations:
      voltage: {enabled: true, deviation_percent: 15}
      current: {enabled: false}
      
  - name: "current_only"
    attack_enabled: true
    manipulations:
      voltage: {enabled: false}
      current: {enabled: true, deviation_percent: 25}
      
  - name: "combined"
    attack_enabled: true
    manipulations:
      voltage: {enabled: true, deviation_percent: 15}
      current: {enabled: true, deviation_percent: 25}
```

### Scenario 3: Test Deviation Levels

```yaml
scenarios:
  - name: "baseline"
    attack_enabled: false
    cycles: 1000
    
  - name: "low_deviation"
    attack_enabled: true
    manipulations:
      voltage: {enabled: true, deviation_percent: 5}
      
  - name: "medium_deviation"
    attack_enabled: true
    manipulations:
      voltage: {enabled: true, deviation_percent: 15}
      
  - name: "high_deviation"
    attack_enabled: true
    manipulations:
      voltage: {enabled: true, deviation_percent: 30}
```

## Tips and Tricks

### 1. Start Small

For initial testing, use fewer cycles:

```yaml
cycles: 10  # Quick test
```

Then scale up for production:

```yaml
cycles: 1000  # Full simulation
```

### 2. Disable Plots for Speed

If you just need the data:

```yaml
output:
  generate_plots: false
```

### 3. Continue on Error

To ensure batch completes even if one scenario fails:

```yaml
execution:
  continue_on_error: true
```

### 4. Custom Output Directory

Organize your results:

```yaml
batch_config:
  output_dir: "./results/experiment_001"
```

### 5. Debug Mode

For troubleshooting:

```bash
python attack_simulator.py --batch my_batch.yaml --log-level DEBUG
```

## Demo Script

Try the demo to see it in action:

```bash
python attack_simulation/examples/demo_scenario_manager.py
```

## Next Steps

1. **Customize Scenarios**: Edit `attack_simulation/config/batch_config.yaml`
2. **Run Experiments**: Execute batch simulations
3. **Analyze Results**: Review comparison reports and plots
4. **Iterate**: Refine scenarios based on results

## Need Help?

- Read the full documentation: `SCENARIO_MANAGER_IMPLEMENTATION.md`
- Check the design document: `.kiro/specs/charging-profile-poisoning-attack/design.md`
- Run tests: `python -m pytest tests/test_scenario_manager.py -v`
- View examples: `attack_simulation/examples/demo_scenario_manager.py`

## Common Issues

**Q: Batch execution is slow**
A: Reduce the number of cycles or scenarios for testing

**Q: No comparison report generated**
A: Ensure you have at least one baseline scenario (`attack_enabled: false`)

**Q: Plots not generated**
A: Check that matplotlib is installed and `generate_plots: true`

**Q: Out of memory**
A: Reduce batch size or number of cycles

## Example Output

After running a batch, you'll see:

```
================================================================================
BATCH EXECUTION: Profile Poisoning Comparative Study
Total scenarios: 6
Output directory: ./results/batch_001
================================================================================

================================================================================
SCENARIO 1/6: baseline
================================================================================

Running scenario: baseline
...
✓ Scenario 'baseline' completed successfully

================================================================================
SCENARIO 2/6: aggressive_voltage
================================================================================

Running scenario: aggressive_voltage
...
✓ Scenario 'aggressive_voltage' completed successfully

...

================================================================================
BATCH EXECUTION COMPLETED
Successful scenarios: 6/6
================================================================================

BATCH SUMMARY
================================================================================

Scenario                  Cycles     Final SoH    Degradation     Rate/Cycle
--------------------------------------------------------------------------------
baseline                  1000       99.00        1.0000          0.001000
aggressive_voltage        1000       95.00        5.0000          0.005000
...

================================================================================
GENERATING CROSS-SCENARIO COMPARISON REPORT
================================================================================

Comparison report generated: ./results/batch_001/comparison
```

Happy experimenting! 🚀
