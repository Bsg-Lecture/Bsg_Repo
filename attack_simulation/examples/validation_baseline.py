#!/usr/bin/env python3
"""
Baseline Scenario Validation Script

This script runs a baseline simulation (no attack) with 1000 charging cycles
to establish normal degradation rates for comparison with attack scenarios.

Requirements: 6.1
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from attack_simulation.models.battery_model import BatteryDegradationModel, DegradationParameters
from attack_simulation.metrics.metrics_collector import MetricsCollector
from attack_simulation.visualization.visualization_engine import VisualizationEngine
from attack_simulation.models.ocpp_models import ChargingProfile, ChargingSchedulePeriod

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
    # Normal charging parameters (optimal for battery health)
    schedule = [
        ChargingSchedulePeriod(
            start_period=0,
            limit=50.0,  # 50A current limit (optimal C-rate ~0.67C for 75Ah battery)
            number_phases=3
        )
    ]
    
    return ChargingProfile(
        id=1,
        stack_level=0,
        charging_profile_purpose="TxDefaultProfile",
        charging_profile_kind="Absolute",
        charging_schedule=schedule,
        voltage_limit=4.2,  # Optimal voltage limit (V)
        current_limit=50.0,  # Optimal current limit (A)
        soc_min=20.0,  # Optimal minimum SoC (%)
        soc_max=80.0   # Optimal maximum SoC (%)
    )


def run_baseline_scenario(cycles: int = 1000, output_dir: str = "./output/validation/baseline") -> dict:
    """
    Run baseline scenario with normal charging profiles
    
    Args:
        cycles: Number of charging cycles to simulate
        output_dir: Output directory for results
        
    Returns:
        Dictionary with validation results
    """
    logger.info("=" * 80)
    logger.info("BASELINE SCENARIO VALIDATION")
    logger.info("=" * 80)
    logger.info(f"Cycles: {cycles}")
    logger.info(f"Output: {output_dir}")
    logger.info("")
    
    # Create output directory
    session_id = f"baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_dir = os.path.join(output_dir, f"session_{session_id}")
    os.makedirs(session_dir, exist_ok=True)
    
    # Initialize battery model with default parameters
    logger.info("Initializing battery degradation model...")
    battery_model = BatteryDegradationModel(initial_capacity_ah=75.0)
    logger.info(f"Initial SoH: {battery_model.soh:.2f}%")
    logger.info(f"Initial Capacity: {battery_model.capacity_ah:.2f} Ah")
    logger.info("")
    
    # Initialize metrics collector
    logger.info("Initializing metrics collector...")
    metrics_collector = MetricsCollector(output_dir=output_dir, session_id=session_id)
    
    # Create normal charging profile
    normal_profile = create_normal_charging_profile()
    
    # Simulate charging cycles
    logger.info(f"Simulating {cycles} charging cycles with normal parameters...")
    logger.info("-" * 80)
    
    cycle_duration_hours = 2.0  # Average charging duration
    
    for cycle_num in range(1, cycles + 1):
        # Record SoH before cycle
        soh_before = battery_model.soh
        
        # Simulate charging cycle with normal profile
        degradation_result = battery_model.simulate_charging_cycle(
            profile=normal_profile,
            duration_hours=cycle_duration_hours
        )
        
        # Calculate energy delivered (simplified)
        energy_kwh = normal_profile.current_limit * normal_profile.voltage_limit * cycle_duration_hours / 1000.0
        
        # Log charging cycle
        metrics_collector.log_charging_cycle(
            cycle_num=cycle_num,
            profile=normal_profile,
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
    
    logger.info("")
    
    # Validation results
    logger.info("=" * 80)
    logger.info("BASELINE VALIDATION RESULTS")
    logger.info("=" * 80)
    logger.info(f"Total Cycles: {summary.total_cycles}")
    logger.info(f"Total Duration: {summary.total_duration_hours:.2f} hours")
    logger.info(f"Initial SoH: {summary.initial_soh:.4f}%")
    logger.info(f"Final SoH: {summary.final_soh:.4f}%")
    logger.info(f"Total Degradation: {summary.total_degradation:.4f}%")
    logger.info(f"Degradation Rate: {summary.degradation_rate_per_cycle:.6f}% per cycle")
    logger.info(f"Remaining Capacity: {battery_model.get_remaining_capacity():.2f} Ah")
    logger.info("")
    
    # Validate normal degradation rate
    expected_degradation_rate = 0.001  # 0.1% per 100 cycles
    tolerance = 0.0005  # 50% tolerance
    
    logger.info("VALIDATION CHECKS:")
    logger.info("-" * 80)
    
    # Check 1: Degradation rate is within expected range
    if abs(summary.degradation_rate_per_cycle - expected_degradation_rate) <= tolerance:
        logger.info(f"✓ Degradation rate within expected range")
        logger.info(f"  Expected: {expected_degradation_rate:.6f}% ± {tolerance:.6f}%")
        logger.info(f"  Actual: {summary.degradation_rate_per_cycle:.6f}%")
        degradation_check = True
    else:
        logger.warning(f"✗ Degradation rate outside expected range")
        logger.warning(f"  Expected: {expected_degradation_rate:.6f}% ± {tolerance:.6f}%")
        logger.warning(f"  Actual: {summary.degradation_rate_per_cycle:.6f}%")
        degradation_check = False
    
    # Check 2: Final SoH is reasonable (should be > 99% after 1000 cycles)
    expected_final_soh = 100.0 - (expected_degradation_rate * cycles)
    if summary.final_soh >= expected_final_soh - 1.0:  # 1% tolerance
        logger.info(f"✓ Final SoH is reasonable")
        logger.info(f"  Expected: ≥ {expected_final_soh - 1.0:.2f}%")
        logger.info(f"  Actual: {summary.final_soh:.4f}%")
        soh_check = True
    else:
        logger.warning(f"✗ Final SoH is lower than expected")
        logger.warning(f"  Expected: ≥ {expected_final_soh - 1.0:.2f}%")
        logger.warning(f"  Actual: {summary.final_soh:.4f}%")
        soh_check = False
    
    # Check 3: No manipulation events (baseline should have zero manipulations)
    manipulation_count = len(metrics_collector.manipulation_events)
    if manipulation_count == 0:
        logger.info(f"✓ No manipulation events (baseline mode)")
        manipulation_check = True
    else:
        logger.warning(f"✗ Unexpected manipulation events: {manipulation_count}")
        manipulation_check = False
    
    logger.info("")
    
    # Overall validation result
    all_checks_passed = degradation_check and soh_check and manipulation_check
    
    if all_checks_passed:
        logger.info("=" * 80)
        logger.info("✓ BASELINE VALIDATION PASSED")
        logger.info("=" * 80)
    else:
        logger.warning("=" * 80)
        logger.warning("✗ BASELINE VALIDATION FAILED")
        logger.warning("=" * 80)
    
    logger.info("")
    logger.info(f"Results saved to: {session_dir}")
    logger.info("")
    
    return {
        'session_dir': session_dir,
        'summary': summary,
        'validation_passed': all_checks_passed,
        'checks': {
            'degradation_rate': degradation_check,
            'final_soh': soh_check,
            'no_manipulation': manipulation_check
        }
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run baseline scenario validation")
    parser.add_argument('--cycles', type=int, default=1000,
                       help='Number of charging cycles to simulate (default: 1000)')
    parser.add_argument('--output', type=str, default='./output/validation/baseline',
                       help='Output directory for results')
    
    args = parser.parse_args()
    
    try:
        results = run_baseline_scenario(cycles=args.cycles, output_dir=args.output)
        
        # Exit with appropriate code
        sys.exit(0 if results['validation_passed'] else 1)
        
    except Exception as e:
        logger.error(f"Baseline validation failed with error: {e}", exc_info=True)
        sys.exit(1)
