# Visualization Engine Implementation

## Overview

The Visualization Engine generates publication-quality plots and reports from attack simulation data. It provides comprehensive visualization capabilities for analyzing battery degradation patterns, attack parameter deviations, and stress factor contributions.

## Features

### 1. Publication-Quality Plots

The engine generates high-resolution plots in both PNG (300 DPI) and PDF formats suitable for academic publications:

- **SoH Timeline Plot**: Shows battery State of Health degradation over charging cycles
- **Baseline Comparison Plot**: Compares baseline vs. attack degradation curves
- **Parameter Deviation Histograms**: Displays distribution of voltage and current manipulations
- **Stress Factor Contributions**: Visualizes relative impact of different stress factors

### 2. Report Generation

- **LaTeX Tables**: Formatted summary statistics for academic papers
- **HTML Reports**: Interactive reports with embedded plots and statistics

### 3. Matplotlib Configuration

The engine is pre-configured with publication-quality settings:
- 300 DPI resolution
- Serif fonts for professional appearance
- Optimized color schemes
- Grid and layout settings for clarity

## Usage

### Basic Usage

```python
from attack_simulation.metrics.metrics_collector import MetricsCollector
from attack_simulation.visualization.visualization_engine import VisualizationEngine

# Initialize metrics collector
metrics = MetricsCollector(output_dir="./output", session_id="my_session")

# ... run simulation and collect metrics ...

# Initialize visualization engine
viz_engine = VisualizationEngine(metrics)

# Generate all visualizations
viz_engine.generate_all_visualizations()
```

### Individual Plot Generation

```python
# Generate specific plots
viz_engine.plot_soh_timeline()
viz_engine.plot_parameter_deviations()
viz_engine.plot_stress_factors()

# Generate reports
viz_engine.generate_latex_table()
viz_engine.generate_html_report()
```

### Baseline Comparison

```python
import pandas as pd

# Load baseline and attack data
baseline_data = pd.read_csv('baseline_session/degradation_timeline.csv')
attack_data = pd.read_csv('attack_session/degradation_timeline.csv')

# Generate comparison plot
viz_engine.plot_baseline_comparison(baseline_data, attack_data)
```

## Output Files

The visualization engine generates the following files in the `plots/` subdirectory:

### Plot Files
- `soh_timeline.png` / `soh_timeline.pdf` - SoH degradation timeline
- `parameter_deviations.png` / `parameter_deviations.pdf` - Parameter deviation histograms
- `stress_factors.png` / `stress_factors.pdf` - Stress factor contributions
- `baseline_comparison.png` / `baseline_comparison.pdf` - Baseline vs. attack comparison

### Report Files
- `summary_table.tex` - LaTeX-formatted summary table
- `report.html` - Interactive HTML report (saved in session root directory)

## Plot Specifications

### SoH Timeline Plot

**Features:**
- Line plot with markers showing SoH degradation over cycles
- Confidence intervals (rolling standard deviation)
- Annotations for significant degradation events (drops > 0.5%)
- Reference lines at 90% and 80% SoH thresholds
- Automatic y-axis scaling with padding

**Use Cases:**
- Tracking battery health over time
- Identifying sudden degradation events
- Comparing degradation rates

### Baseline Comparison Plot

**Features:**
- Dual-line plot (baseline vs. attack)
- Shaded area showing degradation difference
- Statistical significance indicators
- Summary statistics text box
- Reference threshold lines

**Use Cases:**
- Demonstrating attack impact
- Quantifying degradation acceleration
- Research publication figures

### Parameter Deviation Histograms

**Features:**
- Separate subplots for voltage and current deviations
- Mean and standard deviation annotations
- Statistical summary boxes
- Distribution visualization

**Use Cases:**
- Analyzing attack patterns
- Understanding manipulation strategies
- Detecting anomalies

### Stress Factor Contributions

**Features:**
- Stacked area chart showing voltage, current, and SoC stress
- Combined stress factor line overlay
- Average contribution statistics
- Proportional impact visualization

