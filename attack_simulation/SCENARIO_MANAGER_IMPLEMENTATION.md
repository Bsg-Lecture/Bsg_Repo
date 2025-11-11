# Scenario Manager Implementation

## Overview

The Scenario Manager is a component that orchestrates multi-scenario batch experiments for the Charging Profile Poisoning Attack simulation. It enables researchers to run multiple attack scenarios sequentially, compare results, and generate comprehensive reports.

## Features

### 1. Scenario Management Infrastructure
- **ScenarioConfig**: Dataclass for individual scenario configuration
- **BatchConfig**: Dataclass for batch execution configuration
- **Configuration Loading**: YAML-based configuration parsing
- **Scenario Queue**: Manages execution order of scenarios

### 2. Scenario Execution
- **Single Scenario Execution**: Run individual attack scenarios
- **Battery Model Reset**: Reset battery state between scenarios
- **Progress Tracking**: Real-time logging of simulation progress
- **Error Handling**: Graceful failure handling with continue-on-error option

### 3. Batch Execution
- **Sequential Execution**: Run multiple scenarios in order
- **Result Collection**: Aggregate results from all scenarios
- **Batch Summary**: Display summary table of all scenario results

### 4. Cross-Scenario Comparison
- **Consolidated Report**: Generate comprehensive comparison report
- **Pairwise Comparisons**: Compare baseline vs each attack scenario
- **Comparison Plots**: Visualize degradation across scenarios
- **Comparative Statistics**: Export statistics in CSV and JSON formats

## Architecture

```
ScenarioManager
├── load_batch_config()          # Load YAML configuration
├── run_batch()                  # Execute all scenarios
├── run_scenario()               # Execute single scenario
└── generate_comparison_report() # Generate cross-scenario comparison
    ├── _generate_consolidated_report()
    ├── _generate_pairwise_comparisons()
    ├── _generate_comparison_plots()
    └── _export_comparative_statistics()
```

## Configuration Format

### Batch Configuration (batch_config.yaml)

```yaml
batch_config:
  name: "Profile Poisoning Comparative Study"
  output_dir: "./results/batch_001"
  
  scenarios:
    - name: "baseline"
      attack_enabled: false
      cycles: 1000
      description: "Normal charging without manipulation"
      
    - name: "aggressive_voltage"
      attack_enabled: true
      strategy: "aggressive"
      cycles: 1000
      description: "Maximum voltage overstress attack"
      manipulations:
        voltage:
          enabled: true
          deviation_percent: 20
        current:
          enabled: false
        charging_curve:
          enabled: false

battery_model:
  initial_capacity_ah: 75.0
  reset_between_scenarios: true

output:
  generate_comparison_report: true
  generate_plots: true
  export_format: ["csv", "json"]

execution:
  parallel: false
  continue_on_error: true
```

## Usage

### Basic Usage

```python
import asyncio
from attack_simulation.core.scenario_manager import ScenarioManager

async def main():
    # Initialize manager with batch configuration
    manager = ScenarioManager('config/batch_config.yaml')
    
    # Run all scenarios
    results = await manager.run_batch()
    
    # Generate comparison report
    manager.generate_comparison_report(results)

asyncio.run(main())
```

### Command-Line Usage

```bash
# Run batch simulation
python attack_simulator.py --batch config/batch_config.yaml

# With custom output directory
python attack_simulator.py --batch config/batch_config.yaml --output-dir ./my_results

# With debug logging
python attack_simulator.py --batch config/batch_config.yaml --log-level DEBUG
```

## Output Structure

