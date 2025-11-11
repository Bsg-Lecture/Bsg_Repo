"""
Demonstration of Attack Engine functionality
Shows how to use the attack engine to manipulate charging profiles
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from attack_simulation.core.attack_engine import (
    AttackEngine, AttackConfig, AttackStrategy
)
from attack_simulation.metrics.metrics_collector import MetricsCollector
import json


def print_profile(profile, title="Profile"):
    """Pretty print a charging profile"""
    print(f"\n{title}:")
    print(json.dumps(profile, indent=2))


def demo_aggressive_attack():
    """Demonstrate aggressive attack strategy"""
    print("\n" + "="*60)
    print("DEMO: Aggressive Attack Strategy")
    print("="*60)
    
    # Create aggressive attack configuration
    config = AttackConfig(
        enabled=True,
        strategy=AttackStrategy.AGGRESSIVE,
        voltage_deviation_percent=20.0,
        current_deviation_percent=30.0,
        curve_modification_type='flatten'
    )
    
    # Initialize attack engine
    engine = AttackEngine(config)
    
    # Sample charging profile (OCPP 1.6 format)
    original_profile = {
        'id': 1,
        'stackLevel': 0,
        'chargingProfilePurpose': 'TxProfile',
        'chargingProfileKind': 'Absolute',
        'chargingSchedule': {
            'chargingRateUnit': 'A',
            'chargingSchedulePeriod': [
                {'startPeriod': 0, 'limit': 32.0, 'numberPhases': 3},
                {'startPeriod': 3600, 'limit': 24.0, 'numberPhases': 3},
                {'startPeriod': 7200, 'limit': 16.0, 'numberPhases': 3}
            ]
        }
    }
    
    print_profile(original_profile, "Original Profile")
    
    # Apply attack
    modified_profile = engine.manipulate_charging_profile(original_profile)
    
    print_profile(modified_profile, "Modified Profile (Aggressive)")
    
    # Show summary
    print("\nManipulation Summary:")
    summary = engine.get_manipulation_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")


def demo_subtle_attack():
    """Demonstrate subtle attack strategy"""
    print("\n" + "="*60)
    print("DEMO: Subtle Attack Strategy")
    print("="*60)
    
    # Create subtle attack configuration
    config = AttackConfig(
        enabled=True,
        strategy=AttackStrategy.SUBTLE,
        voltage_deviation_percent=20.0,
        current_deviation_percent=30.0,
        curve_enabled=False  # Disable curve manipulation for subtlety
    )
    
    # Initialize attack engine
    engine = AttackEngine(config)
    
    # Sample charging profile
    original_profile = {
        'id': 1,
        'stackLevel': 0,
        'chargingSchedule': {
            'chargingRateUnit': 'A',
            'chargingSchedulePeriod': [
                {'startPeriod': 0, 'limit': 32.0}
            ]
        }
    }
    
    print_profile(original_profile, "Original Profile")
    
    # Apply attack
    modified_profile = engine.manipulate_charging_profile(original_profile)
    
    print_profile(modified_profile, "Modified Profile (Subtle)")
    
    # Calculate actual deviation
    orig_limit = original_profile['chargingSchedule']['chargingSchedulePeriod'][0]['limit']
    mod_limit = modified_profile['chargingSchedule']['chargingSchedulePeriod'][0]['limit']
    actual_deviation = ((mod_limit - orig_limit) / orig_limit) * 100
    
    print(f"\nActual Deviation: {actual_deviation:.2f}%")
    print("Note: Subtle strategy uses only 20% of configured deviation")


def demo_random_attack():
    """Demonstrate random attack strategy"""
    print("\n" + "="*60)
    print("DEMO: Random Attack Strategy")
    print("="*60)
    
    # Create random attack configuration
    config = AttackConfig(
        enabled=True,
        strategy=AttackStrategy.RANDOM,
        randomization_enabled=True,
        randomization_seed=42,
        randomization_deviation_range=(5, 25)
    )
    
    # Initialize attack engine
    engine = AttackEngine(config)
    
    # Sample charging profile
    original_profile = {
        'id': 1,
        'stackLevel': 0,
        'chargingSchedule': {
            'chargingRateUnit': 'A',
            'chargingSchedulePeriod': [
                {'startPeriod': 0, 'limit': 32.0}
            ]
        }
    }
    
    print_profile(original_profile, "Original Profile")
    
    # Apply attack multiple times to show randomness
    print("\nApplying random attack 3 times:")
    for i in range(3):
        modified_profile = engine.manipulate_charging_profile(original_profile)
        mod_limit = modified_profile['chargingSchedule']['chargingSchedulePeriod'][0]['limit']
        orig_limit = original_profile['chargingSchedule']['chargingSchedulePeriod'][0]['limit']
        deviation = ((mod_limit - orig_limit) / orig_limit) * 100
        print(f"  Attempt {i+1}: {orig_limit}A -> {mod_limit:.2f}A ({deviation:.2f}% deviation)")


def demo_message_filtering():
    """Demonstrate message type filtering"""
    print("\n" + "="*60)
    print("DEMO: Message Type Filtering")
    print("="*60)
    
    config = AttackConfig(enabled=True)
    engine = AttackEngine(config)
    
    # Test different message types
    messages = [
        [2, "msg-001", "SetChargingProfile", {}],
        [2, "msg-002", "BootNotification", {}],
        [2, "msg-003", "Heartbeat", {}],
        [2, "msg-004", "SetChargingProfileRequest", {}],
    ]
    
    print("\nMessage Filtering Results:")
    for msg in messages:
        message_type = msg[2]
        should_manipulate = engine.should_manipulate(msg)
        status = "✓ MANIPULATE" if should_manipulate else "✗ SKIP"
        print(f"  {message_type:30s} -> {status}")


def main():
    """Run all demonstrations"""
    print("\n" + "="*60)
    print("ATTACK ENGINE DEMONSTRATION")
    print("="*60)
    
    demo_aggressive_attack()
    demo_subtle_attack()
    demo_random_attack()
    demo_message_filtering()
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)


if __name__ == '__main__':
    main()
