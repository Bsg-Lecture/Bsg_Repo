#!/usr/bin/env python3
"""
Comparison Analysis Runner
Compares baseline and attack simulation results
"""

import sys
import os
import argparse
import logging

# Add attack_simulation to path
sys.path.insert(0, os.path.dirname(__file__))

from attack_simulation.metrics.comparison_analyzer import ComparisonAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_comparison_analysis(baseline_dir: str, attack_dir: str, output_dir: str = None):
    """
    Run comparison analysis between baseline and attack simulations
    
    Args:
        baseline_dir: Path to baseline simulation session directory
        attack_dir: Path to attack simulation session directory
        output_dir: Optional output directory for comparison results
    """
    logger.info("=" * 80)
    logger.info("BASELINE VS ATTACK COMPARISON ANALYSIS")
    logger.info("=" * 80)
    
    # Validate input directories
    if not os.path.exists(baseline_dir):
        logger.error(f"Baseline directory not found: {baseline_dir}")
        return False
    
    if not os.path.exists(attack_dir):
        logger.error(f"Attack directory not found: {attack_dir}")
        return False
    
    logger.info(f"\nBaseline session: {baseline_dir}")
    logger.info(f"Attack session: {attack_dir}")
    
    # Initialize comparison analyzer
    logger.info(f"\nInitializing comparison analyzer...")
    analyzer = ComparisonAnalyzer(
        baseline_session_dir=baseline_dir,
        attack_session_dir=attack_dir,
        output_dir=output_dir
    )
    
    # Load simulation data
    logger.info(f"\nLoading simulation data...")
    if not analyzer.load_simulation_data():
        logger.error("Failed to load simulation data")
        return False
    
    logger.info("Simulation data loaded successfully")
    
    # Calculate metrics
    logger.info(f"\nCalculating comparison metrics...")
    
    # Degradation difference
    degradation_diff = analyzer.calculate_degradation_difference()
    logger.info(f"  Degradation difference: {degradation_diff:.4f}%")
    
    # Acceleration factor
    acceleration_factor = analyzer.compute_degradation_acceleration_factor()
    logger.info(f"  Acceleration factor: {acceleration_factor:.2f}x")
    
    # Generate comprehensive metrics
    logger.info(f"\nGenerating comprehensive comparison metrics...")
    metrics = analyzer.generate_comparison_metrics()
    
    logger.info(f"\nComparison Summary:")
    logger.info(f"  Baseline:")
    logger.info(f"    - Final SoH: {metrics.baseline_final_soh:.2f}%")
    logger.info(f"    - Total Degradation: {metrics.baseline_total_degradation:.4f}%")
    logger.info(f"    - Degradation Rate: {metrics.baseline_degradation_rate:.6f}% per cycle")
    
    logger.info(f"  Attack:")
    logger.info(f"    - Final SoH: {metrics.attack_final_soh:.2f}%")
    logger.info(f"    - Total Degradation: {metrics.attack_total_degradation:.4f}%")
    logger.info(f"    - Degradation Rate: {metrics.attack_degradation_rate:.6f}% per cycle")
    
    logger.info(f"  Impact:")
    logger.info(f"    - Degradation Difference: {metrics.degradation_difference:.4f}%")
    logger.info(f"    - Acceleration Factor: {metrics.degradation_acceleration_factor:.2f}x")
    
    if metrics.baseline_cycles_to_90_percent and metrics.attack_cycles_to_90_percent:
        speedup = metrics.baseline_cycles_to_90_percent / metrics.attack_cycles_to_90_percent
        logger.info(f"    - Attack reached 90% SoH {speedup:.2f}x faster")
    
    # Generate reports
    logger.info(f"\nGenerating comparison report...")
    report_path = analyzer.generate_comparison_report(metrics)
    logger.info(f"Report saved to: {report_path}")
    
    # Export to CSV
    logger.info(f"\nExporting comparison to CSV...")
    csv_path = analyzer.export_comparison_csv(metrics)
    logger.info(f"CSV saved to: {csv_path}")
    
    logger.info(f"\nAll comparison results saved to: {analyzer.output_dir}")
    
    logger.info("\n" + "=" * 80)
    logger.info("COMPARISON ANALYSIS COMPLETED")
    logger.info("=" * 80)
    
    return True


def find_latest_session(base_dir: str, pattern: str = "session_") -> str:
    """
    Find the latest session directory in a base directory
    
    Args:
        base_dir: Base directory to search
        pattern: Session directory name pattern
        
    Returns:
        Path to latest session directory or None
    """
    if not os.path.exists(base_dir):
        return None
    
    sessions = [
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d)) and d.startswith(pattern)
    ]
    
    if not sessions:
        return None
    
    # Sort by name (assumes timestamp in name)
    sessions.sort(reverse=True)
    return os.path.join(base_dir, sessions[0])


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Compare baseline and attack simulation results'
    )
    parser.add_argument(
        '--baseline',
        type=str,
        required=False,
        help='Path to baseline simulation session directory'
    )
    parser.add_argument(
        '--attack',
        type=str,
        required=False,
        help='Path to attack simulation session directory'
    )
    parser.add_argument(
        '--baseline-dir',
        type=str,
        default='./output/baseline',
        help='Base directory for baseline simulations (will use latest session)'
    )
    parser.add_argument(
        '--attack-dir',
        type=str,
        default='./output/attack',
        help='Base directory for attack simulations (will use latest session)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output directory for comparison results'
    )
    
    args = parser.parse_args()
    
    # Determine baseline session directory
    if args.baseline:
        baseline_session = args.baseline
    else:
        logger.info(f"Finding latest baseline session in: {args.baseline_dir}")
        baseline_session = find_latest_session(args.baseline_dir)
        if not baseline_session:
            logger.error(f"No baseline sessions found in: {args.baseline_dir}")
            logger.info("Run a baseline simulation first using: python run_baseline_simulation.py")
            sys.exit(1)
        logger.info(f"Using baseline session: {baseline_session}")
    
    # Determine attack session directory
    if args.attack:
        attack_session = args.attack
    else:
        logger.info(f"Finding latest attack session in: {args.attack_dir}")
        attack_session = find_latest_session(args.attack_dir)
        if not attack_session:
            logger.error(f"No attack sessions found in: {args.attack_dir}")
            logger.info("Run an attack simulation first using: python attack_simulator.py")
            sys.exit(1)
        logger.info(f"Using attack session: {attack_session}")
    
    # Run comparison analysis
    try:
        success = run_comparison_analysis(
            baseline_dir=baseline_session,
            attack_dir=attack_session,
            output_dir=args.output
        )
        
        if not success:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error running comparison analysis: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
