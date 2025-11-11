# Attack Detection Simulation - Implementation Guide

## Overview

The Attack Detection Simulation framework provides statistical anomaly detection capabilities for identifying manipulated OCPP charging profiles. It includes comprehensive performance evaluation tools with ROC curves, AUC calculation, and confusion matrix visualization.

## Components

### 1. Anomaly Detector (`anomaly_detector.py`)

The core detection engine that analyzes charging profiles for anomalies.

**Key Classes:**

- `AnomalyDetector`: Main detection engine
- `DetectionConfig`: Configuration for detection parameters
- `DetectionEvent`: Record of a single detection event
- `DetectionMetrics`: Performance metrics (TP, FP, TN, FN)
- `DetectionResult`: Result of anomaly detection

**Detection Methods:**

1. **Statistical Detection**: Uses baseline statistics and z-scores
2. **Range-Based Detection**: Checks for parameter range violations
3. **Pattern-Based Detection**: Analyzes charging curve irregularities

### 2. Performance Evaluator (`performance_evaluator.py`)

Evaluates detection performance with comprehensive visualizations.

**Key Features:**

- ROC curve generation and AUC calculation
- Precision-Recall curves
- Confusion matrix visualization
- Threshold analysis plots

## Quick Start

### Basic Detection

```python
from attack_simulation.detection import AnomalyDetector, DetectionConfig

# Create configuration
config = DetectionConfig(
    enabled=True,
    method=DetectionMethod.STATISTICAL,
    current_threshold_percent=15.0,
    baseline_current_mean=30.0,
    baseline_current_std=5.0
)

# Initialize detector
detector = AnomalyDetector(config)

# Detect anomalies in a charging profile
profile = {
    'chargingSchedule': {
        'chargingRateUnit': 'A',
        'chargingSchedulePeriod': [
            {'startPeriod': 0, 'limit': 45.0},  # Suspicious high value
            {'startPeriod': 1800, 'limit': 48.0}
        ]
    }
}

result = detector.detect_anomaly(profile, message_id="msg_001", is_manipulated=True)

print(f"Anomalous: {result.is_anomalous}")
print(f"Confidence: {result.confidence_score:.2f}")
print(f"Detected anomalies: {result.anomalous_parameters}")
```

### Performance Evaluation

```python
from attack_simulation.detection import DetectionPerformanceEvaluator

# Create evaluator
evaluator = DetectionPerformanceEvaluator(output_dir="./output")

# Collect predictions: list of (confidence_score, is_actually_anomalous) tuples
predictions = [
    (0.8, True),   # High confidence, actually anomalous
    (0.3, False),  # Low confidence, actually normal
    (0.9, True),   # High confidence, actually anomalous
    (0.1, False),  # Low confidence, actually normal
    # ... more predictions
]

# Calculate ROC curve and AUC
roc_points, auc = evaluator.calculate_roc_curve(predictions)
print(f"AUC: {auc:.4f}")

# Generate ROC curve plot
evaluator.plot_roc_curve(roc_points, auc, "./output/roc_curve.png")

# Generate confusion matrix
metrics = detector.get_detection_metrics()
evaluator.plot_confusion_matrix(
    true_positives=metrics.true_positives,
    false_positives=metrics.false_positives,
    true_negatives=metrics.true_negatives,
    false_negatives=metrics.false_negatives,
    output_path="./output/confusion_matrix.png"
)
```

## Configuration

### Detection Configuration File (`detection_config.yaml`)

```yaml
detection_config:
  enabled: true
  method: "statistical"  # statistical, range_based, pattern_based
  
  # Statistical detection thresholds
  thresholds:
    voltage_percent: 10.0   # % deviation to trigger detection
    current_percent: 15.0
    power_percent: 12.0
  
  # Range-based detection (absolute limits)
  ranges:
    voltage_min: 3.0
    voltage_max: 4.2
    current_min: 0.0
    current_max: 60.0
  
  # Pattern-based detection
  pattern:
    enable_curve_analysis: true
    curve_smoothness_threshold: 0.3
  
  # Baseline parameters (from normal operation)
  baseline:
    voltage_mean: 3.7
    voltage_std: 0.2
    current_mean: 30.0
    current_std: 5.0
    power_mean: 7.0
    power_std: 1.5
```

