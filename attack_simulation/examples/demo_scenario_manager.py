#!/usr/bin/env python3
"""
Demo script for ScenarioManager

This script demonstrates how to use the ScenarioManager to run batch simulations
with multiple attack scenarios and generate comparison reports.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from attack_simulation.core.scenario_manager import ScenarioManager


def setup_logging():
    """Configure logging for the demo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


async def main():
    """Main demo function"""
    print("=" * 80)
    print("SCENARIO MANAGER DEMO")
    print("=" * 80)
    print()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Path to batch configuration
    batch_config_path = Path(__file__).parent.parent / 'config' / 'batch_config.yaml'
    
    if not batch_config_path.exists():
        logger.error(f"Batch configuration not found: {batch_config_path}")
        return
    
    logger.info(f"Using batch configuration: {batch_config_path}")
    
    try:
        # Initialize ScenarioManager
        logger.info("Initializing ScenarioManager...")
        manager = ScenarioManager(str(batch_config_path))
        
        # Display loaded scenarios
        print("\nLoaded Scenarios:")
        print("-" * 80)
        for i, scenario in enumerate(manager.scenarios, 1):
            print(f"{i}. {scenario.name}")
            print(f"   Description: {scenario.description}")
            print(f"   Attack Enabled: {scenario.attack_enabled}")
            print(f"   Strategy: {scenario.strategy}")
            print(f"   Cycles: {scenario.cycles}")
            print()
        
        # Run batch execution
        print("\n" + "=" * 80)
        print("STARTING BATCH EXECUTION")
        print("=" * 80)
        print()
        
        results = await manager.run_batch()
        
        # Generate comparison report
        print("\n" + "=" * 80)
        print("GENERATING COMPARISON REPORT")
        print("=" * 80)
        print()
        
        manager.generate_comparison_report(results)
        
        print("\n" + "=" * 80)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"\nResults saved to: {manager.batch_config.output_dir}")
        print()
        
    except KeyboardInterrupt:
        logger.info("\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
