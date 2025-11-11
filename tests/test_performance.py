"""
Performance tests for Attack Simulation System
Tests throughput, resource usage, and scalability
"""

import pytest
import time
import os
import tempfile
import shutil
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from attack_simulation.core.attack_engine import AttackEngine, AttackConfig, AttackStrategy
from attack_simulation.models.battery_model import BatteryDegradationModel
from attack_simulation.metrics.metrics_collector import MetricsCollector


class TestMessageProcessingThroughput:
    """Test message processing throughput"""
    
    def test_attack_engine_throughput(self):
        """Measure messages processed per second by attack engine"""
        config = AttackConfig(
            enabled=True,
            strategy=AttackStrategy.AGGRESSIVE,
            voltage_deviation_percent=15.0
        )
        
        engine = AttackEngine(config)
        
        # Create sample charging profile
        profile = {
            'chargingProfileId': 1,
            'chargingSchedule': {
                'chargingRateUnit': 'A',
                'chargingSchedulePeriod': [
                    {'startPeriod': 0, 'limit': 32.0}
                ]
            }
        }
        
        # Measure throughput
        num_messages = 1000
        start_time = time.time()
        
        for i in range(num_messages):
            modified = engine.manipulate_charging_profile(profile)
        
        end_time = time.time()
        elapsed = end_time - start_time
        throughput = num_messages / elapsed
        
        print(f"\nAttack Engine Throughput: {throughput:.2f} messages/second")
        print(f"Average processing time: {(elapsed/num_messages)*1000:.2f} ms/message")
        
        # Should process at least 100 messages per second
        assert throughput > 100, f"Throughput too low: {throughput:.2f} msg/s"
    
    def test_battery_model_throughput(self):
        """Measure battery simulation cycles per second"""
        model = BatteryDegradationModel()
        
        profile = {
            'voltage': 3.8,
            'current': 0.7,
            'soc_min': 20.0,
            'soc_max': 80.0
        }
        
        # Measure throughput
        num_cycles = 1000
        start_time = time.time()
        
        for i in range(num_cycles):
            result = model.simulate_charging_cycle(profile, duration_hours=1.0)
        
        end_time = time.time()
        elapsed = end_time - start_time
        throughput = num_cycles / elapsed
        
        print(f"\nBattery Model Throughput: {throughput:.2f} cycles/second")
        print(f"Average simulation time: {(elapsed/num_cycles)*1000:.2f} ms/cycle")
        
        # Should simulate at least 500 cycles per second
        assert throughput > 500, f"Throughput too low: {throughput:.2f} cycles/s"
    
    def test_metrics_logging_throughput(self):
        """Measure metrics logging throughput"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            metrics = MetricsCollector(temp_dir, "perf_test")
            
            # Measure logging throughput
            num_events = 1000
            start_time = time.time()
            
            for i in range(num_events):
                metrics.log_manipulation(
                    timestamp=datetime.now(),
                    original={'voltage': 3.7},
                    modified={'voltage': 4.0},
                    parameter_name='voltage',
                    original_value=3.7,
                    modified_value=4.0,
                    deviation_percent=8.1
                )
            
            end_time = time.time()
            elapsed = end_time - start_time
            throughput = num_events / elapsed
            
            print(f"\nMetrics Logging Throughput: {throughput:.2f} events/second")
            print(f"Average logging time: {(elapsed/num_events)*1000:.2f} ms/event")
            
            # Should log at least 1000 events per second
            assert throughput > 1000, f"Throughput too low: {throughput:.2f} events/s"
        
        finally:
            shutil.rmtree(temp_dir)


class TestResourceUsage:
    """Test resource usage during batch execution"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed")
    def test_memory_usage_during_simulation(self, temp_output_dir):
        """Test memory usage during extended simulation"""
        process = psutil.Process(os.getpid())
        
        # Get initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run simulation
        metrics = MetricsCollector(temp_output_dir, "memory_test")
        model = BatteryDegradationModel()
        engine = AttackEngine(AttackConfig(enabled=True))
        
        profile = {
            'voltage': 3.8,
            'current': 0.7,
            'soc_min': 20.0,
            'soc_max': 80.0
        }
        
        # Simulate 1000 cycles
        for i in range(1000):
            result = model.simulate_charging_cycle(profile, duration_hours=1.0)
            metrics.log_charging_cycle(
                cycle_num=i+1,
                profile=profile,
                duration=1.0,
                energy_kwh=50.0,
                soh_before=result.soh_before,
                soh_after=result.soh_after
            )
        
        # Get final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"\nInitial memory: {initial_memory:.2f} MB")
        print(f"Final memory: {final_memory:.2f} MB")
        print(f"Memory increase: {memory_increase:.2f} MB")
        
        # Memory increase should be reasonable (< 100 MB for 1000 cycles)
        assert memory_increase < 100, f"Memory usage too high: {memory_increase:.2f} MB"
    
    @pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed")
    def test_cpu_usage_during_simulation(self, temp_output_dir):
        """Test CPU usage during simulation"""
        process = psutil.Process(os.getpid())
        
        # Start CPU monitoring
        process.cpu_percent(interval=None)
        
        # Run simulation
        model = BatteryDegradationModel()
        
        profile = {
            'voltage': 3.8,
            'current': 0.7,
            'soc_min': 20.0,
            'soc_max': 80.0
        }
        
        start_time = time.time()
        
        # Simulate 500 cycles
        for i in range(500):
            result = model.simulate_charging_cycle(profile, duration_hours=1.0)
        
        elapsed = time.time() - start_time
        
        # Get CPU usage
        cpu_percent = process.cpu_percent(interval=None)
        
        print(f"\nCPU usage: {cpu_percent:.2f}%")
        print(f"Elapsed time: {elapsed:.2f} seconds")
        print(f"Cycles per second: {500/elapsed:.2f}")
        
        # CPU usage should be reasonable
        # Note: This is a rough check and may vary by system
        assert cpu_percent < 100, f"CPU usage too high: {cpu_percent:.2f}%"
    
    def test_disk_io_during_export(self, temp_output_dir):
        """Test disk I/O during CSV export"""
        metrics = MetricsCollector(temp_output_dir, "disk_test")
        
        # Add large dataset
        profile = {'voltage': 3.8, 'current': 0.5, 'soc_min': 20.0, 'soc_max': 80.0}
        
        for i in range(5000):
            metrics.log_charging_cycle(
                cycle_num=i+1,
                profile=profile,
                duration=2.0,
                energy_kwh=50.0,
                soh_before=100.0 - i*0.01,
                soh_after=100.0 - (i+1)*0.01
            )
        
        # Measure export time
        start_time = time.time()
        metrics.export_to_csv()
        elapsed = time.time() - start_time
        
        print(f"\nCSV export time for 5000 cycles: {elapsed:.2f} seconds")
        print(f"Export rate: {5000/elapsed:.2f} cycles/second")
        
        # Export should complete in reasonable time (< 5 seconds for 5000 cycles)
        assert elapsed < 5.0, f"Export too slow: {elapsed:.2f} seconds"


