# EmuOCPP Integration Guide

This guide explains how to integrate the Charging Profile Poisoning Attack Simulator with the existing EmuOCPP infrastructure.

## Overview

The attack simulator acts as a Man-in-the-Middle (MITM) proxy between the EmuOCPP server (CSMS) and client (Charge Point). It intercepts OCPP messages, manipulates charging profiles, and forwards them transparently.

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   CSMS      │◄───────►│    MITM     │◄───────►│  Charge     │
│  (Server)   │         │   Proxy     │         │   Point     │
│  Port 9000  │         │  Port 9001  │         │  (Client)   │
└─────────────┘         └─────────────┘         └─────────────┘
                              │
                              │ Intercept & Manipulate
                              ▼
                        Attack Engine
```

## Configuration Compatibility

### Server Configuration

The attack simulator is compatible with existing `charging/server_config.yaml` settings:

- **OCPP Version**: Supports OCPP 1.6, 2.0, and 2.0.1 (matches `ocpp_version` field)
- **Security Profiles**: Supports profiles 0, 1, 2, 3 (matches `security_profile` field)
- **Host/Port**: Proxy connects to `server_host:server_port` (default: 127.0.0.1:9000)

**Example server_config.yaml:**
```yaml
server_host: 127.0.0.1
server_port: 9000
ocpp_version: 2.0.1
security_profile: 0
```

**Corresponding attack_config.yaml:**
```yaml
proxy:
  csms_host: "127.0.0.1"  # Matches server_host
  csms_port: 9000         # Matches server_port
  listen_port: 9001       # Proxy listens here for client
  ssl_enabled: false      # false for security_profile 0
```

### Client Configuration

The client must be configured to connect to the **proxy** instead of directly to the server:

**Original client_config.yaml:**
```yaml
csms_url: ws://127.0.0.1:9000/
```

**Modified for attack simulation:**
```yaml
csms_url: ws://127.0.0.1:9001/  # Connect to proxy port
```

The proxy will forward all traffic to the actual CSMS at port 9000.

## Setup Instructions

### Step 1: Configure EmuOCPP Server

1. Edit `charging/server_config.yaml` with your desired settings
2. Note the `server_host`, `server_port`, and `ocpp_version`
3. Start the server:
   ```bash
   python charging/server.py
   ```

### Step 2: Configure Attack Simulator

1. Edit `attack_simulation/config/attack_config.yaml`
2. Update proxy settings to match server configuration:
   ```yaml
   proxy:
     csms_host: "127.0.0.1"  # Match server_host
     csms_port: 9000         # Match server_port
     listen_port: 9001       # Proxy port (different from server)
   ```

3. Configure attack parameters as desired

### Step 3: Start Attack Simulator

Start the attack simulator (which includes the MITM proxy):
```bash
python attack_simulator.py --config attack_simulation/config/attack_config.yaml
```

The proxy will:
- Connect to CSMS at 127.0.0.1:9000
- Listen for client connections at 127.0.0.1:9001

### Step 4: Configure and Start Client

1. Edit `charging/client_config.yaml`
2. Update CSMS URL to point to proxy:
   ```yaml
   csms_url: ws://127.0.0.1:9001/  # Proxy port, not server port
   ```

3. Start the client:
   ```bash
   python charging/client.py
   ```

The client will connect to the proxy, which forwards traffic to the server.

## Security Profile Support

### Profile 0 (Unsecured WebSocket)

```yaml
# server_config.yaml
security_profile: 0

# attack_config.yaml
proxy:
  ssl_enabled: false
```

### Profile 1 (Basic Authentication)

```yaml
# server_config.yaml
security_profile: 1

# attack_config.yaml
proxy:
  ssl_enabled: false
  # Basic auth is handled at application layer
```

### Profile 2 (TLS with Basic Authentication)

```yaml
# server_config.yaml
security_profile: 2

# attack_config.yaml
proxy:
  ssl_enabled: true
  cert_file: "./certs/server_cert.pem"
  key_file: "./certs/server_key.pem"
```

### Profile 3 (TLS with Client Certificates)

```yaml
# server_config.yaml
security_profile: 3

# attack_config.yaml
proxy:
  ssl_enabled: true
  cert_file: "./certs/server_cert.pem"
  key_file: "./certs/server_key.pem"
  ca_cert_file: "./certs/ca_cert.pem"
  verify_client_cert: true
