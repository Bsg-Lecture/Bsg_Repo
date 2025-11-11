"""
Demo script for Visualization Engine
Demonstrates generating plots and reports from simulation data
"""

import os
import sys
import logging
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from attack_simulation.metrics.metrics_collector import MetricsCollector
from attack_simulation.visualization.visualization_engine import VisualizationEngine
from attack_simulation.models.battery_model import BatteryDegradationModel, DegradationResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_simulation_data(metrics_collector, num_cycles=100):
    """
    Create sample simulation data for visualization testing
    
    Args:
        metrics_collector: MetricsCollector instance
        num_cycles: Number of charging cycles to simulate
    """
    logger.info(f"Creating sample simulation data with {num_cycles} cycles")
    
    # Initialize battery model
    battery = BatteryDegradationModel(initial_capacity_ah=75.0)
    
    # Simulate charging cycles with varying parameters
    for cycle in range(num_cycles):
        # Simulate voltage and current with some variation
        voltage = 4.0 + (cycle / num_cycles) * 0.3  # Gradually increase voltage
        current = 50.0 + (cycle % 10) * 2.0  # Vary current
        soc_min = 20.0
        soc_max = 80.0
        duration = 1.5
        energy = 50.0
        
        # Calculate degradation
        soh_before = battery.soh
        
        # Create charging profile
        profile = {
            'voltage': voltage,
            'current': current,
            'soc_min': soc_min,
            'soc_max': soc_max
        }
        
        # Simulate charging cycle
        degradation_result = battery.simulate_charging_cycle(
            profile=profile,
            duration_hours=duration
        )
        
        soh_after = battery.soh
        
        metrics_collector.log_charging_cycle(
            cycle_num=cycle,
            profile=profile,
            duration=duration,
            energy_kwh=energy,
            soh_before=soh_before,
            soh_after=soh_after
        )
        
        # Log degradation event
        metrics_collector.log_degradation_event(degradation_result, cycle_num=cycle)
        
        # Log some manipulations (simulate attack)
        if cycle % 5 == 0:
            original_voltage = voltage - 0.2
            deviation = ((voltage - original_voltage) / original_voltage) * 100
            
            metrics_collector.log_manipulation(
                timestamp=pd.Timestamp.now(),
                original={'voltage': original_voltage},
                modified={'voltage': voltage},
                parameter_name='voltage',
                original_value=original_voltage,
                modified_value=voltage,
                deviation_percent=deviation
            )
        
        if cycle % 7 == 0:
            original_current = current - 5.0
            deviation = ((current - original_current) / original_current) * 100
            
            metrics_collector.log_manipulation(
                timestamp=pd.Timestamp.now(),
                original={'current': original_current},
                modified={'current': current},
                parameter_name='current',
                original_value=original_current,
                modified_value=current,
                deviation_percent=deviation
            )
    
    logger.info(f"Sample data created: {num_cycles} cycles, Final SoH: {battery.soh:.2f}%")


