#!/usr/bin/env python3
"""
Subtle Attack Scenario Validation Script

This script runs a subtle attack simulation with minimal parameter deviations
for 1000 charging cycles to evaluate detection difficulty and stealthy degradation.

Requirements: 4.3
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import logging
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from attack_simulation.models.battery_model import BatteryDegradationModel, DegradationParameters
from attack_simulation.metrics.metrics_collector import MetricsCollector
from attack_simulation.visualization.visualization_engine import VisualizationEngine
from attack_simulation.core.attack_engine import AttackEngine, AttackConfig, AttackStrategy
from attack_simulation.models.ocpp_models import ChargingProfile, ChargingSchedulePeriod
from attack_simulation.detection.anomaly_detector import AnomalyDetector, DetectionConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_normal_charging_profile() -> ChargingProfile:
    """
    Create a normal (manufacturer-recommended) charging profile
    
    Returns:
        ChargingProfile with optimal parameters
    """
    schedule = [
        ChargingSchedulePeriod(
            start_period=0,
            limit=50.0,
            number_phases=3
        )
    ]
    
    return ChargingProfile(
        id=1,
        stack_level=0,
        charging_profile_purpose="TxDefaultProfile",
        charging_profile_kind="Absolute",
        charging_schedule=schedule,
        voltage_limit=4.2,
        current_limit=50.0,
        soc_min=20.0,
        soc_max=80.0
    )


def run_subtle_attack_scenario(cycles: int = 1000,
                               output_dir: str = "./output/validation/subtle",
                               baseline_dir: str = None,
                               enable_detection: bool = True) -> dict:
    """
    Run subtle attack scenario with minimal parameter deviations
    
    Args:
        cycles: Number of charging cycles to simulate
        output_dir: Output directory for results
        baseline_dir: Path to baseline results for comparison (optional)
        enable_detection: Enable anomaly detection to test evasion
        
    Returns:
        Dictionary with validation results
    """
    logger.info("=" * 80)
    logger.info("SUBTLE ATTACK SCENARIO VALIDATION")
    logger.info("=" * 80)
    logger.info(f"Cycles: {cycles}")
    logger.info(f"Output: {output_dir}")
    logger.info(f"Detection: {'Enabled' if enable_detection else 'Disabled'}")
    logger.info("")
    
    # Create output directory
    session_id = f"subtle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_dir = os.path.join(output_dir, f"session_{session_id}")
    os.makedirs(session_dir, exist_ok=True)
    
    # Initialize battery model
    logger.info("Initializing battery degradation model...")
    battery_model = BatteryDegradationModel(initial_capacity_ah=75.0)
    logger.info(f"Initial SoH: {battery_model.soh:.2f}%")
    logger.info(f"Initial Capacity: {battery_model.capacity_ah:.2f} Ah")
    logger.info("")
    
    # Initialize metrics collector
    logger.info("Initializing metrics collector...")
    metrics_collector = MetricsCollector(output_dir=output_dir, session_id=session_id)
    
    # Configure subtle attack
    logger.info("Configuring subtle attack engine...")
    attack_config = AttackConfig(
        enabled=True,
        strategy=AttackStrategy.SUBTLE,
        voltage_enabled=True,
        voltage_deviation_percent=5.0,  # Only 5% voltage increase
        voltage_target_range=(4.2, 4.3),
        current_enabled=True,
        current_deviation_percent=8.0,  # Only 8% current increase
        current_target_range=(50, 60),
        curve_enabled=False,  # Disable curve manipulation (too obvious)
        curve_modification_type="flatten"
    )
    
    attack_engine = AttackEngine(config=attack_config, metrics_collector=metrics_collector)
    
    logger.info(f"  Strategy: {attack_config.strategy.value}")
    logger.info(f"  Voltage manipulation: {attack_config.voltage_deviation_percent}% (minimal)")
    logger.info(f"  Current manipulation: {attack_config.current_deviation_percent}% (minimal)")
    logger.info(f"  Curve manipulation: Disabled (too detectable)")
    logger.info("")
    
    # Initialize anomaly detector if enabled
    detector = None
    detection_results = {'detections': 0, 'false_negatives': 0, 'detection_rate': 0.0}
    
    if enable_detection:
        logger.info("Initializing anomaly detector...")
        detection_config = DetectionConfig(
            enabled=True,
            voltage_threshold_percent=10.0,  # 10% threshold
            current_threshold_percent=15.0,  # 15% threshold
            statistical_method="zscore",
            zscore_threshold=2.0
        )
        detector = AnomalyDetector(config=detection_config)
        logger.info(f"  Voltage threshold: {detection_config.voltage_threshold_percent}%")
        logger.info(f"  Current threshold: {detection_config.current_threshold_percent}%")
        logger.info("")
    
    # Create normal charging profile (will be manipulated by attack engine)
    normal_profile = create_normal_charging_profile()
    
    # Simulate charging cycles with subtle attack
    logger.info(f"Simulating {cycles} charging cycles with subtle attack...")
    logger.info("-" * 80)
    
    cycle_duration_hours = 2.0
    detections = 0
    
    for cycle_num in range(1, cycles + 1):
        # Record SoH before cycle
        soh_before = battery_model.soh
        
        # Apply subtle attack manipulation to profile
        poisoned_profile = attack_engine.manipulate_charging_profile(normal_profile)
        
        # Test detection if enabled
        if detector:
            is_anomalous = detector.detect_anomaly(
                original_profile=normal_profile,
                modified_profile=poisoned_profile
            )
            if is_anomalous:
                detections += 1
        
        # Simulate charging cycle with poisoned profile
        degradation_result = battery_model.simulate_charging_cycle(
            profile=poisoned_profile,
            duration_hours=cycle_duration_hours
        )
        
        # Calculate energy delivered
        energy_kwh = poisoned_profile.current_limit * poisoned_profile.voltage_limit * cycle_duration_hours / 1000.0
        
        # Log charging cycle
        metrics_collector.log_charging_cycle(
            cycle_num=cycle_num,
            profile=poisoned_profile,
            duration=cycle_duration_hours,
            energy_kwh=energy_kwh,
            soh_before=soh_before,
            soh_after=battery_model.soh
        )
        
        # Log degradation event
        metrics_collector.log_degradation_event(degradation_result)
        
        # Progress reporting
        if cycle_num % 100 == 0 or cycle_num == cycles:
            logger.info(f"Cycle {cycle_num}/{cycles}: SoH = {battery_model.soh:.4f}%, "
                       f"Degradation = {degradation_result.degradation_percent:.6f}%")
    
    logger.info("-" * 80)
    logger.info("")
    
    # Calculate detection results
    if enable_detection:
        manipulation_count = len(metrics_collector.manipulation_events)
        detection_rate = (detections / manipulation_count * 100) if manipulation_count > 0 else 0
        false_negatives = manipulation_count - detections
        
        detection_results = {
            'detections': detections,
            'false_negatives': false_negatives,
            'total_manipulations': manipulation_count,
            'detection_rate': detection_rate
        }
    
    # Generate summary
    logger.info("Generating summary report...")
    summary = metrics_collector.generate_summary_report()
    
    # Export metrics
    logger.info("Exporting metrics to CSV...")
    metrics_collector.export_to_csv()
    
    # Generate visualizations
    logger.info("Generating visualizations...")
    viz_engine = VisualizationEngine(metrics_collector)
    
    # SoH timeline plot
    plot_path = os.path.join(session_dir, "plots", "soh_timeline.png")
    viz_engine.plot_soh_timeline(output_path=plot_path)
    logger.info(f"  - SoH timeline: {plot_path}")
    
    # Stress factors plot
    plot_path = os.path.join(session_dir, "plots", "stress_factors.png")
    viz_engine.plot_stress_factors(output_path=plot_path)
    logger.info(f"  - Stress factors: {plot_path}")
    
    # Parameter deviations plot
    plot_path = os.path.join(session_dir, "plots", "parameter_deviations.png")
    viz_engine.plot_parameter_deviations(output_path=plot_path)
    logger.info(f"  - Parameter deviations: {plot_path}")
    
    logger.info("")
    
    # Attack results
    logger.info("=" * 80)
    logger.info("SUBTLE ATTACK RESULTS")
    logger.info("=" * 80)
    logger.info(f"Total Cycles: {summary.total_cycles}")
    logger.info(f"Total Duration: {summary.total_duration_hours:.2f} hours")
    logger.info(f"Initial SoH: {summary.initial_soh:.4f}%")
    logger.info(f"Final SoH: {summary.final_soh:.4f}%")
    logger.info(f"Total Degradation: {summary.total_degradation:.4f}%")
    logger.info(f"Degradation Rate: {summary.degradation_rate_per_cycle:.6f}% per cycle")
    logger.info(f"Remaining Capacity: {battery_model.get_remaining_capacity():.2f} Ah")
    logger.info(f"Manipulation Events: {len(metrics_collector.manipulation_events)}")
    logger.info(f"Avg Voltage Deviation: {summary.average_voltage_deviation:.2f}%")
    logger.info(f"Avg Current Deviation: {summary.average_current_deviation:.2f}%")
    logger.info("")
    
    # Detection results
    if enable_detection:
        logger.info("=" * 80)
        logger.info("DETECTION EVASION RESULTS")
        logger.info("=" * 80)
        logger.info(f"Total Manipulations: {detection_results['total_manipulations']}")
        logger.info(f"Detected: {detection_results['detections']}")
        logger.info(f"Undetected: {detection_results['false_negatives']}")
        logger.info(f"Detection Rate: {detection_results['detection_rate']:.2f}%")
        logger.info("")
    
    # Compare with baseline if available
    comparison_result = None
    if baseline_dir:
        logger.info("=" * 80)
        logger.info("BASELINE COMPARISON")
        logger.info("=" * 80)
        
        try:
            # Find baseline summary file
            baseline_summary_path = None
            for root, dirs, files in os.walk(baseline_dir):
                if 'summary.json' in files:
                    baseline_summary_path = os.path.join(root, 'summary.json')
                    break
            
            if baseline_summary_path:
                logger.info(f"Loading baseline from: {baseline_summary_path}")
                
                # Load baseline summary
                with open(baseline_summary_path, 'r') as f:
                    baseline_data = json.load(f)
                
                baseline_final_soh = baseline_data.get('final_soh', 100.0)
                baseline_degradation = baseline_data.get('total_degradation', 0.0)
                baseline_rate = baseline_data.get('degradation_rate_per_cycle', 0.0)
                
                # Calculate comparison metrics
                degradation_difference = summary.total_degradation - baseline_degradation
                acceleration_factor = summary.degradation_rate_per_cycle / baseline_rate if baseline_rate > 0 else 0
                
                logger.info(f"Baseline Final SoH: {baseline_final_soh:.4f}%")
                logger.info(f"Attack Final SoH: {summary.final_soh:.4f}%")
                logger.info(f"SoH Difference: {baseline_final_soh - summary.final_soh:.4f}%")
                logger.info("")
                logger.info(f"Baseline Degradation: {baseline_degradation:.4f}%")
                logger.info(f"Attack Degradation: {summary.total_degradation:.4f}%")
                logger.info(f"Additional Degradation: {degradation_difference:.4f}%")
                logger.info("")
                logger.info(f"Baseline Rate: {baseline_rate:.6f}% per cycle")
                logger.info(f"Attack Rate: {summary.degradation_rate_per_cycle:.6f}% per cycle")
                logger.info(f"Acceleration Factor: {acceleration_factor:.2f}x")
                logger.info("")
                
                comparison_result = {
                    'baseline_final_soh': baseline_final_soh,
                    'attack_final_soh': summary.final_soh,
                    'soh_difference': baseline_final_soh - summary.final_soh,
                    'degradation_difference': degradation_difference,
                    'acceleration_factor': acceleration_factor
                }
                
            else:
                logger.warning("Baseline summary.json not found")
                
        except Exception as e:
            logger.error(f"Failed to load baseline comparison: {e}")
    
    # Validation checks
    logger.info("=" * 80)
    logger.info("VALIDATION CHECKS")
    logger.info("=" * 80)
    
    # Check 1: Attack caused moderate degradation (less than aggressive, more than baseline)
    baseline_expected_degradation = 0.001 * cycles  # Expected baseline: ~1%
    if baseline_expected_degradation * 1.3 < summary.total_degradation < baseline_expected_degradation * 3:
        logger.info(f"✓ Attack caused moderate degradation (stealthy)")
        logger.info(f"  Expected range: {baseline_expected_degradation * 1.3:.2f}% - {baseline_expected_degradation * 3:.2f}%")
        logger.info(f"  Actual: {summary.total_degradation:.4f}%")
        degradation_check = True
    else:
        logger.warning(f"✗ Attack degradation outside expected range")
        logger.warning(f"  Expected range: {baseline_expected_degradation * 1.3:.2f}% - {baseline_expected_degradation * 3:.2f}%")
        logger.warning(f"  Actual: {summary.total_degradation:.4f}%")
        degradation_check = False
    
    # Check 2: Manipulation events occurred
    if len(metrics_collector.manipulation_events) > 0:
        logger.info(f"✓ Manipulation events recorded: {len(metrics_collector.manipulation_events)}")
        manipulation_check = True
    else:
        logger.warning(f"✗ No manipulation events recorded")
        manipulation_check = False
    
    # Check 3: Parameter deviations are minimal (below 10%)
    if summary.average_voltage_deviation < 10.0 and summary.average_current_deviation < 15.0:
        logger.info(f"✓ Parameter deviations are minimal (stealthy)")
        logger.info(f"  Voltage: {summary.average_voltage_deviation:.2f}% (< 10%)")
        logger.info(f"  Current: {summary.average_current_deviation:.2f}% (< 15%)")
        deviation_check = True
    else:
        logger.warning(f"✗ Parameter deviations too high (not stealthy)")
        logger.warning(f"  Voltage: {summary.average_voltage_deviation:.2f}% (should be < 10%)")
        logger.warning(f"  Current: {summary.average_current_deviation:.2f}% (should be < 15%)")
        deviation_check = False
    
    # Check 4: Low detection rate (if detection enabled)
    detection_check = True
    if enable_detection:
        if detection_results['detection_rate'] < 50.0:  # Less than 50% detected
            logger.info(f"✓ Low detection rate (successful evasion)")
            logger.info(f"  Detection rate: {detection_results['detection_rate']:.2f}% (< 50%)")
        else:
            logger.warning(f"✗ High detection rate (failed evasion)")
            logger.warning(f"  Detection rate: {detection_results['detection_rate']:.2f}% (should be < 50%)")
            detection_check = False
    
    # Check 5: Acceleration factor (if baseline available)
    acceleration_check = True
    if comparison_result:
        if 1.3 <= comparison_result['acceleration_factor'] <= 2.5:
            logger.info(f"✓ Moderate degradation acceleration (stealthy)")
            logger.info(f"  Acceleration factor: {comparison_result['acceleration_factor']:.2f}x (1.3-2.5x)")
        else:
            logger.warning(f"✗ Acceleration factor outside expected range")
            logger.warning(f"  Acceleration factor: {comparison_result['acceleration_factor']:.2f}x (expected: 1.3-2.5x)")
            acceleration_check = False
    
    logger.info("")
    
    # Overall validation result
    all_checks_passed = (degradation_check and manipulation_check and 
                        deviation_check and detection_check and acceleration_check)
    
    if all_checks_passed:
        logger.info("=" * 80)
        logger.info("✓ SUBTLE ATTACK VALIDATION PASSED")
        logger.info("=" * 80)
    else:
        logger.warning("=" * 80)
        logger.warning("✗ SUBTLE ATTACK VALIDATION FAILED")
        logger.warning("=" * 80)
    
    logger.info("")
    logger.info(f"Results saved to: {session_dir}")
    logger.info("")
    
    return {
        'session_dir': session_dir,
        'summary': summary,
        'comparison': comparison_result,
        'detection': detection_results,
        'validation_passed': all_checks_passed,
        'checks': {
            'moderate_degradation': degradation_check,
            'manipulation_events': manipulation_check,
            'minimal_deviations': deviation_check,
            'low_detection_rate': detection_check,
            'acceleration_factor': acceleration_check
        }
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run subtle attack scenario validation")
    parser.add_argument('--cycles', type=int, default=1000,
                       help='Number of charging cycles to simulate (default: 1000)')
    parser.add_argument('--output', type=str, default='./output/validation/subtle',
                       help='Output directory for results')
    parser.add_argument('--baseline', type=str, default=None,
                       help='Path to baseline results for comparison')
    parser.add_argument('--no-detection', action='store_true',
                       help='Disable anomaly detection')
    
    args = parser.parse_args()
    
    try:
        results = run_subtle_attack_scenario(
            cycles=args.cycles,
            output_dir=args.output,
            baseline_dir=args.baseline,
            enable_detection=not args.no_detection
        )
        
        # Exit with appropriate code
        sys.exit(0 if results['validation_passed'] else 1)
        
    except Exception as e:
        logger.error(f"Subtle attack validation failed with error: {e}", exc_info=True)
        sys.exit(1)
