"""
Metrics Collection System for attack simulation data
"""

import os
import csv
import json
import logging
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SimulationSummary:
    """Summary statistics for a simulation run"""
    session_id: str
    total_cycles: int
    total_duration_hours: float
    initial_soh: float
    final_soh: float
    total_degradation: float
    degradation_rate_per_cycle: float
    average_voltage_deviation: float = 0.0
    average_current_deviation: float = 0.0
    
    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)


class MetricsCollector:
    """
    Collects and persists simulation metrics
    """
    
    def __init__(self, output_dir: str, session_id: str):
        """
        Initialize with output directory and unique session ID
        
        Args:
            output_dir: Base output directory
            session_id: Unique session identifier
        """
        self.output_dir = output_dir
        self.session_id = session_id
        self.session_dir = os.path.join(output_dir, f"session_{session_id}")
        
        # Create session directory structure
        Path(self.session_dir).mkdir(parents=True, exist_ok=True)
        
        # Create plots subdirectory
        self.plots_dir = os.path.join(self.session_dir, 'plots')
        Path(self.plots_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize data storage
        self.manipulations: List[Dict[str, Any]] = []
        self.charging_cycles: List[Dict[str, Any]] = []
        self.degradation_events: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []
        self.detection_events: List[Dict[str, Any]] = []
        
        # Define CSV file paths
        self.manipulations_csv = os.path.join(self.session_dir, 'manipulations.csv')
        self.charging_cycles_csv = os.path.join(self.session_dir, 'charging_cycles.csv')
        self.degradation_timeline_csv = os.path.join(self.session_dir, 'degradation_timeline.csv')
        self.errors_csv = os.path.join(self.session_dir, 'errors.csv')
        self.detection_events_csv = os.path.join(self.session_dir, 'detection_events.csv')
        self.summary_json = os.path.join(self.session_dir, 'summary.json')
        
        # Initialize CSV files with headers
        self._initialize_csv_files()
        
        logger.info(f"MetricsCollector initialized: {self.session_dir}")
    
    def _initialize_csv_files(self) -> None:
        """Initialize CSV files with appropriate headers"""
        
        # Manipulations CSV
        with open(self.manipulations_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'parameter_name', 'original_value', 
                'modified_value', 'deviation_percent'
            ])
        
        # Charging cycles CSV
        with open(self.charging_cycles_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'cycle_num', 'timestamp', 'duration_hours', 'energy_kwh',
                'voltage_avg', 'current_avg', 'soc_min', 'soc_max',
                'soh_before', 'soh_after', 'degradation_percent'
            ])
        
        # Degradation timeline CSV
        with open(self.degradation_timeline_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'cycle_num', 'soh', 'voltage_stress',
                'current_stress', 'soc_stress', 'combined_stress'
            ])
        
        # Errors CSV
        with open(self.errors_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'error_type', 'error_message', 'context'
            ])
        
        # Detection events CSV
        with open(self.detection_events_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'message_id', 'parameter_name', 'observed_value',
                'expected_value', 'deviation_percent', 'confidence_score',
                'is_anomaly', 'detection_method'
            ])
        
        logger.debug("CSV files initialized with headers")
    
    def log_manipulation(self, timestamp: datetime, 
                        original: Dict[str, Any],
                        modified: Dict[str, Any],
                        parameter_name: str = "unknown",
                        original_value: float = 0.0,
                        modified_value: float = 0.0,
                        deviation_percent: float = 0.0) -> None:
        """
        Record charging profile manipulation event
        
        Args:
            timestamp: Event timestamp
            original: Original charging profile
            modified: Modified charging profile
            parameter_name: Name of the manipulated parameter
            original_value: Original parameter value
            modified_value: Modified parameter value
            deviation_percent: Percentage deviation
        """
        manipulation_event = {
            'timestamp': timestamp.isoformat(),
            'parameter_name': parameter_name,
            'original_value': original_value,
            'modified_value': modified_value,
            'deviation_percent': deviation_percent,
            'original_profile': original,
            'modified_profile': modified
        }
        
        self.manipulations.append(manipulation_event)
        logger.debug(f"Manipulation logged: {parameter_name} ({deviation_percent:.2f}% deviation)")
    
    def log_charging_cycle(self, cycle_num: int, 
                          profile: Dict[str, Any],
                          duration: float,
                          energy_kwh: float,
                          soh_before: float,
                          soh_after: float) -> None:
        """
        Record completed charging cycle metrics
        
        Args:
            cycle_num: Cycle number
            profile: Charging profile used
            duration: Cycle duration in hours
            energy_kwh: Energy delivered in kWh
            soh_before: SoH before cycle
            soh_after: SoH after cycle
        """
        # Extract profile parameters
        voltage_avg = profile.get('voltage', 0.0)
        current_avg = profile.get('current', 0.0)
        soc_min = profile.get('soc_min', 0.0)
        soc_max = profile.get('soc_max', 100.0)
        
        # Calculate degradation
        degradation_percent = soh_before - soh_after
        
        # Create cycle event
        cycle_event = {
            'cycle_num': cycle_num,
            'timestamp': datetime.now().isoformat(),
            'duration_hours': duration,
            'energy_kwh': energy_kwh,
            'voltage_avg': voltage_avg,
            'current_avg': current_avg,
            'soc_min': soc_min,
            'soc_max': soc_max,
            'soh_before': soh_before,
            'soh_after': soh_after,
            'degradation_percent': degradation_percent
        }
        
        self.charging_cycles.append(cycle_event)
        logger.debug(f"Charging cycle {cycle_num} logged: SoH {soh_before:.2f}% -> {soh_after:.2f}%")
    
    def log_degradation_event(self, degradation_result: Any, cycle_num: int = 0) -> None:
        """
        Record detailed degradation calculation
        
        Args:
            degradation_result: DegradationResult object
            cycle_num: Current cycle number
        """
        degradation_event = {
            'timestamp': datetime.now().isoformat(),
            'cycle_num': cycle_num,
            'soh': degradation_result.soh_after,
            'voltage_stress': degradation_result.voltage_stress_factor,
            'current_stress': degradation_result.current_stress_factor,
            'soc_stress': degradation_result.soc_stress_factor,
            'combined_stress': degradation_result.combined_stress_factor,
            'degradation_percent': degradation_result.degradation_percent
        }
        
        self.degradation_events.append(degradation_event)
        logger.debug(f"Degradation event logged: cycle {cycle_num}, SoH {degradation_result.soh_after:.2f}%")
    
    def log_error(self, error: Exception, context: str = "") -> None:
        """
        Log error event
        
        Args:
            error: Exception that occurred
            context: Additional context information
        """
        timestamp = datetime.now().isoformat()
        error_event = {
            'timestamp': timestamp,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        }
        self.errors.append(error_event)
        
        # Write error to CSV immediately for real-time tracking
        try:
            with open(self.errors_csv, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp,
                    type(error).__name__,
                    str(error),
                    context
                ])
        except Exception as e:
            logger.error(f"Failed to write error to CSV: {e}")
        
        logger.error(f"Error logged: {error_event}")
    
    def log_detection_event(self, detection_event: Any) -> None:
        """
        Log anomaly detection event
        
        Args:
            detection_event: DetectionEvent object
        """
        event_dict = {
            'timestamp': detection_event.timestamp.isoformat(),
            'message_id': detection_event.message_id,
            'parameter_name': detection_event.parameter_name,
            'observed_value': detection_event.observed_value,
            'expected_value': detection_event.expected_value,
            'deviation_percent': detection_event.deviation_percent,
            'confidence_score': detection_event.confidence_score,
            'is_anomaly': detection_event.is_anomaly,
            'detection_method': detection_event.detection_method
        }
        self.detection_events.append(event_dict)
        
        # Write to CSV immediately for real-time tracking
        try:
            with open(self.detection_events_csv, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    event_dict['timestamp'],
                    event_dict['message_id'],
                    event_dict['parameter_name'],
                    event_dict['observed_value'],
                    event_dict['expected_value'],
                    event_dict['deviation_percent'],
                    event_dict['confidence_score'],
                    event_dict['is_anomaly'],
                    event_dict['detection_method']
                ])
        except Exception as e:
            logger.error(f"Failed to write detection event to CSV: {e}")
        
        logger.debug(f"Detection event logged: {detection_event.parameter_name} "
                    f"(confidence: {detection_event.confidence_score:.2f})")
    
    def export_to_csv(self) -> None:
        """
        Export all metrics to CSV files
        """
        logger.info("Exporting metrics to CSV files")
        
        try:
            # Export manipulations
            self._export_manipulations_csv()
            
            # Export charging cycles
            self._export_charging_cycles_csv()
            
            # Export degradation timeline
            self._export_degradation_timeline_csv()
            
            logger.info(f"Metrics exported successfully to {self.session_dir}")
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            self.log_error(e, "export_to_csv")
    
    def _export_manipulations_csv(self) -> None:
        """Export manipulation events to CSV"""
        if not self.manipulations:
            logger.debug("No manipulations to export")
            return
        
        with open(self.manipulations_csv, 'a', newline='') as f:
            writer = csv.writer(f)
            for event in self.manipulations:
                writer.writerow([
                    event['timestamp'],
                    event['parameter_name'],
                    event['original_value'],
                    event['modified_value'],
                    event['deviation_percent']
                ])
        
        logger.debug(f"Exported {len(self.manipulations)} manipulation events")
    
    def _export_charging_cycles_csv(self) -> None:
        """Export charging cycle data to CSV"""
        if not self.charging_cycles:
            logger.debug("No charging cycles to export")
            return
        
        with open(self.charging_cycles_csv, 'a', newline='') as f:
            writer = csv.writer(f)
            for cycle in self.charging_cycles:
                writer.writerow([
                    cycle['cycle_num'],
                    cycle['timestamp'],
                    cycle['duration_hours'],
                    cycle['energy_kwh'],
                    cycle['voltage_avg'],
                    cycle['current_avg'],
                    cycle['soc_min'],
                    cycle['soc_max'],
                    cycle['soh_before'],
                    cycle['soh_after'],
                    cycle['degradation_percent']
                ])
        
        logger.debug(f"Exported {len(self.charging_cycles)} charging cycles")
    
    def _export_degradation_timeline_csv(self) -> None:
        """Export degradation timeline to CSV"""
        if not self.degradation_events:
            logger.debug("No degradation events to export")
            return
        
        with open(self.degradation_timeline_csv, 'a', newline='') as f:
            writer = csv.writer(f)
            for event in self.degradation_events:
                writer.writerow([
                    event['timestamp'],
                    event['cycle_num'],
                    event['soh'],
                    event['voltage_stress'],
                    event['current_stress'],
                    event['soc_stress'],
                    event['combined_stress']
                ])
        
        logger.debug(f"Exported {len(self.degradation_events)} degradation events")
    
    def generate_summary_report(self) -> SimulationSummary:
        """
        Generate statistical summary of simulation
        
        Returns:
            SimulationSummary object
        """
        logger.info("Generating summary report")
        
        # Calculate aggregate statistics
        total_cycles = len(self.charging_cycles)
        total_duration_hours = sum(cycle['duration_hours'] for cycle in self.charging_cycles)
        
        # Get initial and final SoH
        initial_soh = 100.0
        final_soh = 100.0
        
        if self.charging_cycles:
            initial_soh = self.charging_cycles[0]['soh_before']
            final_soh = self.charging_cycles[-1]['soh_after']
        
        # Calculate total degradation
        total_degradation = initial_soh - final_soh
        
        # Calculate degradation rate per cycle
        degradation_rate_per_cycle = 0.0
        if total_cycles > 0:
            degradation_rate_per_cycle = total_degradation / total_cycles
        
        # Calculate average voltage and current deviations
        average_voltage_deviation = 0.0
        average_current_deviation = 0.0
        
        if self.manipulations:
            voltage_deviations = [
                abs(m['deviation_percent']) 
                for m in self.manipulations 
                if 'voltage' in m['parameter_name'].lower()
            ]
            current_deviations = [
                abs(m['deviation_percent']) 
                for m in self.manipulations 
                if 'current' in m['parameter_name'].lower()
            ]
            
            if voltage_deviations:
                average_voltage_deviation = sum(voltage_deviations) / len(voltage_deviations)
            if current_deviations:
                average_current_deviation = sum(current_deviations) / len(current_deviations)
        
        # Create summary object
        summary = SimulationSummary(
            session_id=self.session_id,
            total_cycles=total_cycles,
            total_duration_hours=total_duration_hours,
            initial_soh=initial_soh,
            final_soh=final_soh,
            total_degradation=total_degradation,
            degradation_rate_per_cycle=degradation_rate_per_cycle,
            average_voltage_deviation=average_voltage_deviation,
            average_current_deviation=average_current_deviation
        )
        
        # Export summary to JSON
        try:
            with open(self.summary_json, 'w') as f:
                json.dump(summary.to_dict(), f, indent=2)
            logger.info(f"Summary report saved to {self.summary_json}")
        except Exception as e:
            logger.error(f"Failed to save summary report: {e}")
            self.log_error(e, "generate_summary_report")
        
        return summary
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """
        Save simulation configuration to file
        
        Args:
            config: Configuration dictionary
        """
        config_path = os.path.join(self.session_dir, 'config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Configuration saved: {config_path}")