class TestScalability:
    """Test scalability with large cycle counts"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_scalability_1000_cycles(self, temp_output_dir):
        """Test performance with 1000 charging cycles"""
        metrics = MetricsCollector(temp_output_dir, "scale_1000")
        model = BatteryDegradationModel()
        
        profile = {
            'voltage': 3.8,
            'current': 0.7,
            'soc_min': 20.0,
            'soc_max': 80.0
        }
        
        start_time = time.time()
        
        for i in range(1000):
            result = model.simulate_charging_cycle(profile, duration_hours=1.0)
            metrics.log_charging_cycle(
                cycle_num=i+1,
                profile=profile,
                duration=1.0,
                energy_kwh=50.0,
                soh_before=result.soh_before,
                soh_after=result.soh_after
            )
        
        elapsed = time.time() - start_time
        
        print(f"\n1000 cycles completed in: {elapsed:.2f} seconds")
        print(f"Average time per cycle: {(elapsed/1000)*1000:.2f} ms")
        
        # Should complete in reasonable time (< 5 seconds)
        assert elapsed < 5.0, f"1000 cycles too slow: {elapsed:.2f} seconds"
    
    def test_scalability_10000_cycles(self, temp_output_dir):
        """Test performance with 10000 charging cycles"""
        metrics = MetricsCollector(temp_output_dir, "scale_10000")
        model = BatteryDegradationModel()
        
        profile = {
            'voltage': 3.8,
            'current': 0.7,
            'soc_min': 20.0,
            'soc_max': 80.0
        }
        
        start_time = time.time()
        
        for i in range(10000):
            result = model.simulate_charging_cycle(profile, duration_hours=1.0)
            
            # Only log every 10th cycle to reduce overhead
            if i % 10 == 0:
                metrics.log_charging_cycle(
                    cycle_num=i+1,
                    profile=profile,
                    duration=1.0,
                    energy_kwh=50.0,
                    soh_before=result.soh_before,
                    soh_after=result.soh_after
                )
        
        elapsed = time.time() - start_time
        
        print(f"\n10000 cycles completed in: {elapsed:.2f} seconds")
        print(f"Average time per cycle: {(elapsed/10000)*1000:.2f} ms")
        print(f"Throughput: {10000/elapsed:.2f} cycles/second")
        
        # Should complete in reasonable time (< 30 seconds)
        assert elapsed < 30.0, f"10000 cycles too slow: {elapsed:.2f} seconds"
    
    def test_linear_scaling(self, temp_output_dir):
        """Test that performance scales linearly with cycle count"""
        model = BatteryDegradationModel()
        
        profile = {
            'voltage': 3.8,
            'current': 0.7,
            'soc_min': 20.0,
            'soc_max': 80.0
        }
        
        # Test different cycle counts
        cycle_counts = [100, 500, 1000]
        times = []
        
        for count in cycle_counts:
            model.reset()
            start_time = time.time()
            
            for i in range(count):
                result = model.simulate_charging_cycle(profile, duration_hours=1.0)
            
            elapsed = time.time() - start_time
            times.append(elapsed)
            
            print(f"\n{count} cycles: {elapsed:.3f} seconds ({elapsed/count*1000:.3f} ms/cycle)")
        
        # Calculate scaling factor
        # Time should scale roughly linearly
        time_per_cycle_100 = times[0] / cycle_counts[0]
        time_per_cycle_1000 = times[2] / cycle_counts[2]
        
        scaling_factor = time_per_cycle_1000 / time_per_cycle_100
        
        print(f"\nScaling factor (1000 vs 100): {scaling_factor:.2f}x")
        
        # Scaling should be close to linear (< 2x difference)
        assert scaling_factor < 2.0, f"Non-linear scaling detected: {scaling_factor:.2f}x"


class TestConcurrentPerformance:
    """Test performance under concurrent operations"""
    
    def test_concurrent_attack_engine_operations(self):
        """Test attack engine performance with concurrent operations"""
        import threading
        
        config = AttackConfig(enabled=True)
        engine = AttackEngine(config)
        
        profile = {
            'chargingSchedule': {
                'chargingRateUnit': 'A',
                'chargingSchedulePeriod': [
                    {'startPeriod': 0, 'limit': 32.0}
                ]
            }
        }
        
        results = []
        
        def manipulate_profiles(count):
            start = time.time()
            for i in range(count):
                modified = engine.manipulate_charging_profile(profile)
            elapsed = time.time() - start
            results.append(elapsed)
        
        # Create multiple threads
        threads = []
        num_threads = 4
        operations_per_thread = 250
        
        start_time = time.time()
        
        for i in range(num_threads):
            thread = threading.Thread(target=manipulate_profiles, args=(operations_per_thread,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        total_elapsed = time.time() - start_time
        total_operations = num_threads * operations_per_thread
        throughput = total_operations / total_elapsed
        
        print(f"\nConcurrent operations: {total_operations}")
        print(f"Total time: {total_elapsed:.2f} seconds")
        print(f"Throughput: {throughput:.2f} operations/second")
        
        # Should maintain reasonable throughput
        assert throughput > 100, f"Concurrent throughput too low: {throughput:.2f} ops/s"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
