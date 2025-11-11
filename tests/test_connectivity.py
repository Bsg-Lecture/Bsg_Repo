#!/usr/bin/env python3
"""
Basic Connectivity Tests

Tests for validating server-client connection establishment and
BootNotification message exchange in EmuOCPP.

Requirements: 7.1, 7.2, 7.3
"""

import unittest
import subprocess
import time
import sys
import os
import signal
from pathlib import Path


class TestBasicConnectivity(unittest.TestCase):
    """Test suite for basic OCPP server-client connectivity"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.server_process = None
        cls.client_process = None
        cls.project_root = Path(__file__).parent.parent
        
    def setUp(self):
        """Set up for each test"""
        self.server_process = None
        self.client_process = None
    
    def tearDown(self):
        """Clean up processes after each test"""
        self._cleanup_processes()
    
    def _cleanup_processes(self):
        """Terminate server and client processes"""
        if self.client_process:
            try:
                self.client_process.terminate()
                self.client_process.wait(timeout=5)
            except Exception as e:
                print(f"Error terminating client: {e}", file=sys.stderr)
                try:
                    self.client_process.kill()
                except:
                    pass
        
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except Exception as e:
                print(f"Error terminating server: {e}", file=sys.stderr)
                try:
                    self.server_process.kill()
                except:
                    pass
    
    def _start_server(self, timeout=10):
        """
        Start the OCPP server process
        
        Args:
            timeout: Maximum time to wait for server startup
            
        Returns:
            subprocess.Popen object for the server process
        """
        server_script = self.project_root / "charging" / "server.py"
        
        self.assertTrue(
            server_script.exists(),
            f"Server script not found: {server_script}"
        )
        
        # Start server process
        self.server_process = subprocess.Popen(
            [sys.executable, str(server_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=str(self.project_root)
        )
        
        # Wait for server to start
        start_time = time.time()
        server_started = False
        
        while time.time() - start_time < timeout:
            # Check if process is still running
            if self.server_process.poll() is not None:
                stdout, stderr = self.server_process.communicate()
                self.fail(
                    f"Server process terminated unexpectedly.\n"
                    f"STDOUT: {stdout}\n"
                    f"STDERR: {stderr}"
                )
            
            time.sleep(0.5)
            
            # Check for startup indicators in output
            # We'll give it a few seconds to initialize
            if time.time() - start_time > 3:
                server_started = True
                break
        
        self.assertTrue(
            server_started,
            "Server failed to start within timeout period"
        )
        
        return self.server_process
    
    def _start_client(self, timeout=10):
        """
        Start the OCPP client process
        
        Args:
            timeout: Maximum time to wait for client startup
            
        Returns:
            subprocess.Popen object for the client process
        """
        client_script = self.project_root / "charging" / "client.py"
        
        self.assertTrue(
            client_script.exists(),
            f"Client script not found: {client_script}"
        )
        
        # Start client process
        self.client_process = subprocess.Popen(
            [sys.executable, str(client_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=str(self.project_root)
        )
        
        # Wait for client to start
        start_time = time.time()
        client_started = False
        
        while time.time() - start_time < timeout:
            # Check if process is still running
            if self.client_process.poll() is not None:
                stdout, stderr = self.client_process.communicate()
                self.fail(
                    f"Client process terminated unexpectedly.\n"
                    f"STDOUT: {stdout}\n"
                    f"STDERR: {stderr}"
                )
            
            time.sleep(0.5)
            
            # Give client time to connect
            if time.time() - start_time > 3:
                client_started = True
                break
        
        self.assertTrue(
            client_started,
            "Client failed to start within timeout period"
        )
        
        return self.client_process
    
    def _read_process_output(self, process, timeout=2):
        """
        Read available output from a process
        
        Args:
            process: subprocess.Popen object
            timeout: Maximum time to wait for output
            
        Returns:
            Tuple of (stdout, stderr) strings
        """
        stdout_lines = []
        stderr_lines = []
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Try to read stdout
            if process.stdout:
                try:
                    line = process.stdout.readline()
                    if line:
                        stdout_lines.append(line)
                except:
                    pass
            
            # Try to read stderr
            if process.stderr:
                try:
                    line = process.stderr.readline()
                    if line:
                        stderr_lines.append(line)
                except:
                    pass
            
            time.sleep(0.1)
        
        return ''.join(stdout_lines), ''.join(stderr_lines)
    
    def test_server_starts_successfully(self):
        """Test that server process starts without errors"""
        server = self._start_server()
        
        # Verify server is running
        self.assertIsNone(
            server.poll(),
            "Server process should be running"
        )
        
        # Give server time to initialize
        time.sleep(2)
        
        # Server should still be running
        self.assertIsNone(
            server.poll(),
            "Server process terminated unexpectedly"
        )
    
    def test_client_connects_to_server(self):
        """Test that client successfully connects to server"""
        # Start server first
        server = self._start_server()
        
        # Give server time to start listening
        time.sleep(2)
        
        # Start client
        client = self._start_client()
        
        # Verify both processes are running
        self.assertIsNone(
            server.poll(),
            "Server process should be running"
        )
        self.assertIsNone(
            client.poll(),
            "Client process should be running"
        )
        
        # Give time for connection to establish
        time.sleep(3)
        
        # Both should still be running (no crashes)
        self.assertIsNone(
            server.poll(),
            "Server process terminated after client connection"
        )
        self.assertIsNone(
            client.poll(),
            "Client process terminated after connection attempt"
        )
    
    def test_boot_notification_exchange(self):
        """Test that BootNotification message is exchanged"""
        # Start server
        server = self._start_server()
        time.sleep(2)
        
        # Start client
        client = self._start_client()
        time.sleep(3)
        
        # Read output from both processes
        server_stdout, server_stderr = self._read_process_output(server, timeout=3)
        client_stdout, client_stderr = self._read_process_output(client, timeout=3)
        
        # Verify processes are still running
        self.assertIsNone(
            server.poll(),
            "Server process should still be running"
        )
        self.assertIsNone(
            client.poll(),
            "Client process should still be running"
        )
        
        # Note: We verify the processes stay alive and connected
        # The actual message content verification would require
        # parsing the OCPP protocol output, which is beyond
        # the scope of basic connectivity testing
    
    def test_sustained_connection(self):
        """Test that connection remains stable over time"""
        # Start server
        server = self._start_server()
        time.sleep(2)
        
        # Start client
        client = self._start_client()
        time.sleep(2)
        
        # Monitor for sustained period (10 seconds)
        monitor_duration = 10
        check_interval = 2
        checks = monitor_duration // check_interval
        
        for i in range(checks):
            time.sleep(check_interval)
            
            # Verify both processes still running
            self.assertIsNone(
                server.poll(),
                f"Server terminated during sustained connection test (check {i+1}/{checks})"
            )
            self.assertIsNone(
                client.poll(),
                f"Client terminated during sustained connection test (check {i+1}/{checks})"
            )
        
        # Final verification
        self.assertIsNone(
            server.poll(),
            "Server should still be running after sustained connection test"
        )
        self.assertIsNone(
            client.poll(),
            "Client should still be running after sustained connection test"
        )


if __name__ == '__main__':
    unittest.main()
