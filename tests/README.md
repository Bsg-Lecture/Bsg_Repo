# EmuOCPP Automated Tests

This directory contains automated tests for validating the EmuOCPP setup and functionality.

## Test Suites

### 1. Configuration Validation Tests (`test_config_validation.py`)
Tests that validate YAML configuration files for proper structure and consistency.

**What it tests:**
- YAML files exist and are parseable
- All required configuration keys are present
- Values are consistent between server and client configs
- OCPP version, security profile, and URL match correctly

**Requirements covered:** 3.4, 4.5

### 2. Basic Connectivity Tests (`test_connectivity.py`)
Tests that validate server-client connection establishment and message exchange.

**What it tests:**
- Server process starts successfully
- Client connects to server
- BootNotification message exchange
- Sustained connection stability

**Requirements covered:** 7.1, 7.2, 7.3

## Running the Tests

### Quick Start

Run all tests:
```bash
python run_tests.py all
```

Run only configuration tests:
```bash
python run_tests.py config
```

Run only connectivity tests:
```bash
python run_tests.py connectivity
```

### Individual Test Files

Run a specific test file:
```bash
python -m unittest tests.test_config_validation
python -m unittest tests.test_connectivity
```

Run a specific test case:
```bash
python -m unittest tests.test_config_validation.TestConfigValidation.test_ocpp_version_consistency
```

## Prerequisites

### For Configuration Tests
- Virtual environment activated
- PyYAML installed (`pip install -r requirements.txt`)
- Config files present in `charging/` directory

### For Connectivity Tests
**IMPORTANT:** Connectivity tests require additional setup:

1. **Stop any running server instances**
   - Port 9000 must be available
   - Check with: `netstat -ano | findstr :9000` (Windows)
   - Kill process if needed: `taskkill /PID <process_id> /F`

2. **Network interface requirement**
   - The server requires a valid network interface name
   - On Windows, common interfaces: `Ethernet`, `Wi-Fi`, `vEthernet`
   - The tests currently use default interface `ens33` (Linux-style)
   - You may need to modify the server startup to use a Windows interface

3. **Manual connectivity testing recommended**
   - Due to platform-specific network interface requirements
   - Start server manually: `python charging\server.py -iface Wi-Fi`
   - Start client manually: `python charging\client.py`
   - Verify connection in logs

## Test Results Interpretation

### Success
```
Ran X tests in Y.YYYs

OK
```
All tests passed successfully.

### Partial Failure
```
Ran X tests in Y.YYYs

FAILED (failures=N)
```
Some tests failed. Review the traceback for details.

### Common Issues

#### Port Already in Use
```
OSError: [Errno 10048] error while attempting to bind on address
```
**Solution:** Stop any running server instances before running connectivity tests.

#### Invalid Network Interface
```
Not a valid network interface
```
**Solution:** The server needs a valid network interface parameter. On Windows, you may need to:
- Modify server startup to use a Windows interface name
- Or run server manually with: `python charging\server.py -iface Wi-Fi`

#### Missing Dependencies
```
ModuleNotFoundError: No module named 'yaml'
```
**Solution:** Install dependencies: `pip install -r requirements.txt`

## Test Coverage

| Requirement | Test Coverage |
|-------------|---------------|
| 3.4 - Config validation | ✓ test_config_validation.py |
| 4.5 - Config consistency | ✓ test_config_validation.py |
| 7.1 - Server startup | ✓ test_connectivity.py |
| 7.2 - Client connection | ✓ test_connectivity.py |
| 7.3 - Message exchange | ✓ test_connectivity.py |

## Continuous Integration

For CI/CD pipelines, run configuration tests only:
```bash
python run_tests.py config
```

Connectivity tests require environment-specific setup and are better suited for manual integration testing.

## Troubleshooting

### Tests hang or timeout
- Check if server/client processes are stuck
- Verify port availability
- Ensure network connectivity

### Tests fail intermittently
- Network timing issues
- Increase timeout values in test code
- Check system resource availability

### All connectivity tests fail
- This is expected if prerequisites aren't met
- Configuration tests should still pass
- Follow the prerequisites section above

## Contributing

When adding new tests:
1. Follow the existing test structure
2. Use descriptive test names
3. Include docstrings explaining what is tested
4. Reference requirements in comments
5. Clean up resources in tearDown methods
