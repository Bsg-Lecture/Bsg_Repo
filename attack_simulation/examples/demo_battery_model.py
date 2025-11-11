"""
Demonstration of Battery Degradation Model
Shows how battery health degrades under different charging conditions
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from attack_simulation.models.battery_model import (
    BatteryDegradationModel, DegradationParameters
)


def demo_optimal_charging():
    """Demonstrate battery degradation with optimal charging parameters"""
    print("\n" + "="*70)
    print("DEMO 1: Optimal Charging Conditions")
    print("="*70)
    
    model = BatteryDegradationModel(initial_capacity_ah=75.0)
    
    # Optimal charging profile
    profile = {
        'voltage': 3.7,      # Optimal voltage
        'current': 0.5,      # Optimal C-rate
        'soc_min': 20.0,     # Optimal SoC range
        'soc_max': 80.0
    }
    
    print(f"\nInitial State:")
    print(f"  SoH: {model.soh:.2f}%")
    print(f"  Capacity: {model.get_remaining_capacity():.2f} Ah")
    
    print(f"\nCharging Profile:")
    print(f"  Voltage: {profile['voltage']} V")
    print(f"  Current: {profile['current']} C")
    print(f"  SoC Range: {profile['soc_min']}-{profile['soc_max']}%")
    
    # Simulate 100 cycles
    print(f"\nSimulating 100 charging cycles...")
    for i in range(100):
        result = model.simulate_charging_cycle(profile, duration_hours=1.0)
        if (i + 1) % 20 == 0:
            print(f"  Cycle {i+1}: SoH = {result.soh_after:.4f}%, "
                  f"Degradation = {result.degradation_percent:.6f}%")
    
    print(f"\nFinal State:")
    print(f"  SoH: {model.soh:.4f}%")
    print(f"  Capacity: {model.get_remaining_capacity():.2f} Ah")
    print(f"  Total Cycles: {model.cycle_count}")
    print(f"  Total Degradation: {100.0 - model.soh:.4f}%")


def demo_aggressive_charging():
    """Demonstrate battery degradation with aggressive charging parameters"""
    print("\n" + "="*70)
    print("DEMO 2: Aggressive Charging (Attack Scenario)")
    print("="*70)
    
    model = BatteryDegradationModel(initial_capacity_ah=75.0)
    
    # Aggressive charging profile (simulating attack)
    profile = {
        'voltage': 4.3,      # High voltage (overstress)
        'current': 1.5,      # High C-rate
        'soc_min': 5.0,      # Low SoC (stress)
        'soc_max': 95.0      # High SoC (stress)
    }
    
    print(f"\nInitial State:")
    print(f"  SoH: {model.soh:.2f}%")
    print(f"  Capacity: {model.get_remaining_capacity():.2f} Ah")
    
    print(f"\nCharging Profile (Poisoned):")
    print(f"  Voltage: {profile['voltage']} V (HIGH)")
    print(f"  Current: {profile['current']} C (HIGH)")
    print(f"  SoC Range: {profile['soc_min']}-{profile['soc_max']}% (EXTREME)")
    
    # Simulate 100 cycles
    print(f"\nSimulating 100 charging cycles...")
    for i in range(100):
        result = model.simulate_charging_cycle(profile, duration_hours=1.0)
        if (i + 1) % 20 == 0:
            print(f"  Cycle {i+1}: SoH = {result.soh_after:.4f}%, "
                  f"Degradation = {result.degradation_percent:.6f}%, "
                  f"Stress = {result.combined_stress_factor:.2f}x")
    
    print(f"\nFinal State:")
    print(f"  SoH: {model.soh:.4f}%")
    print(f"  Capacity: {model.get_remaining_capacity():.2f} Ah")
    print(f"  Total Cycles: {model.cycle_count}")
    print(f"  Total Degradation: {100.0 - model.soh:.4f}%")


def demo_comparison():
    """Compare optimal vs aggressive charging side-by-side"""
    print("\n" + "="*70)
    print("DEMO 3: Baseline vs Attack Comparison")
    print("="*70)
    
    # Baseline model
    baseline = BatteryDegradationModel(initial_capacity_ah=75.0)
    baseline_profile = {
        'voltage': 3.7,
        'current': 0.5,
        'soc_min': 20.0,
        'soc_max': 80.0
    }
    
    # Attack model
    attack = BatteryDegradationModel(initial_capacity_ah=75.0)
    attack_profile = {
        'voltage': 4.3,
        'current': 1.5,
        'soc_min': 5.0,
        'soc_max': 95.0
    }
    
    print(f"\n{'Cycle':<10} {'Baseline SoH':<15} {'Attack SoH':<15} {'Difference':<15}")
    print("-" * 70)
    
    # Simulate 200 cycles
    for i in range(200):
        baseline_result = baseline.simulate_charging_cycle(baseline_profile, 1.0)
        attack_result = attack.simulate_charging_cycle(attack_profile, 1.0)
        
        if (i + 1) % 40 == 0:
            diff = baseline.soh - attack.soh
            print(f"{i+1:<10} {baseline.soh:<15.4f} {attack.soh:<15.4f} {diff:<15.4f}")
    
    print("\n" + "="*70)
    print("Summary:")
    print(f"  Baseline Final SoH: {baseline.soh:.4f}%")
    print(f"  Attack Final SoH: {attack.soh:.4f}%")
    print(f"  Additional Degradation from Attack: {baseline.soh - attack.soh:.4f}%")
    print(f"  Degradation Acceleration Factor: "
          f"{(100.0 - attack.soh) / (100.0 - baseline.soh):.2f}x")


def demo_stress_factors():
    """Demonstrate individual stress factor calculations"""
    print("\n" + "="*70)
    print("DEMO 4: Stress Factor Analysis")
    print("="*70)
    
    model = BatteryDegradationModel()
    
    print("\nVoltage Stress Factors:")
    voltages = [3.2, 3.5, 3.7, 4.0, 4.2, 4.4]
    for v in voltages:
        stress = model.calculate_voltage_stress_factor(v)
        print(f"  {v:.1f}V: {stress:.4f}x")
    
    print("\nCurrent Stress Factors:")
    currents = [0.2, 0.5, 0.8, 1.0, 1.5, 2.0]
    for c in currents:
        stress = model.calculate_current_stress_factor(c)
        print(f"  {c:.1f}C: {stress:.4f}x")
    
    print("\nSoC Cycling Stress Factors:")
    soc_ranges = [
        (20, 80),   # Optimal
        (10, 90),   # Moderate stress
        (5, 95),    # High stress
        (0, 100)    # Extreme stress
    ]
    for soc_min, soc_max in soc_ranges:
        stress = model.calculate_soc_cycling_factor(soc_min, soc_max)
        print(f"  {soc_min}-{soc_max}%: {stress:.4f}x")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("Battery Degradation Model Demonstration")
    print("="*70)
    
    demo_optimal_charging()
    demo_aggressive_charging()
    demo_comparison()
    demo_stress_factors()
    
    print("\n" + "="*70)
    print("Demonstration Complete!")
    print("="*70 + "\n")
