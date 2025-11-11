#!/usr/bin/env python3
"""
Baseline Simulation Runner
Runs attack simulation in baseline mode (transparent proxy, no manipulation)
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# Add attack_simulation to path
sys.path.insert(0, os.path.dirname(__file__))

from attack_simulation.core.attack_engine import AttackEngine, AttackConfig
from attack_simulation.models.battery_model import BatteryDegradationModel, DegradationParameters
from attack_simulation.metrics.metrics_collector import MetricsCollector
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_baseline_simulation(config_path: str, cycles: int = 1000, output_dir: str = None):
    """
    Run baseline simulation with no attack manipulation
    
    Args:
        config_path: Path to baseline configuration file
        cycles: Number of charging cycles to simulate
        output_dir: Optional output directory override
    """
    logger.info("=" * 80)
    logger.info("BASELINE SIMULATION")
    logger.info("=" * 80)
    
    # Load configuration
    logger.info(f"Loading configuration from: {config_path}")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Extract configuration sections
    attack_cfg = config.get('attack_config', {})
    battery_cfg = config.get('battery_model', {})
    metrics_cfg = config.get('metrics', {})
    simulation_cfg = config.get('simulation', {})
    
    # Verify attack is disabled for baseline
    if attack_cfg.get('enabled', False):
        logger.warning("Attack is enabled in config! Forcing disabled for baseline simulation.")
        attack_cfg['enabled'] = False
    
    # Set output directory
    if output_dir:
        metrics_cfg['output_dir'] = output_dir
    else:
        output_dir = metrics_cfg.get('output_dir', './output/baseline')
    
    # Override cycles if specified
    if cycles:
        simulation_cfg['cycles'] = cycles
    
    cycles = simulation_cfg.get('cycles', 1000)
    cycle_duration = simulation_cfg.get('cycle_duration_hours', 2.0)
    
    logger.info(f"Baseline simulation configuration:")
    logger.info(f"  - Cycles: {cycles}")
    logger.info(f"  - Cycle duration: {cycle_duration} hours")
    logger.info(f"  - Output directory: {output_dir}")
    logger.info(f"  - Attack enabled: {attack_cfg.get('enabled', False)}")
    
    # Initialize components
    session_id = f"baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    logger.info(f"\nInitializing simulation components...")
    logger.info(f"Session ID: {session_id}")
    
    # Initialize metrics collector
    metrics_collector = MetricsCollector(
        output_dir=output_dir,
        session_id=session_id
    )
    
    # Initialize attack engine (disabled for baseline)
    attack_config = AttackConfig.from_dict(attack_cfg)
    attack_engine = AttackEngine(
        config=attack_config,
        metrics_collector=metrics_collector
    )
    
    # Initialize battery degradation model
    initial_capacity = battery_cfg.get('initial_capacity_ah', 75.0)
    degradation_params_cfg = battery_cfg.get('degradation_params', {})
    
    degradation_params = DegradationParameters(
        optimal_voltage=degradation_params_cfg.get('optimal_voltage', 3.7),
        voltage_stress_coefficient=degradation_params_cfg.get('voltage_stress_coefficient', 0.5),
        optimal_c_rate=degradation_params_cfg.get('optimal_c_rate', 0.5),
        current_stress_coefficient=degradation_params_cfg.get('current_stress_coefficient', 0.3),
        optimal_soc_min=degradation_params_cfg.get('optimal_soc_min', 20.0),
        optimal_soc_max=degradation_params_cfg.get('optimal_soc_max', 80.0),
        soc_stress_coefficient=degradation_params_cfg.get('soc_stress_coefficient', 0.2),
        base_degradation_per_cycle=degradation_params_cfg.get('base_degradation_per_cycle', 0.001)
    )
    
    battery_model = BatteryDegradationModel(
        initial_capacity_ah=initial_capacity,
        params=degradation_params
    )
    
    logger.info(f"Battery model initialized: {initial_capacity} Ah capacity, SoH: {battery_model.soh:.2f}%")
    
    # Save configuration
    metrics_collector.save_config(config)
    
    # Run simulation
    logger.info(f"\nStarting baseline simulation...")
    logger.info(f"Simulating {cycles} charging cycles...")
    
    for cycle_num in range(1, cycles + 1):
        # Simulate normal charging profile (no manipulation)
        normal_profile = {
            'voltage': degradation_params.optimal_voltage,
            'current': initial_capacity * degradation_params.optimal_c_rate,
            'soc_min': degradation_params.optimal_soc_min,
            'soc_max': degradation_params.optimal_soc_max
        }
        
        # Get SoH before cycle
        soh_before = battery_model.soh
        
        # Simulate charging cycle
        degradation_result = battery_model.simulate_charging_cycle(
            profile=normal_profile,
            duration_hours=cycle_duration
        )
        
        # Log cycle data
        energy_kwh = (normal_profile['soc_max'] - normal_profile['soc_min']) / 100.0 * initial_capacity * 3.7 / 1000.0
        
        metrics_collector.log_charging_cycle(
            cycle_num=cycle_num,
            profile=normal_profile,
            duration=cycle_duration,
            energy_kwh=energy_kwh,
            soh_before=soh_before,
            soh_after=battery_model.soh
        )
        
        # Log degradation event
        metrics_collector.log_degradation_event(
            degradation_result=degradation_result,
            cycle_num=cycle_num
        )
        
        # Progress logging
        if cycle_num % 100 == 0:
            logger.info(f"  Cycle {cycle_num}/{cycles}: SoH = {battery_model.soh:.4f}%")
    
    logger.info(f"\nSimulation completed!")
    logger.info(f"Final SoH: {battery_model.soh:.4f}%")
    logger.info(f"Total degradation: {100.0 - battery_model.soh:.4f}%")
    
    # Export metrics
    logger.info(f"\nExporting metrics...")
    metrics_collector.export_to_csv()
    
    # Generate summary report
    summary = metrics_collector.generate_summary_report()
    
    logger.info(f"\nBaseline Simulation Summary:")
    logger.info(f"  - Session ID: {summary.session_id}")
    logger.info(f"  - Total Cycles: {summary.total_cycles}")
    logger.info(f"  - Initial SoH: {summary.initial_soh:.2f}%")
    logger.info(f"  - Final SoH: {summary.final_soh:.2f}%")
    logger.info(f"  - Total Degradation: {summary.total_degradation:.4f}%")
    logger.info(f"  - Degradation Rate: {summary.degradation_rate_per_cycle:.6f}% per cycle")
    
    logger.info(f"\nResults saved to: {metrics_collector.session_dir}")
    
    logger.info("=" * 80)
    logger.info("BASELINE SIMULATION COMPLETED")
    logger.info("=" * 80)
    
    return metrics_collector.session_dir


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Run baseline simulation (no attack manipulation)'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='attack_simulation/config/baseline_config.yaml',
        help='Path to baseline configuration file'
    )
    parser.add_argument(
        '--cycles',
        type=int,
        default=1000,
        help='Number of charging cycles to simulate'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for results'
    )
    
    args = parser.parse_args()
    
    # Check if config file exists
    if not os.path.exists(args.config):
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)
    
    # Run baseline simulation
    try:
        session_dir = run_baseline_simulation(
            config_path=args.config,
            cycles=args.cycles,
            output_dir=args.output_dir
        )
        logger.info(f"\nBaseline simulation session: {session_dir}")
        
    except Exception as e:
        logger.error(f"Error running baseline simulation: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
