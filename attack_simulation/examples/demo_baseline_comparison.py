"""
Demo script for baseline comparison functionality
Demonstrates how to run baseline simulations and compare with attack simulations
"""

import sys
import os
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from attack_simulation.metrics.comparison_analyzer import ComparisonAnalyzer, ComparisonMetrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_baseline_comparison():
    """
    Demonstrate baseline vs attack comparison analysis
    """
    logger.info("=" * 80)
    logger.info("BASELINE COMPARISON DEMO")
    logger.info("=" * 80)
    
    # Example session directories (these would be created by actual simulations)
    baseline_session = "./output/baseline/session_baseline_20241110_120000"
    attack_session = "./output/attack/session_attack_20241110_130000"
    
    # Check if example data exists
    if not os.path.exists(baseline_session):
        logger.warning(f"Baseline session not found: {baseline_session}")
        logger.info("Creating example baseline session data...")
        create_example_baseline_data(baseline_session)
    
    if not os.path.exists(attack_session):
        logger.warning(f"Attack session not found: {attack_session}")
        logger.info("Creating example attack session data...")
        create_example_attack_data(attack_session)
    
    # Initialize comparison analyzer
    logger.info("\n1. Initializing Comparison Analyzer")
    analyzer = ComparisonAnalyzer(
        baseline_session_dir=baseline_session,
        attack_session_dir=attack_session,
        output_dir="./output/comparison"
    )
    
    # Load simulation data
    logger.info("\n2. Loading Simulation Data")
    if not analyzer.load_simulation_data():
        logger.error("Failed to load simulation data")
        return
    
    # Calculate degradation difference
    logger.info("\n3. Calculating Degradation Difference")
    degradation_diff = analyzer.calculate_degradation_difference()
    logger.info(f"   Degradation Difference: {degradation_diff:.4f}%")
    
    # Compute acceleration factor
    logger.info("\n4. Computing Degradation Acceleration Factor")
    acceleration_factor = analyzer.compute_degradation_acceleration_factor()
    logger.info(f"   Acceleration Factor: {acceleration_factor:.2f}x")
    
    # Generate comparison metrics
    logger.info("\n5. Generating Comparison Metrics")
    metrics = analyzer.generate_comparison_metrics()
    logger.info(f"   Baseline Final SoH: {metrics.baseline_final_soh:.2f}%")
    logger.info(f"   Attack Final SoH: {metrics.attack_final_soh:.2f}%")
    logger.info(f"   Degradation Acceleration: {metrics.degradation_acceleration_factor:.2f}x")
    
    # Generate comparison report
    logger.info("\n6. Generating Comparison Report")
    report_path = analyzer.generate_comparison_report(metrics)
    logger.info(f"   Report saved to: {report_path}")
    
    # Export to CSV
    logger.info("\n7. Exporting Comparison to CSV")
    csv_path = analyzer.export_comparison_csv(metrics)
    logger.info(f"   CSV saved to: {csv_path}")
    
    logger.info("\n" + "=" * 80)
    logger.info("DEMO COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)


def create_example_baseline_data(session_dir: str):
    """
    Create example baseline simulation data for demonstration
    
    Args:
        session_dir: Directory to create example data in
    """
    import json
    import csv
    from pathlib import Path
    
    Path(session_dir).mkdir(parents=True, exist_ok=True)
    
    # Create summary.json
    summary = {
        "session_id": "baseline_20241110_120000",
        "total_cycles": 1000,
        "total_duration_hours": 2000.0,
        "initial_soh": 100.0,
        "final_soh": 99.0,
        "total_degradation": 1.0,
        "degradation_rate_per_cycle": 0.001,
        "average_voltage_deviation": 0.0,
        "average_current_deviation": 0.0
    }
    
    with open(os.path.join(session_dir, 'summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Create degradation_timeline.csv
    with open(os.path.join(session_dir, 'degradation_timeline.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'cycle_num', 'soh', 'voltage_stress', 
                        'current_stress', 'soc_stress', 'combined_stress'])
        
        # Generate example degradation timeline
        for i in range(0, 1001, 50):
            soh = 100.0 - (i * 0.001)
            writer.writerow([
                f"2024-11-10T12:{i%60:02d}:00",
                i,
                f"{soh:.4f}",
                "1.0",
                "1.0",
                "1.0",
                "1.0"
            ])
    
    logger.info(f"Created example baseline data in {session_dir}")


def create_example_attack_data(session_dir: str):
    """
    Create example attack simulation data for demonstration
    
    Args:
        session_dir: Directory to create example data in
    """
    import json
    import csv
    from pathlib import Path
    
    Path(session_dir).mkdir(parents=True, exist_ok=True)
    
    # Create summary.json
    summary = {
        "session_id": "attack_20241110_130000",
        "total_cycles": 1000,
        "total_duration_hours": 2000.0,
        "initial_soh": 100.0,
        "final_soh": 97.5,
        "total_degradation": 2.5,
        "degradation_rate_per_cycle": 0.0025,
        "average_voltage_deviation": 15.0,
        "average_current_deviation": 25.0
    }
    
    with open(os.path.join(session_dir, 'summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Create degradation_timeline.csv
    with open(os.path.join(session_dir, 'degradation_timeline.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'cycle_num', 'soh', 'voltage_stress',
                        'current_stress', 'soc_stress', 'combined_stress'])
        
        # Generate example degradation timeline (faster degradation)
        for i in range(0, 1001, 50):
            soh = 100.0 - (i * 0.0025)
            writer.writerow([
                f"2024-11-10T13:{i%60:02d}:00",
                i,
                f"{soh:.4f}",
                "1.5",
                "1.3",
                "1.0",
                "1.95"
            ])
    
    # Create manipulations.csv
    with open(os.path.join(session_dir, 'manipulations.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'parameter_name', 'original_value',
                        'modified_value', 'deviation_percent'])
        
        # Generate example manipulation events
        for i in range(0, 100):
            writer.writerow([
                f"2024-11-10T13:{i%60:02d}:00",
                f"limit_period_{i%3}",
                "32.0",
                "36.8",
                "15.0"
            ])
    
    logger.info(f"Created example attack data in {session_dir}")


if __name__ == "__main__":
    demo_baseline_comparison()