def demo_visualization_engine():
    """
    Demonstrate the Visualization Engine functionality
    """
    logger.info("=" * 80)
    logger.info("VISUALIZATION ENGINE DEMO")
    logger.info("=" * 80)
    
    # Create output directory
    output_dir = "./output/demo_visualization"
    session_id = "demo_viz_001"
    
    # Initialize metrics collector
    logger.info("\n1. Initializing MetricsCollector...")
    metrics = MetricsCollector(output_dir=output_dir, session_id=session_id)
    
    # Create sample simulation data
    logger.info("\n2. Creating sample simulation data...")
    create_sample_simulation_data(metrics, num_cycles=100)
    
    # Export metrics to CSV
    logger.info("\n3. Exporting metrics to CSV...")
    metrics.export_to_csv()
    
    # Generate summary report
    logger.info("\n4. Generating summary report...")
    summary = metrics.generate_summary_report()
    logger.info(f"   - Total Cycles: {summary.total_cycles}")
    logger.info(f"   - Final SoH: {summary.final_soh:.2f}%")
    logger.info(f"   - Total Degradation: {summary.total_degradation:.4f}%")
    
    # Initialize visualization engine
    logger.info("\n5. Initializing VisualizationEngine...")
    viz_engine = VisualizationEngine(metrics)
    
    # Generate individual plots
    logger.info("\n6. Generating SoH timeline plot...")
    viz_engine.plot_soh_timeline()
    
    logger.info("\n7. Generating parameter deviation plots...")
    viz_engine.plot_parameter_deviations()
    
    logger.info("\n8. Generating stress factors plot...")
    viz_engine.plot_stress_factors()
    
    # Generate reports
    logger.info("\n9. Generating LaTeX table...")
    viz_engine.generate_latex_table()
    
    logger.info("\n10. Generating HTML report...")
    viz_engine.generate_html_report()
    
    # Generate all visualizations at once
    logger.info("\n11. Testing generate_all_visualizations()...")
    viz_engine.generate_all_visualizations()
    
    logger.info("\n" + "=" * 80)
    logger.info("DEMO COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)
    logger.info(f"\nOutput directory: {metrics.session_dir}")
    logger.info(f"Plots directory: {viz_engine.output_dir}")
    logger.info("\nGenerated files:")
    logger.info("  - soh_timeline.png/pdf")
    logger.info("  - parameter_deviations.png/pdf")
    logger.info("  - stress_factors.png/pdf")
    logger.info("  - summary_table.tex")
    logger.info("  - report.html")


def demo_baseline_comparison_plot():
    """
    Demonstrate baseline vs attack comparison plot
    """
    logger.info("\n" + "=" * 80)
    logger.info("BASELINE COMPARISON PLOT DEMO")
    logger.info("=" * 80)
    
    # Create baseline simulation data
    output_dir = "./output/demo_comparison"
    baseline_session = "baseline_001"
    attack_session = "attack_001"
    
    logger.info("\n1. Creating baseline simulation data...")
    baseline_metrics = MetricsCollector(output_dir=output_dir, session_id=baseline_session)
    create_sample_simulation_data(baseline_metrics, num_cycles=100)
    baseline_metrics.export_to_csv()
    
    logger.info("\n2. Creating attack simulation data...")
    attack_metrics = MetricsCollector(output_dir=output_dir, session_id=attack_session)
    
    # Create attack data with more aggressive degradation
    battery = BatteryDegradationModel(initial_capacity_ah=75.0)
    for cycle in range(100):
        voltage = 4.2 + (cycle / 100) * 0.4  # Higher voltage (attack)
        current = 60.0 + (cycle % 10) * 3.0  # Higher current (attack)
        soc_min = 10.0  # Worse SoC range
        soc_max = 95.0
        duration = 1.5
        energy = 55.0
        
        soh_before = battery.soh
        
        profile = {
            'voltage': voltage,
            'current': current,
            'soc_min': soc_min,
            'soc_max': soc_max
        }
        
        degradation_result = battery.simulate_charging_cycle(
            profile=profile,
            duration_hours=duration
        )
        soh_after = battery.soh
        
        attack_metrics.log_charging_cycle(
            cycle_num=cycle,
            profile=profile,
            duration=duration,
            energy_kwh=energy,
            soh_before=soh_before,
            soh_after=soh_after
        )
        
        attack_metrics.log_degradation_event(degradation_result, cycle_num=cycle)
    
    attack_metrics.export_to_csv()
    
    logger.info("\n3. Generating comparison plot...")
    viz_engine = VisualizationEngine(attack_metrics)
    
    # Load baseline and attack degradation data
    baseline_csv = Path(baseline_metrics.session_dir) / 'degradation_timeline.csv'
    attack_csv = Path(attack_metrics.session_dir) / 'degradation_timeline.csv'
    
    baseline_data = pd.read_csv(baseline_csv)
    attack_data = pd.read_csv(attack_csv)
    
    viz_engine.plot_baseline_comparison(baseline_data, attack_data)
    
    logger.info("\n" + "=" * 80)
    logger.info("COMPARISON DEMO COMPLETED")
    logger.info("=" * 80)
    logger.info(f"\nComparison plot saved in: {viz_engine.output_dir}")


if __name__ == "__main__":
    try:
        # Run main visualization demo
        demo_visualization_engine()
        
        # Run baseline comparison demo
        demo_baseline_comparison_plot()
        
        logger.info("\n✅ All demos completed successfully!")
        
    except Exception as e:
        logger.error(f"\n❌ Demo failed: {e}", exc_info=True)
        sys.exit(1)