```
results/batch_001/
├── session_baseline_20240101_120000/
│   ├── config.json
│   ├── manipulations.csv
│   ├── charging_cycles.csv
│   ├── degradation_timeline.csv
│   ├── summary.json
│   └── plots/
│       └── soh_timeline.png
├── session_aggressive_voltage_20240101_120500/
│   ├── config.json
│   ├── manipulations.csv
│   ├── charging_cycles.csv
│   ├── degradation_timeline.csv
│   ├── summary.json
│   └── plots/
│       └── soh_timeline.png
└── comparison/
    ├── consolidated_report.txt
    ├── comparative_statistics.csv
    ├── comparative_statistics.json
    ├── plots/
    │   ├── final_soh_comparison.png
    │   ├── degradation_rate_comparison.png
    │   └── soh_timeline_all_scenarios.png
    └── pairwise/
        └── baseline_vs_aggressive_voltage/
            ├── comparison_report.txt
            ├── comparison_metrics.json
            └── comparison_metrics.csv
```

## API Reference

### ScenarioConfig

```python
@dataclass
class ScenarioConfig:
    """Configuration for a single attack scenario"""
    name: str
    attack_enabled: bool = True
    strategy: str = "aggressive"
    cycles: int = 1000
    description: str = ""
    manipulations: Dict[str, Any] = field(default_factory=dict)
    randomization: Dict[str, Any] = field(default_factory=dict)
    
    def to_attack_config(self) -> AttackConfig:
        """Convert scenario config to AttackConfig"""
```

### BatchConfig

```python
@dataclass
class BatchConfig:
    """Configuration for batch execution"""
    name: str
    output_dir: str
    scenarios: List[ScenarioConfig]
    battery_model: Dict[str, Any] = field(default_factory=dict)
    proxy: Dict[str, Any] = field(default_factory=dict)
    output: Dict[str, Any] = field(default_factory=dict)
    execution: Dict[str, Any] = field(default_factory=dict)
```

### ScenarioManager

```python
class ScenarioManager:
    """Manages execution of multiple attack scenarios"""
    
    def __init__(self, batch_config_path: str):
        """Initialize with batch configuration file"""
    
    def load_batch_config(self) -> None:
        """Load batch configuration from YAML file"""
    
    async def run_batch(self) -> List[SimulationSummary]:
        """Execute all scenarios in batch configuration"""
    
    async def run_scenario(self, scenario: ScenarioConfig) -> SimulationSummary:
        """Execute single scenario"""
    
    def generate_comparison_report(self, results: List[SimulationSummary]) -> None:
        """Generate cross-scenario comparison report"""
```

## Examples

### Example 1: Simple Batch Execution

```python
import asyncio
from attack_simulation.core.scenario_manager import ScenarioManager

async def run_simple_batch():
    manager = ScenarioManager('config/batch_config.yaml')
    results = await manager.run_batch()
    manager.generate_comparison_report(results)
    print(f"Completed {len(results)} scenarios")

asyncio.run(run_simple_batch())
```

### Example 2: Custom Scenario Configuration

```python
from attack_simulation.core.scenario_manager import ScenarioConfig

# Create custom scenario
scenario = ScenarioConfig(
    name="custom_attack",
    attack_enabled=True,
    strategy="subtle",
    cycles=500,
    description="Custom subtle attack",
    manipulations={
        'voltage': {'enabled': True, 'deviation_percent': 5.0},
        'current': {'enabled': True, 'deviation_percent': 10.0}
    }
)

# Convert to attack config
attack_config = scenario.to_attack_config()
```

### Example 3: Analyzing Results

```python
async def analyze_results():
    manager = ScenarioManager('config/batch_config.yaml')
    results = await manager.run_batch()
    
    # Find baseline and attack scenarios
    baseline = next(r for r in results if 'baseline' in r.session_id)
    attacks = [r for r in results if 'baseline' not in r.session_id]
    
    # Compare degradation
    for attack in attacks:
        scenario_name = attack.session_id.rsplit('_', 2)[0]
        accel_factor = attack.degradation_rate_per_cycle / baseline.degradation_rate_per_cycle
        print(f"{scenario_name}: {accel_factor:.2f}x acceleration")

asyncio.run(analyze_results())
```

