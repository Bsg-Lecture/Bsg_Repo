"""
Unit tests for Battery Degradation Model
Tests the core functionality of battery health simulation
"""

import unittest
from attack_simulation.models.battery_model import (
    BatteryDegradationModel, DegradationParameters, DegradationResult
)


class TestDegradationParameters(unittest.TestCase):
    """Test DegradationParameters dataclass"""
    
    def test_default_parameters(self):
        """Test default parameter values"""
        params = DegradationParameters()
        self.assertEqual(params.optimal_voltage, 3.7)
        self.assertEqual(params.optimal_c_rate, 0.5)
        self.assertEqual(params.optimal_soc_min, 20.0)
        self.assertEqual(params.optimal_soc_max, 80.0)
        self.assertEqual(params.base_degradation_per_cycle, 0.001)
    
    def test_custom_parameters(self):
        """Test custom parameter values"""
        params = DegradationParameters(
            optimal_voltage=3.8,
            optimal_c_rate=0.7,
            base_degradation_per_cycle=0.002
        )
        self.assertEqual(params.optimal_voltage, 3.8)
        self.assertEqual(params.optimal_c_rate, 0.7)
        self.assertEqual(params.base_degradation_per_cycle, 0.002)


class TestBatteryDegradationModel(unittest.TestCase):
    """Test BatteryDegradationModel functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.model = BatteryDegradationModel(initial_capacity_ah=75.0)
    
    def test_initialization(self):
        """Test battery model initialization"""
        self.assertEqual(self.model.soh, 100.0)
        self.assertEqual(self.model.cycle_count, 0)
        self.assertEqual(self.model.capacity_ah, 75.0)
        self.assertIsNotNone(self.model.params)
    
    def test_get_remaining_capacity(self):
        """Test remaining capacity calculation"""
        self.model.soh = 90.0
        remaining = self.model.get_remaining_capacity()
        self.assertAlmostEqual(remaining, 67.5, places=1)  # 75 * 0.9
    
    def test_update_soh(self):
        """Test SoH update"""
        initial_soh = self.model.soh
        self.model.update_soh(0.5)
        self.assertEqual(self.model.soh, initial_soh - 0.5)
        self.assertEqual(self.model.cycle_count, 1)
    
    def test_update_soh_minimum_bound(self):
        """Test SoH cannot go below 0%"""
        self.model.soh = 0.5
        self.model.update_soh(1.0)
        self.assertEqual(self.model.soh, 0.0)
    
    def test_reset(self):
        """Test battery model reset"""
        self.model.soh = 85.0
        self.model.cycle_count = 100
        self.model.reset()
        self.assertEqual(self.model.soh, 100.0)
        self.assertEqual(self.model.cycle_count, 0)


class TestStressFactorCalculations(unittest.TestCase):
    """Test stress factor calculation methods"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.model = BatteryDegradationModel()
    
    def test_voltage_stress_optimal(self):
        """Test voltage stress at optimal voltage"""
        stress = self.model.calculate_voltage_stress_factor(3.7)
        self.assertAlmostEqual(stress, 1.0, places=2)
    
    def test_voltage_stress_overvoltage(self):
        """Test voltage stress with overvoltage"""
        stress = self.model.calculate_voltage_stress_factor(4.2)
        self.assertGreater(stress, 1.0)
    
    def test_voltage_stress_undervoltage(self):
        """Test voltage stress with undervoltage"""
        stress = self.model.calculate_voltage_stress_factor(3.2)
        self.assertGreater(stress, 1.0)
    
    def test_current_stress_optimal(self):
        """Test current stress at optimal C-rate"""
        stress = self.model.calculate_current_stress_factor(0.5)
        self.assertAlmostEqual(stress, 1.0, places=2)
    
    def test_current_stress_high_rate(self):
        """Test current stress with high C-rate"""
        stress = self.model.calculate_current_stress_factor(1.5)
        self.assertGreater(stress, 1.0)
    
    def test_current_stress_low_rate(self):
        """Test current stress with low C-rate"""
        stress = self.model.calculate_current_stress_factor(0.1)
        self.assertGreater(stress, 1.0)
    
    def test_soc_stress_optimal_range(self):
        """Test SoC stress within optimal range"""
        stress = self.model.calculate_soc_cycling_factor(20.0, 80.0)
        self.assertAlmostEqual(stress, 1.0, places=2)
    
    def test_soc_stress_low_soc(self):
        """Test SoC stress with low SoC"""
        stress = self.model.calculate_soc_cycling_factor(10.0, 80.0)
        self.assertGreater(stress, 1.0)
    
    def test_soc_stress_high_soc(self):
        """Test SoC stress with high SoC"""
        stress = self.model.calculate_soc_cycling_factor(20.0, 95.0)
        self.assertGreater(stress, 1.0)
    
    def test_soc_stress_both_extremes(self):
        """Test SoC stress with both low and high SoC"""
        stress = self.model.calculate_soc_cycling_factor(5.0, 95.0)
        self.assertGreater(stress, 1.0)
    
    def test_temperature_stress_placeholder(self):
        """Test temperature stress factor (placeholder)"""
        stress = self.model.calculate_temperature_stress_factor(25.0)
        self.assertEqual(stress, 1.0)


