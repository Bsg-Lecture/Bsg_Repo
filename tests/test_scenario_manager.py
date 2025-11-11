"""
Unit tests for ScenarioManager
"""

import pytest
import asyncio
import os
import tempfile
import yaml
from pathlib import Path

# Check if pytest-asyncio is available
try:
    import pytest_asyncio
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

from attack_simulation.core.scenario_manager import (
    ScenarioManager, 
    ScenarioConfig, 
    BatchConfig
)
from attack_simulation.core.attack_engine import AttackStrategy


class TestScenarioConfig:
    """Tests for ScenarioConfig"""
    
    def test_scenario_config_creation(self):
        """Test creating a ScenarioConfig"""
        scenario = ScenarioConfig(
            name="test_scenario",
            attack_enabled=True,
            strategy="aggressive",
            cycles=100
        )
        
        assert scenario.name == "test_scenario"
        assert scenario.attack_enabled is True
        assert scenario.strategy == "aggressive"
        assert scenario.cycles == 100
        assert isinstance(scenario.manipulations, dict)
    
    def test_scenario_to_attack_config(self):
        """Test converting ScenarioConfig to AttackConfig"""
        scenario = ScenarioConfig(
            name="test",
            attack_enabled=True,
            strategy="aggressive",
            cycles=100,
            manipulations={
                'voltage': {
                    'enabled': True,
                    'deviation_percent': 20.0
                },
                'current': {
                    'enabled': False
                }
            }
        )
        
        attack_config = scenario.to_attack_config()
        
        assert attack_config.enabled is True
        assert attack_config.strategy == AttackStrategy.AGGRESSIVE
        assert attack_config.voltage_enabled is True
        assert attack_config.voltage_deviation_percent == 20.0
        assert attack_config.current_enabled is False


class TestScenarioManager:
    """Tests for ScenarioManager"""
    
    @pytest.fixture
    def temp_batch_config(self):
        """Create a temporary batch configuration file"""
        config_data = {
            'batch_config': {
                'name': 'Test Batch',
                'output_dir': './test_output',
                'scenarios': [
                    {
                        'name': 'baseline',
                        'attack_enabled': False,
                        'cycles': 10,
                        'description': 'Baseline test'
                    },
                    {
                        'name': 'aggressive_test',
                        'attack_enabled': True,
                        'strategy': 'aggressive',
                        'cycles': 10,
                        'description': 'Aggressive attack test',
                        'manipulations': {
                            'voltage': {
                                'enabled': True,
                                'deviation_percent': 15.0
                            }
                        }
                    }
                ]
            },
            'battery_model': {
                'initial_capacity_ah': 75.0,
                'reset_between_scenarios': True
            },
            'output': {
                'generate_comparison_report': True,
                'generate_plots': False
            },
            'execution': {
                'parallel': False,
                'continue_on_error': True
            }
        }
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_scenario_manager_initialization(self, temp_batch_config):
        """Test ScenarioManager initialization"""
        manager = ScenarioManager(temp_batch_config)
        
        assert manager.batch_config is not None
        assert manager.batch_config.name == 'Test Batch'
        assert len(manager.scenarios) == 2
        assert manager.scenarios[0].name == 'baseline'
        assert manager.scenarios[1].name == 'aggressive_test'
    
    def test_load_batch_config(self, temp_batch_config):
        """Test loading batch configuration"""
        manager = ScenarioManager(temp_batch_config)
        
        # Check batch config
        assert manager.batch_config.name == 'Test Batch'
        assert manager.batch_config.output_dir == './test_output'
        
        # Check scenarios
        assert len(manager.scenarios) == 2
        
        baseline = manager.scenarios[0]
        assert baseline.name == 'baseline'
        assert baseline.attack_enabled is False
        assert baseline.cycles == 10
        
        attack = manager.scenarios[1]
        assert attack.name == 'aggressive_test'
        assert attack.attack_enabled is True
        assert attack.strategy == 'aggressive'
        assert attack.cycles == 10
    
    @pytest.mark.skipif(not ASYNC_AVAILABLE, reason="pytest-asyncio not installed")
    def test_run_scenario(self, temp_batch_config):
        """Test running a single scenario"""
        manager = ScenarioManager(temp_batch_config)
        
        # Run baseline scenario
        scenario = manager.scenarios[0]
        
        # Run async function synchronously for testing
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(manager.run_scenario(scenario))
        
        # Check result
        assert result is not None
        assert result.total_cycles == 10
        assert result.initial_soh == 100.0
        assert result.final_soh < 100.0  # Should have some degradation
        assert result.total_degradation > 0
    
    @pytest.mark.skipif(not ASYNC_AVAILABLE, reason="pytest-asyncio not installed")
    def test_run_batch(self, temp_batch_config):
        """Test running batch execution"""
        manager = ScenarioManager(temp_batch_config)
        
        # Run batch
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(manager.run_batch())
        
        # Check results
        assert len(results) == 2
        assert all(r.total_cycles == 10 for r in results)
        assert all(r.final_soh < 100.0 for r in results)
        
        # Attack scenario should have more degradation than baseline
        baseline_result = results[0]
        attack_result = results[1]
        assert attack_result.total_degradation > baseline_result.total_degradation
    
    def test_create_sample_charging_profile(self, temp_batch_config):
        """Test creating sample charging profile"""
        manager = ScenarioManager(temp_batch_config)
        scenario = manager.scenarios[0]
        
        profile = manager._create_sample_charging_profile(scenario)
        
        assert 'chargingProfileId' in profile
        assert 'chargingSchedule' in profile
        assert 'chargingSchedulePeriod' in profile['chargingSchedule']
        assert len(profile['chargingSchedule']['chargingSchedulePeriod']) > 0
    
    def test_extract_battery_parameters(self, temp_batch_config):
        """Test extracting battery parameters from charging profile"""
        manager = ScenarioManager(temp_batch_config)
        
        profile = {
            'chargingSchedule': {
                'chargingRateUnit': 'A',
                'chargingSchedulePeriod': [
                    {'startPeriod': 0, 'limit': 32.0, 'numberPhases': 3}
                ]
            }
        }
        
        params = manager._extract_battery_parameters(profile)
        
        assert 'voltage' in params
        assert 'current' in params
        assert 'soc_min' in params
        assert 'soc_max' in params
        assert 'temperature' in params
        
        assert params['voltage'] > 0
        assert params['current'] > 0
        assert 0 <= params['soc_min'] <= 100
        assert 0 <= params['soc_max'] <= 100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
