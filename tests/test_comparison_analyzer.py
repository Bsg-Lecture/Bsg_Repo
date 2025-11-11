"""
Tests for Comparison Analyzer
"""

import unittest
import os
import json
import csv
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from attack_simulation.metrics.comparison_analyzer import ComparisonAnalyzer, ComparisonMetrics


class TestComparisonAnalyzer(unittest.TestCase):
    """Test cases for ComparisonAnalyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directories for test data
        self.test_dir = tempfile.mkdtemp()
        self.baseline_dir = os.path.join(self.test_dir, 'baseline_session')
        self.attack_dir = os.path.join(self.test_dir, 'attack_session')
        self.output_dir = os.path.join(self.test_dir, 'comparison')
        
        Path(self.baseline_dir).mkdir(parents=True, exist_ok=True)
        Path(self.attack_dir).mkdir(parents=True, exist_ok=True)
        
        # Create test baseline data
        self._create_baseline_data()
        
        # Create test attack data
        self._create_attack_data()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _create_baseline_data(self):
        """Create test baseline simulation data"""
        # Create summary.json
        summary = {
            "session_id": "baseline_test",
            "total_cycles": 1000,
            "total_duration_hours": 2000.0,
            "initial_soh": 100.0,
            "final_soh": 99.0,
            "total_degradation": 1.0,
            "degradation_rate_per_cycle": 0.001,
            "average_voltage_deviation": 0.0,
            "average_current_deviation": 0.0
        }
        
        with open(os.path.join(self.baseline_dir, 'summary.json'), 'w') as f:
            json.dump(summary, f)
        
        # Create degradation_timeline.csv
        with open(os.path.join(self.baseline_dir, 'degradation_timeline.csv'), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'cycle_num', 'soh', 'voltage_stress',
                           'current_stress', 'soc_stress', 'combined_stress'])
            
            for i in range(0, 1001, 100):
                soh = 100.0 - (i * 0.001)
                writer.writerow([
                    f"2024-11-10T12:00:00",
                    i,
                    f"{soh:.4f}",
                    "1.0",
                    "1.0",
                    "1.0",
                    "1.0"
                ])
    
    def _create_attack_data(self):
        """Create test attack simulation data"""
        # Create summary.json
        summary = {
            "session_id": "attack_test",
            "total_cycles": 1000,
            "total_duration_hours": 2000.0,
            "initial_soh": 100.0,
            "final_soh": 97.5,
            "total_degradation": 2.5,
            "degradation_rate_per_cycle": 0.0025,
            "average_voltage_deviation": 15.0,
            "average_current_deviation": 25.0
        }
        
        with open(os.path.join(self.attack_dir, 'summary.json'), 'w') as f:
            json.dump(summary, f)
        
        # Create degradation_timeline.csv
        with open(os.path.join(self.attack_dir, 'degradation_timeline.csv'), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'cycle_num', 'soh', 'voltage_stress',
                           'current_stress', 'soc_stress', 'combined_stress'])
            
            for i in range(0, 1001, 100):
                soh = 100.0 - (i * 0.0025)
                writer.writerow([
                    f"2024-11-10T13:00:00",
                    i,
                    f"{soh:.4f}",
                    "1.5",
                    "1.3",
                    "1.0",
                    "1.95"
                ])
        
        # Create manipulations.csv
        with open(os.path.join(self.attack_dir, 'manipulations.csv'), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'parameter_name', 'original_value',
                           'modified_value', 'deviation_percent'])
            
            for i in range(10):
                writer.writerow([
                    f"2024-11-10T13:00:00",
                    f"limit_period_{i}",
                    "32.0",
                    "36.8",
                    "15.0"
                ])
    
    def test_initialization(self):
        """Test ComparisonAnalyzer initialization"""
        analyzer = ComparisonAnalyzer(
            baseline_session_dir=self.baseline_dir,
            attack_session_dir=self.attack_dir,
            output_dir=self.output_dir
        )
        
        self.assertEqual(analyzer.baseline_session_dir, self.baseline_dir)
        self.assertEqual(analyzer.attack_session_dir, self.attack_dir)
        self.assertEqual(analyzer.output_dir, self.output_dir)
        self.assertTrue(os.path.exists(self.output_dir))
    
    def test_load_simulation_data(self):
        """Test loading simulation data"""
        analyzer = ComparisonAnalyzer(
            baseline_session_dir=self.baseline_dir,
            attack_session_dir=self.attack_dir,
            output_dir=self.output_dir
        )
        
        success = analyzer.load_simulation_data()
        
        self.assertTrue(success)
        self.assertIsNotNone(analyzer.baseline_summary)
        self.assertIsNotNone(analyzer.attack_summary)
        self.assertFalse(analyzer.baseline_degradation_data.empty)
        self.assertFalse(analyzer.attack_degradation_data.empty)
        self.assertFalse(analyzer.attack_manipulation_data.empty)
    
    def test_calculate_degradation_difference(self):
        """Test degradation difference calculation"""
        analyzer = ComparisonAnalyzer(
            baseline_session_dir=self.baseline_dir,
            attack_session_dir=self.attack_dir,
            output_dir=self.output_dir
        )
        
        analyzer.load_simulation_data()
        degradation_diff = analyzer.calculate_degradation_difference()
        
        # Attack degradation (2.5%) - Baseline degradation (1.0%) = 1.5%
        self.assertAlmostEqual(degradation_diff, 1.5, places=4)
    
    def test_compute_degradation_acceleration_factor(self):
        """Test degradation acceleration factor calculation"""
        analyzer = ComparisonAnalyzer(
            baseline_session_dir=self.baseline_dir,
            attack_session_dir=self.attack_dir,
            output_dir=self.output_dir
        )
        
        analyzer.load_simulation_data()
        acceleration_factor = analyzer.compute_degradation_acceleration_factor()
        
        # Attack rate (0.0025) / Baseline rate (0.001) = 2.5x
        self.assertAlmostEqual(acceleration_factor, 2.5, places=2)
    
    def test_find_cycles_to_threshold(self):
        """Test finding cycles to reach SoH threshold"""
        analyzer = ComparisonAnalyzer(
            baseline_session_dir=self.baseline_dir,
            attack_session_dir=self.attack_dir,
            output_dir=self.output_dir
        )
        
        analyzer.load_simulation_data()
        
        # Baseline should not reach 90% in 1000 cycles (only degrades to 99%)
        baseline_90 = analyzer.find_cycles_to_threshold(analyzer.baseline_degradation_data, 90.0)
        self.assertIsNone(baseline_90)
        
        # Attack should not reach 90% in 1000 cycles (only degrades to 97.5%)
        attack_90 = analyzer.find_cycles_to_threshold(analyzer.attack_degradation_data, 90.0)
        self.assertIsNone(attack_90)
    
    def test_generate_comparison_metrics(self):
        """Test comprehensive comparison metrics generation"""
        analyzer = ComparisonAnalyzer(
            baseline_session_dir=self.baseline_dir,
            attack_session_dir=self.attack_dir,
            output_dir=self.output_dir
        )
        
        analyzer.load_simulation_data()
        metrics = analyzer.generate_comparison_metrics()
        
        self.assertIsInstance(metrics, ComparisonMetrics)
        self.assertEqual(metrics.baseline_session_id, "baseline_test")
        self.assertEqual(metrics.attack_session_id, "attack_test")
        self.assertAlmostEqual(metrics.baseline_final_soh, 99.0, places=2)
        self.assertAlmostEqual(metrics.attack_final_soh, 97.5, places=2)
        self.assertAlmostEqual(metrics.degradation_difference, 1.5, places=4)
        self.assertAlmostEqual(metrics.degradation_acceleration_factor, 2.5, places=2)
        self.assertEqual(metrics.baseline_cycles, 1000)
        self.assertEqual(metrics.attack_cycles, 1000)
    
    def test_generate_comparison_report(self):
        """Test comparison report generation"""
        analyzer = ComparisonAnalyzer(
            baseline_session_dir=self.baseline_dir,
            attack_session_dir=self.attack_dir,
            output_dir=self.output_dir
        )
        
        analyzer.load_simulation_data()
        report_path = analyzer.generate_comparison_report()
        
        self.assertTrue(os.path.exists(report_path))
        self.assertTrue(report_path.endswith('comparison_report.txt'))
        
        # Check that metrics JSON was also created
        metrics_json_path = os.path.join(self.output_dir, 'comparison_metrics.json')
        self.assertTrue(os.path.exists(metrics_json_path))
        
        # Verify report content
        with open(report_path, 'r') as f:
            content = f.read()
            self.assertIn("BASELINE VS ATTACK SIMULATION COMPARISON REPORT", content)
            self.assertIn("baseline_test", content)
            self.assertIn("attack_test", content)
            self.assertIn("Degradation Acceleration Factor", content)
    
    def test_export_comparison_csv(self):
        """Test CSV export of comparison metrics"""
        analyzer = ComparisonAnalyzer(
            baseline_session_dir=self.baseline_dir,
            attack_session_dir=self.attack_dir,
            output_dir=self.output_dir
        )
        
        analyzer.load_simulation_data()
        csv_path = analyzer.export_comparison_csv()
        
        self.assertTrue(os.path.exists(csv_path))
        self.assertTrue(csv_path.endswith('comparison_metrics.csv'))
        
        # Verify CSV content
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            # Check header
            self.assertEqual(rows[0], ['Metric', 'Baseline', 'Attack', 'Difference/Factor'])
            
            # Check that we have data rows
            self.assertGreater(len(rows), 1)
    
    def test_missing_baseline_data(self):
        """Test handling of missing baseline data"""
        # Create analyzer with non-existent baseline directory
        missing_baseline = os.path.join(self.test_dir, 'missing_baseline')
        
        analyzer = ComparisonAnalyzer(
            baseline_session_dir=missing_baseline,
            attack_session_dir=self.attack_dir,
            output_dir=self.output_dir
        )
        
        success = analyzer.load_simulation_data()
        self.assertFalse(success)
    
    def test_missing_attack_data(self):
        """Test handling of missing attack data"""
        # Create analyzer with non-existent attack directory
        missing_attack = os.path.join(self.test_dir, 'missing_attack')
        
        analyzer = ComparisonAnalyzer(
            baseline_session_dir=self.baseline_dir,
            attack_session_dir=missing_attack,
            output_dir=self.output_dir
        )
        
        success = analyzer.load_simulation_data()
        self.assertFalse(success)


if __name__ == '__main__':
    unittest.main()
