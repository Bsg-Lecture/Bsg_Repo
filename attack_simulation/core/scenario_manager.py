"""
Scenario Manager for orchestrating multi-scenario experiments
"""

import logging
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import yaml

from ..models.battery_model import BatteryDegradationModel, DegradationParameters
from ..metrics.metrics_collector import MetricsCollector, SimulationSummary
from ..core.attack_engine import AttackEngine, AttackConfig, AttackStrategy
from ..metrics.comparison_analyzer import ComparisonAnalyzer
from ..visualization.visualization_engine import VisualizationEngine

logger = logging.getLogger(__name__)


@dataclass
class ScenarioConfig:
    """Configuration for a single attack scenario"""
    name: str
    attack_enabled: bool = True
    strategy: str = "aggressive"
    cycles: int = 1000
    description: str = ""
    manipulations: Dict[str, Any] = field(default_factory=dict)
    randomization: Dict[str, Any] = field(default_factory=dict)
    
    def to_attack_config(self) -> AttackConfig:
        """
        Convert scenario config to AttackConfig
        
        Returns:
            AttackConfig instance
        """
        # Extract manipulation settings
        voltage_cfg = self.manipulations.get('voltage', {})
        current_cfg = self.manipulations.get('current', {})
        curve_cfg = self.manipulations.get('charging_curve', {})
        
        # Parse strategy
        try:
            strategy = AttackStrategy(self.strategy)
        except ValueError:
            logger.warning(f"Invalid strategy '{self.strategy}', defaulting to AGGRESSIVE")
            strategy = AttackStrategy.AGGRESSIVE
        
        return AttackConfig(
            enabled=self.attack_enabled,
            strategy=strategy,
            voltage_enabled=voltage_cfg.get('enabled', True),
            voltage_deviation_percent=voltage_cfg.get('deviation_percent', 15.0),
            voltage_target_range=tuple(voltage_cfg.get('target_range', [4.2, 4.35])),
            current_enabled=current_cfg.get('enabled', True),
            current_deviation_percent=current_cfg.get('deviation_percent', 25.0),
            current_target_range=tuple(current_cfg.get('target_range', [50, 80])),
            curve_enabled=curve_cfg.get('enabled', True),
            curve_modification_type=curve_cfg.get('modification_type', 'flatten'),
            randomization_enabled=self.randomization.get('enabled', False),
            randomization_seed=self.randomization.get('seed', 42),
            randomization_deviation_range=tuple(self.randomization.get('deviation_range', [5, 30]))
        )


@dataclass
class BatchConfig:
    """Configuration for batch execution"""
    name: str
    output_dir: str
    scenarios: List[ScenarioConfig]
    battery_model: Dict[str, Any] = field(default_factory=dict)
    proxy: Dict[str, Any] = field(default_factory=dict)
    output: Dict[str, Any] = field(default_factory=dict)
    execution: Dict[str, Any] = field(default_factory=dict)