### Loading Configuration

```python
from attack_simulation.detection import DetectionConfig

# Load from YAML file
config = DetectionConfig.from_yaml("config/detection_config.yaml")

# Or create programmatically
config = DetectionConfig(
    enabled=True,
    method=DetectionMethod.STATISTICAL,
    current_threshold_percent=15.0,
    baseline_current_mean=30.0,
    baseline_current_std=5.0
)
```

## Detection Methods

### 1. Statistical Detection

Uses baseline statistics to detect deviations:

- Calculates z-scores for parameters
- Compares against threshold percentages
- Best for detecting significant deviations

**When to use:** When you have baseline statistics from normal operation

### 2. Range-Based Detection

Checks for absolute parameter violations:

- Detects values outside safe ranges
- Simple and interpretable
- Good for hard limits

**When to use:** When you have known safe operating ranges

### 3. Pattern-Based Detection

Analyzes charging curve patterns:

- Detects irregular charging curves
- Calculates curve smoothness
- Identifies unnatural patterns

**When to use:** When attacks modify charging curve shapes

## Performance Metrics

### Confusion Matrix

|                    | Predicted Normal | Predicted Anomaly |
|--------------------|------------------|-------------------|
| **Actually Normal**    | True Negative    | False Positive    |
| **Actually Anomaly**   | False Negative   | True Positive     |

### Key Metrics

- **Accuracy**: (TP + TN) / Total
- **Precision**: TP / (TP + FP) - How many detected anomalies are real
- **Recall**: TP / (TP + FN) - How many real anomalies are detected
- **F1 Score**: Harmonic mean of precision and recall
- **AUC**: Area Under ROC Curve - Overall detection quality

### Accessing Metrics

```python
metrics = detector.get_detection_metrics()

print(f"Accuracy:  {metrics.get_accuracy():.2%}")
print(f"Precision: {metrics.get_precision():.2%}")
print(f"Recall:    {metrics.get_recall():.2%}")
print(f"F1 Score:  {metrics.get_f1_score():.2%}")
```

## ROC Curve Analysis

The ROC (Receiver Operating Characteristic) curve shows the trade-off between true positive rate and false positive rate at different detection thresholds.

### Interpreting AUC

- **AUC = 1.0**: Perfect detection
- **AUC = 0.9-1.0**: Excellent detection
- **AUC = 0.8-0.9**: Good detection
- **AUC = 0.7-0.8**: Fair detection
- **AUC = 0.5**: Random guessing (no better than chance)

### Finding Optimal Threshold

```python
# Calculate ROC curve
roc_points, auc = evaluator.calculate_roc_curve(predictions)

# Find threshold with best F1 score
best_f1 = 0
optimal_threshold = 0.5

for point in roc_points:
    if point.precision + point.recall > 0:
        f1 = 2 * (point.precision * point.recall) / (point.precision + point.recall)
        if f1 > best_f1:
            best_f1 = f1
            optimal_threshold = point.threshold

print(f"Optimal threshold: {optimal_threshold:.3f}")
print(f"Best F1 score: {best_f1:.3f}")
```

## Integration with Metrics Collector

The detection framework integrates with the metrics collector for logging:

```python
from attack_simulation.metrics.metrics_collector import MetricsCollector
from attack_simulation.detection import AnomalyDetector, DetectionConfig

# Create metrics collector
metrics_collector = MetricsCollector(
    output_dir="./output",
    session_id="detection_session_001"
)

# Create detector with metrics collector
config = DetectionConfig(enabled=True)
detector = AnomalyDetector(config, metrics_collector=metrics_collector)

# Detection events are automatically logged to CSV
result = detector.detect_anomaly(profile, message_id="msg_001", is_manipulated=True)

# Detection events saved to: output/session_detection_session_001/detection_events.csv
```

