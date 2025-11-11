"""
Demo script for MetricsCollector functionality
"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from attack_simulation.metrics.metrics_collector import MetricsCollector
from attack_simulation.models.battery_model import BatteryDegradationModel


def demo_metrics_collection():
    """Demonstrate metrics collection functionality"""
    
    print("=" * 70)
    print("MetricsCollector Demo")
    print("=" * 70)
    
    # Initialize metrics collector
    output_dir = "./output"
    session_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"\n1. Initializing MetricsCollector...")
    print(f"   Output directory: {output_dir}")
    print(f"   Session ID: {session_id}")
    
    collector = MetricsCollector(output_dir, session_id)
    print(f"   ✓ Session directory created: {collector.session_dir}")
    print(f"   ✓ CSV files initialized")
    
    # Save configuration
    print(f"\n2. Saving simulation configuration...")
    config = {
        'attack_enabled': True,
        'strategy': 'aggressive',
        'voltage_deviation_percent': 15.0,
        'current_deviation_percent': 20.0,
        'num_cycles': 10
    }
    collector.save_config(config)
    print(f"   ✓ Configuration saved")
    
    # Initialize battery model
    print(f"\n3. Running simulation with battery degradation model...")
    battery = BatteryDegradationModel(initial_capacity_ah=75.0)
    
    # Simulate charging cycles
    num_cycles = 10
    
    for cycle in range(1, num_cycles + 1):
        print(f"\n   Cycle {cycle}/{num_cycles}:")
        
        # Define charging profile (with attack manipulation)
        if cycle % 2 == 0:
            # Aggressive attack profile
            profile = {
                'voltage': 4.2,  # High voltage
                'current': 1.0,  # High current
                'soc_min': 10.0,  # Low SoC
                'soc_max': 95.0   # High SoC
            }
            
            # Log manipulation
            collector.log_manipulation(
                timestamp=datetime.now(),
                original={'voltage': 3.7},
                modified={'voltage': 4.2},
                parameter_name='voltage',
                original_value=3.7,
                modified_value=4.2,
                deviation_percent=13.5
            )
            print(f"      - Attack profile applied (voltage: 4.2V)")
        else:
            # Normal profile
            profile = {
                'voltage': 3.7,
                'current': 0.5,
                'soc_min': 20.0,
                'soc_max': 80.0
            }
            print(f"      - Normal profile applied (voltage: 3.7V)")
        
        # Simulate charging cycle
        soh_before = battery.soh
        degradation_result = battery.simulate_charging_cycle(
            profile=profile,
            duration_hours=2.0
        )
        
        # Log charging cycle
        collector.log_charging_cycle(
            cycle_num=cycle,
            profile=profile,
            duration=2.0,
            energy_kwh=50.0,
            soh_before=soh_before,
            soh_after=battery.soh
        )
        
        # Log degradation event
        collector.log_degradation_event(degradation_result, cycle_num=cycle)
        
        print(f"      - SoH: {soh_before:.2f}% → {battery.soh:.2f}%")
        print(f"      - Degradation: {degradation_result.degradation_percent:.4f}%")
        print(f"      - Combined stress: {degradation_result.combined_stress_factor:.4f}")
    
    # Export metrics to CSV
    print(f"\n4. Exporting metrics to CSV files...")
    collector.export_to_csv()
    print(f"   ✓ Manipulations exported: {len(collector.manipulations)} events")
    print(f"   ✓ Charging cycles exported: {len(collector.charging_cycles)} cycles")
    print(f"   ✓ Degradation events exported: {len(collector.degradation_events)} events")
    
    # Generate summary report
    print(f"\n5. Generating summary report...")
    summary = collector.generate_summary_report()
    
    print(f"\n   Summary Statistics:")
    print(f"   -------------------")
    print(f"   Session ID: {summary.session_id}")
    print(f"   Total cycles: {summary.total_cycles}")
    print(f"   Total duration: {summary.total_duration_hours:.1f} hours")
    print(f"   Initial SoH: {summary.initial_soh:.2f}%")
    print(f"   Final SoH: {summary.final_soh:.2f}%")
    print(f"   Total degradation: {summary.total_degradation:.4f}%")
    print(f"   Degradation rate: {summary.degradation_rate_per_cycle:.6f}% per cycle")
    print(f"   Avg voltage deviation: {summary.average_voltage_deviation:.2f}%")
    
    # Display output files
    print(f"\n6. Output files created:")
    print(f"   -------------------")
    print(f"   Session directory: {collector.session_dir}")
    print(f"   - config.json")
    print(f"   - manipulations.csv")
    print(f"   - charging_cycles.csv")
    print(f"   - degradation_timeline.csv")
    print(f"   - summary.json")
    print(f"   - plots/ (directory for visualizations)")
    
    print(f"\n" + "=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)
    
    return collector


if __name__ == '__main__':
    demo_metrics_collection()
