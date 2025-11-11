#!/usr/bin/env python3
"""
Configuration Validation Tests

Tests for validating YAML configuration files for EmuOCPP server and client.
Verifies all required keys are present and values are consistent between configs.

Requirements: 3.4, 4.5
"""

import unittest
import yaml
from pathlib import Path


class TestConfigValidation(unittest.TestCase):
    """Test suite for configuration file validation"""
    
    @classmethod
    def setUpClass(cls):
        """Load configuration files once for all tests"""
        cls.server_config_path = Path("charging/server_config.yaml")
        cls.client_config_path = Path("charging/client_config.yaml")
        
        # Load server config
        with open(cls.server_config_path, 'r') as f:
            cls.server_config = yaml.safe_load(f)
        
        # Load client config
        with open(cls.client_config_path, 'r') as f:
            cls.client_config = yaml.safe_load(f)
    
    def test_server_config_file_exists(self):
        """Test that server_config.yaml file exists"""
        self.assertTrue(
            self.server_config_path.exists(),
            f"Server config file not found: {self.server_config_path}"
        )
    
    def test_client_config_file_exists(self):
        """Test that client_config.yaml file exists"""
        self.assertTrue(
            self.client_config_path.exists(),
            f"Client config file not found: {self.client_config_path}"
        )
    
    def test_server_config_valid_yaml(self):
        """Test that server config is valid YAML"""
        self.assertIsNotNone(self.server_config, "Server config failed to parse")
        self.assertIsInstance(self.server_config, dict, "Server config is not a dictionary")
    
    def test_client_config_valid_yaml(self):
        """Test that client config is valid YAML"""
        self.assertIsNotNone(self.client_config, "Client config failed to parse")
        self.assertIsInstance(self.client_config, dict, "Client config is not a dictionary")
    
    def test_server_required_keys_present(self):
        """Test that all required keys are present in server config"""
        required_keys = ['server_host', 'server_port', 'ocpp_version', 'security_profile']
        
        for key in required_keys:
            with self.subTest(key=key):
                self.assertIn(
                    key,
                    self.server_config,
                    f"Required key '{key}' missing from server config"
                )
    
    def test_client_required_keys_present(self):
        """Test that all required keys are present in client config"""
        required_keys = ['csms_url', 'ocpp_version', 'security_profile', 'identification']
        
        for key in required_keys:
            with self.subTest(key=key):
                self.assertIn(
                    key,
                    self.client_config,
                    f"Required key '{key}' missing from client config"
                )
    
    def test_ocpp_version_consistency(self):
        """Test that OCPP version matches between server and client"""
        server_version = self.server_config.get('ocpp_version')
        client_version = self.client_config.get('ocpp_version')
        
        self.assertEqual(
            server_version,
            client_version,
            f"OCPP version mismatch: server={server_version}, client={client_version}"
        )
    
    def test_security_profile_consistency(self):
        """Test that security profile matches between server and client"""
        server_security = self.server_config.get('security_profile')
        client_security = self.client_config.get('security_profile')
        
        self.assertEqual(
            server_security,
            client_security,
            f"Security profile mismatch: server={server_security}, client={client_security}"
        )
    
    def test_client_url_matches_server_config(self):
        """Test that client URL matches server host and port"""
        server_host = self.server_config.get('server_host')
        server_port = self.server_config.get('server_port')
        client_url = self.client_config.get('csms_url')
        
        expected_url = f"ws://{server_host}:{server_port}/"
        
        self.assertEqual(
            client_url,
            expected_url,
            f"Client URL mismatch: expected={expected_url}, got={client_url}"
        )
    
    def test_server_host_valid(self):
        """Test that server host is a valid value"""
        server_host = self.server_config.get('server_host')
        
        self.assertIsNotNone(server_host, "Server host is None")
        self.assertIsInstance(server_host, str, "Server host is not a string")
        self.assertTrue(len(server_host) > 0, "Server host is empty")
    
    def test_server_port_valid(self):
        """Test that server port is a valid port number"""
        server_port = self.server_config.get('server_port')
        
        self.assertIsNotNone(server_port, "Server port is None")
        self.assertIsInstance(server_port, int, "Server port is not an integer")
        self.assertGreater(server_port, 0, "Server port must be positive")
        self.assertLessEqual(server_port, 65535, "Server port must be <= 65535")
    
    def test_client_identification_valid(self):
        """Test that client identification is valid"""
        identification = self.client_config.get('identification')
        
        self.assertIsNotNone(identification, "Client identification is None")
        self.assertIsInstance(identification, str, "Client identification is not a string")
        self.assertTrue(len(identification) > 0, "Client identification is empty")


if __name__ == '__main__':
    unittest.main()
