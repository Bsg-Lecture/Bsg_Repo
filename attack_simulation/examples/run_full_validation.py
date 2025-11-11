#!/usr/bin/env python3
"""
Full Validation Suite Runner

This script runs all validation scenarios in sequence:
1. Baseline scenario (1000 cycles)
2. Aggressive attack scenario (1000 cycles)
3. Subtle attack scenario (1000 cycles)
4. Generate publication materials

This provides a complete validation of the charging profile poisoning attack
simulation system and generates all materials needed for research publication.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from validation_baseline import run_baseline_scenario
from validation_aggressive import run_aggressive_attack_scenario
from validation_subtle import run_subtle_attack_scenario
from generate_publication_materials import generate_publication_materials

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_full_validation(cycles: int = 1000, output_base_dir: str = "./output/validation"):
    """
    Run complete validation suite
    
    Args:
        cycles: Number of charging cycles for each scenario
        output_base_dir: Base output directory for all results
    """
    start_time = datetime.now()
    
    logger.info("=" * 80)
    logger.info("FULL VALIDATION SUITE")
    logger.info("=" * 80)
    logger.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Cycles per scenario: {cycles}")
    logger.info(f"Output directory: {output_base_dir}")
    logger.info("")
    
    results = {
        'baseline': None,
        'aggressive': None,
        'subtle': None,
        'publication': None
    }
    
    validation_passed = True
    
    # Step 1: Run baseline scenario
    logger.info("=" * 80)
    logger.info("STEP 1/4: BASELINE SCENARIO")
    logger.info("=" * 80)
    logger.info("")
    
    try:
        baseline_output = os.path.join(output_base_dir, "baseline")
        baseline_results = run_baseline_scenario(cycles=cycles, output_dir=baseline_output)
        results['baseline'] = baseline_results
        
        if not baseline_results['validation_passed']:
            logger.warning("⚠ Baseline validation failed")
            validation_passed = False
        else:
            logger.info("✓ Baseline validation passed")
        
        logger.info("")
        
    except Exception as e:
        logger.error(f"✗ Baseline scenario failed: {e}", exc_info=True)
        validation_passed = False
        logger.info("")
    
    # Step 2: Run aggressive attack scenario
    logger.info("=" * 80)
    logger.info("STEP 2/4: AGGRESSIVE ATTACK SCENARIO")
    logger.info("=" * 80)
    logger.info("")
    
    try:
        aggressive_output = os.path.join(output_base_dir, "aggressive")
        baseline_dir = results['baseline']['session_dir'] if results['baseline'] else None
        
        aggressive_results = run_aggressive_attack_scenario(
            cycles=cycles,
            output_dir=aggressive_output,
            baseline_dir=baseline_dir
        )
        results['aggressive'] = aggressive_results
        
        if not aggressive_results['validation_passed']:
            logger.warning("⚠ Aggressive attack validation failed")
            validation_passed = False
        else:
            logger.info("✓ Aggressive attack validation passed")
        
        logger.info("")
        
    except Exception as e:
        logger.error(f"✗ Aggressive attack scenario failed: {e}", exc_info=True)
        validation_passed = False
        logger.info("")
    
    # Step 3: Run subtle attack scenario
    logger.info("=" * 80)
    logger.info("STEP 3/4: SUBTLE ATTACK SCENARIO")
    logger.info("=" * 80)
    logger.info("")
    
    try:
        subtle_output = os.path.join(output_base_dir, "subtle")
        baseline_dir = results['baseline']['session_dir'] if results['baseline'] else None
        
        subtle_results = run_subtle_attack_scenario(
            cycles=cycles,
            output_dir=subtle_output,
            baseline_dir=baseline_dir,
            enable_detection=True
        )
        results['subtle'] = subtle_results
        
        if not subtle_results['validation_passed']:
            logger.warning("⚠ Subtle attack validation failed")
            validation_passed = False
        else:
            logger.info("✓ Subtle attack validation passed")
        
        logger.info("")
        
    except Exception as e:
        logger.error(f"✗ Subtle attack scenario failed: {e}", exc_info=True)
        validation_passed = False
        logger.info("")
    
    # Step 4: Generate publication materials
    logger.info("=" * 80)
    logger.info("STEP 4/4: GENERATE PUBLICATION MATERIALS")
    logger.info("=" * 80)
    logger.info("")
    
    try:
        if all([results['baseline'], results['aggressive'], results['subtle']]):
            scenario_dirs = {
                'baseline': results['baseline']['session_dir'],
                'aggressive': results['aggressive']['session_dir'],
                'subtle': results['subtle']['session_dir']
            }
            
            publication_output = os.path.join(output_base_dir, "publication")
            generate_publication_materials(scenario_dirs, publication_output)
            results['publication'] = {'output_dir': publication_output}
            
            logger.info("✓ Publication materials generated")
        else:
            logger.warning("⚠ Skipping publication materials (some scenarios failed)")
        
        logger.info("")
        
    except Exception as e:
        logger.error(f"✗ Publication materials generation failed: {e}", exc_info=True)
        logger.info("")
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("=" * 80)
    logger.info("VALIDATION SUITE COMPLETE")
    logger.info("=" * 80)
    logger.info(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Total duration: {duration}")
    logger.info("")
    
    logger.info("Results Summary:")
    logger.info("-" * 80)
    
    if results['baseline']:
        status = "✓ PASSED" if results['baseline']['validation_passed'] else "✗ FAILED"
        logger.info(f"  Baseline: {status}")
        logger.info(f"    - Session: {results['baseline']['session_dir']}")
    else:
        logger.info(f"  Baseline: ✗ ERROR")
    
    if results['aggressive']:
        status = "✓ PASSED" if results['aggressive']['validation_passed'] else "✗ FAILED"
        logger.info(f"  Aggressive: {status}")
        logger.info(f"    - Session: {results['aggressive']['session_dir']}")
    else:
        logger.info(f"  Aggressive: ✗ ERROR")
    
    if results['subtle']:
        status = "✓ PASSED" if results['subtle']['validation_passed'] else "✗ FAILED"
        logger.info(f"  Subtle: {status}")
        logger.info(f"    - Session: {results['subtle']['session_dir']}")
    else:
        logger.info(f"  Subtle: ✗ ERROR")
    
    if results['publication']:
        logger.info(f"  Publication: ✓ GENERATED")
        logger.info(f"    - Output: {results['publication']['output_dir']}")
    else:
        logger.info(f"  Publication: ✗ NOT GENERATED")
    
    logger.info("")
    
    if validation_passed:
        logger.info("=" * 80)
        logger.info("✓ ALL VALIDATIONS PASSED")
        logger.info("=" * 80)
    else:
        logger.warning("=" * 80)
        logger.warning("✗ SOME VALIDATIONS FAILED")
        logger.warning("=" * 80)
    
    logger.info("")
    logger.info(f"All results saved to: {output_base_dir}")
    logger.info("")
    
    return {
        'validation_passed': validation_passed,
        'results': results,
        'duration': duration
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run full validation suite")
    parser.add_argument('--cycles', type=int, default=1000,
                       help='Number of charging cycles per scenario (default: 1000)')
    parser.add_argument('--output', type=str, default='./output/validation',
                       help='Base output directory for all results')
    
    args = parser.parse_args()
    
    try:
        suite_results = run_full_validation(cycles=args.cycles, output_base_dir=args.output)
        
        # Exit with appropriate code
        sys.exit(0 if suite_results['validation_passed'] else 1)
        
    except Exception as e:
        logger.error(f"Validation suite failed with error: {e}", exc_info=True)
        sys.exit(1)
