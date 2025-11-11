# Validation Scenarios

This directory contains validation scripts for the Charging Profile Poisoning Attack simulation system. These scripts run comprehensive validation scenarios to verify system functionality and generate research publication materials.

## Overview

The validation suite consists of three main scenarios:

1. **Baseline Scenario** - Normal charging without attacks (establishes reference degradation)
2. **Aggressive Attack Scenario** - Maximum parameter manipulation (demonstrates attack impact)
3. **Subtle Attack Scenario** - Minimal parameter deviations (tests detection evasion)

## Quick Start

### Run Full Validation Suite

Run all scenarios in sequence and generate publication materials:

```bash
cd EmuOCPP
python attack_simulation/examples/run_full_validation.py --cycles 1000
```

This will:
- Run baseline scenario (1000 cycles)
- Run aggressive attack scenario (1000 cycles)
- Run subtle attack scenario (1000 cycles)
- Generate all publication materials (plots, tables, summaries)

Results will be saved to `./output/validation/`

### Run Individual Scenarios

#### Baseline Scenario

```bash
python attack_simulation/examples/validation_baseline.py --cycles 1000
```

**Purpose**: Establish normal degradation rate without attacks

**Validation Checks**:
- Degradation rate within expected range (0.001% ± 0.0005% per cycle)
- Final SoH reasonable (> 99% after 1000 cycles)
- No manipulation events

**Expected Results**:
- Total degradation: ~1.0%
- Final SoH: ~99.0%
- Degradation rate: ~0.001% per cycle

#### Aggressive Attack Scenario

```bash
python attack_simulation/examples/validation_aggressive.py \
    --cycles 1000 \
    --baseline ./output/validation/baseline
```

**Purpose**: Demonstrate maximum attack impact with high parameter deviations

**Attack Configuration**:
- Voltage manipulation: +20%
- Current manipulation: +30%
- Charging curve: Flattened

**Validation Checks**:
- Significant degradation (> 2x baseline)
- Manipulation events recorded
- Parameter deviations match configuration
- Acceleration factor ≥ 2.0x

**Expected Results**:
- Total degradation: ~2-4%
- Acceleration factor: 2-4x baseline
- High detectability

#### Subtle Attack Scenario

```bash
python attack_simulation/examples/validation_subtle.py \
    --cycles 1000 \
    --baseline ./output/validation/baseline
```

**Purpose**: Test stealthy attack with minimal deviations to evade detection

**Attack Configuration**:
- Voltage manipulation: +5% (minimal)
- Current manipulation: +8% (minimal)
- Charging curve: Disabled (too obvious)

**Validation Checks**:
- Moderate degradation (1.3-3x baseline)
- Minimal parameter deviations (< 10% voltage, < 15% current)
- Low detection rate (< 50%)
- Moderate acceleration factor (1.3-2.5x)

**Expected Results**:
- Total degradation: ~1.3-2.5%
- Acceleration factor: 1.3-2.5x baseline
- Low detectability (< 50% detection rate)

## Generate Publication Materials

After running all scenarios, generate publication-ready materials:

```bash
python attack_simulation/examples/generate_publication_materials.py \
    --baseline ./output/validation/baseline/session_* \
    --aggressive ./output/validation/aggressive/session_* \
    --subtle ./output/validation/subtle/session_* \
    --output ./output/publication
```

**Generated Materials**:

1. **LaTeX Tables**:
   - `tables/degradation_comparison.tex` - Comparison of all scenarios
   - `tables/detection_performance.tex` - Detection performance metrics

2. **Plots**:
   - SoH timeline plots for each scenario
   - Stress factor breakdowns
   - Parameter deviation histograms

3. **Documents**:
   - `RESULTS_SUMMARY.txt` - Comprehensive results summary
   - `PUBLICATION_CHECKLIST.txt` - Checklist of materials

## Output Structure

