# Validation Quickstart Guide

This guide provides quick instructions for running the complete validation suite for the Charging Profile Poisoning Attack simulation system.

## Prerequisites

- Python 3.8 or higher
- EmuOCPP framework installed
- All dependencies installed (`pip install -r requirements.txt`)

## Quick Validation (Recommended)

Run the complete validation suite with a single command:

```bash
cd EmuOCPP
python attack_simulation/examples/run_full_validation.py --cycles 1000
```

This will:
1. ✓ Run baseline scenario (1000 cycles, ~5-10 minutes)
2. ✓ Run aggressive attack scenario (1000 cycles, ~5-10 minutes)
3. ✓ Run subtle attack scenario with detection (1000 cycles, ~5-10 minutes)
4. ✓ Generate all publication materials (plots, tables, summaries)

**Total time**: ~15-30 minutes

**Output location**: `./output/validation/`

## Individual Scenarios

### 1. Baseline Scenario

Establish normal degradation rate without attacks:

```bash
python attack_simulation/examples/validation_baseline.py --cycles 1000
```

**Expected output**:
- Final SoH: ~99.0%
- Degradation rate: ~0.001% per cycle
- Validation: PASSED ✓

### 2. Aggressive Attack Scenario

Test maximum attack impact:

```bash
python attack_simulation/examples/validation_aggressive.py \
    --cycles 1000 \
    --baseline ./output/validation/baseline
```

**Expected output**:
- Final SoH: ~96-98%
- Acceleration factor: 2-4x baseline
- Validation: PASSED ✓

### 3. Subtle Attack Scenario

Test stealthy attack with detection evasion:

```bash
python attack_simulation/examples/validation_subtle.py \
    --cycles 1000 \
    --baseline ./output/validation/baseline
```

**Expected output**:
- Final SoH: ~97-99%
- Acceleration factor: 1.3-2.5x baseline
- Detection rate: < 50%
- Validation: PASSED ✓

## Generate Publication Materials

After running all scenarios:

```bash
python attack_simulation/examples/generate_publication_materials.py \
    --baseline ./output/validation/baseline/session_* \
    --aggressive ./output/validation/aggressive/session_* \
    --subtle ./output/validation/subtle/session_* \
    --output ./output/publication
```

**Generated materials**:
- LaTeX tables for papers
- Publication-quality plots
- Comprehensive results summary
- Publication checklist

## Fast Validation (Testing)

For quick testing with fewer cycles:

```bash
python attack_simulation/examples/run_full_validation.py --cycles 100
```

**Note**: Results will be less statistically significant but useful for testing.

## Validation Results

### Success Criteria

All scenarios should pass these validation checks:

**Baseline**:
- ✓ Degradation rate: 0.001% ± 0.0005% per cycle
- ✓ Final SoH: ≥ 98% after 1000 cycles
- ✓ No manipulation events

**Aggressive Attack**:
- ✓ Total degradation > 2x baseline
- ✓ Manipulation events recorded
- ✓ Parameter deviations match config (±5%)
- ✓ Acceleration factor ≥ 2.0x

**Subtle Attack**:
- ✓ Moderate degradation (1.3-3x baseline)
- ✓ Minimal deviations (< 10% voltage, < 15% current)
- ✓ Low detection rate (< 50%)
- ✓ Acceleration factor: 1.3-2.5x

### Output Structure

```
output/validation/
├── baseline/
│   └── session_baseline_*/
│       ├── summary.json
│       ├── charging_cycles.csv
│       ├── degradation_timeline.csv
│       └── plots/
├── aggressive/
│   └── session_aggressive_*/
│       ├── summary.json
│       ├── manipulations.csv
│       └── plots/
├── subtle/
│   └── session_subtle_*/
│       ├── summary.json
│       ├── manipulations.csv
│       └── plots/
└── publication/
    ├── RESULTS_SUMMARY.txt
    ├── PUBLICATION_CHECKLIST.txt
    ├── tables/
    │   ├── degradation_comparison.tex
    │   └── detection_performance.tex
    └── plots/
```

## Troubleshooting

### Validation Fails

If a validation fails:

1. Check the log output for specific failure reasons
2. Review the generated CSV files for anomalies
3. Verify battery model parameters are correct
4. Ensure attack configuration matches expected values

### Import Errors

If you get import errors:

```bash
# Ensure you're in the EmuOCPP directory
cd EmuOCPP

# Verify Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run with explicit path
python -m attack_simulation.examples.run_full_validation
```

### Performance Issues

If validation is too slow:

- Reduce cycles: `--cycles 100` (for testing)
- Run scenarios individually instead of full suite
- Check system resources (CPU, memory)

## Next Steps

After successful validation:

1. **Review Results**: Check `output/validation/publication/RESULTS_SUMMARY.txt`
2. **Examine Plots**: Review all generated plots in `plots/` directories
3. **Use LaTeX Tables**: Copy tables from `tables/` to your paper
4. **Customize**: Modify validation scripts for your specific research needs

## Documentation

For more details:

- [Validation Scenarios README](attack_simulation/examples/VALIDATION_SCENARIOS_README.md)
- [Usage Guide](attack_simulation/USAGE_GUIDE.md)
- [Troubleshooting Guide](attack_simulation/TROUBLESHOOTING_GUIDE.md)

## Support

For issues:
1. Check existing documentation
2. Review log files in `./logs/`
3. Open an issue on the project repository

## Ethical Notice

⚠️ **IMPORTANT**: These validation scenarios are for research and educational purposes only.

- Do NOT use on production systems
- Do NOT use on real charging infrastructure
- Follow responsible disclosure practices
- Respect ethical research guidelines

---

**Quick Command Reference**:

```bash
# Full validation suite
python attack_simulation/examples/run_full_validation.py --cycles 1000

# Individual scenarios
python attack_simulation/examples/validation_baseline.py --cycles 1000
python attack_simulation/examples/validation_aggressive.py --cycles 1000 --baseline ./output/validation/baseline
python attack_simulation/examples/validation_subtle.py --cycles 1000 --baseline ./output/validation/baseline

# Generate publication materials
python attack_simulation/examples/generate_publication_materials.py \
    --baseline ./output/validation/baseline/session_* \
    --aggressive ./output/validation/aggressive/session_* \
    --subtle ./output/validation/subtle/session_* \
    --output ./output/publication
```
