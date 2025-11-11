"""
Comparison Analyzer for baseline vs attack simulation data
"""

import os
import json
import csv
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ComparisonMetrics:
    """Metrics comparing baseline and attack simulations"""
    baseline_session_id: str
    attack_session_id: str
    
    # Degradation comparison
    baseline_final_soh: float
    attack_final_soh: float
    baseline_total_degradation: float
    attack_total_degradation: float
    degradation_difference: float
    degradation_acceleration_factor: float
    
    # Cycle comparison
    baseline_cycles: int
    attack_cycles: int
    baseline_degradation_rate: float
    attack_degradation_rate: float
    
    # Time to reach degradation thresholds
    baseline_cycles_to_90_percent: Optional[int] = None
    attack_cycles_to_90_percent: Optional[int] = None
    baseline_cycles_to_80_percent: Optional[int] = None
    attack_cycles_to_80_percent: Optional[int] = None
    
    # Statistical significance
    mean_deviation_voltage: float = 0.0
    mean_deviation_current: float = 0.0
    
    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)


class ComparisonAnalyzer:
    """
    Analyzes and compares baseline and attack simulation data
    """
    
    def __init__(self, baseline_session_dir: str, attack_session_dir: str, output_dir: str = None):
        """
        Initialize comparison analyzer
        
        Args:
            baseline_session_dir: Path to baseline simulation session directory
            attack_session_dir: Path to attack simulation session directory
            output_dir: Optional output directory for comparison reports
        """
        self.baseline_session_dir = baseline_session_dir
        self.attack_session_dir = attack_session_dir
        
        # Set output directory
        if output_dir:
            self.output_dir = output_dir
        else:
            # Create comparison directory in parent of baseline
            parent_dir = os.path.dirname(baseline_session_dir)
            self.output_dir = os.path.join(parent_dir, "comparison")
        
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Load simulation data
        self.baseline_summary = None
        self.attack_summary = None
        self.baseline_degradation_data = None
        self.attack_degradation_data = None
        self.attack_manipulation_data = None
        
        logger.info(f"ComparisonAnalyzer initialized")
        logger.info(f"Baseline: {baseline_session_dir}")
        logger.info(f"Attack: {attack_session_dir}")
        logger.info(f"Output: {self.output_dir}")
    
    def load_simulation_data(self) -> bool:
        """
        Load baseline and attack simulation data
        
        Returns:
            True if data loaded successfully
        """
        logger.info("Loading simulation data...")
        
        try:
            # Load baseline summary
            baseline_summary_path = os.path.join(self.baseline_session_dir, 'summary.json')
            if not os.path.exists(baseline_summary_path):
                logger.error(f"Baseline summary not found: {baseline_summary_path}")
                return False
            
            with open(baseline_summary_path, 'r') as f:
                self.baseline_summary = json.load(f)
            logger.info(f"Loaded baseline summary: {self.baseline_summary['session_id']}")
            
            # Load attack summary
            attack_summary_path = os.path.join(self.attack_session_dir, 'summary.json')
            if not os.path.exists(attack_summary_path):
                logger.error(f"Attack summary not found: {attack_summary_path}")
                return False
            
            with open(attack_summary_path, 'r') as f:
                self.attack_summary = json.load(f)
            logger.info(f"Loaded attack summary: {self.attack_summary['session_id']}")
            
            # Load degradation timeline data
            self.baseline_degradation_data = self._load_degradation_timeline(
                os.path.join(self.baseline_session_dir, 'degradation_timeline.csv')
            )
            self.attack_degradation_data = self._load_degradation_timeline(
                os.path.join(self.attack_session_dir, 'degradation_timeline.csv')
            )
            
            # Load attack manipulation data
            manipulation_path = os.path.join(self.attack_session_dir, 'manipulations.csv')
            if os.path.exists(manipulation_path):
                self.attack_manipulation_data = self._load_manipulation_data(manipulation_path)
                logger.info(f"Loaded {len(self.attack_manipulation_data)} manipulation events")
            else:
                logger.warning("No manipulation data found for attack simulation")
                self.attack_manipulation_data = pd.DataFrame()
            
            logger.info("Simulation data loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading simulation data: {e}")
            return False
    
    def _load_degradation_timeline(self, csv_path: str) -> pd.DataFrame:
        """
        Load degradation timeline CSV data
        
        Args:
            csv_path: Path to degradation timeline CSV
            
        Returns:
            DataFrame with degradation data
        """
        if not os.path.exists(csv_path):
            logger.warning(f"Degradation timeline not found: {csv_path}")
            return pd.DataFrame()
        
        df = pd.read_csv(csv_path)
        logger.debug(f"Loaded {len(df)} degradation events from {csv_path}")
        return df
    
    def _load_manipulation_data(self, csv_path: str) -> pd.DataFrame:
        """
        Load manipulation data CSV
        
        Args:
            csv_path: Path to manipulations CSV
            
        Returns:
            DataFrame with manipulation data
        """
        if not os.path.exists(csv_path):
            return pd.DataFrame()
        
        df = pd.read_csv(csv_path)
        return df
    
    def calculate_degradation_difference(self) -> float:
        """
        Calculate degradation difference between baseline and attack
        
        Returns:
            Degradation difference (attack - baseline)
        """
        if not self.baseline_summary or not self.attack_summary:
            logger.error("Summary data not loaded")
            return 0.0
        
        baseline_deg = self.baseline_summary.get('total_degradation', 0.0)
        attack_deg = self.attack_summary.get('total_degradation', 0.0)
        
        difference = attack_deg - baseline_deg
        logger.info(f"Degradation difference: {difference:.4f}% (attack - baseline)")
        
        return difference
    
    def compute_degradation_acceleration_factor(self) -> float:
        """
        Compute degradation acceleration factor
        
        Returns:
            Acceleration factor (attack_rate / baseline_rate)
        """
        if not self.baseline_summary or not self.attack_summary:
            logger.error("Summary data not loaded")
            return 1.0
        
        baseline_rate = self.baseline_summary.get('degradation_rate_per_cycle', 0.0)
        attack_rate = self.attack_summary.get('degradation_rate_per_cycle', 0.0)
        
        if baseline_rate == 0:
            logger.warning("Baseline degradation rate is zero, cannot compute acceleration factor")
            return 1.0
        
        acceleration_factor = attack_rate / baseline_rate
        logger.info(f"Degradation acceleration factor: {acceleration_factor:.2f}x")
        
        return acceleration_factor
    
    def find_cycles_to_threshold(self, degradation_data: pd.DataFrame, threshold_soh: float) -> Optional[int]:
        """
        Find number of cycles to reach a specific SoH threshold
        
        Args:
            degradation_data: DataFrame with degradation timeline
            threshold_soh: SoH threshold to find (e.g., 90.0 for 90%)
            
        Returns:
            Cycle number when threshold was reached, or None if not reached
        """
        if degradation_data.empty:
            return None
        
        # Find first cycle where SoH drops below threshold
        below_threshold = degradation_data[degradation_data['soh'] <= threshold_soh]
        
        if below_threshold.empty:
            return None
        
        return int(below_threshold.iloc[0]['cycle_num'])
    
    def generate_comparison_metrics(self) -> ComparisonMetrics:
        """
        Generate comprehensive comparison metrics
        
        Returns:
            ComparisonMetrics object
        """
        logger.info("Generating comparison metrics...")
        
        if not self.baseline_summary or not self.attack_summary:
            raise ValueError("Simulation data not loaded. Call load_simulation_data() first.")
        
        # Calculate degradation metrics
        degradation_diff = self.calculate_degradation_difference()
        acceleration_factor = self.compute_degradation_acceleration_factor()
        
        # Find cycles to reach degradation thresholds
        baseline_90 = self.find_cycles_to_threshold(self.baseline_degradation_data, 90.0)
        attack_90 = self.find_cycles_to_threshold(self.attack_degradation_data, 90.0)
        baseline_80 = self.find_cycles_to_threshold(self.baseline_degradation_data, 80.0)
        attack_80 = self.find_cycles_to_threshold(self.attack_degradation_data, 80.0)
        
        # Calculate mean deviations from manipulation data
        mean_voltage_dev = 0.0
        mean_current_dev = 0.0
        
        if not self.attack_manipulation_data.empty:
            voltage_manip = self.attack_manipulation_data[
                self.attack_manipulation_data['parameter_name'].str.contains('voltage', case=False, na=False)
            ]
            current_manip = self.attack_manipulation_data[
                self.attack_manipulation_data['parameter_name'].str.contains('current', case=False, na=False)
            ]
            
            if not voltage_manip.empty:
                mean_voltage_dev = voltage_manip['deviation_percent'].abs().mean()
            if not current_manip.empty:
                mean_current_dev = current_manip['deviation_percent'].abs().mean()
        
        # Create comparison metrics object
        metrics = ComparisonMetrics(
            baseline_session_id=self.baseline_summary['session_id'],
            attack_session_id=self.attack_summary['session_id'],
            baseline_final_soh=self.baseline_summary['final_soh'],
            attack_final_soh=self.attack_summary['final_soh'],
            baseline_total_degradation=self.baseline_summary['total_degradation'],
            attack_total_degradation=self.attack_summary['total_degradation'],
            degradation_difference=degradation_diff,
            degradation_acceleration_factor=acceleration_factor,
            baseline_cycles=self.baseline_summary['total_cycles'],
            attack_cycles=self.attack_summary['total_cycles'],
            baseline_degradation_rate=self.baseline_summary['degradation_rate_per_cycle'],
            attack_degradation_rate=self.attack_summary['degradation_rate_per_cycle'],
            baseline_cycles_to_90_percent=baseline_90,
            attack_cycles_to_90_percent=attack_90,
            baseline_cycles_to_80_percent=baseline_80,
            attack_cycles_to_80_percent=attack_80,
            mean_deviation_voltage=mean_voltage_dev,
            mean_deviation_current=mean_current_dev
        )
        
        logger.info("Comparison metrics generated successfully")
        return metrics
    
    def generate_comparison_report(self, metrics: ComparisonMetrics = None) -> str:
        """
        Generate comparison report
        
        Args:
            metrics: Optional ComparisonMetrics object (will be generated if not provided)
            
        Returns:
            Path to generated report file
        """
        logger.info("Generating comparison report...")
        
        if metrics is None:
            metrics = self.generate_comparison_metrics()
        
        # Generate report content
        report_lines = [
            "=" * 80,
            "BASELINE VS ATTACK SIMULATION COMPARISON REPORT",
            "=" * 80,
            "",
            f"Baseline Session: {metrics.baseline_session_id}",
            f"Attack Session: {metrics.attack_session_id}",
            "",
            "-" * 80,
            "DEGRADATION COMPARISON",
            "-" * 80,
            "",
            f"Baseline Final SoH: {metrics.baseline_final_soh:.2f}%",
            f"Attack Final SoH: {metrics.attack_final_soh:.2f}%",
            "",
            f"Baseline Total Degradation: {metrics.baseline_total_degradation:.4f}%",
            f"Attack Total Degradation: {metrics.attack_total_degradation:.4f}%",
            f"Degradation Difference: {metrics.degradation_difference:.4f}%",
            "",
            f"Degradation Acceleration Factor: {metrics.degradation_acceleration_factor:.2f}x",
            "",
            "-" * 80,
            "CYCLE COMPARISON",
            "-" * 80,
            "",
            f"Baseline Cycles: {metrics.baseline_cycles}",
            f"Attack Cycles: {metrics.attack_cycles}",
            "",
            f"Baseline Degradation Rate: {metrics.baseline_degradation_rate:.6f}% per cycle",
            f"Attack Degradation Rate: {metrics.attack_degradation_rate:.6f}% per cycle",
            "",
            "-" * 80,
            "TIME TO DEGRADATION THRESHOLDS",
            "-" * 80,
            "",
        ]
        
        # Add threshold information
        if metrics.baseline_cycles_to_90_percent:
            report_lines.append(f"Baseline Cycles to 90% SoH: {metrics.baseline_cycles_to_90_percent}")
        else:
            report_lines.append("Baseline Cycles to 90% SoH: Not reached")
        
        if metrics.attack_cycles_to_90_percent:
            report_lines.append(f"Attack Cycles to 90% SoH: {metrics.attack_cycles_to_90_percent}")
            if metrics.baseline_cycles_to_90_percent:
                speedup = metrics.baseline_cycles_to_90_percent / metrics.attack_cycles_to_90_percent
                report_lines.append(f"  → Attack reached 90% SoH {speedup:.2f}x faster")
        else:
            report_lines.append("Attack Cycles to 90% SoH: Not reached")
        
        report_lines.append("")
        
        if metrics.baseline_cycles_to_80_percent:
            report_lines.append(f"Baseline Cycles to 80% SoH: {metrics.baseline_cycles_to_80_percent}")
        else:
            report_lines.append("Baseline Cycles to 80% SoH: Not reached")
        
        if metrics.attack_cycles_to_80_percent:
            report_lines.append(f"Attack Cycles to 80% SoH: {metrics.attack_cycles_to_80_percent}")
            if metrics.baseline_cycles_to_80_percent:
                speedup = metrics.baseline_cycles_to_80_percent / metrics.attack_cycles_to_80_percent
                report_lines.append(f"  → Attack reached 80% SoH {speedup:.2f}x faster")
        else:
            report_lines.append("Attack Cycles to 80% SoH: Not reached")
        
        report_lines.extend([
            "",
            "-" * 80,
            "ATTACK MANIPULATION STATISTICS",
            "-" * 80,
            "",
            f"Mean Voltage Deviation: {metrics.mean_deviation_voltage:.2f}%",
            f"Mean Current Deviation: {metrics.mean_deviation_current:.2f}%",
            "",
            "=" * 80,
        ])
        
        # Write report to file
        report_path = os.path.join(self.output_dir, 'comparison_report.txt')
        with open(report_path, 'w') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Comparison report saved: {report_path}")
        
        # Also save metrics as JSON
        metrics_json_path = os.path.join(self.output_dir, 'comparison_metrics.json')
        with open(metrics_json_path, 'w') as f:
            json.dump(metrics.to_dict(), f, indent=2)
        
        logger.info(f"Comparison metrics saved: {metrics_json_path}")
        
        # Print report to console
        print('\n'.join(report_lines))
        
        return report_path
    
    def export_comparison_csv(self, metrics: ComparisonMetrics = None) -> str:
        """
        Export comparison metrics to CSV format
        
        Args:
            metrics: Optional ComparisonMetrics object
            
        Returns:
            Path to CSV file
        """
        if metrics is None:
            metrics = self.generate_comparison_metrics()
        
        csv_path = os.path.join(self.output_dir, 'comparison_metrics.csv')
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Metric', 'Baseline', 'Attack', 'Difference/Factor'])
            
            # Write data rows
            writer.writerow(['Session ID', metrics.baseline_session_id, metrics.attack_session_id, '-'])
            writer.writerow(['Final SoH (%)', f"{metrics.baseline_final_soh:.2f}", 
                           f"{metrics.attack_final_soh:.2f}", '-'])
            writer.writerow(['Total Degradation (%)', f"{metrics.baseline_total_degradation:.4f}",
                           f"{metrics.attack_total_degradation:.4f}", 
                           f"{metrics.degradation_difference:.4f}"])
            writer.writerow(['Degradation Rate (% per cycle)', 
                           f"{metrics.baseline_degradation_rate:.6f}",
                           f"{metrics.attack_degradation_rate:.6f}",
                           f"{metrics.degradation_acceleration_factor:.2f}x"])
            writer.writerow(['Total Cycles', metrics.baseline_cycles, metrics.attack_cycles, '-'])
            writer.writerow(['Cycles to 90% SoH', 
                           metrics.baseline_cycles_to_90_percent or 'Not reached',
                           metrics.attack_cycles_to_90_percent or 'Not reached', '-'])
            writer.writerow(['Cycles to 80% SoH',
                           metrics.baseline_cycles_to_80_percent or 'Not reached',
                           metrics.attack_cycles_to_80_percent or 'Not reached', '-'])
            writer.writerow(['Mean Voltage Deviation (%)', '-', 
                           f"{metrics.mean_deviation_voltage:.2f}", '-'])
            writer.writerow(['Mean Current Deviation (%)', '-',
                           f"{metrics.mean_deviation_current:.2f}", '-'])
        
        logger.info(f"Comparison CSV exported: {csv_path}")
        return csv_path