**Use Cases:**
- Understanding degradation causes
- Identifying dominant stress factors
- Optimizing attack strategies

## HTML Report

The HTML report provides an interactive overview of the simulation:

**Sections:**
- Summary statistics cards
- Attack detection alerts
- Embedded plot images
- Detailed metrics table
- Professional styling with gradients and shadows

**Features:**
- Responsive design
- Color-coded statistics
- Visual hierarchy
- Print-friendly layout

## LaTeX Table

The LaTeX table is formatted for direct inclusion in academic papers:

```latex
\begin{table}[htbp]
\centering
\caption{Attack Simulation Summary Statistics}
\label{tab:attack_simulation_summary}
\begin{tabular}{|l|r|}
\hline
\textbf{Metric} & \textbf{Value} \\
\hline
...
\end{tabular}
\end{table}
```

## Demo Script

Run the demo to see all visualization features:

```bash
python attack_simulation/examples/demo_visualization.py
```

The demo creates:
1. Sample simulation data with 100 charging cycles
2. All visualization plots
3. LaTeX table and HTML report
4. Baseline vs. attack comparison

## Dependencies

- `matplotlib` - Plotting library
- `numpy` - Numerical operations
- `pandas` - Data manipulation
- `pathlib` - File path handling

## Configuration

### Matplotlib Settings

The engine configures matplotlib with these defaults:

```python
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'serif'
```

These can be customized by modifying the `_configure_matplotlib()` method.

### Custom Output Paths

All plot methods accept an optional `output_path` parameter:

```python
viz_engine.plot_soh_timeline(output_path='custom/path/soh_plot.png')
```

## Integration with Comparison Analyzer

The visualization engine works seamlessly with the ComparisonAnalyzer:

```python
from attack_simulation.metrics.comparison_analyzer import ComparisonAnalyzer

# Create analyzer
analyzer = ComparisonAnalyzer(
    baseline_session_dir='./output/baseline',
    attack_session_dir='./output/attack'
)

# Load data
analyzer.load_simulation_data()

# Generate comparison plot using visualization engine
viz_engine.plot_baseline_comparison(
    analyzer.baseline_degradation_data,
    analyzer.attack_degradation_data
)
```

## Best Practices

1. **Always export metrics to CSV before visualization**
   ```python
   metrics.export_to_csv()
   ```

2. **Generate summary report before creating visualizations**
   ```python
   summary = metrics.generate_summary_report()
   ```

3. **Use `generate_all_visualizations()` for complete output**
   ```python
   viz_engine.generate_all_visualizations()
   ```

4. **Check for data availability before plotting**
   - The engine handles missing data gracefully with warnings

5. **Save plots in both PNG and PDF formats**
   - PNG for presentations and web
   - PDF for publications and vector graphics

## Troubleshooting

### Issue: Plots not generating

**Solution:** Ensure metrics have been exported to CSV:
```python
metrics.export_to_csv()
```

### Issue: Missing data warnings

**Solution:** Check that simulation has logged data:
```python
# Verify data exists
print(f"Cycles: {len(metrics.charging_cycles)}")
print(f"Degradation events: {len(metrics.degradation_events)}")
```

### Issue: Font rendering issues

**Solution:** Matplotlib may need font cache rebuild:
```python
import matplotlib.font_manager
matplotlib.font_manager._rebuild()
```

## Future Enhancements

Potential improvements for future versions:

1. **Interactive Plots**: Plotly integration for web-based interactivity
2. **Animation**: Time-lapse animations of degradation
3. **3D Visualizations**: Multi-parameter stress factor surfaces
4. **Custom Themes**: User-configurable color schemes and styles
5. **Batch Comparison**: Multi-scenario comparison plots
6. **Statistical Analysis**: Confidence intervals and hypothesis testing
7. **Export Formats**: SVG, EPS for additional publication formats

## References

- Matplotlib Documentation: https://matplotlib.org/
- Publication Quality Plots: https://matplotlib.org/stable/tutorials/introductory/customizing.html
- LaTeX Integration: https://matplotlib.org/stable/tutorials/text/usetex.html
