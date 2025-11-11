"""
Demo script for anomaly detection framework
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from attack_simulation.detection import (
    AnomalyDetector,
    DetectionConfig,
    DetectionMethod
)
from attack_simulation.metrics.metrics_collector import MetricsCollector
from datetime import datetime


def create_normal_profile():
    """Create a normal charging profile"""
    return {
        'chargingSchedule': {
            'chargingRateUnit': 'A',
            'chargingSchedulePeriod': [
                {'startPeriod': 0, 'limit': 30.0},
                {'startPeriod': 1800, 'limit': 32.0},
                {'startPeriod': 3600, 'limit': 28.0},
                {'startPeriod': 5400, 'limit': 25.0}
            ]
        }
    }


def create_manipulated_profile():
    """Create a manipulated charging profile with overstressed parameters"""
    return {
        'chargingSchedule': {
            'chargingRateUnit': 'A',
            'chargingSchedulePeriod': [
                {'startPeriod': 0, 'limit': 45.0},   # 50% increase
                {'startPeriod': 1800, 'limit': 48.0},  # 50% increase
                {'startPeriod': 3600, 'limit': 42.0},  # 50% increase
                {'startPeriod': 5400, 'limit': 37.5}   # 50% increase
            ]
        }
    }


def create_subtle_attack_profile():
    """Create a subtly manipulated profile"""
    return {
        'chargingSchedule': {
            'chargingRateUnit': 'A',
            'chargingSchedulePeriod': [
                {'startPeriod': 0, 'limit': 33.0},   # 10% increase
                {'startPeriod': 1800, 'limit': 35.2},  # 10% increase
                {'startPeriod': 3600, 'limit': 30.8},  # 10% increase
                {'startPeriod': 5400, 'limit': 27.5}   # 10% increase
            ]
        }
    }


def demo_statistical_detection():
    """Demonstrate statistical anomaly detection"""
    print("\n" + "="*60)
    print("DEMO: Statistical Anomaly Detection")
    print("="*60)
    
    # Create detection config
    config = DetectionConfig(
        enabled=True,
        method=DetectionMethod.STATISTICAL,
        current_threshold_percent=15.0,
        baseline_current_mean=30.0,
        baseline_current_std=5.0
    )
    
    # Create detector
    detector = AnomalyDetector(config)
    
    # Test with normal profile
    print("\n1. Testing normal profile...")
    normal_profile = create_normal_profile()
    result = detector.detect_anomaly(normal_profile, message_id="msg_001", is_manipulated=False)
    
    print(f"   Is anomalous: {result.is_anomalous}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Anomalies detected: {result.anomalous_parameters}")
    
    # Test with manipulated profile
    print("\n2. Testing manipulated profile...")
    manipulated_profile = create_manipulated_profile()
    result = detector.detect_anomaly(manipulated_profile, message_id="msg_002", is_manipulated=True)
    
    print(f"   Is anomalous: {result.is_anomalous}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Anomalies detected: {result.anomalous_parameters}")
    
    for anomaly in result.detected_anomalies:
        print(f"   - {anomaly.parameter_name}: {anomaly.observed_value:.2f} "
              f"(expected: {anomaly.expected_value:.2f}, "
              f"deviation: {anomaly.deviation_percent:.1f}%)")
    
    # Test with subtle attack
    print("\n3. Testing subtle attack profile...")
    subtle_profile = create_subtle_attack_profile()
    result = detector.detect_anomaly(subtle_profile, message_id="msg_003", is_manipulated=True)
    
    print(f"   Is anomalous: {result.is_anomalous}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Anomalies detected: {result.anomalous_parameters}")
    
    # Show detection metrics
    print("\n4. Detection Performance Metrics:")
    metrics = detector.get_detection_metrics()
    print(f"   Accuracy: {metrics.get_accuracy():.2%}")
    print(f"   Precision: {metrics.get_precision():.2%}")
    print(f"   Recall: {metrics.get_recall():.2%}")
    print(f"   F1 Score: {metrics.get_f1_score():.2%}")
    print(f"   True Positives: {metrics.true_positives}")
    print(f"   False Positives: {metrics.false_positives}")
    print(f"   True Negatives: {metrics.true_negatives}")
    print(f"   False Negatives: {metrics.false_negatives}")


def demo_range_based_detection():
    """Demonstrate range-based anomaly detection"""
    print("\n" + "="*60)
    print("DEMO: Range-Based Anomaly Detection")
    print("="*60)
    
    # Create detection config with strict ranges
    config = DetectionConfig(
        enabled=True,
        method=DetectionMethod.RANGE_BASED,
        current_min=0.0,
        current_max=40.0  # Strict maximum
    )
    
    # Create detector
    detector = AnomalyDetector(config)
    
    # Test with normal profile (within range)
    print("\n1. Testing normal profile (within range)...")
    normal_profile = create_normal_profile()
    result = detector.detect_anomaly(normal_profile, message_id="msg_004", is_manipulated=False)
    
    print(f"   Is anomalous: {result.is_anomalous}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    
    # Test with manipulated profile (exceeds range)
    print("\n2. Testing manipulated profile (exceeds range)...")
    manipulated_profile = create_manipulated_profile()
    result = detector.detect_anomaly(manipulated_profile, message_id="msg_005", is_manipulated=True)
    
    print(f"   Is anomalous: {result.is_anomalous}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Anomalies detected: {result.anomalous_parameters}")
    
    for anomaly in result.detected_anomalies:
        print(f"   - {anomaly.parameter_name}: {anomaly.observed_value:.2f} "
              f"exceeds maximum {anomaly.expected_value:.2f}")


def demo_pattern_based_detection():
    """Demonstrate pattern-based anomaly detection"""
    print("\n" + "="*60)
    print("DEMO: Pattern-Based Anomaly Detection")
    print("="*60)
    
    # Create detection config
    config = DetectionConfig(
        enabled=True,
        method=DetectionMethod.PATTERN_BASED,
        enable_curve_analysis=True,
        curve_smoothness_threshold=0.3
    )
    
    # Create detector
    detector = AnomalyDetector(config)
    
    # Create irregular charging curve
    irregular_profile = {
        'chargingSchedule': {
            'chargingRateUnit': 'A',
            'chargingSchedulePeriod': [
                {'startPeriod': 0, 'limit': 30.0},
                {'startPeriod': 1800, 'limit': 50.0},  # Sudden jump
                {'startPeriod': 3600, 'limit': 20.0},  # Sudden drop
                {'startPeriod': 5400, 'limit': 45.0}   # Sudden jump
            ]
        }
    }
    
    print("\n1. Testing irregular charging curve...")
    result = detector.detect_anomaly(irregular_profile, message_id="msg_006", is_manipulated=True)
    
    print(f"   Is anomalous: {result.is_anomalous}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Anomalies detected: {result.anomalous_parameters}")
    
    for anomaly in result.detected_anomalies:
        print(f"   - {anomaly.parameter_name}: irregularity score {anomaly.observed_value:.4f}")
        print(f"     Details: {anomaly.details}")


def demo_with_metrics_collector():
    """Demonstrate detection with metrics collection"""
    print("\n" + "="*60)
    print("DEMO: Detection with Metrics Collection")
    print("="*60)
    
    # Create metrics collector
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    metrics_collector = MetricsCollector(
        output_dir="./output",
        session_id=f"detection_demo_{session_id}"
    )
    
    # Create detection config
    config = DetectionConfig(
        enabled=True,
        method=DetectionMethod.STATISTICAL,
        current_threshold_percent=15.0
    )
    
    # Create detector with metrics collector
    detector = AnomalyDetector(config, metrics_collector=metrics_collector)
    
    # Run multiple detections
    print("\n1. Running detection on multiple profiles...")
    
    profiles = [
        (create_normal_profile(), "msg_007", False),
        (create_manipulated_profile(), "msg_008", True),
        (create_normal_profile(), "msg_009", False),
        (create_subtle_attack_profile(), "msg_010", True),
    ]
    
    for profile, msg_id, is_manipulated in profiles:
        result = detector.detect_anomaly(profile, message_id=msg_id, is_manipulated=is_manipulated)
        print(f"   {msg_id}: anomalous={result.is_anomalous}, "
              f"confidence={result.confidence_score:.2f}")
    
    # Show final metrics
    print("\n2. Final Detection Metrics:")
    metrics = detector.get_detection_metrics()
    print(f"   Total detections: {metrics.total_detections}")
    print(f"   Accuracy: {metrics.get_accuracy():.2%}")
    print(f"   Precision: {metrics.get_precision():.2%}")
    print(f"   Recall: {metrics.get_recall():.2%}")
    print(f"   F1 Score: {metrics.get_f1_score():.2%}")
    
    print(f"\n3. Detection events saved to: {metrics_collector.detection_events_csv}")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("ANOMALY DETECTION FRAMEWORK DEMO")
    print("="*60)
    
    demo_statistical_detection()
    demo_range_based_detection()
    demo_pattern_based_detection()
    demo_with_metrics_collector()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
