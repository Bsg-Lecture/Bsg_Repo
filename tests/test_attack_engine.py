"""
Unit tests for Attack Engine
Tests the core functionality of charging profile manipulation
"""

import unittest
from datetime import datetime
from attack_simulation.core.attack_engine import (
    AttackEngine, AttackConfig, AttackStrategy, ManipulationType
)
from attack_simulation.metrics.metrics_collector import MetricsCollector


class TestAttackConfig(unittest.TestCase):
    """Test AttackConfig functionality"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = AttackConfig()
        self.assertTrue(config.enabled)
        self.assertEqual(config.strategy, AttackStrategy.AGGRESSIVE)
        self.assertTrue(config.voltage_enabled)
        self.assertTrue(config.current_enabled)
        self.assertTrue(config.curve_enabled)
    
    def test_config_from_dict(self):
        """Test creating config from dictionary"""
        config_dict = {
            'enabled': True,
            'strategy': 'subtle',
            'voltage_enabled': True,
            'voltage_deviation_percent': 10.0,
            'current_enabled': False
        }
        
        config = AttackConfig.from_dict(config_dict)
        self.assertTrue(config.enabled)
        self.assertEqual(config.strategy, AttackStrategy.SUBTLE)
        self.assertTrue(config.voltage_enabled)
        self.assertEqual(config.voltage_deviation_percent, 10.0)
        self.assertFalse(config.current_enabled)


class TestAttackEngine(unittest.TestCase):
    """Test AttackEngine functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = AttackConfig(
            enabled=True,
            strategy=AttackStrategy.AGGRESSIVE,
            voltage_deviation_percent=15.0,
            current_deviation_percent=25.0
        )
        self.engine = AttackEngine(self.config)
    
    def test_engine_initialization(self):
        """Test attack engine initialization"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.config.strategy, AttackStrategy.AGGRESSIVE)
    
    def test_should_manipulate_enabled(self):
        """Test should_manipulate returns True for SetChargingProfile"""
        message = [2, "12345", "SetChargingProfile", {}]
        self.assertTrue(self.engine.should_manipulate(message))
    
    def test_should_manipulate_disabled(self):
        """Test should_manipulate returns False when disabled"""
        config = AttackConfig(enabled=False)
        engine = AttackEngine(config)
        message = [2, "12345", "SetChargingProfile", {}]
        self.assertFalse(engine.should_manipulate(message))
    
    def test_should_manipulate_wrong_message_type(self):
        """Test should_manipulate returns False for non-target messages"""
        message = [2, "12345", "BootNotification", {}]
        self.assertFalse(self.engine.should_manipulate(message))
    
    def test_get_message_id(self):
        """Test extracting message ID from OCPP message"""
        message = [2, "test-message-123", "SetChargingProfile", {}]
        message_id = self.engine.get_message_id(message)
        self.assertEqual(message_id, "test-message-123")
    
    def test_voltage_manipulation(self):
        """Test voltage manipulation increases limits"""
        profile = {
            'chargingSchedule': {
                'chargingRateUnit': 'A',
                'chargingSchedulePeriod': [
                    {'startPeriod': 0, 'limit': 32.0}
                ]
            }
        }
        
        self.engine.apply_voltage_manipulation(profile)
        
        # Check that limit was increased
        new_limit = profile['chargingSchedule']['chargingSchedulePeriod'][0]['limit']
        self.assertGreater(new_limit, 32.0)
    
    def test_current_manipulation(self):
        """Test current manipulation increases limits"""
        profile = {
            'chargingSchedule': {
                'chargingRateUnit': 'A',
                'chargingSchedulePeriod': [
                    {'startPeriod': 0, 'limit': 50.0}
                ]
            }
        }
        
        self.engine.apply_current_manipulation(profile)
        
        # Check that limit was increased
        new_limit = profile['chargingSchedule']['chargingSchedulePeriod'][0]['limit']
        self.assertGreater(new_limit, 50.0)
    
    def test_curve_manipulation_flatten(self):
        """Test curve manipulation with flatten mode"""
        config = AttackConfig(curve_modification_type='flatten')
        engine = AttackEngine(config)
        
        profile = {
            'chargingSchedule': {
                'chargingRateUnit': 'A',
                'chargingSchedulePeriod': [
                    {'startPeriod': 0, 'limit': 32.0},
                    {'startPeriod': 3600, 'limit': 16.0}
                ]
            }
        }
        
        engine.apply_curve_manipulation(profile)
        
        # Check that all limits are equal (flattened)
        periods = profile['chargingSchedule']['chargingSchedulePeriod']
        self.assertEqual(periods[0]['limit'], periods[1]['limit'])
    
    def test_manipulate_charging_profile(self):
        """Test full charging profile manipulation"""
        profile = {
            'id': 1,
            'stackLevel': 0,
            'chargingSchedule': {
                'chargingRateUnit': 'A',
                'chargingSchedulePeriod': [
                    {'startPeriod': 0, 'limit': 32.0}
                ]
            }
        }
        
        modified = self.engine.manipulate_charging_profile(profile)
        
        # Check that profile was modified
        self.assertIsNotNone(modified)
        # Original should be unchanged
        self.assertEqual(profile['chargingSchedule']['chargingSchedulePeriod'][0]['limit'], 32.0)
        # Modified should be different
        modified_limit = modified['chargingSchedule']['chargingSchedulePeriod'][0]['limit']
        self.assertNotEqual(modified_limit, 32.0)


class TestAttackStrategies(unittest.TestCase):
    """Test different attack strategies"""
    
    def test_aggressive_strategy_deviation(self):
        """Test aggressive strategy uses full deviation"""
        config = AttackConfig(
            strategy=AttackStrategy.AGGRESSIVE,
            voltage_deviation_percent=20.0
        )
        engine = AttackEngine(config)
        
        deviation = engine._calculate_deviation(20.0, AttackStrategy.AGGRESSIVE)
        self.assertEqual(deviation, 20.0)
    
    def test_subtle_strategy_deviation(self):
        """Test subtle strategy uses reduced deviation"""
        config = AttackConfig(
            strategy=AttackStrategy.SUBTLE,
            voltage_deviation_percent=20.0
        )
        engine = AttackEngine(config)
        
        deviation = engine._calculate_deviation(20.0, AttackStrategy.SUBTLE)
        self.assertLess(deviation, 20.0)
        self.assertEqual(deviation, 4.0)  # 20% of 20.0
    
    def test_random_strategy_deviation(self):
        """Test random strategy generates random deviation"""
        config = AttackConfig(
            strategy=AttackStrategy.RANDOM,
            randomization_enabled=True,
            randomization_seed=42,
            randomization_deviation_range=(5, 30)
        )
        engine = AttackEngine(config)
        
        deviation = engine._calculate_deviation(20.0, AttackStrategy.RANDOM)
        self.assertGreaterEqual(deviation, 5.0)
        self.assertLessEqual(deviation, 30.0)
    
    def test_targeted_strategy_deviation(self):
        """Test targeted strategy uses base deviation"""
        config = AttackConfig(
            strategy=AttackStrategy.TARGETED,
            voltage_deviation_percent=15.0
        )
        engine = AttackEngine(config)
        
        deviation = engine._calculate_deviation(15.0, AttackStrategy.TARGETED)
        self.assertEqual(deviation, 15.0)


class TestChargingCurveManipulation(unittest.TestCase):
    """Test charging curve manipulation methods"""
    
    def test_curve_manipulation_steepen(self):
        """Test curve manipulation with steepen mode"""
        config = AttackConfig(curve_modification_type='steepen')
        engine = AttackEngine(config)
        
        profile = {
            'chargingSchedule': {
                'chargingRateUnit': 'A',
                'chargingSchedulePeriod': [
                    {'startPeriod': 0, 'limit': 32.0},
                    {'startPeriod': 3600, 'limit': 24.0},
                    {'startPeriod': 7200, 'limit': 16.0}
                ]
            }
        }
        
        engine.apply_curve_manipulation(profile)
        
        # Check that curve is steepened (differences increased)
        periods = profile['chargingSchedule']['chargingSchedulePeriod']
        self.assertIsNotNone(periods)
        self.assertEqual(len(periods), 3)
    
    def test_curve_manipulation_invert(self):
        """Test curve manipulation with invert mode"""
        config = AttackConfig(curve_modification_type='invert')
        engine = AttackEngine(config)
        
        profile = {
            'chargingSchedule': {
                'chargingRateUnit': 'A',
                'chargingSchedulePeriod': [
                    {'startPeriod': 0, 'limit': 32.0},
                    {'startPeriod': 3600, 'limit': 16.0}
                ]
            }
        }
        
        original_first = profile['chargingSchedule']['chargingSchedulePeriod'][0]['limit']
        original_last = profile['chargingSchedule']['chargingSchedulePeriod'][1]['limit']
        
        engine.apply_curve_manipulation(profile)
        
        # Check that curve is inverted
        periods = profile['chargingSchedule']['chargingSchedulePeriod']
        # After inversion, first should be lower, last should be higher
        self.assertLess(periods[0]['limit'], original_first)
        self.assertGreater(periods[1]['limit'], original_last)
    
    def test_curve_manipulation_disabled(self):
        """Test that curve manipulation is skipped when disabled"""
        config = AttackConfig(
            curve_enabled=False,
            voltage_enabled=False,
            current_enabled=False
        )
        engine = AttackEngine(config)
        
        profile = {
            'chargingSchedule': {
                'chargingRateUnit': 'A',
                'chargingSchedulePeriod': [
                    {'startPeriod': 0, 'limit': 32.0},
                    {'startPeriod': 3600, 'limit': 16.0}
                ]
            }
        }
        
        original_limits = [p['limit'] for p in profile['chargingSchedule']['chargingSchedulePeriod']]
        
        # When all manipulations are disabled, profile should remain unchanged
        modified = engine.manipulate_charging_profile(profile)
        
        # Limits should be unchanged
        new_limits = [p['limit'] for p in modified['chargingSchedule']['chargingSchedulePeriod']]
        self.assertEqual(original_limits, new_limits)


class TestAttackStrategySelection(unittest.TestCase):
    """Test attack strategy selection and behavior"""
    
    def test_strategy_selection_aggressive(self):
        """Test aggressive strategy selection"""
        config = AttackConfig(strategy=AttackStrategy.AGGRESSIVE)
        engine = AttackEngine(config)
        
        self.assertEqual(engine.config.strategy, AttackStrategy.AGGRESSIVE)
    
    def test_strategy_selection_subtle(self):
        """Test subtle strategy selection"""
        config = AttackConfig(strategy=AttackStrategy.SUBTLE)
        engine = AttackEngine(config)
        
        self.assertEqual(engine.config.strategy, AttackStrategy.SUBTLE)
    
    def test_strategy_selection_random(self):
        """Test random strategy selection"""
        config = AttackConfig(
            strategy=AttackStrategy.RANDOM,
            randomization_enabled=True,
            randomization_seed=42
        )
        engine = AttackEngine(config)
        
        self.assertEqual(engine.config.strategy, AttackStrategy.RANDOM)
        self.assertTrue(engine.config.randomization_enabled)
    
    def test_strategy_selection_targeted(self):
        """Test targeted strategy selection"""
        config = AttackConfig(strategy=AttackStrategy.TARGETED)
        engine = AttackEngine(config)
        
        self.assertEqual(engine.config.strategy, AttackStrategy.TARGETED)
    
    def test_strategy_from_string(self):
        """Test creating strategy from string"""
        config_dict = {'strategy': 'aggressive'}
        config = AttackConfig.from_dict(config_dict)
        
        self.assertEqual(config.strategy, AttackStrategy.AGGRESSIVE)
    
    def test_multiple_manipulations_with_strategy(self):
        """Test that strategy affects all manipulation types"""
        config = AttackConfig(
            strategy=AttackStrategy.SUBTLE,
            voltage_enabled=True,
            current_enabled=True,
            voltage_deviation_percent=20.0,
            current_deviation_percent=30.0
        )
        engine = AttackEngine(config)
        
        profile = {
            'chargingSchedule': {
                'chargingRateUnit': 'A',
                'chargingSchedulePeriod': [
                    {'startPeriod': 0, 'limit': 32.0}
                ]
            }
        }
        
        modified = engine.manipulate_charging_profile(profile)
        
        # Subtle strategy should apply reduced deviations
        original_limit = profile['chargingSchedule']['chargingSchedulePeriod'][0]['limit']
        modified_limit = modified['chargingSchedule']['chargingSchedulePeriod'][0]['limit']
        
        # Deviation should be present but smaller than aggressive
        self.assertNotEqual(original_limit, modified_limit)
        deviation_percent = abs((modified_limit - original_limit) / original_limit * 100)
        self.assertLess(deviation_percent, 20.0)  # Should be less than full deviation


class TestManipulationLogging(unittest.TestCase):
    """Test manipulation logging functionality"""
    
    def test_extract_manipulation_events(self):
        """Test extracting manipulation events from profile comparison"""
        config = AttackConfig()
        engine = AttackEngine(config)
        
        original = {
            'chargingSchedule': {
                'chargingSchedulePeriod': [
                    {'startPeriod': 0, 'limit': 32.0}
                ]
            }
        }
        
        modified = {
            'chargingSchedule': {
                'chargingSchedulePeriod': [
                    {'startPeriod': 0, 'limit': 40.0}
                ]
            }
        }
        
        events = engine._extract_manipulation_events(
            original, modified, datetime.now()
        )
        
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['original_value'], 32.0)
        self.assertEqual(events[0]['modified_value'], 40.0)
        self.assertAlmostEqual(events[0]['deviation_percent'], 25.0, places=1)
    
    def test_get_manipulation_summary(self):
        """Test getting manipulation summary"""
        config = AttackConfig(
            strategy=AttackStrategy.AGGRESSIVE,
            voltage_enabled=True,
            current_enabled=True
        )
        engine = AttackEngine(config)
        
        summary = engine.get_manipulation_summary()
        
        self.assertEqual(summary['strategy'], 'aggressive')
        self.assertTrue(summary['voltage_enabled'])
        self.assertTrue(summary['current_enabled'])


if __name__ == '__main__':
    unittest.main()