```
output/validation/
├── baseline/
│   └── session_baseline_YYYYMMDD_HHMMSS/
│       ├── summary.json
│       ├── charging_cycles.csv
│       ├── degradation_timeline.csv
│       └── plots/
│           ├── soh_timeline.png
│           └── stress_factors.png
├── aggressive/
│   └── session_aggressive_YYYYMMDD_HHMMSS/
│       ├── summary.json
│       ├── manipulations.csv
│       ├── charging_cycles.csv
│       ├── degradation_timeline.csv
│       └── plots/
│           ├── soh_timeline.png
│           ├── stress_factors.png
│           └── parameter_deviations.png
├── subtle/
│   └── session_subtle_YYYYMMDD_HHMMSS/
│       ├── summary.json
│       ├── manipulations.csv
│       ├── charging_cycles.csv
│       ├── degradation_timeline.csv
│       └── plots/
│           ├── soh_timeline.png
│           ├── stress_factors.png
│           └── parameter_deviations.png
└── publication/
    ├── RESULTS_SUMMARY.txt
    ├── PUBLICATION_CHECKLIST.txt
    ├── tables/
    │   ├── degradation_comparison.tex
    │   └── detection_performance.tex
    └── plots/
        ├── baseline_soh_timeline.png
        ├── aggressive_soh_timeline.png
        ├── subtle_soh_timeline.png
        └── ...
```

## Command-Line Options

### Common Options

All validation scripts support these options:

- `--cycles N` - Number of charging cycles to simulate (default: 1000)
- `--output DIR` - Output directory for results
- `--baseline DIR` - Path to baseline results for comparison

### Subtle Attack Options

- `--no-detection` - Disable anomaly detection testing

## Validation Criteria

### Baseline Scenario

| Metric | Expected Value | Tolerance |
|--------|---------------|-----------|
| Degradation Rate | 0.001% per cycle | ± 0.0005% |
| Final SoH (1000 cycles) | 99.0% | ± 1.0% |
| Manipulation Events | 0 | Exact |

### Aggressive Attack Scenario

| Metric | Expected Value | Criteria |
|--------|---------------|----------|
| Total Degradation | > 2% | > 2x baseline |
| Voltage Deviation | 20% | ± 5% |
| Current Deviation | 30% | ± 5% |
| Acceleration Factor | ≥ 2.0x | Compared to baseline |

### Subtle Attack Scenario

| Metric | Expected Value | Criteria |
|--------|---------------|----------|
| Total Degradation | 1.3-3% | 1.3-3x baseline |
| Voltage Deviation | < 10% | Minimal |
| Current Deviation | < 15% | Minimal |
| Detection Rate | < 50% | Low detectability |
| Acceleration Factor | 1.3-2.5x | Moderate |

## Troubleshooting

### Validation Failures

If a validation fails, check:

1. **Degradation Rate Issues**:
   - Verify battery model parameters in configuration
   - Check that stress factor calculations are correct
   - Review degradation timeline CSV for anomalies

2. **Manipulation Issues**:
   - Verify attack engine configuration
   - Check manipulation events CSV
   - Ensure attack is enabled in configuration

3. **Detection Issues**:
   - Verify detection thresholds in configuration
   - Check that detector is properly initialized
   - Review detection logs

### Performance Issues

For faster validation (testing purposes):

```bash
# Run with fewer cycles
python attack_simulation/examples/run_full_validation.py --cycles 100
```

**Note**: Fewer cycles will produce less statistically significant results.

## Research Use

These validation scenarios are designed for research purposes:

1. **Reproducibility**: All scenarios use fixed parameters and random seeds
2. **Comparability**: Baseline provides reference for all attack scenarios
3. **Publication-Ready**: Generated materials are formatted for academic papers

### Citation

If you use these validation scenarios in research, please cite:

```
[Citation information to be added]
```

## Ethical Considerations

⚠️ **IMPORTANT**: These validation scenarios are for research and educational purposes only.

- Do NOT use on production systems
- Do NOT use on real charging infrastructure
- Do NOT use for malicious purposes
- Follow responsible disclosure practices

## Requirements

- Python 3.8+
- EmuOCPP framework installed
- Required packages: pandas, matplotlib, numpy, pyyaml

## Support

For issues or questions:

1. Check the main [TROUBLESHOOTING_GUIDE.md](../TROUBLESHOOTING_GUIDE.md)
2. Review [USAGE_GUIDE.md](../USAGE_GUIDE.md)
3. Open an issue on the project repository

## License

[License information to be added]
