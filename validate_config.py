#!/usr/bin/env python3
"""
EmuOCPP Environment Validation Script

This script validates the complete EmuOCPP setup including:
- Python version compatibility
- Virtual environment status
- Package installation
- Configuration file validity
- Port availability
"""

import sys
import os
import socket
import subprocess
from pathlib import Path

# Color codes for terminal output (Windows compatible)
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print a formatted section header"""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")

def check_python_version():
    """Check if Python version meets minimum requirements"""
    print_header("1. Python Version Check")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print(f"Current Python version: {version_str}")
    
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python version {version_str} meets requirements (>= 3.8)")
        return True
    else:
        print_error(f"Python version {version_str} is too old. Requires Python 3.8 or higher")
        return False

def check_venv_status():
    """Check if running inside a virtual environment"""
    print_header("2. Virtual Environment Check")
    
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print_success("Running inside virtual environment")
        print(f"  Virtual environment path: {sys.prefix}")
        return True
    else:
        print_warning("NOT running inside virtual environment")
        print("  Recommendation: Activate venv with 'venv\\Scripts\\activate' (Windows)")
        return False

def check_venv_exists():
    """Check if venv directory exists"""
    venv_path = Path("venv")
    
    if venv_path.exists() and venv_path.is_dir():
        print_success("Virtual environment directory exists")
        
        # Check for activation scripts
        activate_script = venv_path / "Scripts" / "activate.bat"
        if activate_script.exists():
            print_success("Activation script found (Windows)")
        else:
            print_warning("Activation script not found")
        
        return True
    else:
        print_error("Virtual environment directory 'venv' not found")
        print("  Run: python -m venv venv")
        return False

def check_packages():
    """Check if required packages are installed"""
    print_header("3. Package Installation Check")
    
    required_packages = [
        'websockets',
        'yaml',
        'asyncio'
    ]
    
    all_installed = True
    
    for package in required_packages:
        # Special handling for yaml (PyYAML)
        import_name = 'yaml' if package == 'yaml' else package
        
        try:
            __import__(import_name)
            print_success(f"Package '{package}' is installed")
        except ImportError:
            print_error(f"Package '{package}' is NOT installed")
            all_installed = False
    
    if not all_installed:
        print("\n  Run: pip install -r requirements.txt")
    
    return all_installed

def check_requirements_file():
    """Check if requirements.txt exists"""
    req_file = Path("requirements.txt")
    
    if req_file.exists():
        print_success("requirements.txt file found")
        try:
            with open(req_file, 'r') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                print(f"  Found {len(lines)} package requirements")
        except Exception as e:
            print_warning(f"Could not read requirements.txt: {e}")
        return True
    else:
        print_error("requirements.txt file not found")
        return False

def check_config_files():
    """Validate configuration files"""
    print_header("4. Configuration File Validation")
    
    server_config_path = Path("charging/server_config.yaml")
    client_config_path = Path("charging/client_config.yaml")
    
    all_valid = True
    
    # Check server config
    if not server_config_path.exists():
        print_error(f"Server config not found: {server_config_path}")
        return False
    
    # Check client config
    if not client_config_path.exists():
        print_error(f"Client config not found: {client_config_path}")
        return False
    
    try:
        import yaml
        
        # Load server config
        with open(server_config_path, 'r') as f:
            server = yaml.safe_load(f)
        
        print_success("Server config loaded successfully")
        
        # Validate required server keys
        required_server_keys = ['server_host', 'server_port', 'ocpp_version', 'security_profile']
        for key in required_server_keys:
            if key not in server:
                print_error(f"  Missing required key in server config: {key}")
                all_valid = False
            else:
                print(f"  {key}: {server[key]}")
        
        # Load client config
        with open(client_config_path, 'r') as f:
            client = yaml.safe_load(f)
        
        print_success("Client config loaded successfully")
        
        # Validate required client keys
        required_client_keys = ['csms_url', 'ocpp_version', 'security_profile', 'identification']
        for key in required_client_keys:
            if key not in client:
                print_error(f"  Missing required key in client config: {key}")
                all_valid = False
            else:
                print(f"  {key}: {client[key]}")
        
        if all_valid:
            # Validate matching values
            print("\n" + "-" * 60)
            print("Configuration Consistency Check:")
            print("-" * 60)
            
            expected_url = f"ws://{server['server_host']}:{server['server_port']}/"
            url_match = client['csms_url'] == expected_url
            version_match = client['ocpp_version'] == server['ocpp_version']
            security_match = client['security_profile'] == server['security_profile']
            
            if url_match:
                print_success(f"URL matches: {client['csms_url']}")
            else:
                print_error(f"URL mismatch!")
                print(f"  Expected: {expected_url}")
                print(f"  Got: {client['csms_url']}")
                all_valid = False
            
            if version_match:
                print_success(f"OCPP version matches: {server['ocpp_version']}")
            else:
                print_error(f"OCPP version mismatch!")
                print(f"  Server: {server['ocpp_version']}")
                print(f"  Client: {client['ocpp_version']}")
                all_valid = False
            
            if security_match:
                print_success(f"Security profile matches: {server['security_profile']}")
            else:
                print_error(f"Security profile mismatch!")
                print(f"  Server: {server['security_profile']}")
                print(f"  Client: {client['security_profile']}")
                all_valid = False
        
        return all_valid
        
    except yaml.YAMLError as e:
        print_error(f"YAML parsing error: {e}")
        return False
    except Exception as e:
        print_error(f"Error validating config files: {e}")
        return False

def check_port_availability():
    """Check if the configured port is available"""
    print_header("5. Port Availability Check")
    
    try:
        import yaml
        
        # Load server config to get port
        with open("charging/server_config.yaml", 'r') as f:
            server = yaml.safe_load(f)
        
        host = server.get('server_host', '127.0.0.1')
        port = server.get('server_port', 9000)
        
        # Try to bind to the port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        
        result = sock.connect_ex((host, port))
        
        if result == 0:
            print_warning(f"Port {port} is currently IN USE")
            print(f"  A process is already listening on {host}:{port}")
            print(f"  This could be the OCPP server (which is fine)")
            print(f"  Or another application (which would cause conflicts)")
            sock.close()
            return True  # Not necessarily an error
        else:
            print_success(f"Port {port} is AVAILABLE")
            print(f"  Ready to start OCPP server on {host}:{port}")
            sock.close()
            return True
            
    except Exception as e:
        print_error(f"Error checking port availability: {e}")
        return False

def check_project_structure():
    """Check if key project files and directories exist"""
    print_header("6. Project Structure Check")
    
    required_items = [
        ("charging/", True),
        ("charging/server.py", False),
        ("charging/client.py", False),
        ("charging/server_config.yaml", False),
        ("charging/client_config.yaml", False),
        ("requirements.txt", False),
    ]
    
    all_exist = True
    
    for item, is_dir in required_items:
        path = Path(item)
        
        if is_dir:
            if path.exists() and path.is_dir():
                print_success(f"Directory exists: {item}")
            else:
                print_error(f"Directory missing: {item}")
                all_exist = False
        else:
            if path.exists() and path.is_file():
                print_success(f"File exists: {item}")
            else:
                print_error(f"File missing: {item}")
                all_exist = False
    
    return all_exist

def main():
    """Run all validation checks"""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}EmuOCPP Environment Validation{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")
    
    results = {
        "Python Version": check_python_version(),
        "Virtual Environment": check_venv_status() and check_venv_exists(),
        "Required Packages": check_requirements_file() and check_packages(),
        "Configuration Files": check_config_files(),
        "Port Availability": check_port_availability(),
        "Project Structure": check_project_structure(),
    }
    
    # Summary
    print_header("Validation Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    for check, result in results.items():
        if result:
            print_success(f"{check}: PASSED")
        else:
            print_error(f"{check}: FAILED")
    
    print(f"\n{'-' * 60}")
    print(f"Overall: {passed}/{total} checks passed")
    print(f"{'-' * 60}")
    
    if passed == total:
        print_success("\n✓ All validation checks PASSED!")
        print("  Your EmuOCPP environment is ready to use.")
        print("\nNext steps:")
        print("  1. Start server: python charging\\server.py")
        print("  2. Start client: python charging\\client.py (in separate terminal)")
        return 0
    else:
        print_error("\n✗ Some validation checks FAILED")
        print("  Please review the errors above and fix them before proceeding.")
        print("\nCommon fixes:")
        print("  - Activate venv: venv\\Scripts\\activate")
        print("  - Install packages: pip install -r requirements.txt")
        print("  - Check config files in charging/ directory")
        return 1

if __name__ == "__main__":
    sys.exit(main())