## Example Use Cases

### 1. Evaluating Attack Detection

```python
# Test detector against known attacks
test_cases = [
    (normal_profile, False),
    (aggressive_attack_profile, True),
    (subtle_attack_profile, True),
]

for profile, is_attack in test_cases:
    result = detector.detect_anomaly(profile, is_manipulated=is_attack)
    print(f"Attack: {is_attack}, Detected: {result.is_anomalous}, "
          f"Confidence: {result.confidence_score:.2f}")
```

### 2. Comparing Detection Methods

```python
methods = [
    DetectionMethod.STATISTICAL,
    DetectionMethod.RANGE_BASED,
    DetectionMethod.PATTERN_BASED
]

for method in methods:
    config = DetectionConfig(enabled=True, method=method)
    detector = AnomalyDetector(config)
    
    # Run detection on test set
    for profile, is_attack in test_profiles:
        detector.detect_anomaly(profile, is_manipulated=is_attack)
    
    metrics = detector.get_detection_metrics()
    print(f"{method.value}: F1={metrics.get_f1_score():.2%}")
```

### 3. Threshold Tuning

```python
# Test different thresholds
thresholds = [5.0, 10.0, 15.0, 20.0, 25.0]

for threshold in thresholds:
    config = DetectionConfig(
        enabled=True,
        current_threshold_percent=threshold
    )
    detector = AnomalyDetector(config)
    
    # Run detection
    for profile, is_attack in test_profiles:
        detector.detect_anomaly(profile, is_manipulated=is_attack)
    
    metrics = detector.get_detection_metrics()
    print(f"Threshold {threshold}%: "
          f"Precision={metrics.get_precision():.2%}, "
          f"Recall={metrics.get_recall():.2%}")
```

## Demo Scripts

### Run Detection Demo

```bash
cd EmuOCPP
python attack_simulation/examples/demo_anomaly_detection.py
```

This demonstrates:
- Statistical detection
- Range-based detection
- Pattern-based detection
- Metrics collection

### Run Performance Evaluation Demo

```bash
cd EmuOCPP
python attack_simulation/examples/demo_detection_performance.py
```

This demonstrates:
- ROC curve generation
- AUC calculation
- Confusion matrix visualization
- Threshold analysis
- Comprehensive performance reports

## Output Files

Detection results are saved to the session directory:

```
output/session_<session_id>/
├── detection_events.csv       # All detection events
├── manipulations.csv          # Attack manipulations
├── charging_cycles.csv        # Charging cycle data
├── degradation_timeline.csv   # Battery degradation
└── plots/
    ├── roc_curve.png
    ├── precision_recall_curve.png
    ├── confusion_matrix.png
    └── threshold_analysis.png
```

## Best Practices

1. **Establish Baseline**: Collect statistics from normal operation before detection
2. **Tune Thresholds**: Use ROC analysis to find optimal detection thresholds
3. **Combine Methods**: Use multiple detection methods for better coverage
4. **Monitor Performance**: Track detection metrics over time
5. **Update Baselines**: Periodically update baseline statistics as system evolves

## Troubleshooting

### Low Detection Rate (High False Negatives)

- Lower detection thresholds
- Use more sensitive detection methods
- Check if baseline statistics are accurate

### High False Positive Rate

- Increase detection thresholds
- Update baseline statistics with more normal data
- Use range-based detection for hard limits

### Poor AUC Score

- Verify ground truth labels are correct
- Check if attacks are actually detectable
- Consider using different detection methods
- Collect more diverse training data

## Requirements

- Python 3.7+
- numpy (for ROC calculations)
- matplotlib (for visualizations)
- PyYAML (for configuration)

Install dependencies:

```bash
pip install numpy matplotlib pyyaml
```

## References

- Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
- Design Document: Section on Attack Detection Simulation
- Related: Attack Engine, Metrics Collector, Visualization Engine
