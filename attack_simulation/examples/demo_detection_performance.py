"""
Demo script for detection performance evaluation with ROC curves and confusion matrix
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from attack_simulation.detection import (
    AnomalyDetector,
    DetectionConfig,
    DetectionMethod,
    DetectionPerformanceEvaluator
)
from datetime import datetime
import random


def create_test_profiles(num_normal: int = 50, num_manipulated: int = 50):
    """
    Create test dataset with normal and manipulated profiles
    
    Args:
        num_normal: Number of normal profiles
        num_manipulated: Number of manipulated profiles
        
    Returns:
        List of (profile, is_manipulated) tuples
    """
    profiles = []
    
    # Create normal profiles with slight variations
    for i in range(num_normal):
        base_limit = 30.0 + random.uniform(-3, 3)
        profile = {
            'chargingSchedule': {
                'chargingRateUnit': 'A',
                'chargingSchedulePeriod': [
                    {'startPeriod': 0, 'limit': base_limit + random.uniform(-2, 2)},
                    {'startPeriod': 1800, 'limit': base_limit + random.uniform(-2, 2)},
                    {'startPeriod': 3600, 'limit': base_limit + random.uniform(-2, 2)},
                    {'startPeriod': 5400, 'limit': base_limit + random.uniform(-2, 2)}
                ]
            }
        }
        profiles.append((profile, False))
    
    # Create manipulated profiles with various attack intensities
    for i in range(num_manipulated):
        # Random attack intensity between 10% and 60%
        attack_intensity = random.uniform(0.1, 0.6)
        base_limit = 30.0 * (1 + attack_intensity)
        
        profile = {
            'chargingSchedule': {
                'chargingRateUnit': 'A',
                'chargingSchedulePeriod': [
                    {'startPeriod': 0, 'limit': base_limit + random.uniform(-2, 2)},
                    {'startPeriod': 1800, 'limit': base_limit + random.uniform(-2, 2)},
                    {'startPeriod': 3600, 'limit': base_limit + random.uniform(-2, 2)},
                    {'startPeriod': 5400, 'limit': base_limit + random.uniform(-2, 2)}
                ]
            }
        }
        profiles.append((profile, True))
    
    # Shuffle profiles
    random.shuffle(profiles)
    
    return profiles


def demo_roc_curve_generation():
    """Demonstrate ROC curve generation and AUC calculation"""
    print("\n" + "="*60)
    print("DEMO: ROC Curve Generation and AUC Calculation")
    print("="*60)
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Create test dataset
    print("\n1. Creating test dataset...")
    test_profiles = create_test_profiles(num_normal=100, num_manipulated=100)
    print(f"   Created {len(test_profiles)} test profiles")
    print(f"   - Normal: {sum(1 for _, is_manip in test_profiles if not is_manip)}")
    print(f"   - Manipulated: {sum(1 for _, is_manip in test_profiles if is_manip)}")
    
    # Create detector
    print("\n2. Initializing anomaly detector...")
    config = DetectionConfig(
        enabled=True,
        method=DetectionMethod.STATISTICAL,
        current_threshold_percent=15.0,
        baseline_current_mean=30.0,
        baseline_current_std=5.0
    )
    detector = AnomalyDetector(config)
    
    # Run detection on all profiles
    print("\n3. Running detection on all profiles...")
    predictions = []
    
    for i, (profile, is_manipulated) in enumerate(test_profiles):
        result = detector.detect_anomaly(
            profile, 
            message_id=f"msg_{i:03d}", 
            is_manipulated=is_manipulated
        )
        
        # Store (confidence_score, is_actually_anomalous) for ROC calculation
        predictions.append((result.confidence_score, is_manipulated))
    
    print(f"   Completed {len(predictions)} detections")
    
    # Calculate ROC curve and AUC
    print("\n4. Calculating ROC curve and AUC...")
    evaluator = DetectionPerformanceEvaluator(output_dir="./output")
    roc_points, auc = evaluator.calculate_roc_curve(predictions)
    
    print(f"   ROC curve points: {len(roc_points)}")
    print(f"   AUC: {auc:.4f}")
    
    # Show some key ROC points
    print("\n5. Key ROC points:")
    print(f"   {'Threshold':<12} {'TPR':<8} {'FPR':<8} {'Precision':<10} {'Recall':<8}")
    print(f"   {'-'*60}")
    
    # Show points at different thresholds
    for point in roc_points[::max(1, len(roc_points)//10)]:
        print(f"   {point.threshold:<12.3f} {point.true_positive_rate:<8.3f} "
              f"{point.false_positive_rate:<8.3f} {point.precision:<10.3f} "
              f"{point.recall:<8.3f}")
    
    # Generate ROC curve plot
    print("\n6. Generating ROC curve plot...")
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"./output/detection_performance_{session_id}"
    
    roc_path = os.path.join(output_dir, 'roc_curve.png')
    os.makedirs(output_dir, exist_ok=True)
    evaluator.plot_roc_curve(roc_points, auc, roc_path)
    print(f"   ROC curve saved to: {roc_path}")
    
    return detector, evaluator, roc_points, auc, output_dir


def demo_confusion_matrix():
    """Demonstrate confusion matrix visualization"""
    print("\n" + "="*60)
    print("DEMO: Confusion Matrix Visualization")
    print("="*60)
    
    # Set random seed
    random.seed(42)
    
    # Create test dataset
    print("\n1. Creating test dataset...")
    test_profiles = create_test_profiles(num_normal=80, num_manipulated=80)
    
    # Create detector
    config = DetectionConfig(
        enabled=True,
        method=DetectionMethod.STATISTICAL,
        current_threshold_percent=15.0
    )
    detector = AnomalyDetector(config)
    
    # Run detection
    print("\n2. Running detection...")
    for i, (profile, is_manipulated) in enumerate(test_profiles):
        detector.detect_anomaly(
            profile, 
            message_id=f"msg_{i:03d}", 
            is_manipulated=is_manipulated
        )
    
    # Get detection metrics
    metrics = detector.get_detection_metrics()
    
    print("\n3. Detection Metrics:")
    print(f"   True Positives:  {metrics.true_positives}")
    print(f"   False Positives: {metrics.false_positives}")
    print(f"   True Negatives:  {metrics.true_negatives}")
    print(f"   False Negatives: {metrics.false_negatives}")
    print(f"   Total:           {metrics.total_detections}")
    print(f"\n   Accuracy:  {metrics.get_accuracy():.2%}")
    print(f"   Precision: {metrics.get_precision():.2%}")
    print(f"   Recall:    {metrics.get_recall():.2%}")
    print(f"   F1 Score:  {metrics.get_f1_score():.2%}")
    
    # Generate confusion matrix plot
    print("\n4. Generating confusion matrix plot...")
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"./output/confusion_matrix_{session_id}"
    os.makedirs(output_dir, exist_ok=True)
    
    evaluator = DetectionPerformanceEvaluator(output_dir=output_dir)
    cm_path = os.path.join(output_dir, 'confusion_matrix.png')
    
    evaluator.plot_confusion_matrix(
        true_positives=metrics.true_positives,
        false_positives=metrics.false_positives,
        true_negatives=metrics.true_negatives,
        false_negatives=metrics.false_negatives,
        output_path=cm_path
    )
    
    print(f"   Confusion matrix saved to: {cm_path}")


def demo_threshold_analysis():
    """Demonstrate threshold analysis"""
    print("\n" + "="*60)
    print("DEMO: Detection Threshold Analysis")
    print("="*60)
    
    # Set random seed
    random.seed(42)
    
    # Create test dataset
    print("\n1. Creating test dataset...")
    test_profiles = create_test_profiles(num_normal=100, num_manipulated=100)
    
    # Create detector
    config = DetectionConfig(
        enabled=True,
        method=DetectionMethod.STATISTICAL,
        current_threshold_percent=15.0
    )
    detector = AnomalyDetector(config)
    
    # Run detection and collect predictions
    print("\n2. Running detection...")
    predictions = []
    for i, (profile, is_manipulated) in enumerate(test_profiles):
        result = detector.detect_anomaly(
            profile, 
            message_id=f"msg_{i:03d}", 
            is_manipulated=is_manipulated
        )
        predictions.append((result.confidence_score, is_manipulated))
    
    # Calculate ROC curve
    print("\n3. Calculating ROC curve...")
    evaluator = DetectionPerformanceEvaluator()
    roc_points, auc = evaluator.calculate_roc_curve(predictions)
    
    # Generate threshold analysis plot
    print("\n4. Generating threshold analysis plot...")
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"./output/threshold_analysis_{session_id}"
    os.makedirs(output_dir, exist_ok=True)
    
    threshold_path = os.path.join(output_dir, 'threshold_analysis.png')
    evaluator.plot_threshold_analysis(roc_points, threshold_path)
    
    print(f"   Threshold analysis saved to: {threshold_path}")
    
    # Find optimal threshold
    f1_scores = []
    for point in roc_points:
        if point.precision + point.recall > 0:
            f1 = 2 * (point.precision * point.recall) / (point.precision + point.recall)
        else:
            f1 = 0.0
        f1_scores.append((f1, point.threshold))
    
    if f1_scores:
        max_f1, optimal_threshold = max(f1_scores)
        print(f"\n5. Optimal Detection Threshold:")
        print(f"   Threshold: {optimal_threshold:.3f}")
        print(f"   F1 Score:  {max_f1:.3f}")


def demo_comprehensive_evaluation():
    """Demonstrate comprehensive performance evaluation"""
    print("\n" + "="*60)
    print("DEMO: Comprehensive Performance Evaluation")
    print("="*60)
    
    # Set random seed
    random.seed(42)
    
    # Create test dataset
    print("\n1. Creating test dataset...")
    test_profiles = create_test_profiles(num_normal=150, num_manipulated=150)
    print(f"   Total profiles: {len(test_profiles)}")
    
    # Create detector
    print("\n2. Initializing detector...")
    config = DetectionConfig(
        enabled=True,
        method=DetectionMethod.STATISTICAL,
        current_threshold_percent=15.0,
        baseline_current_mean=30.0,
        baseline_current_std=5.0
    )
    detector = AnomalyDetector(config)
    
    # Run detection
    print("\n3. Running detection on all profiles...")
    predictions = []
    for i, (profile, is_manipulated) in enumerate(test_profiles):
        result = detector.detect_anomaly(
            profile, 
            message_id=f"msg_{i:03d}", 
            is_manipulated=is_manipulated
        )
        predictions.append((result.confidence_score, is_manipulated))
        
        if (i + 1) % 50 == 0:
            print(f"   Progress: {i+1}/{len(test_profiles)} profiles processed")
    
    # Calculate ROC curve
    print("\n4. Calculating ROC curve and AUC...")
    evaluator = DetectionPerformanceEvaluator()
    roc_points, auc = evaluator.calculate_roc_curve(predictions)
    print(f"   AUC: {auc:.4f}")
    
    # Generate comprehensive report
    print("\n5. Generating comprehensive performance report...")
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"./output/comprehensive_evaluation_{session_id}"
    
    metrics = detector.get_detection_metrics()
    report = evaluator.generate_performance_report(
        detection_metrics=metrics,
        roc_points=roc_points,
        auc=auc,
        output_dir=output_dir
    )
    
    print("\n6. Performance Report Summary:")
    print(f"   AUC:                  {report['auc']:.4f}")
    print(f"   Accuracy:             {report['accuracy']:.2%}")
    print(f"   Precision:            {report['precision']:.2%}")
    print(f"   Recall:               {report['recall']:.2%}")
    print(f"   F1 Score:             {report['f1_score']:.2%}")
    print(f"   False Positive Rate:  {report['false_positive_rate']:.2%}")
    
    print(f"\n7. All plots saved to: {output_dir}")
    print(f"   - ROC Curve:              {report['plots']['roc_curve']}")
    print(f"   - Precision-Recall Curve: {report['plots']['precision_recall_curve']}")
    print(f"   - Confusion Matrix:       {report['plots']['confusion_matrix']}")
    print(f"   - Threshold Analysis:     {report['plots']['threshold_analysis']}")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("DETECTION PERFORMANCE EVALUATION DEMO")
    print("="*60)
    
    try:
        demo_roc_curve_generation()
        demo_confusion_matrix()
        demo_threshold_analysis()
        demo_comprehensive_evaluation()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        print("\nAll performance evaluation plots have been generated.")
        print("Check the ./output directory for results.")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
