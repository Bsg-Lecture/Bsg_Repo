#!/usr/bin/env python3
"""
Convenience wrapper for running attack simulations
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run attack simulator with default config if not specified"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run attack simulation (convenience wrapper)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test (100 cycles)
  python run_attack.py --cycles 100
  
  # Full simulation (1000 cycles)
  python run_attack.py --cycles 1000
  
  # With custom config
  python run_attack.py --config my_config.yaml --cycles 500
  
  # With debug logging
  python run_attack.py --cycles 100 --log-level DEBUG
        """
    )
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_config = os.path.join(script_dir, 'attack_simulation', 'config', 'attack_config.yaml')
    
    parser.add_argument('--config', 
                       default=default_config,
                       help='Attack configuration file (default: attack_config.yaml)')
    parser.add_argument('--cycles', type=int, default=100,
                       help='Number of charging cycles (default: 100)')
    parser.add_argument('--output-dir', default='./output/attack',
                       help='Output directory (default: ./output/attack)')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level (default: INFO)')
    
    args = parser.parse_args()
    
    # Build command for attack_simulator.py
    cmd_args = [
        'attack_simulator.py',
        '--config', args.config,
        '--cycles', str(args.cycles),
        '--output-dir', args.output_dir,
        '--log-level', args.log_level
    ]
    
    print(f"Running: python {' '.join(cmd_args)}")
    print()
    
    # Import and run attack_simulator
    import attack_simulator
    
    # Override sys.argv for attack_simulator
    sys.argv = cmd_args
    
    # Run the simulator
    return attack_simulator.main()

if __name__ == "__main__":
    sys.exit(main())
