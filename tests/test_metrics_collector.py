"""
Unit tests for MetricsCollector
"""

import os
import csv
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

import pytest

from attack_simulation.metrics.metrics_collector import MetricsCollector, SimulationSummary
from attack_simulation.models.battery_model import DegradationResult


class TestMetricsCollector:
    """Test suite for MetricsCollector"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def metrics_collector(self, temp_output_dir):
        """Create MetricsCollector instance"""
        session_id = "test_session_001"
        return MetricsCollector(temp_output_dir, session_id)
    
    def test_initialization(self, metrics_collector, temp_output_dir):
        """Test MetricsCollector initialization"""
        # Check session directory created
        assert os.path.exists(metrics_collector.session_dir)
        
        # Check plots directory created
        assert os.path.exists(metrics_collector.plots_dir)
        
        # Check CSV files initialized with headers
        assert os.path.exists(metrics_collector.manipulations_csv)
        assert os.path.exists(metrics_collector.charging_cycles_csv)
        assert os.path.exists(metrics_collector.degradation_timeline_csv)
        assert os.path.exists(metrics_collector.errors_csv)
    
    def test_log_manipulation(self, metrics_collector):
        """Test logging manipulation events"""
        timestamp = datetime.now()
        original = {'voltage': 3.7}
        modified = {'voltage': 4.2}
        
        metrics_collector.log_manipulation(
            timestamp=timestamp,
            original=original,
            modified=modified,
            parameter_name='voltage',
            original_value=3.7,
            modified_value=4.2,
            deviation_percent=13.5
        )
        
        assert len(metrics_collector.manipulations) == 1
        assert metrics_collector.manipulations[0]['parameter_name'] == 'voltage'
        assert metrics_collector.manipulations[0]['deviation_percent'] == 13.5
    
    def test_log_charging_cycle(self, metrics_collector):
        """Test logging charging cycle data"""
        profile = {
            'voltage': 3.8,
            'current': 0.5,
            'soc_min': 20.0,
            'soc_max': 80.0
        }
        
        metrics_collector.log_charging_cycle(
            cycle_num=1,
            profile=profile,
            duration=2.5,
            energy_kwh=50.0,
            soh_before=100.0,
            soh_after=99.95
        )
        
        assert len(metrics_collector.charging_cycles) == 1
        cycle = metrics_collector.charging_cycles[0]
        assert cycle['cycle_num'] == 1
        assert cycle['voltage_avg'] == 3.8
        assert cycle['soh_before'] == 100.0
        assert cycle['soh_after'] == 99.95
    
    def test_log_degradation_event(self, metrics_collector):
        """Test logging degradation events"""
        degradation_result = DegradationResult(
            soh_before=100.0,
            soh_after=99.95,
            degradation_percent=0.05,
            voltage_stress_factor=1.2,
            current_stress_factor=1.1,
            soc_stress_factor=1.0,
            combined_stress_factor=1.32
        )
        
        metrics_collector.log_degradation_event(degradation_result, cycle_num=1)
        
        assert len(metrics_collector.degradation_events) == 1
        event = metrics_collector.degradation_events[0]
        assert event['cycle_num'] == 1
        assert event['soh'] == 99.95
        assert event['combined_stress'] == 1.32
    
    def test_log_error(self, metrics_collector):
        """Test error logging"""
        error = ValueError("Test error")
        context = "test_context"
        
        metrics_collector.log_error(error, context)
        
        assert len(metrics_collector.errors) == 1
        assert metrics_collector.errors[0]['error_type'] == 'ValueError'
        assert metrics_collector.errors[0]['context'] == context
        
        # Check error written to CSV
        with open(metrics_collector.errors_csv, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 2  # Header + 1 error
    
    def test_export_to_csv(self, metrics_collector):
        """Test CSV export functionality"""
        # Add some test data
        timestamp = datetime.now()
        metrics_collector.log_manipulation(
            timestamp=timestamp,
            original={'voltage': 3.7},
            modified={'voltage': 4.2},
            parameter_name='voltage',
            original_value=3.7,
            modified_value=4.2,
            deviation_percent=13.5
        )
        
        profile = {'voltage': 3.8, 'current': 0.5, 'soc_min': 20.0, 'soc_max': 80.0}
        metrics_collector.log_charging_cycle(
            cycle_num=1,
            profile=profile,
            duration=2.5,
            energy_kwh=50.0,
            soh_before=100.0,
            soh_after=99.95
        )
        
        degradation_result = DegradationResult(
            soh_before=100.0,
            soh_after=99.95,
            degradation_percent=0.05,
            voltage_stress_factor=1.2,
            current_stress_factor=1.1,
            soc_stress_factor=1.0,
            combined_stress_factor=1.32
        )
        metrics_collector.log_degradation_event(degradation_result, cycle_num=1)
        
        # Export to CSV
        metrics_collector.export_to_csv()
        
        # Verify manipulations CSV
        with open(metrics_collector.manipulations_csv, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 2  # Header + 1 manipulation
        
        # Verify charging cycles CSV
        with open(metrics_collector.charging_cycles_csv, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 2  # Header + 1 cycle
        
        # Verify degradation timeline CSV
        with open(metrics_collector.degradation_timeline_csv, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 2  # Header + 1 event
    
    def test_generate_summary_report(self, metrics_collector):
        """Test summary report generation"""
        # Add test data
        profile = {'voltage': 3.8, 'current': 0.5, 'soc_min': 20.0, 'soc_max': 80.0}
        
        for i in range(5):
            metrics_collector.log_charging_cycle(
                cycle_num=i+1,
                profile=profile,
                duration=2.0,
                energy_kwh=50.0,
                soh_before=100.0 - i*0.1,
                soh_after=100.0 - (i+1)*0.1
            )
        
        # Generate summary
        summary = metrics_collector.generate_summary_report()
        
        assert summary.session_id == metrics_collector.session_id
        assert summary.total_cycles == 5
        assert summary.total_duration_hours == 10.0
        assert summary.initial_soh == 100.0
        assert summary.final_soh == 99.5
        assert summary.total_degradation == 0.5
        
        # Check summary JSON file created
        assert os.path.exists(metrics_collector.summary_json)
        
        # Verify JSON content
        with open(metrics_collector.summary_json, 'r') as f:
            summary_data = json.load(f)
            assert summary_data['total_cycles'] == 5
            assert summary_data['final_soh'] == 99.5
    
    def test_save_config(self, metrics_collector):
        """Test configuration saving"""
        config = {
            'attack_enabled': True,
            'strategy': 'aggressive',
            'voltage_deviation': 15.0
        }
        
        metrics_collector.save_config(config)
        
        config_path = os.path.join(metrics_collector.session_dir, 'config.json')
        assert os.path.exists(config_path)
        
        # Verify config content
        with open(config_path, 'r') as f:
            loaded_config = json.load(f)
            assert loaded_config['attack_enabled'] == True
            assert loaded_config['strategy'] == 'aggressive'
    
    def test_csv_format_validation(self, metrics_collector):
        """Test CSV export format is correct"""
        # Add test data
        timestamp = datetime.now()
        metrics_collector.log_manipulation(
            timestamp=timestamp,
            original={'voltage': 3.7},
            modified={'voltage': 4.2},
            parameter_name='voltage',
            original_value=3.7,
            modified_value=4.2,
            deviation_percent=13.5
        )
        
        metrics_collector.export_to_csv()
        
        # Read and validate CSV format
        with open(metrics_collector.manipulations_csv, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            assert len(rows) == 1
            row = rows[0]
            
            # Check all expected columns exist
            assert 'timestamp' in row
            assert 'parameter_name' in row
            assert 'original_value' in row
            assert 'modified_value' in row
            assert 'deviation_percent' in row
            
            # Validate data types
            assert row['parameter_name'] == 'voltage'
            assert float(row['original_value']) == 3.7
            assert float(row['modified_value']) == 4.2
            assert float(row['deviation_percent']) == 13.5
    
    def test_data_integrity(self, metrics_collector):
        """Test data integrity across multiple operations"""
        # Log multiple events
        for i in range(10):
            timestamp = datetime.now()
            metrics_collector.log_manipulation(
                timestamp=timestamp,
                original={'voltage': 3.7},
                modified={'voltage': 3.7 + i * 0.1},
                parameter_name='voltage',
                original_value=3.7,
                modified_value=3.7 + i * 0.1,
                deviation_percent=(i * 0.1 / 3.7) * 100
            )
        
        # Export to CSV
        metrics_collector.export_to_csv()
        
        # Read back and verify
        with open(metrics_collector.manipulations_csv, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            assert len(rows) == 10
            
            # Verify data integrity
            for i, row in enumerate(rows):
                expected_modified = 3.7 + i * 0.1
                actual_modified = float(row['modified_value'])
                assert abs(actual_modified - expected_modified) < 0.01
    
    def test_concurrent_logging(self, metrics_collector):
        """Test concurrent logging operations"""
        import threading
        
        def log_manipulations(start_idx, count):
            for i in range(count):
                timestamp = datetime.now()
                metrics_collector.log_manipulation(
                    timestamp=timestamp,
                    original={'voltage': 3.7},
                    modified={'voltage': 4.0},
                    parameter_name=f'voltage_{start_idx}_{i}',
                    original_value=3.7,
                    modified_value=4.0,
                    deviation_percent=8.1
                )
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=log_manipulations, args=(i, 10))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all events were logged
        assert len(metrics_collector.manipulations) == 50
    
    def test_empty_export(self, metrics_collector):
        """Test exporting with no data"""
        # Export without logging any data
        metrics_collector.export_to_csv()
        
        # CSV files should exist with headers only
        with open(metrics_collector.manipulations_csv, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 1  # Header only
        
        with open(metrics_collector.charging_cycles_csv, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 1  # Header only
    
    def test_summary_with_no_cycles(self, metrics_collector):
        """Test summary generation with no charging cycles"""
        summary = metrics_collector.generate_summary_report()
        
        assert summary.total_cycles == 0
        assert summary.total_duration_hours == 0.0
        assert summary.initial_soh == 100.0
        assert summary.final_soh == 100.0
        assert summary.total_degradation == 0.0
    
    def test_large_dataset_export(self, metrics_collector):
        """Test exporting large dataset"""
        # Log many events
        profile = {'voltage': 3.8, 'current': 0.5, 'soc_min': 20.0, 'soc_max': 80.0}
        
        for i in range(1000):
            metrics_collector.log_charging_cycle(
                cycle_num=i+1,
                profile=profile,
                duration=2.0,
                energy_kwh=50.0,
                soh_before=100.0 - i*0.01,
                soh_after=100.0 - (i+1)*0.01
            )
        
        # Export should complete without errors
        metrics_collector.export_to_csv()
        
        # Verify file exists and has correct number of rows
        with open(metrics_collector.charging_cycles_csv, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 1001  # Header + 1000 cycles
    
    def test_error_logging_multiple_errors(self, metrics_collector):
        """Test logging multiple errors"""
        errors = [
            ValueError("Error 1"),
            TypeError("Error 2"),
            RuntimeError("Error 3")
        ]
        
        for error in errors:
            metrics_collector.log_error(error, f"context_{error.__class__.__name__}")
        
        assert len(metrics_collector.errors) == 3
        
        # Verify all errors written to CSV
        with open(metrics_collector.errors_csv, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 4  # Header + 3 errors


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
