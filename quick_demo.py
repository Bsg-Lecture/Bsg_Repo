#!/usr/bin/env python3
"""
Quick demo script - Runs a simple attack simulation without needing server
"""

import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_quick_demo():
    """Run a quick demonstration of the attack simulation"""
    
    print("=" * 70)
    print("🚀 EmuOCPP Attack Simulation - Quick Demo")
    print("=" * 70)
    print()
    
    try:
        # Import components
        from attack_simulation.core import AttackEngine, AttackConfig
        from attack_simulation.models import BatteryDegradationModel
        from attack_simulation.metrics import MetricsCollector
        
        print("✅ All components imported successfully")
        print()
        
        # Initialize components
        print("📋 Initializing components...")
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "attack_simulation", "config", "attack_config.yaml")
        config = AttackConfig.from_yaml(config_path)
        battery = BatteryDegradationModel(initial_capacity_ah=75.0)
        session_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        metrics = MetricsCollector("./output/demo", session_id)
        engine = AttackEngine(config, metrics)
        
        print(f"✅ Attack Engine: {config.strategy.value} strategy")
        print(f"✅ Battery Model: {battery.capacity_ah} Ah, SoH: {battery.soh:.2f}%")
        print(f"✅ Session ID: {session_id}")
        print()
        
        # Run simulation
        print("🔄 Running simulation (10 cycles)...")
        print("-" * 70)
        
        for cycle in range(10):
            # Create charging profile
            profile = {
                'voltage': 4.2,
                'current': 0.5,
                'soc_min': 20.0,
                'soc_max': 80.0
            }
            
            # Simulate battery degradation
            result = battery.simulate_charging_cycle(profile, duration_hours=2.0)
            
            # Log metrics
            metrics.log_charging_cycle(
                cycle_num=cycle + 1,
                profile=profile,
                duration=2.0,
                energy_kwh=50.0,
                soh_before=result.soh_before,
                soh_after=result.soh_after
            )
            metrics.log_degradation_event(result, cycle_num=cycle + 1)
            
            if (cycle + 1) % 5 == 0:
                print(f"Cycle {cycle + 1:2d}: SoH = {result.soh_after:.4f}% "
                      f"(degradation: {result.degradation_percent:.6f}%)")
        
        print("-" * 70)
        print()
        
        # Export results
        print("💾 Exporting results...")
        metrics.export_to_csv()
        summary = metrics.generate_summary_report()
        
        print()
        print("=" * 70)
        print("📊 SIMULATION RESULTS")
        print("=" * 70)
        print(f"Total Cycles:           {summary.total_cycles}")
        print(f"Initial SoH:            {summary.initial_soh:.2f}%")
        print(f"Final SoH:              {summary.final_soh:.4f}%")
        print(f"Total Degradation:      {summary.total_degradation:.4f}%")
        print(f"Degradation per Cycle:  {summary.degradation_rate_per_cycle:.6f}%")
        print()
        print(f"📁 Results saved to: {metrics.session_dir}")
        print("=" * 70)
        print()
        print("✅ Demo completed successfully!")
        print()
        print("Next steps:")
        print("  1. Check results in: ./output/demo/")
        print("  2. View CSV files for detailed data")
        print("  3. Read GETTING_STARTED.md for full simulation")
        print()
        
        return 0
        
    except Exception as e:
        print()
        print("❌ Error occurred:")
        print(f"   {str(e)}")
        print()
        print("Troubleshooting:")
        print("  1. Make sure you're in the EmuOCPP directory")
        print("  2. Check that all dependencies are installed: pip install -r requirements.txt")
        print("  3. See TROUBLESHOOTING.md for more help")
        print()
        logger.exception("Demo failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_quick_demo())
