#!/usr/bin/env python3
"""
Charging Profile Poisoning Attack Simulator

Main entry point for running attack simulations on OCPP charging infrastructure.

This tool simulates charging profile poisoning attacks on OCPP-based EV charging
infrastructure to demonstrate security vulnerabilities and quantify battery
degradation impact.

For research and educational purposes only.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add attack_simulation to path
sys.path.insert(0, str(Path(__file__).parent))

from attack_simulation.core import ScenarioManager

__version__ = "1.0.0"
__author__ = "EmuOCPP Research Team"


def setup_logging(log_level: str, log_file: str = None, quiet: bool = False):
    """
    Configure logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        quiet: If True, suppress console output
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    handlers = []
    
    # Console handler (unless quiet mode)
    if not quiet:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                            datefmt='%H:%M:%S')
        )
        handlers.append(console_handler)
    
    # File handler
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=level,
        handlers=handlers
    )


def parse_arguments():
    """
    Parse command-line arguments
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        prog='attack_simulator',
        description="""
Charging Profile Poisoning Attack Simulator

Simulates malicious manipulation of OCPP charging profile parameters to
demonstrate security vulnerabilities and quantify battery degradation impact.

This tool is designed for research and educational purposes only.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run single scenario with default config
  python attack_simulator.py --config attack_simulation/config/attack_config.yaml
  
  # Run baseline simulation (no attack)
  python attack_simulator.py --config attack_simulation/config/baseline_config.yaml
  
  # Run batch of scenarios for comparative analysis
  python attack_simulator.py --batch attack_simulation/config/batch_config.yaml
  
  # Run with debug logging and custom output directory
  python attack_simulator.py --config attack_simulation/config/attack_config.yaml \\
      --log-level DEBUG --output-dir ./results/experiment_001
  
  # Run with custom cycle count
  python attack_simulator.py --config attack_simulation/config/attack_config.yaml \\
      --cycles 2000
  
  # Quick baseline comparison workflow:
  python run_baseline_simulation.py --cycles 1000
  python attack_simulator.py --config attack_simulation/config/attack_config.yaml --cycles 1000
  python run_comparison_analysis.py

Configuration Files:
  attack_config.yaml    - Single attack scenario configuration
  baseline_config.yaml  - Baseline (no attack) configuration
  batch_config.yaml     - Multiple scenarios for batch execution
  detection_config.yaml - Anomaly detection configuration

Documentation:
  attack_simulation/README.md                    - Main documentation
  BASELINE_COMPARISON_QUICKSTART.md              - Quick start guide
  attack_simulation/SCENARIO_MANAGER_QUICKSTART.md - Batch execution guide

For more information, visit: https://github.com/vfg27/EmuOCPP
        """
    )
    
    # Version information
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s v{__version__} by {__author__}'
    )
    
    # Configuration options
    config_group = parser.add_argument_group('Configuration Options')
    config_group.add_argument(
        '--config',
        type=str,
        metavar='FILE',
        help='Path to attack configuration file (single scenario)'
    )
    
    config_group.add_argument(
        '--batch',
        type=str,
        metavar='FILE',
        help='Path to batch configuration file (multiple scenarios)'
    )
    
    # Simulation options
    sim_group = parser.add_argument_group('Simulation Options')
    sim_group.add_argument(
        '--cycles',
        type=int,
        metavar='N',
        help='Number of charging cycles to simulate (overrides config file)'
    )
    
    sim_group.add_argument(
        '--output-dir',
        type=str,
        metavar='DIR',
        default='./output',
        help='Output directory for results (default: ./output)'
    )
    
    sim_group.add_argument(
        '--session-id',
        type=str,
        metavar='ID',
        help='Custom session ID for output files (default: auto-generated)'
    )
    
    # Logging options
    log_group = parser.add_argument_group('Logging Options')
    log_group.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level (default: INFO)'
    )
    
    log_group.add_argument(
        '--log-file',
        type=str,
        metavar='FILE',
        help='Path to log file (default: logs/attack_simulation.log)'
    )
    
    log_group.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress console output (log to file only)'
    )
    
    # Advanced options
    advanced_group = parser.add_argument_group('Advanced Options')
    advanced_group.add_argument(
        '--no-plots',
        action='store_true',
        help='Skip plot generation (faster execution)'
    )
    
    advanced_group.add_argument(
        '--export-format',
        type=str,
        nargs='+',
        choices=['csv', 'json', 'both'],
        default=['both'],
        help='Export format for metrics (default: both)'
    )
    
    advanced_group.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate configuration without running simulation'
    )
    
    return parser.parse_args()


async def run_single_scenario(config_path: str, output_dir: str):
    """
    Run a single attack scenario
    
    Args:
        config_path: Path to configuration file
        output_dir: Output directory for results
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Running single scenario: {config_path}")
    
    # Implementation will be completed in later tasks
    logger.warning("Single scenario execution not yet implemented")
    logger.info("This will be implemented in task 2 (MITM Proxy) and task 3 (Attack Engine)")


