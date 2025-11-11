#!/usr/bin/env python3
"""
Integration Test Script

Tests compatibility between attack simulator and EmuOCPP server/client configurations.
"""

import sys
import yaml
from pathlib import Path


def load_yaml(file_path):
    """Load YAML configuration file"""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"✗ Failed to load {file_path}: {e}")
        return None


def test_server_config():
    """Test server configuration compatibility"""
    print("\n=== Testing Server Configuration ===")
    
    server_config_path = Path("charging/server_config.yaml")
    if not server_config_path.exists():
        print(f"✗ Server config not found: {server_config_path}")
        return False
    
    config = load_yaml(server_config_path)
    if not config:
        return False
    
    # Check required fields
    required_fields = ['server_host', 'server_port', 'ocpp_version', 'security_profile']
    for field in required_fields:
        if field not in config:
            print(f"✗ Missing required field: {field}")
            return False
        print(f"✓ {field}: {config[field]}")
    
    # Validate OCPP version
    valid_versions = ['1.6', '2.0', '2.0.1', 1.6, 2.0, 2.01]
    if config['ocpp_version'] not in valid_versions:
        print(f"⚠ Warning: Unusual OCPP version: {config['ocpp_version']}")
    
    # Validate security profile
    if config['security_profile'] not in [0, 1, 2, 3]:
        print(f"⚠ Warning: Invalid security profile: {config['security_profile']}")
    
    print("✓ Server configuration is valid")
    return True


def test_client_config():
    """Test client configuration compatibility"""
    print("\n=== Testing Client Configuration ===")
    
    client_config_path = Path("charging/client_config.yaml")
    if not client_config_path.exists():
        print(f"✗ Client config not found: {client_config_path}")
        return False
    
    config = load_yaml(client_config_path)
    if not config:
        return False
    
    # Check required fields
    required_fields = ['csms_url', 'ocpp_version', 'security_profile']
    for field in required_fields:
        if field not in config:
            print(f"✗ Missing required field: {field}")
            return False
        print(f"✓ {field}: {config[field]}")
    
    # Check if client is configured to use proxy
    csms_url = config['csms_url']
    if ':9001' in csms_url:
        print("✓ Client is configured to connect to proxy (port 9001)")
    elif ':9000' in csms_url:
        print("⚠ Warning: Client is configured to connect directly to server (port 9000)")
        print("  For attack simulation, update csms_url to use port 9001 (proxy)")
    else:
        print(f"⚠ Warning: Unusual CSMS URL: {csms_url}")
    
    print("✓ Client configuration is valid")
    return True


def test_attack_config():
    """Test attack simulator configuration compatibility"""
    print("\n=== Testing Attack Simulator Configuration ===")
    
    attack_config_path = Path("attack_simulation/config/attack_config.yaml")
    if not attack_config_path.exists():
        print(f"✗ Attack config not found: {attack_config_path}")
        return False
    
    config = load_yaml(attack_config_path)
    if not config:
        return False
    
    # Check proxy settings
    if 'proxy' not in config:
        print("✗ Missing proxy configuration")
        return False
    
    proxy = config['proxy']
    required_fields = ['csms_host', 'csms_port', 'listen_port']
    for field in required_fields:
        if field not in proxy:
            print(f"✗ Missing proxy field: {field}")
            return False
        print(f"✓ proxy.{field}: {proxy[field]}")
    
    # Check if proxy settings match server
    server_config = load_yaml("charging/server_config.yaml")
    if server_config:
        if proxy['csms_host'] != server_config.get('server_host'):
            print(f"⚠ Warning: Proxy csms_host ({proxy['csms_host']}) != server_host ({server_config.get('server_host')})")
        if proxy['csms_port'] != server_config.get('server_port'):
            print(f"⚠ Warning: Proxy csms_port ({proxy['csms_port']}) != server_port ({server_config.get('server_port')})")
    
    print("✓ Attack simulator configuration is valid")
    return True


def test_configuration_consistency():
    """Test consistency across all configurations"""
    print("\n=== Testing Configuration Consistency ===")
    
    server_config = load_yaml("charging/server_config.yaml")
    client_config = load_yaml("charging/client_config.yaml")
    attack_config = load_yaml("attack_simulation/config/attack_config.yaml")
    
    if not all([server_config, client_config, attack_config]):
        print("✗ Cannot test consistency - missing configurations")
        return False
    
    # Check OCPP version consistency
    server_version = str(server_config.get('ocpp_version', ''))
    client_version = str(client_config.get('ocpp_version', ''))
    
    if server_version != client_version:
        print(f"⚠ Warning: OCPP version mismatch - Server: {server_version}, Client: {client_version}")
    else:
        print(f"✓ OCPP version consistent: {server_version}")
    
    # Check security profile consistency
    server_profile = server_config.get('security_profile', -1)
    client_profile = client_config.get('security_profile', -1)
    
    if server_profile != client_profile:
        print(f"⚠ Warning: Security profile mismatch - Server: {server_profile}, Client: {client_profile}")
    else:
        print(f"✓ Security profile consistent: {server_profile}")
    
    # Check SSL configuration
    ssl_enabled = attack_config.get('proxy', {}).get('ssl_enabled', False)
    if server_profile > 1 and not ssl_enabled:
        print(f"⚠ Warning: Security profile {server_profile} requires SSL, but proxy ssl_enabled is False")
    elif server_profile <= 1 and ssl_enabled:
        print(f"⚠ Warning: Security profile {server_profile} doesn't require SSL, but proxy ssl_enabled is True")
    else:
        print(f"✓ SSL configuration matches security profile")
    
    print("✓ Configuration consistency check complete")
    return True


def main():
    """Run all integration tests"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  EmuOCPP Integration Test                                    ║")
    print("║  Testing compatibility with attack simulator                 ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    results = []
    
    # Run tests
    results.append(("Server Config", test_server_config()))
    results.append(("Client Config", test_client_config()))
    results.append(("Attack Config", test_attack_config()))
    results.append(("Consistency", test_configuration_consistency()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All integration tests passed!")
        print("  You can now run the attack simulator with EmuOCPP")
        return 0
    else:
        print("\n⚠ Some tests failed or have warnings")
        print("  Review the output above and fix configuration issues")
        return 1


if __name__ == '__main__':
    sys.exit(main())
