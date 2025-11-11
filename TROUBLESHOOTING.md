# EmuOCPP Troubleshooting Guide

This guide provides solutions to common issues encountered during EmuOCPP setup and operation on Windows systems.

## Table of Contents

1. [Dependency Installation Errors](#dependency-installation-errors)
2. [Port Conflict Errors](#port-conflict-errors)
3. [Connection Errors](#connection-errors)
4. [Configuration File Errors](#configuration-file-errors)
5. [Virtual Environment Issues](#virtual-environment-issues)
6. [Python Version Issues](#python-version-issues)

---

## Dependency Installation Errors

### Error: pip install fails with "error: Microsoft Visual C++ 14.0 or greater is required"

**Symptom:**
```
error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools"
```

**Cause:** Missing C++ build tools required for compiling Python packages with native extensions.

**Solution:**

1. Download and install Microsoft C++ Build Tools:
   ```
   https://visualstudio.microsoft.com/visual-cpp-build-tools/
   ```

2. During installation, select "Desktop development with C++"

3. After installation, restart your terminal and retry:
   ```cmd
   pip install -r requirements.txt
   ```

### Error: "Could not find a version that satisfies the requirement"

**Symptom:**
```
ERROR: Could not find a version that satisfies the requirement <package_name>
```

**Cause:** Outdated pip version or network connectivity issues.

**Solution:**

1. Upgrade pip:
   ```cmd
   python -m pip install --upgrade pip
   ```

2. Retry installation:
   ```cmd
   pip install -r requirements.txt
   ```

3. If issue persists, check internet connection and try with verbose output:
   ```cmd
   pip install -r requirements.txt -v
   ```

---

## Port Conflict Errors

### Error: "Address already in use" or "OSError: [WinError 10048]"

**Symptom:**
```
OSError: [WinError 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted
```

**Cause:** Port 9000 is already in use by another process.

**Solution:**

**Option 1: Find and terminate the conflicting process**

1. Find the process using port 9000:
   ```cmd
   netstat -ano | findstr :9000
   ```

2. Note the PID (Process ID) from the last column

3. Terminate the process:
   ```cmd
   taskkill /PID <PID> /F
   ```
   Replace `<PID>` with the actual process ID

**Option 2: Change the server port**

1. Edit `EmuOCPP/charging/server_config.yaml`:
   ```yaml
   server_port: 9001
   ```

2. Edit `EmuOCPP/charging/client_config.yaml` to match:
   ```yaml
   csms_url: "ws://127.0.0.1:9001/"
   ```

3. Restart both server and client

---

## Connection Errors

### Error: "Connection refused" or "[WinError 10061]"

**Symptom:**
```
ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it
```

**Cause:** OCPP server is not running or client is connecting to wrong address.

**Solution:**

1. Verify server is running:
   - Check if server terminal shows "Server started" or similar message
   - Verify server is listening on correct port:
     ```cmd
     netstat -ano | findstr :9000
     ```

2. If server is not running, start it:
   ```cmd
   cd EmuOCPP
   venv\Scripts\activate
   python charging\server.py
   ```

3. Verify client configuration matches server:
   - Open `charging/client_config.yaml`
   - Ensure `csms_url` matches server address: `ws://127.0.0.1:9000/`

4. Check Windows Firewall (rare but possible):
   ```cmd
   netsh advfirewall firewall add rule name="EmuOCPP" dir=in action=allow protocol=TCP localport=9000
   ```

### Error: "WebSocket connection failed"

**Symptom:**
```
websockets.exceptions.InvalidStatusCode: server rejected WebSocket connection: HTTP 400
```

**Cause:** OCPP version mismatch or invalid WebSocket URL.

**Solution:**

1. Verify both configs use same OCPP version:
   - `server_config.yaml`: `ocpp_version: "2.0.1"`
   - `client_config.yaml`: `ocpp_version: "2.0.1"`

2. Ensure client URL ends with trailing slash:
   ```yaml
   csms_url: "ws://127.0.0.1:9000/"
   ```

3. Restart both server and client after configuration changes

---

## Configuration File Errors

### Error: "yaml.scanner.ScannerError" or "mapping values are not allowed here"

**Symptom:**
```
yaml.scanner.ScannerError: mapping values are not allowed here
  in "server_config.yaml", line 3, column 15
```

**Cause:** Invalid YAML syntax in configuration file.

**Solution:**

1. Open the configuration file mentioned in the error

2. Check line number indicated in error message

3. Common YAML syntax issues:
   - **Missing space after colon:**
     ```yaml
     # Wrong
     server_port:9000
     
     # Correct
     server_port: 9000
     ```

   - **Incorrect indentation:**
     ```yaml
     # Wrong (tabs or inconsistent spaces)
     server_host: 127.0.0.1
       server_port: 9000
     
     # Correct (consistent spaces)
     server_host: 127.0.0.1
     server_port: 9000
     ```

   - **Missing quotes for strings with special characters:**
     ```yaml
     # Wrong
     csms_url: ws://127.0.0.1:9000/
     
     # Correct
     csms_url: "ws://127.0.0.1:9000/"
     ```

4. Validate YAML syntax using the validation script:
   ```cmd
   python validate_config.py
   ```

### Error: "KeyError" when starting server or client

**Symptom:**
```
KeyError: 'server_port'
```

**Cause:** Missing required configuration key in YAML file.

**Solution:**

1. Ensure all required keys are present in `server_config.yaml`:
   ```yaml
   server_host: 127.0.0.1
   server_port: 9000
   ocpp_version: "2.0.1"
   security_profile: 0
   ```

2. Ensure all required keys are present in `client_config.yaml`:
   ```yaml
   csms_url: "ws://127.0.0.1:9000/"
   ocpp_version: "2.0.1"
   security_profile: 0
   identification: "CP-01"
   ```

3. Run validation script to check configuration:
   ```cmd
   python validate_config.py
   ```

---

## Virtual Environment Issues

### Error: "venv\Scripts\activate is not recognized"

**Symptom:**
```
'venv\Scripts\activate' is not recognized as an internal or external command
```

**Cause:** Virtual environment not created or incorrect path.

**Solution:**

1. Verify you're in the EmuOCPP directory:
   ```cmd
   cd EmuOCPP
   ```

2. Check if venv directory exists:
   ```cmd
   dir venv
   ```

3. If venv doesn't exist, create it:
   ```cmd
   python -m venv venv
   ```

4. Activate using correct Windows syntax:
   ```cmd
   venv\Scripts\activate
   ```

5. Verify activation by checking prompt shows `(venv)`

### Error: "Execution of scripts is disabled on this system"

**Symptom:**
```
venv\Scripts\activate.ps1 cannot be loaded because running scripts is disabled on this system
```

**Cause:** PowerShell execution policy restriction.

**Solution:**

**Option 1: Use Command Prompt instead of PowerShell**
```cmd
cmd
cd EmuOCPP
venv\Scripts\activate
```

**Option 2: Change PowerShell execution policy (requires admin)**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then retry activation:
```powershell
venv\Scripts\activate
```

---

## Python Version Issues

### Error: "Python was not found"

**Symptom:**
```
'python' is not recognized as an internal or external command
```

**Cause:** Python not installed or not in system PATH.

**Solution:**

1. Download and install Python 3.8 or higher:
   ```
   https://www.python.org/downloads/
   ```

2. During installation, check "Add Python to PATH"

3. Restart terminal and verify:
   ```cmd
   python --version
   ```

4. If still not found, try:
   ```cmd
   py --version
   ```
   Use `py` instead of `python` in all commands

### Error: "Python version too old"

**Symptom:**
```
ERROR: This package requires Python 3.8 or higher
```

**Cause:** Installed Python version is below 3.8.

**Solution:**

1. Check current version:
   ```cmd
   python --version
   ```

2. Install Python 3.8 or higher from:
   ```
   https://www.python.org/downloads/
   ```

3. If multiple Python versions installed, use specific version:
   ```cmd
   py -3.8 -m venv venv
   ```

---

## Additional Diagnostics

### Run the validation script

To check your environment setup:

```cmd
cd EmuOCPP
python validate_config.py
```

This will verify:
- Python version
- Virtual environment status
- Package installation
- Configuration file validity
- Port availability

### Check process status

To verify server and client are running:

```cmd
netstat -ano | findstr :9000
tasklist | findstr python
```

### View detailed error logs

Run server or client with Python's verbose mode:

```cmd
python -v charging\server.py
```

---

## Getting Help

If you encounter an error not covered in this guide:

1. Check the error message for specific file names and line numbers
2. Run the validation script: `python validate_config.py`
3. Review the configuration files for syntax errors
4. Ensure all previous setup steps completed successfully
5. Check the EmuOCPP repository issues page for similar problems

## Quick Reference Commands

```cmd
# Check Python version
python --version

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows CMD)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Check port usage
netstat -ano | findstr :9000

# Kill process by PID
taskkill /PID <PID> /F

# Validate configuration
python validate_config.py

# Start server
python charging\server.py

# Start client (in separate terminal)
python charging\client.py
```