class TestChargingCycleSimulation(unittest.TestCase):
    """Test charging cycle simulation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.model = BatteryDegradationModel()
    
    def test_simulate_optimal_cycle(self):
        """Test simulation with optimal charging parameters"""
        profile = {
            'voltage': 3.7,
            'current': 0.5,
            'soc_min': 20.0,
            'soc_max': 80.0
        }
        
        result = self.model.simulate_charging_cycle(profile, duration_hours=1.0)
        
        self.assertIsInstance(result, DegradationResult)
        self.assertEqual(result.soh_before, 100.0)
        self.assertLess(result.soh_after, 100.0)
        self.assertGreater(result.degradation_percent, 0.0)
        self.assertAlmostEqual(result.voltage_stress_factor, 1.0, places=1)
        self.assertAlmostEqual(result.current_stress_factor, 1.0, places=1)
        self.assertAlmostEqual(result.soc_stress_factor, 1.0, places=1)
    
    def test_simulate_aggressive_cycle(self):
        """Test simulation with aggressive charging parameters"""
        profile = {
            'voltage': 4.3,  # High voltage
            'current': 1.5,  # High C-rate
            'soc_min': 5.0,  # Low SoC
            'soc_max': 95.0  # High SoC
        }
        
        result = self.model.simulate_charging_cycle(profile, duration_hours=1.0)
        
        # Aggressive parameters should cause higher degradation
        self.assertGreater(result.voltage_stress_factor, 1.0)
        self.assertGreater(result.current_stress_factor, 1.0)
        self.assertGreater(result.soc_stress_factor, 1.0)
        self.assertGreater(result.combined_stress_factor, 1.0)
        self.assertGreater(result.degradation_percent, 0.001)
    
    def test_simulate_multiple_cycles(self):
        """Test multiple charging cycles"""
        profile = {
            'voltage': 4.0,
            'current': 0.8,
            'soc_min': 20.0,
            'soc_max': 80.0
        }
        
        initial_soh = self.model.soh
        
        # Simulate 10 cycles
        for i in range(10):
            result = self.model.simulate_charging_cycle(profile, duration_hours=1.0)
            self.assertLess(result.soh_after, result.soh_before)
        
        # SoH should have decreased
        self.assertLess(self.model.soh, initial_soh)
        self.assertEqual(self.model.cycle_count, 10)
    
    def test_simulate_with_duration_scaling(self):
        """Test that longer duration causes more degradation"""
        profile = {
            'voltage': 4.0,
            'current': 0.8,
            'soc_min': 20.0,
            'soc_max': 80.0
        }
        
        # Short duration
        model1 = BatteryDegradationModel()
        result1 = model1.simulate_charging_cycle(profile, duration_hours=0.5)
        
        # Long duration
        model2 = BatteryDegradationModel()
        result2 = model2.simulate_charging_cycle(profile, duration_hours=2.0)
        
        # Longer duration should cause more degradation
        self.assertGreater(result2.degradation_percent, result1.degradation_percent)


class TestDegradationResult(unittest.TestCase):
    """Test DegradationResult dataclass"""
    
    def test_degradation_result_creation(self):
        """Test creating DegradationResult"""
        result = DegradationResult(
            soh_before=100.0,
            soh_after=99.9,
            degradation_percent=0.1,
            voltage_stress_factor=1.2,
            current_stress_factor=1.1,
            soc_stress_factor=1.05,
            combined_stress_factor=1.386
        )
        
        self.assertEqual(result.soh_before, 100.0)
        self.assertEqual(result.soh_after, 99.9)
        self.assertEqual(result.degradation_percent, 0.1)
        self.assertEqual(result.voltage_stress_factor, 1.2)
        self.assertEqual(result.current_stress_factor, 1.1)
        self.assertEqual(result.soc_stress_factor, 1.05)
        self.assertEqual(result.combined_stress_factor, 1.386)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_soh_at_zero_percent(self):
        """Test battery behavior at 0% SoH"""
        model = BatteryDegradationModel()
        model.soh = 0.1
        
        # Apply large degradation
        model.update_soh(0.5)
        
        # SoH should not go below 0
        self.assertEqual(model.soh, 0.0)
        self.assertGreaterEqual(model.soh, 0.0)
    
    def test_soh_with_negative_degradation(self):
        """Test SoH behavior with negative degradation (improvement)"""
        model = BatteryDegradationModel()
        model.soh = 95.0
        
        # Apply negative degradation (improvement)
        model.update_soh(-5.0)
        
        # SoH should increase
        self.assertEqual(model.soh, 100.0)
    
    def test_extreme_voltage_stress(self):
        """Test stress factor with extreme voltage"""
        model = BatteryDegradationModel()
        
        # Very high voltage
        stress_high = model.calculate_voltage_stress_factor(5.0)
        self.assertGreater(stress_high, 1.0)
        
        # Very low voltage
        stress_low = model.calculate_voltage_stress_factor(2.0)
        self.assertGreater(stress_low, 1.0)
    
    def test_extreme_current_stress(self):
        """Test stress factor with extreme current"""
        model = BatteryDegradationModel()
        
        # Very high C-rate
        stress_high = model.calculate_current_stress_factor(3.0)
        self.assertGreater(stress_high, 1.0)
        
        # Very low C-rate
        stress_low = model.calculate_current_stress_factor(0.01)
        self.assertGreater(stress_low, 1.0)
    
    def test_extreme_soc_range(self):
        """Test stress factor with extreme SoC range"""
        model = BatteryDegradationModel()
        
        # Full range (0-100%)
        stress_full = model.calculate_soc_cycling_factor(0.0, 100.0)
        self.assertGreater(stress_full, 1.0)
        
        # Very narrow range
        stress_narrow = model.calculate_soc_cycling_factor(49.0, 51.0)
        self.assertGreaterEqual(stress_narrow, 1.0)
    
    def test_zero_duration_cycle(self):
        """Test charging cycle with zero duration"""
        model = BatteryDegradationModel()
        
        profile = {
            'voltage': 3.7,
            'current': 0.5,
            'soc_min': 20.0,
            'soc_max': 80.0
        }
        
        result = model.simulate_charging_cycle(profile, duration_hours=0.0)
        
        # Zero duration should result in minimal degradation
        self.assertAlmostEqual(result.degradation_percent, 0.0, places=5)
        self.assertEqual(result.soh_before, result.soh_after)
    
    def test_very_long_duration_cycle(self):
        """Test charging cycle with very long duration"""
        model = BatteryDegradationModel()
        
        profile = {
            'voltage': 4.0,
            'current': 0.8,
            'soc_min': 20.0,
            'soc_max': 80.0
        }
        
        # Simulate 100 hour cycle
        result = model.simulate_charging_cycle(profile, duration_hours=100.0)
        
        # Long duration should cause significant degradation
        self.assertGreater(result.degradation_percent, 0.1)
        self.assertLess(result.soh_after, result.soh_before)
    
    def test_remaining_capacity_at_zero_soh(self):
        """Test remaining capacity calculation at 0% SoH"""
        model = BatteryDegradationModel(initial_capacity_ah=75.0)
        model.soh = 0.0
        
        remaining = model.get_remaining_capacity()
        self.assertEqual(remaining, 0.0)
    
    def test_remaining_capacity_at_full_soh(self):
        """Test remaining capacity calculation at 100% SoH"""
        model = BatteryDegradationModel(initial_capacity_ah=75.0)
        model.soh = 100.0
        
        remaining = model.get_remaining_capacity()
        self.assertEqual(remaining, 75.0)
    
    def test_cycle_count_increments(self):
        """Test that cycle count increments correctly"""
        model = BatteryDegradationModel()
        
        profile = {
            'voltage': 3.7,
            'current': 0.5,
            'soc_min': 20.0,
            'soc_max': 80.0
        }
        
        initial_count = model.cycle_count
        
        # Run 5 cycles
        for i in range(5):
            model.simulate_charging_cycle(profile, duration_hours=1.0)
        
        self.assertEqual(model.cycle_count, initial_count + 5)
    
    def test_reset_clears_cycle_count(self):
        """Test that reset clears cycle count"""
        model = BatteryDegradationModel()
        
        profile = {
            'voltage': 3.7,
            'current': 0.5,
            'soc_min': 20.0,
            'soc_max': 80.0
        }
        
        # Run some cycles
        for i in range(10):
            model.simulate_charging_cycle(profile, duration_hours=1.0)
        
        self.assertGreater(model.cycle_count, 0)
        
        # Reset
        model.reset()
        
        self.assertEqual(model.cycle_count, 0)


class TestDegradationAccuracy(unittest.TestCase):
    """Test degradation calculation accuracy"""
    
    def test_consistent_degradation_calculation(self):
        """Test that degradation calculation is consistent"""
        model1 = BatteryDegradationModel()
        model2 = BatteryDegradationModel()
        
        profile = {
            'voltage': 4.0,
            'current': 0.8,
            'soc_min': 20.0,
            'soc_max': 80.0
        }
        
        result1 = model1.simulate_charging_cycle(profile, duration_hours=1.0)
        result2 = model2.simulate_charging_cycle(profile, duration_hours=1.0)
        
        # Results should be identical
        self.assertEqual(result1.degradation_percent, result2.degradation_percent)
        self.assertEqual(result1.soh_after, result2.soh_after)
    
    def test_degradation_accumulation(self):
        """Test that degradation accumulates over cycles"""
        model = BatteryDegradationModel()
        
        profile = {
            'voltage': 4.0,
            'current': 0.8,
            'soc_min': 20.0,
            'soc_max': 80.0
        }
        
        soh_values = [model.soh]
        
        # Run 20 cycles
        for i in range(20):
            result = model.simulate_charging_cycle(profile, duration_hours=1.0)
            soh_values.append(result.soh_after)
        
        # SoH should decrease monotonically
        for i in range(len(soh_values) - 1):
            self.assertGreaterEqual(soh_values[i], soh_values[i + 1])
    
    def test_stress_factor_multiplication(self):
        """Test that combined stress is product of individual stresses"""
        model = BatteryDegradationModel()
        
        profile = {
            'voltage': 4.2,
            'current': 1.2,
            'soc_min': 10.0,
            'soc_max': 90.0
        }
        
        result = model.simulate_charging_cycle(profile, duration_hours=1.0)
        
        # Combined stress should be approximately the product
        expected_combined = (result.voltage_stress_factor * 
                           result.current_stress_factor * 
                           result.soc_stress_factor)
        
        self.assertAlmostEqual(result.combined_stress_factor, expected_combined, places=2)


if __name__ == '__main__':
    unittest.main()
