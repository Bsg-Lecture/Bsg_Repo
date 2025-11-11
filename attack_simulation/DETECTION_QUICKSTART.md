# Attack Detection Simulation - Quick Start Guide

## Overview

The Attack Detection Simulation framework provides anomaly detection for OCPP charging profile manipulation attacks with comprehensive performance evaluation tools.

## Quick Start

### 1. Run Basic Detection Demo

```bash
cd EmuOCPP
python attack_simulation/examples/demo_anomaly_detection.py
```

This demonstrates:
- Statistical anomaly detection
- Range-based detection
- Pattern-based detection
- Detection metrics tracking

### 2. Run Performance Evaluation Demo

```bash
cd EmuOCPP
python attack_simulation/examples/demo_detection_performance.py
```

This demonstrates:
- ROC curve generation and AUC calculation
- Confusion matrix visualization
- Threshold analysis
- Comprehensive performance reports

## Basic Usage

### Simple Detection

```python
from attack_simulation.detection import AnomalyDetector, DetectionConfig, DetectionMethod

# Create detector
config = DetectionConfig(
    enabled=True,
    method=DetectionMethod.STATISTICAL,
    current_threshold_percent=15.0
)
detector = AnomalyDetector(config)

# Detect anomalies
profile = {
    'chargingSchedule': {
        'chargingRateUnit': 'A',
        'chargingSchedulePeriod': [
            {'startPeriod': 0, 'limit': 45.0}  # Suspicious value
        ]
    }
}

result = detector.detect_anomaly(profile, message_id="msg_001", is_manipulated=True)
print(f"Anomalous: {result.is_anomalous}, Confidence: {result.confidence_score:.2f}")
```

### Performance Evaluation

```python
from attack_simulation.detection import DetectionPerformanceEvaluator

# Create evaluator
evaluator = DetectionPerformanceEvaluator(output_dir="./output")

# Collect predictions: (confidence_score, is_actually_anomalous)
predictions = [(0.8, True), (0.3, False), (0.9, True), ...]

# Calculate ROC and AUC
roc_points, auc = evaluator.calculate_roc_curve(predictions)
print(f"AUC: {auc:.4f}")

# Generate visualizations
evaluator.plot_roc_curve(roc_points, auc, "./output/roc_curve.png")
```

## Configuration

### Load from YAML

```python
config = DetectionConfig.from_yaml("attack_simulation/config/detection_config.yaml")
```

### Key Parameters

- `current_threshold_percent`: Deviation threshold for detection (default: 15%)
- `baseline_current_mean`: Expected normal current (default: 30.0 A)
- `baseline_current_std`: Standard deviation of normal current (default: 5.0 A)

## Detection Methods

1. **Statistical**: Uses z-scores and baseline statistics
2. **Range-Based**: Checks absolute parameter limits
3. **Pattern-Based**: Analyzes charging curve irregularities

## Performance Metrics

- **AUC**: Area Under ROC Curve (0.5 = random, 1.0 = perfect)
- **Accuracy**: Overall correctness
- **Precision**: How many detections are correct
- **Recall**: How many attacks are detected
- **F1 Score**: Balance of precision and recall

## Output Files

Results are saved to:

```
output/session_<id>/
├── detection_events.csv       # All detection events
├── plots/
│   ├── roc_curve.png
│   ├── confusion_matrix.png
│   └── threshold_analysis.png
```

## Next Steps

- See `DETECTION_FRAMEWORK_IMPLEMENTATION.md` for detailed documentation
- Tune detection thresholds using ROC analysis
- Integrate with attack simulation scenarios
- Evaluate different detection methods

## Requirements

- Python 3.7+
- numpy
- matplotlib
- PyYAML

```bash
pip install numpy matplotlib pyyaml
```