## Testing

Run the test suite:

```bash
# Run all scenario manager tests
python -m pytest tests/test_scenario_manager.py -v

# Run specific test
python -m pytest tests/test_scenario_manager.py::TestScenarioManager::test_load_batch_config -v

# Run with coverage
python -m pytest tests/test_scenario_manager.py --cov=attack_simulation.core.scenario_manager
```

## Demo Script

Run the demo script to see the Scenario Manager in action:

```bash
python attack_simulation/examples/demo_scenario_manager.py
```

## Performance Considerations

### Sequential vs Parallel Execution

Currently, only sequential execution is implemented. Parallel execution is planned for future releases.

**Sequential Execution:**
- Pros: Simple, predictable, easier to debug
- Cons: Slower for large batches
- Use case: Small to medium batches (< 10 scenarios)

**Parallel Execution (Future):**
- Pros: Faster for large batches
- Cons: More complex, higher resource usage
- Use case: Large batches (> 10 scenarios)

### Memory Management

- Battery model is reset between scenarios to prevent memory leaks
- Metrics are exported to CSV after each scenario to free memory
- Large batches may require monitoring system resources

### Optimization Tips

1. **Reduce Cycles**: Use fewer cycles for initial testing (e.g., 100 instead of 1000)
2. **Disable Plots**: Set `generate_plots: false` for faster execution
3. **Continue on Error**: Enable `continue_on_error: true` to complete batch despite failures
4. **Batch Size**: Keep batch size reasonable (< 20 scenarios)

## Troubleshooting

### Common Issues

**Issue: "Batch configuration file not found"**
- Solution: Check the path to your batch_config.yaml file
- Ensure the file exists and is readable

**Issue: "No baseline scenario found for comparison"**
- Solution: Ensure at least one scenario has `attack_enabled: false`
- The baseline scenario is required for pairwise comparisons

**Issue: "Failed to generate comparison plots"**
- Solution: Check that matplotlib is installed
- Verify that degradation_timeline.csv files exist for all scenarios
- Set `generate_plots: false` to skip plot generation

**Issue: "Scenario execution failed"**
- Solution: Check the error logs for specific failure reason
- Enable `continue_on_error: true` to continue with remaining scenarios
- Verify battery model parameters are valid

### Debug Mode

Enable debug logging for detailed execution information:

```bash
python attack_simulator.py --batch config/batch_config.yaml --log-level DEBUG
```

## Future Enhancements

1. **Parallel Execution**: Implement parallel scenario execution for faster batch processing
2. **Real-time Monitoring**: Add web dashboard for monitoring batch progress
3. **Scenario Templates**: Provide pre-configured scenario templates
4. **Advanced Comparisons**: Add statistical significance testing
5. **Export Formats**: Support additional export formats (Excel, LaTeX)
6. **Scenario Dependencies**: Allow scenarios to depend on previous results
7. **Checkpoint/Resume**: Enable resuming interrupted batch executions

## References

- Design Document: `.kiro/specs/charging-profile-poisoning-attack/design.md`
- Requirements: `.kiro/specs/charging-profile-poisoning-attack/requirements.md`
- Attack Engine: `attack_simulation/ATTACK_ENGINE_IMPLEMENTATION.md`
- Battery Model: `attack_simulation/BATTERY_MODEL_IMPLEMENTATION.md`
- Metrics Collector: `attack_simulation/METRICS_COLLECTOR_IMPLEMENTATION.md`
- Comparison Analyzer: `attack_simulation/BASELINE_COMPARISON_IMPLEMENTATION.md`

## Contributing

When contributing to the Scenario Manager:

1. Follow the existing code style and patterns
2. Add unit tests for new functionality
3. Update this documentation
4. Test with various batch configurations
5. Ensure backward compatibility with existing configs

## License

This implementation is part of the EmuOCPP project and follows the same license.