```

## OCPP Version Support

The attack simulator automatically detects and handles all OCPP versions:

- **OCPP 1.6**: Supported (limited transaction support)
- **OCPP 2.0**: Fully supported
- **OCPP 2.0.1**: Fully supported (recommended)

Set `ocpp_version` in `server_config.yaml` to your desired version.

## Testing Integration

### Quick Integration Test

1. Start server:
   ```bash
   python charging/server.py
   ```

2. Start attack simulator in baseline mode (no manipulation):
   ```bash
   python attack_simulator.py --config attack_simulation/config/baseline_config.yaml
   ```

3. In another terminal, start client:
   ```bash
   python charging/client.py
   ```

4. Verify in logs:
   - Server shows connection from proxy (127.0.0.1:9001)
   - Proxy shows connections from both server and client
   - Client successfully communicates through proxy

### Verify Message Flow

Check that OCPP messages flow correctly:

1. **BootNotification**: Client → Proxy → Server → Proxy → Client
2. **Heartbeat**: Bidirectional through proxy
3. **SetChargingProfile**: Server → Proxy (manipulated) → Client

## Troubleshooting

### Client Cannot Connect

**Problem**: Client fails to connect to proxy

**Solution**:
- Verify proxy is running and listening on correct port
- Check `csms_url` in `client_config.yaml` points to proxy port (9001)
- Check firewall settings

### Proxy Cannot Connect to Server

**Problem**: Proxy cannot reach CSMS

**Solution**:
- Verify server is running on configured host/port
- Check `csms_host` and `csms_port` in `attack_config.yaml`
- Verify server is accepting connections

### SSL/TLS Errors

**Problem**: Certificate verification failures

**Solution**:
- Ensure certificate paths are correct in configuration
- Verify certificates are valid and not expired
- Check that security_profile matches ssl_enabled setting

### Message Parsing Errors

**Problem**: OCPP messages fail to parse

**Solution**:
- Verify OCPP version consistency across server, proxy, and client
- Check that message format matches OCPP specification
- Enable DEBUG logging to see raw messages

## Advanced Configuration

### Using Existing Certificates

If you have existing EmuOCPP certificates:

```yaml
proxy:
  ssl_enabled: true
  cert_file: "./emuocpp_ttp_cert.pem"
  key_file: "./emuocpp_ttp_key.pem"
```

### Custom Port Configuration

To use different ports:

```yaml
# server_config.yaml
server_port: 8000

# attack_config.yaml
proxy:
  csms_port: 8000      # Match server
  listen_port: 8001    # Proxy port

# client_config.yaml
csms_url: ws://127.0.0.1:8001/
```

### Multiple Clients

The proxy supports multiple simultaneous client connections:

```yaml
# attack_config.yaml
proxy:
  max_clients: 10  # Maximum concurrent clients
```

## Integration with Existing Scripts

### Using with run_baseline_simulation.py

The baseline simulation script is already integrated:

```bash
python run_baseline_simulation.py --cycles 1000
```

This automatically:
- Loads `baseline_config.yaml`
- Starts proxy in transparent mode
- Runs simulation without manipulation

### Using with run_comparison_analysis.py

The comparison script works with existing output:

```bash
python run_comparison_analysis.py \
  --baseline ./output/baseline/session_baseline_20241110_120000 \
  --attack ./output/attack/session_attack_20241110_130000
```

## Best Practices

1. **Always test with baseline first**: Verify integration works without attacks
2. **Use consistent OCPP versions**: Ensure server, proxy, and client use same version
3. **Monitor logs**: Enable INFO or DEBUG logging during initial setup
4. **Separate output directories**: Use different output dirs for baseline and attack runs
5. **Document configuration**: Keep notes on which configs were used for each experiment

## Example Workflow

Complete workflow for running an attack simulation:

```bash
# Terminal 1: Start EmuOCPP server
cd EmuOCPP
python charging/server.py

# Terminal 2: Start attack simulator
python attack_simulator.py --config attack_simulation/config/attack_config.yaml

# Terminal 3: Start EmuOCPP client (configured to connect to proxy)
python charging/client.py

# After simulation completes, analyze results
python run_comparison_analysis.py
```

## Support

For issues or questions:
- Check `TROUBLESHOOTING.md` for common problems
- Review logs in `./logs/` directory
- See `attack_simulation/README.md` for detailed documentation
- Visit: https://github.com/vfg27/EmuOCPP

## References

- EmuOCPP Documentation: `README.md`
- Attack Simulator Documentation: `attack_simulation/README.md`
- Baseline Comparison Guide: `BASELINE_COMPARISON_QUICKSTART.md`
- OCPP Specification: https://www.openchargealliance.org/