class ScenarioManager:
    """
    Manages execution of multiple attack scenarios
    """
    
    def __init__(self, batch_config_path: str):
        """
        Load batch configuration file
        
        Args:
            batch_config_path: Path to batch configuration YAML file
        """
        self.batch_config_path = batch_config_path
        self.batch_config: Optional[BatchConfig] = None
        self.scenarios: List[ScenarioConfig] = []
        self.results: List[SimulationSummary] = []
        self.scenario_sessions: Dict[str, str] = {}  # Maps scenario name to session directory
        
        logger.info(f"ScenarioManager initialized with config: {batch_config_path}")
        
        # Load configuration
        self.load_batch_config()
    
    def load_batch_config(self) -> None:
        """
        Load batch configuration from YAML file
        """
        logger.info(f"Loading batch configuration from: {self.batch_config_path}")
        
        try:
            with open(self.batch_config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Extract batch configuration
            batch_cfg = config_data.get('batch_config', {})
            
            # Parse scenarios
            scenarios_data = batch_cfg.get('scenarios', [])
            self.scenarios = []
            
            for scenario_data in scenarios_data:
                scenario = ScenarioConfig(
                    name=scenario_data.get('name', 'unnamed'),
                    attack_enabled=scenario_data.get('attack_enabled', True),
                    strategy=scenario_data.get('strategy', 'aggressive'),
                    cycles=scenario_data.get('cycles', 1000),
                    description=scenario_data.get('description', ''),
                    manipulations=scenario_data.get('manipulations', {}),
                    randomization=scenario_data.get('randomization', {})
                )
                self.scenarios.append(scenario)
                logger.info(f"Loaded scenario: {scenario.name} ({scenario.cycles} cycles)")
            
            # Create BatchConfig
            self.batch_config = BatchConfig(
                name=batch_cfg.get('name', 'Unnamed Batch'),
                output_dir=batch_cfg.get('output_dir', './results/batch_001'),
                scenarios=self.scenarios,
                battery_model=config_data.get('battery_model', {}),
                proxy=config_data.get('proxy', {}),
                output=config_data.get('output', {}),
                execution=config_data.get('execution', {})
            )
            
            # Create output directory
            Path(self.batch_config.output_dir).mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Batch configuration loaded: {self.batch_config.name}")
            logger.info(f"Total scenarios: {len(self.scenarios)}")
            logger.info(f"Output directory: {self.batch_config.output_dir}")
            
        except FileNotFoundError:
            logger.error(f"Batch configuration file not found: {self.batch_config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading batch configuration: {e}")
            raise
    
    async def run_batch(self) -> List[SimulationSummary]:
        """
        Execute all scenarios in batch configuration
        
        Returns:
            List of simulation summary results
        """
        logger.info("=" * 80)
        logger.info(f"BATCH EXECUTION: {self.batch_config.name}")
        logger.info(f"Total scenarios: {len(self.scenarios)}")
        logger.info(f"Output directory: {self.batch_config.output_dir}")
        logger.info("=" * 80)
        
        # Check execution mode
        parallel = self.batch_config.execution.get('parallel', False)
        
        if parallel:
            logger.warning("Parallel execution not yet implemented, falling back to sequential")
        
        # Sequential execution
        self.results = []
        
        for idx, scenario in enumerate(self.scenarios, 1):
            logger.info(f"\n{'=' * 80}")
            logger.info(f"SCENARIO {idx}/{len(self.scenarios)}: {scenario.name}")
            logger.info(f"{'=' * 80}\n")
            
            try:
                # Run scenario
                summary = await self.run_scenario(scenario)
                
                # Collect result
                self.results.append(summary)
                
                logger.info(f"\n✓ Scenario '{scenario.name}' completed successfully\n")
                
                # Reset battery model between scenarios if configured
                if self.batch_config.battery_model.get('reset_between_scenarios', True):
                    logger.info("Battery model will be reset for next scenario")
                
            except Exception as e:
                logger.error(f"✗ Scenario '{scenario.name}' failed: {e}")
                
                # Check if we should continue on error
                if not self.batch_config.execution.get('continue_on_error', True):
                    logger.error("Stopping batch execution due to scenario failure")
                    raise
                
                logger.warning("Continuing with next scenario...")
        
        logger.info("\n" + "=" * 80)
        logger.info("BATCH EXECUTION COMPLETED")
        logger.info(f"Successful scenarios: {len(self.results)}/{len(self.scenarios)}")
        logger.info("=" * 80)
        
        # Print summary of all scenarios
        self._print_batch_summary()
        
        return self.results
    
    def _print_batch_summary(self) -> None:
        """
        Print summary of all scenario results
        """
        if not self.results:
            logger.warning("No results to summarize")
            return
        
        logger.info("\n" + "=" * 80)
        logger.info("BATCH SUMMARY")
        logger.info("=" * 80)
        
        # Create summary table
        logger.info(f"\n{'Scenario':<25} {'Cycles':<10} {'Final SoH':<12} {'Degradation':<15} {'Rate/Cycle':<15}")
        logger.info("-" * 80)
        
        for result in self.results:
            scenario_name = result.session_id.rsplit('_', 2)[0]  # Extract scenario name from session_id
            logger.info(
                f"{scenario_name:<25} "
                f"{result.total_cycles:<10} "
                f"{result.final_soh:<12.2f} "
                f"{result.total_degradation:<15.4f} "
                f"{result.degradation_rate_per_cycle:<15.6f}"
            )
        
        logger.info("=" * 80 + "\n")
    
    async def run_scenario(self, scenario: ScenarioConfig) -> SimulationSummary:
        """
        Execute single scenario
        
        Args:
            scenario: Scenario configuration
            
        Returns:
            Simulation summary result
        """
        logger.info("=" * 80)
        logger.info(f"Running scenario: {scenario.name}")
        logger.info(f"Description: {scenario.description}")
        logger.info(f"Attack enabled: {scenario.attack_enabled}")
        logger.info(f"Strategy: {scenario.strategy}")
        logger.info(f"Cycles: {scenario.cycles}")
        logger.info("=" * 80)
        
        try:
            # Create session ID for this scenario
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = f"{scenario.name}_{timestamp}"
            
            # Initialize metrics collector
            metrics_collector = MetricsCollector(
                output_dir=self.batch_config.output_dir,
                session_id=session_id
            )
            
            # Store session directory for later comparison
            self.scenario_sessions[scenario.name] = metrics_collector.session_dir
            
            # Save scenario configuration
            scenario_config = {
                'name': scenario.name,
                'description': scenario.description,
                'attack_enabled': scenario.attack_enabled,
                'strategy': scenario.strategy,
                'cycles': scenario.cycles,
                'manipulations': scenario.manipulations,
                'randomization': scenario.randomization,
                'batch_name': self.batch_config.name
            }
            metrics_collector.save_config(scenario_config)
            
            # Initialize battery model
            battery_capacity = self.batch_config.battery_model.get('initial_capacity_ah', 75.0)
            battery_model = BatteryDegradationModel(initial_capacity_ah=battery_capacity)
            
            logger.info(f"Battery model initialized: {battery_capacity} Ah")
            
            # Initialize attack engine
            attack_config = scenario.to_attack_config()
            attack_engine = AttackEngine(config=attack_config, metrics_collector=metrics_collector)
            
            logger.info(f"Attack engine initialized: {attack_config.strategy.value}")
            
            # Simulate charging cycles
            logger.info(f"Starting simulation of {scenario.cycles} charging cycles...")
            
            for cycle_num in range(1, scenario.cycles + 1):
                # Create a sample charging profile
                # In a real implementation, this would come from OCPP messages
                charging_profile = self._create_sample_charging_profile(scenario)
                
                # Apply attack manipulation if enabled
                if scenario.attack_enabled:
                    modified_profile = attack_engine.manipulate_charging_profile(charging_profile)
                else:
                    modified_profile = charging_profile
                
                # Extract parameters for battery simulation
                battery_params = self._extract_battery_parameters(modified_profile)
                
                # Simulate charging cycle and calculate degradation
                duration_hours = 1.0  # Assume 1 hour per cycle
                degradation_result = battery_model.simulate_charging_cycle(
                    profile=battery_params,
                    duration_hours=duration_hours
                )
                
                # Log charging cycle
                energy_kwh = battery_params.get('current', 0.5) * battery_capacity * duration_hours
                metrics_collector.log_charging_cycle(
                    cycle_num=cycle_num,
                    profile=battery_params,
                    duration=duration_hours,
                    energy_kwh=energy_kwh,
                    soh_before=degradation_result.soh_before,
                    soh_after=degradation_result.soh_after
                )
                
                # Log degradation event
                metrics_collector.log_degradation_event(
                    degradation_result=degradation_result,
                    cycle_num=cycle_num
                )
                
                # Progress logging
                if cycle_num % 100 == 0 or cycle_num == scenario.cycles:
                    logger.info(
                        f"Progress: {cycle_num}/{scenario.cycles} cycles, "
                        f"SoH: {degradation_result.soh_after:.2f}%"
                    )
            
            # Export metrics to CSV
            metrics_collector.export_to_csv()
            
            # Generate summary report
            summary = metrics_collector.generate_summary_report()
            
            logger.info("=" * 80)
            logger.info(f"Scenario '{scenario.name}' completed successfully")
            logger.info(f"Final SoH: {summary.final_soh:.2f}%")
            logger.info(f"Total degradation: {summary.total_degradation:.4f}%")
            logger.info(f"Degradation rate: {summary.degradation_rate_per_cycle:.6f}% per cycle")
            logger.info("=" * 80)
            
            # Generate visualizations if enabled
            if self.batch_config.output.get('generate_plots', True):
                try:
                    viz_engine = VisualizationEngine(metrics_collector)
                    viz_engine.plot_soh_timeline()
                    logger.info("Visualizations generated successfully")
                except Exception as e:
                    logger.warning(f"Failed to generate visualizations: {e}")
            
            return summary
            
        except Exception as e:
            logger.error(f"Scenario '{scenario.name}' failed: {e}", exc_info=True)
            
            # Handle scenario failure based on configuration
            if not self.batch_config.execution.get('continue_on_error', True):
                raise
            
            # Return a dummy summary to allow batch to continue
            logger.warning(f"Continuing batch execution despite failure in '{scenario.name}'")
            return SimulationSummary(
                session_id=f"{scenario.name}_failed",
                total_cycles=0,
                total_duration_hours=0.0,
                initial_soh=100.0,
                final_soh=100.0,
                total_degradation=0.0,
                degradation_rate_per_cycle=0.0
            )
    
    def _create_sample_charging_profile(self, scenario: ScenarioConfig) -> Dict[str, Any]:
        """
        Create a sample charging profile for simulation
        
        Args:
            scenario: Scenario configuration
            
        Returns:
            Charging profile dictionary
        """
        # Create a basic OCPP-like charging profile structure
        # In a real implementation, this would come from actual OCPP messages
        profile = {
            'chargingProfileId': 1,
            'stackLevel': 0,
            'chargingProfilePurpose': 'TxProfile',
            'chargingProfileKind': 'Absolute',
            'chargingSchedule': {
                'chargingRateUnit': 'A',
                'chargingSchedulePeriod': [
                    {
                        'startPeriod': 0,
                        'limit': 32.0,  # 32A charging current
                        'numberPhases': 3
                    }
                ]
            }
        }
        
        return profile
    
    def _extract_battery_parameters(self, charging_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract battery simulation parameters from charging profile
        
        Args:
            charging_profile: OCPP charging profile
            
        Returns:
            Dictionary with battery parameters (voltage, current, soc_min, soc_max)
        """
        # Extract charging schedule
        schedule = charging_profile.get('chargingSchedule', {})
        periods = schedule.get('chargingSchedulePeriod', [])
        
        # Get charging limit (current or power)
        limit = 32.0  # Default 32A
        if periods:
            limit = periods[0].get('limit', 32.0)
        
        # Convert to battery parameters
        # Assume typical EV battery: 400V nominal, 75 kWh capacity
        nominal_voltage = 400.0  # V
        battery_capacity_ah = 75.0  # Ah
        
        # Calculate C-rate from current limit
        # C-rate = charging_current / battery_capacity
        c_rate = limit / battery_capacity_ah
        
        # Calculate cell voltage (assuming series configuration)
        # For a 400V pack with ~100 cells in series: 400V / 100 = 4.0V per cell
        cell_voltage = 4.0  # V (nominal)
        
        # Adjust voltage based on charging current (higher current = higher voltage)
        # This is a simplified model
        voltage_adjustment = c_rate * 0.1  # Increase voltage with C-rate
        cell_voltage += voltage_adjustment
        
        # SoC range (assume charging from 20% to 80% for optimal battery health)
        soc_min = 20.0
        soc_max = 80.0
        
        return {
            'voltage': cell_voltage,
            'current': c_rate,
            'soc_min': soc_min,
            'soc_max': soc_max,
            'temperature': 25.0  # Assume 25°C ambient
        }
    
    def generate_comparison_report(self, results: List[SimulationSummary]) -> None:
        """
        Generate cross-scenario comparison report
        
        Args:
            results: List of simulation results
        """
        logger.info("=" * 80)
        logger.info("GENERATING CROSS-SCENARIO COMPARISON REPORT")
        logger.info("=" * 80)
        
        if not results or len(results) < 2:
            logger.warning("Need at least 2 scenarios for comparison")
            return
        
        try:
            # Create comparison output directory
            comparison_dir = os.path.join(self.batch_config.output_dir, 'comparison')
            Path(comparison_dir).mkdir(parents=True, exist_ok=True)
            
            # Generate consolidated comparison report
            self._generate_consolidated_report(results, comparison_dir)
            
            # Generate pairwise comparisons (baseline vs each attack scenario)
            self._generate_pairwise_comparisons(results, comparison_dir)
            
            # Generate comparison plots
            if self.batch_config.output.get('generate_plots', True):
                self._generate_comparison_plots(results, comparison_dir)
            
            # Export comparative statistics
            self._export_comparative_statistics(results, comparison_dir)
            
            logger.info(f"Comparison report generated: {comparison_dir}")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Failed to generate comparison report: {e}", exc_info=True)
    
    def _generate_consolidated_report(self, results: List[SimulationSummary], output_dir: str) -> None:
        """
        Generate consolidated comparison report for all scenarios
        
        Args:
            results: List of simulation results
            output_dir: Output directory for report
        """
        logger.info("Generating consolidated comparison report...")
        
        report_path = os.path.join(output_dir, 'consolidated_report.txt')
        
        report_lines = [
            "=" * 80,
            f"CONSOLIDATED COMPARISON REPORT: {self.batch_config.name}",
            "=" * 80,
            "",
            f"Total Scenarios: {len(results)}",
            f"Batch Output Directory: {self.batch_config.output_dir}",
            f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "=" * 80,
            "SCENARIO SUMMARY",
            "=" * 80,
            ""
        ]
        
        # Add table header
        report_lines.extend([
            f"{'Scenario':<25} {'Cycles':<10} {'Final SoH (%)':<15} {'Total Deg (%)':<15} {'Rate/Cycle':<15}",
            "-" * 80
        ])
        
        # Add each scenario
        for result in results:
            scenario_name = result.session_id.rsplit('_', 2)[0]
            report_lines.append(
                f"{scenario_name:<25} "
                f"{result.total_cycles:<10} "
                f"{result.final_soh:<15.2f} "
                f"{result.total_degradation:<15.4f} "
                f"{result.degradation_rate_per_cycle:<15.6f}"
            )
        
        report_lines.extend([
            "",
            "=" * 80,
            "DEGRADATION COMPARISON",
            "=" * 80,
            ""
        ])
        
        # Find baseline scenario (typically the one with attack_enabled=False)
        baseline_result = None
        baseline_name = None
        
        for scenario in self.scenarios:
            if not scenario.attack_enabled:
                # Find corresponding result
                for result in results:
                    if scenario.name in result.session_id:
                        baseline_result = result
                        baseline_name = scenario.name
                        break
                break
        
        if baseline_result:
            report_lines.append(f"Baseline Scenario: {baseline_name}")
            report_lines.append(f"Baseline Final SoH: {baseline_result.final_soh:.2f}%")
            report_lines.append(f"Baseline Degradation: {baseline_result.total_degradation:.4f}%")
            report_lines.append("")
            report_lines.append("Attack Scenarios vs Baseline:")
            report_lines.append("-" * 80)
            
            for result in results:
                scenario_name = result.session_id.rsplit('_', 2)[0]
                
                # Skip baseline itself
                if scenario_name == baseline_name:
                    continue
                
                # Calculate comparison metrics
                deg_diff = result.total_degradation - baseline_result.total_degradation
                accel_factor = (result.degradation_rate_per_cycle / baseline_result.degradation_rate_per_cycle 
                               if baseline_result.degradation_rate_per_cycle > 0 else 1.0)
                
                report_lines.append(f"\n{scenario_name}:")
                report_lines.append(f"  Final SoH: {result.final_soh:.2f}%")
                report_lines.append(f"  Total Degradation: {result.total_degradation:.4f}%")
                report_lines.append(f"  Degradation Difference: {deg_diff:.4f}% ({deg_diff/baseline_result.total_degradation*100:.1f}% increase)")
                report_lines.append(f"  Acceleration Factor: {accel_factor:.2f}x")
        else:
            report_lines.append("No baseline scenario found for comparison")
        
        report_lines.extend([
            "",
            "=" * 80,
            "END OF REPORT",
            "=" * 80
        ])
        
        # Write report to file
        with open(report_path, 'w') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Consolidated report saved: {report_path}")
        
        # Print to console
        print('\n'.join(report_lines))
    
    def _generate_pairwise_comparisons(self, results: List[SimulationSummary], output_dir: str) -> None:
        """
        Generate pairwise comparisons between baseline and attack scenarios
        
        Args:
            results: List of simulation results
            output_dir: Output directory for comparisons
        """
        logger.info("Generating pairwise comparisons...")
        
        # Find baseline scenario
        baseline_scenario = None
        baseline_session_dir = None
        
        for scenario in self.scenarios:
            if not scenario.attack_enabled:
                baseline_scenario = scenario
                baseline_session_dir = self.scenario_sessions.get(scenario.name)
                break
        
        if not baseline_scenario or not baseline_session_dir:
            logger.warning("No baseline scenario found, skipping pairwise comparisons")
            return
        
        # Create pairwise comparison directory
        pairwise_dir = os.path.join(output_dir, 'pairwise')
        Path(pairwise_dir).mkdir(parents=True, exist_ok=True)
        
        # Compare each attack scenario with baseline
        for scenario in self.scenarios:
            if scenario.attack_enabled:
                attack_session_dir = self.scenario_sessions.get(scenario.name)
                
                if not attack_session_dir:
                    logger.warning(f"Session directory not found for scenario: {scenario.name}")
                    continue
                
                try:
                    # Create comparison analyzer
                    comparison_output = os.path.join(pairwise_dir, f"{baseline_scenario.name}_vs_{scenario.name}")
                    analyzer = ComparisonAnalyzer(
                        baseline_session_dir=baseline_session_dir,
                        attack_session_dir=attack_session_dir,
                        output_dir=comparison_output
                    )
                    
                    # Load data
                    if analyzer.load_simulation_data():
                        # Generate comparison report
                        analyzer.generate_comparison_report()
                        
                        # Export CSV
                        analyzer.export_comparison_csv()
                        
                        logger.info(f"Pairwise comparison generated: {baseline_scenario.name} vs {scenario.name}")
                    else:
                        logger.warning(f"Failed to load data for comparison: {scenario.name}")
                        
                except Exception as e:
                    logger.error(f"Failed to generate pairwise comparison for {scenario.name}: {e}")
    
    def _generate_comparison_plots(self, results: List[SimulationSummary], output_dir: str) -> None:
        """
        Generate comparison plots across scenarios
        
        Args:
            results: List of simulation results
            output_dir: Output directory for plots
        """
        logger.info("Generating comparison plots...")
        
        try:
            import matplotlib.pyplot as plt
            import pandas as pd
            
            # Create plots directory
            plots_dir = os.path.join(output_dir, 'plots')
            Path(plots_dir).mkdir(parents=True, exist_ok=True)
            
            # Plot 1: Final SoH comparison
            self._plot_final_soh_comparison(results, plots_dir)
            
            # Plot 2: Degradation rate comparison
            self._plot_degradation_rate_comparison(results, plots_dir)
            
            # Plot 3: SoH timeline comparison (all scenarios on one plot)
            self._plot_soh_timeline_comparison(plots_dir)
            
            logger.info(f"Comparison plots saved to: {plots_dir}")
            
        except Exception as e:
            logger.error(f"Failed to generate comparison plots: {e}", exc_info=True)
    
    def _plot_final_soh_comparison(self, results: List[SimulationSummary], plots_dir: str) -> None:
        """Generate bar chart comparing final SoH across scenarios"""
        import matplotlib.pyplot as plt
        
        scenario_names = [r.session_id.rsplit('_', 2)[0] for r in results]
        final_sohs = [r.final_soh for r in results]
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(range(len(scenario_names)), final_sohs, color='steelblue', alpha=0.8)
        
        # Color baseline differently
        for i, scenario in enumerate(self.scenarios):
            if not scenario.attack_enabled:
                bars[i].set_color('green')
                bars[i].set_alpha(0.6)
        
        plt.xlabel('Scenario')
        plt.ylabel('Final State of Health (%)')
        plt.title('Final SoH Comparison Across Scenarios')
        plt.xticks(range(len(scenario_names)), scenario_names, rotation=45, ha='right')
        plt.axhline(y=100, color='gray', linestyle='--', alpha=0.5, label='Initial SoH')
        plt.grid(axis='y', alpha=0.3)
        plt.legend()
        plt.tight_layout()
        
        output_path = os.path.join(plots_dir, 'final_soh_comparison.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Final SoH comparison plot saved: {output_path}")
    
    def _plot_degradation_rate_comparison(self, results: List[SimulationSummary], plots_dir: str) -> None:
        """Generate bar chart comparing degradation rates across scenarios"""
        import matplotlib.pyplot as plt
        
        scenario_names = [r.session_id.rsplit('_', 2)[0] for r in results]
        deg_rates = [r.degradation_rate_per_cycle * 100 for r in results]  # Convert to percentage
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(range(len(scenario_names)), deg_rates, color='coral', alpha=0.8)
        
        # Color baseline differently
        for i, scenario in enumerate(self.scenarios):
            if not scenario.attack_enabled:
                bars[i].set_color('green')
                bars[i].set_alpha(0.6)
        
        plt.xlabel('Scenario')
        plt.ylabel('Degradation Rate (% per 100 cycles)')
        plt.title('Degradation Rate Comparison Across Scenarios')
        plt.xticks(range(len(scenario_names)), scenario_names, rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        output_path = os.path.join(plots_dir, 'degradation_rate_comparison.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Degradation rate comparison plot saved: {output_path}")
    
    def _plot_soh_timeline_comparison(self, plots_dir: str) -> None:
        """Generate line plot comparing SoH timelines across all scenarios"""
        import matplotlib.pyplot as plt
        import pandas as pd
        
        plt.figure(figsize=(14, 8))
        
        # Plot each scenario's timeline
        for scenario_name, session_dir in self.scenario_sessions.items():
            timeline_csv = os.path.join(session_dir, 'degradation_timeline.csv')
            
            if not os.path.exists(timeline_csv):
                logger.warning(f"Timeline CSV not found for {scenario_name}")
                continue
            
            try:
                df = pd.read_csv(timeline_csv)
                
                # Determine line style based on scenario type
                linestyle = '-'
                linewidth = 2
                alpha = 0.8
                
                # Find if this is baseline
                is_baseline = False
                for scenario in self.scenarios:
                    if scenario.name == scenario_name and not scenario.attack_enabled:
                        is_baseline = True
                        linewidth = 3
                        break
                
                plt.plot(df['cycle_num'], df['soh'], 
                        label=scenario_name, 
                        linestyle=linestyle,
                        linewidth=linewidth,
                        alpha=alpha)
                
            except Exception as e:
                logger.warning(f"Failed to plot timeline for {scenario_name}: {e}")
        
        plt.xlabel('Charging Cycles')
        plt.ylabel('State of Health (%)')
        plt.title('SoH Degradation Timeline - All Scenarios')
        plt.grid(True, alpha=0.3)
        plt.legend(loc='best')
        plt.tight_layout()
        
        output_path = os.path.join(plots_dir, 'soh_timeline_all_scenarios.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"SoH timeline comparison plot saved: {output_path}")
    
    def _export_comparative_statistics(self, results: List[SimulationSummary], output_dir: str) -> None:
        """
        Export comparative statistics to CSV and JSON
        
        Args:
            results: List of simulation results
            output_dir: Output directory
        """
        logger.info("Exporting comparative statistics...")
        
        import csv
        import json
        
        # Prepare data for export
        stats_data = []
        
        for result in results:
            scenario_name = result.session_id.rsplit('_', 2)[0]
            
            # Find corresponding scenario config
            scenario_config = None
            for scenario in self.scenarios:
                if scenario.name == scenario_name:
                    scenario_config = scenario
                    break
            
            stats_entry = {
                'scenario_name': scenario_name,
                'attack_enabled': scenario_config.attack_enabled if scenario_config else None,
                'strategy': scenario_config.strategy if scenario_config else None,
                'total_cycles': result.total_cycles,
                'initial_soh': result.initial_soh,
                'final_soh': result.final_soh,
                'total_degradation': result.total_degradation,
                'degradation_rate_per_cycle': result.degradation_rate_per_cycle,
                'average_voltage_deviation': result.average_voltage_deviation,
                'average_current_deviation': result.average_current_deviation
            }
            
            stats_data.append(stats_entry)
        
        # Export to CSV
        csv_path = os.path.join(output_dir, 'comparative_statistics.csv')
        with open(csv_path, 'w', newline='') as f:
            if stats_data:
                writer = csv.DictWriter(f, fieldnames=stats_data[0].keys())
                writer.writeheader()
                writer.writerows(stats_data)
        
        logger.info(f"Comparative statistics CSV saved: {csv_path}")
        
        # Export to JSON
        json_path = os.path.join(output_dir, 'comparative_statistics.json')
        with open(json_path, 'w') as f:
            json.dump(stats_data, f, indent=2)
        
        logger.info(f"Comparative statistics JSON saved: {json_path}")
