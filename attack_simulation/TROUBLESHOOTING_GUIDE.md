# Attack Simulator Troubleshooting Guide

Comprehensive troubleshooting guide for common issues with the Charging Profile Poisoning Attack Simulator.

## Table of Contents

1. [Connection Issues](#connection-issues)
2. [Configuration Issues](#configuration-issues)
3. [Simulation Issues](#simulation-issues)
4. [Performance Issues](#performance-issues)
5. [Output and Visualization Issues](#output-and-visualization-issues)
6. [Integration Issues](#integration-issues)
7. [Debugging Tips](#debugging-tips)

## Connection Issues

### Issue: Connection Refused to CSMS

**Symptom**:
```
ERROR - Connection refused to 127.0.0.1:9000
ConnectionRefusedError: [Errno 111] Connection refused
```

**Possible Causes**:
1. EmuOCPP server is not running
2. Server is running on different host/port
3. Firewall blocking connection

**Solutions**:

1. **Verify server is running**:
   ```bash
   # Check if server process is running
   ps aux | grep server.py
   
   # Start server if not running
   python charging/server.py
   ```

2. **Check server configuration**:
   ```bash
   cat charging/server_config.yaml | grep -E "server_host|server_port"
   ```
   
   Ensure `attack_config.yaml` proxy settings match:
   ```yaml
   proxy:
     csms_host: "127.0.0.1"  # Must match server_host
     csms_port: 9000         # Must match server_port
   ```

3. **Check firewall**:
   ```bash
   # Windows
   netsh advfirewall firewall show rule name=all | findstr 9000
   
   # Linux
   sudo iptables -L | grep 9000
   ```

4. **Test connection manually**:
   ```bash
   # Test if port is open
   telnet 127.0.0.1 9000
   # Or use netcat
   nc -zv 127.0.0.1 9000
   ```

### Issue: Client Cannot Connect to Proxy

**Symptom**:
```
ERROR - Client connection failed
WebSocketException: Connection to ws://127.0.0.1:9001/ failed
```

**Possible Causes**:
1. Attack simulator/proxy not running
2. Client configured with wrong URL
3. Proxy port already in use

**Solutions**:

1. **Verify proxy is running**:
   ```bash
   # Check attack simulator logs
   tail -f logs/attack_simulation.log
   
   # Should see: "Proxy listening on 127.0.0.1:9001"
   ```

2. **Check client configuration**:
   ```bash
   cat charging/client_config.yaml | grep csms_url
   ```
   
   Should be:
   ```yaml
   csms_url: ws://127.0.0.1:9001/  # Proxy port, not server port
   ```

3. **Check if port is in use**:
   ```bash
   # Windows
   netstat -ano | findstr :9001
   
   # Linux
   lsof -i :9001
   ```
   
   If port is in use, either:
   - Stop the other process
   - Change proxy listen_port in config

4. **Run integration test**:
   ```bash
   python test_integration.py
   ```

### Issue: SSL/TLS Connection Errors

**Symptom**:
```
ERROR - SSL handshake failed
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Possible Causes**:
1. Certificate files not found
2. Certificate expired or invalid
3. Security profile mismatch

**Solutions**:

1. **Verify certificate files exist**:
   ```bash
   ls -l emuocpp_ttp_cert.pem emuocpp_ttp_key.pem
   ```

2. **Check certificate validity**:
   ```bash
   openssl x509 -in emuocpp_ttp_cert.pem -text -noout | grep -E "Not Before|Not After"
   ```

3. **Verify security profile consistency**:
   ```bash
   # Check server
   grep security_profile charging/server_config.yaml
   
   # Check client
   grep security_profile charging/client_config.yaml
   
   # Check proxy SSL setting
   grep ssl_enabled attack_simulation/config/attack_config.yaml
   ```
   
   For security_profile 0 or 1: `ssl_enabled: false`
   For security_profile 2 or 3: `ssl_enabled: true`

4. **Regenerate certificates if needed**:
   ```bash
   # Use EmuOCPP certificate generation script
   python scripts/generate_certificates.py
   ```

## Configuration Issues

### Issue: Configuration File Not Found

**Symptom**:
```
ERROR - Configuration file not found: attack_config.yaml
FileNotFoundError: [Errno 2] No such file or directory
```

**Solutions**:

1. **Use full path**:
   ```bash
   python attack_simulator.py --config attack_simulation/config/attack_config.yaml
   ```

2. **Verify file exists**:
   ```bash
   ls -l attack_simulation/config/attack_config.yaml
   ```

3. **Check current directory**:
   ```bash
   pwd
   # Should be in EmuOCPP root directory
   ```

### Issue: Invalid Configuration Format

**Symptom**:
```
ERROR - Failed to parse configuration
yaml.scanner.ScannerError: mapping values are not allowed here
```

**Solutions**:

1. **Validate YAML syntax**:
   ```bash
   python -c "import yaml; yaml.safe_load(open('attack_simulation/config/attack_config.yaml'))"
   ```

2. **Check indentation** (YAML is indentation-sensitive):
   ```yaml
   # Correct
   attack_config:
     enabled: true
     strategy: "aggressive"
   
   # Incorrect (wrong indentation)
   attack_config:
   enabled: true
     strategy: "aggressive"
   ```

3. **Check for tabs** (use spaces only):
   ```bash
   # Find tabs in config file
   grep -P '\t' attack_simulation/config/attack_config.yaml
   ```

### Issue: Invalid Parameter Values

**Symptom**:
```
ERROR - Invalid cycle count: -100 (must be positive)
ValueError: deviation_percent must be between 0 and 100
```

**Solutions**:

1. **Validate cycle count**:
   ```bash
   python attack_simulator.py --config attack_config.yaml --cycles 1000
   # Must be positive integer
   ```

2. **Check deviation percentages**:
   ```yaml
   manipulations:
     voltage:
       deviation_percent: 15  # Must be 0-100
   ```

3. **Run dry-run to validate**:
   ```bash
   python attack_simulator.py --config attack_config.yaml --dry-run
   ```

## Simulation Issues

### Issue: No Manipulation Detected

**Symptom**:
- Simulation runs but no manipulation events logged
- Results identical to baseline

**Possible Causes**:
1. Attack disabled in configuration
2. No SetChargingProfile messages intercepted
3. Manipulation filters too restrictive

**Solutions**:

1. **Verify attack is enabled**:
   ```yaml
   attack_config:
     enabled: true  # Must be true
   ```

2. **Check manipulation settings**:
   ```yaml
   manipulations:
     voltage:
       enabled: true  # At least one must be enabled
     current:
       enabled: true
   ```

3. **Enable debug logging**:
   ```bash
   python attack_simulator.py --config attack_config.yaml --log-level DEBUG
   ```
   
   Look for:
   ```
   DEBUG - Intercepted message: SetChargingProfile
   DEBUG - Applying voltage manipulation: 4.2V -> 4.83V
   ```

4. **Verify OCPP messages are being sent**:
   - Check if server is sending SetChargingProfile messages
   - May need to trigger charging session from client

### Issue: Simulation Hangs or Freezes

**Symptom**:
- Simulation starts but never completes
- No progress updates
- CPU usage at 100%

**Possible Causes**:
1. Infinite loop in attack logic
2. Deadlock in async operations
3. Resource exhaustion

**Solutions**:

1. **Check for infinite loops**:
   ```bash
   # Monitor CPU usage
   top -p $(pgrep -f attack_simulator)
   ```

2. **Enable debug logging**:
   ```bash
   python attack_simulator.py --config attack_config.yaml --log-level DEBUG
   ```
   
   Check last log entry to see where it's stuck

3. **Reduce cycle count for testing**:
   ```bash
   python attack_simulator.py --config attack_config.yaml --cycles 10
   ```

4. **Check for resource limits**:
   ```bash
   # Check memory usage
   free -h
   
   # Check disk space
   df -h
   ```

5. **Kill and restart**:
   ```bash
   # Find process
   ps aux | grep attack_simulator
   
   # Kill process
   kill -9 <PID>
   ```

### Issue: Incorrect Degradation Results

**Symptom**:
- SoH values unrealistic (negative, >100%, etc.)
- Degradation too fast or too slow
- Results don't match expected behavior

**Possible Causes**:
1. Incorrect battery model parameters
2. Extreme manipulation values
3. Bug in degradation calculation

**Solutions**:

1. **Verify battery model parameters**:
   ```yaml
   battery_model:
     initial_capacity_ah: 75.0  # Reasonable value
     degradation_params:
       base_degradation_per_cycle: 0.001  # 0.1% per 100 cycles
   ```

2. **Check manipulation values**:
   ```yaml
   manipulations:
     voltage:
       deviation_percent: 15  # Not 150!
   ```

3. **Run baseline first**:
   ```bash
   python run_baseline_simulation.py --cycles 100
   ```
   
   Verify baseline degradation is reasonable (~1% for 100 cycles)

4. **Compare with literature values**:
   - Typical EV battery: 80% SoH after 1000-2000 cycles
   - Accelerated degradation: 2-5x faster

## Performance Issues

### Issue: Simulation Too Slow

**Symptom**:
- Takes hours to complete
- Progress very slow

**Solutions**:

1. **Reduce cycle count for testing**:
   ```bash
   python attack_simulator.py --config attack_config.yaml --cycles 100
   ```

2. **Disable plot generation**:
   ```bash
   python attack_simulator.py --config attack_config.yaml --no-plots
   ```

3. **Reduce logging verbosity**:
   ```bash
   python attack_simulator.py --config attack_config.yaml --log-level WARNING
   ```

4. **Disable CSV export during simulation**:
   ```yaml
   metrics:
     export_csv: false  # Export at end only
   ```

5. **Use batch mode with parallel execution**:
   ```yaml
   execution:
     parallel: true
     max_workers: 4
   ```

### Issue: High Memory Usage

**Symptom**:
- System runs out of memory
- Simulation crashes with MemoryError

**Solutions**:

1. **Reduce cycle count**:
   ```bash
   python attack_simulator.py --config attack_config.yaml --cycles 500
   ```

2. **Disable in-memory data accumulation**:
   ```yaml
   metrics:
     stream_to_disk: true  # Write directly to disk
   ```

3. **Monitor memory usage**:
   ```bash
   # While simulation runs
   watch -n 1 'ps aux | grep attack_simulator'
   ```

## Output and Visualization Issues

### Issue: Plots Not Generated

**Symptom**:
- Simulation completes but no plots in output directory
- Plot generation errors in logs

**Possible Causes**:
1. Matplotlib not installed or misconfigured
2. No display available (headless system)
3. Insufficient data for plotting

**Solutions**:

1. **Install matplotlib**:
   ```bash
   pip install matplotlib pillow
   ```

2. **Set matplotlib backend for headless systems**:
   ```python
   # Add to config or environment
   import matplotlib
   matplotlib.use('Agg')  # Non-interactive backend
   ```

3. **Check plot generation setting**:
   ```yaml
   metrics:
     generate_plots: true
   ```

4. **Verify sufficient data**:
   - Need at least 10 cycles for meaningful plots
   - Check if CSV files have data

5. **Generate plots manually**:
   ```bash
   python attack_simulation/examples/demo_visualization.py
   ```

### Issue: CSV Files Empty or Corrupted

**Symptom**:
- CSV files exist but have no data
- CSV parsing errors

**Solutions**:

1. **Check file permissions**:
   ```bash
   ls -l output/attack/session_*/
   ```

2. **Verify data was collected**:
   ```bash
   wc -l output/attack/session_*/manipulations.csv
   # Should show line count > 1
   ```

3. **Check disk space**:
   ```bash
   df -h
   ```

4. **Re-run with debug logging**:
   ```bash
   python attack_simulator.py --config attack_config.yaml --log-level DEBUG
   ```

## Integration Issues

### Issue: EmuOCPP Version Mismatch

**Symptom**:
```
ERROR - OCPP version mismatch
ValueError: Unsupported OCPP version: 1.5
```

**Solutions**:

1. **Check version consistency**:
   ```bash
   python test_integration.py
   ```

2. **Update configurations to match**:
   ```yaml
   # server_config.yaml
   ocpp_version: 2.0.1
   
   # client_config.yaml
   ocpp_version: 2.0.1
   ```

3. **Supported versions**: 1.6, 2.0, 2.0.1

### Issue: Message Format Errors

**Symptom**:
```
ERROR - Failed to parse OCPP message
JSONDecodeError: Expecting value: line 1 column 1
```

**Solutions**:

1. **Enable message logging**:
   ```bash
   python attack_simulator.py --config attack_config.yaml --log-level DEBUG
   ```

2. **Check OCPP message format**:
   - Should be valid JSON
   - Should follow OCPP specification

3. **Verify protocol version**:
   - OCPP 1.6 uses different format than 2.0/2.0.1

## Debugging Tips

### Enable Debug Logging

```bash
python attack_simulator.py --config attack_config.yaml --log-level DEBUG --log-file debug.log
```

### Check Log Files

```bash
# View recent logs
tail -f logs/attack_simulation.log

# Search for errors
grep ERROR logs/attack_simulation.log

# Search for specific events
grep "manipulation" logs/attack_simulation.log
```

### Use Dry Run Mode

```bash
python attack_simulator.py --config attack_config.yaml --dry-run
```

### Run Integration Test

```bash
python test_integration.py
```

### Test Individual Components

```bash
# Test attack engine
python attack_simulation/examples/demo_attack_engine.py

# Test battery model
python attack_simulation/examples/demo_battery_model.py

# Test metrics collector
python attack_simulation/examples/demo_metrics_collector.py
```

### Monitor Network Traffic

```bash
# Use tcpdump to capture WebSocket traffic
sudo tcpdump -i lo -A 'port 9000 or port 9001'

# Or use Wireshark with OCPP dissector
wireshark -i lo -f "port 9000 or port 9001"
```

### Python Debugger

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use built-in breakpoint() (Python 3.7+)
breakpoint()
```

### Check Python Environment

```bash
# Verify Python version
python --version  # Should be 3.8+

# Check installed packages
pip list | grep -E "websockets|yaml|pandas|matplotlib"

# Verify imports work
python -c "from attack_simulation.core import AttackEngine; print('OK')"
```

## Getting Help

If you're still experiencing issues:

1. **Check documentation**:
   - `attack_simulation/README.md`
   - `attack_simulation/USAGE_GUIDE.md`
   - `attack_simulation/EMUOCPP_INTEGRATION.md`

2. **Run diagnostics**:
   ```bash
   python test_integration.py
   python attack_simulator.py --config attack_config.yaml --dry-run
   ```

3. **Collect debug information**:
   ```bash
   # Run with debug logging
   python attack_simulator.py --config attack_config.yaml --log-level DEBUG --log-file debug.log
   
   # Include in bug report:
   # - debug.log
   # - Configuration files used
   # - Python version and OS
   # - Error messages
   ```

4. **Visit project repository**:
   - https://github.com/vfg27/EmuOCPP
   - Check existing issues
   - Open new issue with debug information

## Common Error Messages

| Error Message | Likely Cause | Solution |
|--------------|--------------|----------|
| `Connection refused` | Server not running | Start EmuOCPP server |
| `FileNotFoundError` | Wrong path | Use full path to config |
| `ModuleNotFoundError` | Missing dependency | `pip install -r requirements.txt` |
| `yaml.scanner.ScannerError` | Invalid YAML | Check indentation and syntax |
| `ValueError: Invalid cycle count` | Negative or zero cycles | Use positive integer |
| `SSL handshake failed` | Certificate issue | Check cert files and security profile |
| `WebSocketException` | Connection failed | Check proxy is running |
| `MemoryError` | Out of memory | Reduce cycle count |

## Prevention Tips

1. **Always run integration test first**:
   ```bash
   python test_integration.py
   ```

2. **Start with small cycle counts**:
   ```bash
   python attack_simulator.py --config attack_config.yaml --cycles 10
   ```

3. **Use dry-run mode**:
   ```bash
   python attack_simulator.py --config attack_config.yaml --dry-run
   ```

4. **Keep configurations in version control**:
   ```bash
   git add attack_simulation/config/*.yaml
   git commit -m "Update attack configuration"
   ```

5. **Document your experiments**:
   - Keep notes on configurations used
   - Save successful configurations
   - Document any issues encountered