async def run_batch_scenarios(batch_config_path: str):
    """
    Run batch of attack scenarios
    
    Args:
        batch_config_path: Path to batch configuration file
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Running batch scenarios: {batch_config_path}")
    
    try:
        manager = ScenarioManager(batch_config_path)
        results = await manager.run_batch()
        
        logger.info(f"Batch execution complete: {len(results)} scenarios")
        
        # Generate comparison report
        manager.generate_comparison_report(results)
        
    except Exception as e:
        logger.error(f"Batch execution failed: {e}", exc_info=True)
        sys.exit(1)


def validate_configuration(args):
    """
    Validate command-line arguments and configuration files
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        True if valid, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    # Check mutual exclusivity
    if not args.config and not args.batch:
        logger.error("Either --config or --batch must be specified")
        logger.info("Use --help for usage information")
        return False
    
    if args.config and args.batch:
        logger.error("Cannot specify both --config and --batch")
        return False
    
    # Check file existence
    config_file = args.config or args.batch
    if not Path(config_file).exists():
        logger.error(f"Configuration file not found: {config_file}")
        return False
    
    # Validate cycles if specified
    if args.cycles and args.cycles <= 0:
        logger.error(f"Invalid cycle count: {args.cycles} (must be positive)")
        return False
    
    return True


def print_banner():
    """Print application banner"""
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║  Charging Profile Poisoning Attack Simulator v{__version__:<15}║
║  {__author__:<58}║
║                                                              ║
║  Research Tool - For Educational Purposes Only               ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """
    Main entry point
    """
    args = parse_arguments()
    
    # Setup logging
    default_log_file = args.log_file or './logs/attack_simulation.log'
    setup_logging(args.log_level, default_log_file, args.quiet)
    logger = logging.getLogger(__name__)
    
    # Print banner (unless quiet)
    if not args.quiet:
        print_banner()
    
    logger.info(f"Attack Simulator v{__version__} starting...")
    logger.info("=" * 60)
    
    # Validate configuration
    if not validate_configuration(args):
        sys.exit(1)
    
    # Dry run mode
    if args.dry_run:
        logger.info("Dry run mode: Configuration validated successfully")
        logger.info("No simulation will be executed")
        sys.exit(0)
    
    # Log configuration
    logger.info(f"Configuration file: {args.config or args.batch}")
    logger.info(f"Output directory: {args.output_dir}")
    if args.cycles:
        logger.info(f"Cycle count override: {args.cycles}")
    if args.session_id:
        logger.info(f"Session ID: {args.session_id}")
    logger.info("=" * 60)
    
    # Run simulation
    try:
        if args.batch:
            asyncio.run(run_batch_scenarios(args.batch))
        else:
            asyncio.run(run_single_scenario(args.config, args.output_dir))
            
        logger.info("=" * 60)
        logger.info("[OK] Simulation completed successfully")
        logger.info(f"Results saved to: {args.output_dir}")
        
    except KeyboardInterrupt:
        logger.warning("\n⚠ Simulation interrupted by user")
        sys.exit(130)  # Standard exit code for SIGINT
    except FileNotFoundError as e:
        logger.error(f"✗ File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"✗ Simulation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
