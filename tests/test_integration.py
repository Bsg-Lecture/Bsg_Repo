"""
Integration tests for Attack Simulation System
Tests end-to-end functionality and component integration
"""

import pytest
import asyncio
import os
import tempfile
import shutil
import json
from datetime import datetime
from pathlib import Path

from attack_simulation.core.attack_engine import AttackEngine, AttackConfig, AttackStrategy
from attack_simulation.models.battery_model import BatteryDegradationModel
from attack_simulation.metrics.metrics_collector import MetricsCollector
from attack_simulation.core.scenario_manager import ScenarioManager, ScenarioConfig


class TestEndToEndAttackSimulation:
    """Test complete attack simulation workflow"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_complete_attack_simulation(self, temp_output_dir):
        """Test end-to-end attack simulation with all components"""
        # Setup
        session_id = "integration_test_001"
        metrics_collector = MetricsCollector(temp_output_dir, session_id)
        
        attack_config = AttackConfig(
            enabled=True,
            strategy=AttackStrategy.AGGRESSIVE,
            voltage_deviation_percent=15.0,
            current_deviation_percent=20.0
        )
        
        attack_engine = AttackEngine(attack_config)
        battery_model = BatteryDegradationModel(initial_capacity_ah=75.0)
        
        # Simulate charging cycles
        num_cycles = 10
        
        for cycle in range(num_cycles):
            # Create sample charging profile
            profile = {
                'chargingProfileId': cycle + 1,
                'chargingSchedule': {
                    'chargingRateUnit': 'A',
                    'chargingSchedulePeriod': [
                        {'startPeriod': 0, 'limit': 32.0}
                    ]
                }
            }
            
            # Manipulate profile
            modified_profile = attack_engine.manipulate_charging_profile(profile)
            
            # Log manipulation
            metrics_collector.log_manipulation(
                timestamp=datetime.now(),
                original=profile,
                modified=modified_profile,
                parameter_name='limit',
                original_value=32.0,
                modified_value=modified_profile['chargingSchedule']['chargingSchedulePeriod'][0]['limit'],
                deviation_percent=attack_config.voltage_deviation_percent
            )
            
            # Simulate battery degradation
            battery_params = {
                'voltage': 3.9,
                'current': 0.7,
                'soc_min': 20.0,
                'soc_max': 80.0
            }
            
            soh_before = battery_model.soh
            degradation_result = battery_model.simulate_charging_cycle(
                battery_params, 
                duration_hours=2.0
            )
            
            # Log charging cycle
            metrics_collector.log_charging_cycle(
                cycle_num=cycle + 1,
                profile=battery_params,
                duration=2.0,
                energy_kwh=50.0,
                soh_before=soh_before,
                soh_after=degradation_result.soh_after
            )
            
            # Log degradation event
            metrics_collector.log_degradation_event(degradation_result, cycle_num=cycle + 1)
        
        # Export metrics
        metrics_collector.export_to_csv()
        
        # Generate summary
        summary = metrics_collector.generate_summary_report()
        
        # Verify results
        assert summary.total_cycles == num_cycles
        assert summary.initial_soh == 100.0
        assert summary.final_soh < 100.0
        assert summary.total_degradation > 0
        
        # Verify files created
        assert os.path.exists(metrics_collector.manipulations_csv)
        assert os.path.exists(metrics_collector.charging_cycles_csv)
        assert os.path.exists(metrics_collector.degradation_timeline_csv)
        assert os.path.exists(metrics_collector.summary_json)
    
    def test_baseline_vs_attack_comparison(self, temp_output_dir):
        """Test baseline vs attack scenario comparison"""
        # Baseline simulation
        baseline_model = BatteryDegradationModel()
        baseline_metrics = MetricsCollector(temp_output_dir, "baseline")
        
        profile = {
            'voltage': 3.7,
            'current': 0.5,
            'soc_min': 20.0,
            'soc_max': 80.0
        }
        
        for i in range(20):
            result = baseline_model.simulate_charging_cycle(profile, duration_hours=2.0)
            baseline_metrics.log_charging_cycle(
                cycle_num=i+1,
                profile=profile,
                duration=2.0,
                energy_kwh=50.0,
                soh_before=result.soh_before,
                soh_after=result.soh_after
            )
        
        baseline_summary = baseline_metrics.generate_summary_report()
        
        # Attack simulation
        attack_model = BatteryDegradationModel()
        attack_metrics = MetricsCollector(temp_output_dir, "attack")
        
        attack_profile = {
            'voltage': 4.2,  # Higher voltage
            'current': 1.0,  # Higher current
            'soc_min': 10.0,  # Lower SoC
            'soc_max': 95.0   # Higher SoC
        }
        
        for i in range(20):
            result = attack_model.simulate_charging_cycle(attack_profile, duration_hours=2.0)
            attack_metrics.log_charging_cycle(
                cycle_num=i+1,
                profile=attack_profile,
                duration=2.0,
                energy_kwh=50.0,
                soh_before=result.soh_before,
                soh_after=result.soh_after
            )
        
        attack_summary = attack_metrics.generate_summary_report()
        
        # Attack should cause more degradation
        assert attack_summary.total_degradation > baseline_summary.total_degradation
        assert attack_summary.final_soh < baseline_summary.final_soh


class TestOCPPMessageIntegration:
    """Test integration with OCPP message handling"""
    
    def test_ocpp_message_manipulation(self):
        """Test manipulating real OCPP SetChargingProfile message"""
        attack_config = AttackConfig(
            enabled=True,
            strategy=AttackStrategy.AGGRESSIVE,
            voltage_deviation_percent=15.0
        )
        
        attack_engine = AttackEngine(attack_config)
        
        # OCPP 2.0.1 SetChargingProfile message
        ocpp_message = [
            2,
            "msg-12345",
            "SetChargingProfile",
            {
                "evseId": 1,
                "chargingProfile": {
                    "id": 1,
                    "stackLevel": 0,
                    "chargingProfilePurpose": "TxProfile",
                    "chargingProfileKind": "Absolute",
                    "chargingSchedule": [
                        {
                            "id": 1,
                            "chargingRateUnit": "A",
                            "chargingSchedulePeriod": [
                                {
                                    "startPeriod": 0,
                                    "limit": 32.0,
                                    "numberPhases": 3
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        
        # Check if should manipulate
        assert attack_engine.should_manipulate(ocpp_message)
        
        # Extract charging profile
        charging_profile = ocpp_message[3]["chargingProfile"]
        
        # Manipulate
        modified_profile = attack_engine.manipulate_charging_profile(charging_profile)
        
        # Verify manipulation occurred
        original_limit = charging_profile["chargingSchedule"][0]["chargingSchedulePeriod"][0]["limit"]
        modified_limit = modified_profile["chargingSchedule"][0]["chargingSchedulePeriod"][0]["limit"]
        
        assert modified_limit != original_limit
        assert modified_limit > original_limit
    
    def test_ocpp_16_message_compatibility(self):
        """Test compatibility with OCPP 1.6 messages"""
        attack_config = AttackConfig(enabled=True)
        attack_engine = AttackEngine(attack_config)
        
        # OCPP 1.6 SetChargingProfile message
        ocpp_16_message = [
            2,
            "msg-67890",
            "SetChargingProfile",
            {
                "connectorId": 1,
                "csChargingProfiles": {
                    "chargingProfileId": 1,
                    "stackLevel": 0,
                    "chargingProfilePurpose": "TxProfile",
                    "chargingProfileKind": "Absolute",
                    "chargingSchedule": {
                        "chargingRateUnit": "A",
                        "chargingSchedulePeriod": [
                            {
                                "startPeriod": 0,
                                "limit": 16.0
                            }
                        ]
                    }
                }
            }
        ]
        
        # Should recognize as SetChargingProfile
        assert attack_engine.should_manipulate(ocpp_16_message)


class TestMultiScenarioBatchExecution:
    """Test multi-scenario batch execution"""
    
    @pytest.fixture
    def batch_config_file(self):
        """Create temporary batch configuration"""
        import yaml
        
        config = {
            'batch_config': {
                'name': 'Integration Test Batch',
                'output_dir': './test_batch_output',
                'scenarios': [
                    {
                        'name': 'baseline',
                        'attack_enabled': False,
                        'cycles': 5
                    },
                    {
                        'name': 'aggressive',
                        'attack_enabled': True,
                        'strategy': 'aggressive',
                        'cycles': 5,
                        'manipulations': {
                            'voltage': {
                                'enabled': True,
                                'deviation_percent': 20.0
                            }
                        }
                    },
                    {
                        'name': 'subtle',
                        'attack_enabled': True,
                        'strategy': 'subtle',
                        'cycles': 5,
                        'manipulations': {
                            'voltage': {
                                'enabled': True,
                                'deviation_percent': 20.0
                            }
                        }
                    }
                ]
            },
            'battery_model': {
                'initial_capacity_ah': 75.0,
                'reset_between_scenarios': True
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            temp_path = f.name
        
        yield temp_path
        
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_batch_execution(self, batch_config_file):
        """Test executing multiple scenarios in batch"""
        manager = ScenarioManager(batch_config_file)
        
        # Verify scenarios loaded
        assert len(manager.scenarios) == 3
        assert manager.scenarios[0].name == 'baseline'
        assert manager.scenarios[1].name == 'aggressive'
        assert manager.scenarios[2].name == 'subtle'
        
        # Run batch
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(manager.run_batch())
        
        # Verify results
        assert len(results) == 3
        
        # All scenarios should complete
        for result in results:
            assert result.total_cycles == 5
            assert result.final_soh < 100.0
        
        # Aggressive should have most degradation
        baseline_deg = results[0].total_degradation
        aggressive_deg = results[1].total_degradation
        subtle_deg = results[2].total_degradation
        
        assert aggressive_deg > baseline_deg
        assert aggressive_deg > subtle_deg


class TestOutputFileGeneration:
    """Test output file generation"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_all_output_files_created(self, temp_output_dir):
        """Verify all expected output files are created"""
        session_id = "file_test_001"
        metrics_collector = MetricsCollector(temp_output_dir, session_id)
        
        # Add some data
        metrics_collector.log_manipulation(
            timestamp=datetime.now(),
            original={'voltage': 3.7},
            modified={'voltage': 4.0},
            parameter_name='voltage',
            original_value=3.7,
            modified_value=4.0,
            deviation_percent=8.1
        )
        
        profile = {'voltage': 3.8, 'current': 0.5, 'soc_min': 20.0, 'soc_max': 80.0}
        metrics_collector.log_charging_cycle(
            cycle_num=1,
            profile=profile,
            duration=2.0,
            energy_kwh=50.0,
            soh_before=100.0,
            soh_after=99.95
        )
        
        # Export and generate summary
        metrics_collector.export_to_csv()
        summary = metrics_collector.generate_summary_report()
        
        # Verify all files exist
        session_dir = os.path.join(temp_output_dir, f"session_{session_id}")
        
        assert os.path.exists(session_dir)
        assert os.path.exists(os.path.join(session_dir, 'manipulations.csv'))
        assert os.path.exists(os.path.join(session_dir, 'charging_cycles.csv'))
        assert os.path.exists(os.path.join(session_dir, 'degradation_timeline.csv'))
        assert os.path.exists(os.path.join(session_dir, 'errors.csv'))
        assert os.path.exists(os.path.join(session_dir, 'summary.json'))
        assert os.path.exists(os.path.join(session_dir, 'plots'))
    
    def test_summary_json_format(self, temp_output_dir):
        """Test summary JSON file format"""
        session_id = "json_test_001"
        metrics_collector = MetricsCollector(temp_output_dir, session_id)
        
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
        
        summary = metrics_collector.generate_summary_report()
        
        # Read and validate JSON
        summary_path = os.path.join(
            temp_output_dir, 
            f"session_{session_id}", 
            'summary.json'
        )
        
        with open(summary_path, 'r') as f:
            data = json.load(f)
        
        # Verify required fields
        assert 'session_id' in data
        assert 'total_cycles' in data
        assert 'initial_soh' in data
        assert 'final_soh' in data
        assert 'total_degradation' in data
        assert 'degradation_rate_per_cycle' in data
        
        # Verify values
        assert data['total_cycles'] == 5
        assert data['initial_soh'] == 100.0
        assert data['final_soh'] == 99.5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
