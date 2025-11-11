"""
OCPP Protocol Version Parser
Handles parsing of OCPP 1.6, 2.0, and 2.0.1 messages
"""

import logging
from typing import Dict, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class OCPPVersion(Enum):
    """OCPP protocol versions"""
    OCPP_16 = "ocpp1.6"
    OCPP_20 = "ocpp2.0"
    OCPP_201 = "ocpp2.0.1"
    UNKNOWN = "unknown"


class OCPPMessageParser:
    """
    Parser for OCPP messages across different protocol versions
    """
    
    def __init__(self, version: OCPPVersion = OCPPVersion.OCPP_16):
        """
        Initialize parser with OCPP version
        
        Args:
            version: OCPP protocol version
        """
        self.version = version
        logger.info(f"OCPPMessageParser initialized for version: {version.value}")
    
    def detect_version(self, subprotocol: Optional[str]) -> OCPPVersion:
        """
        Detect OCPP version from WebSocket subprotocol
        
        Args:
            subprotocol: WebSocket subprotocol string
            
        Returns:
            Detected OCPP version
        """
        if not subprotocol:
            logger.warning("No subprotocol provided, defaulting to OCPP 1.6")
            return OCPPVersion.OCPP_16
        
        subprotocol_lower = subprotocol.lower()
        
        if "ocpp2.0.1" in subprotocol_lower:
            return OCPPVersion.OCPP_201
        elif "ocpp2.0" in subprotocol_lower:
            return OCPPVersion.OCPP_20
        elif "ocpp1.6" in subprotocol_lower:
            return OCPPVersion.OCPP_16
        else:
            logger.warning(f"Unknown subprotocol: {subprotocol}, defaulting to OCPP 1.6")
            return OCPPVersion.OCPP_16
    
    def parse_set_charging_profile(self, payload: Dict) -> Optional[Dict]:
        """
        Parse SetChargingProfile message payload based on OCPP version
        
        Args:
            payload: Message payload dictionary
            
        Returns:
            Parsed charging profile or None if not found
        """
        if self.version == OCPPVersion.OCPP_16:
            return self._parse_ocpp16_charging_profile(payload)
        elif self.version in [OCPPVersion.OCPP_20, OCPPVersion.OCPP_201]:
            return self._parse_ocpp20_charging_profile(payload)
        else:
            logger.error(f"Unsupported OCPP version: {self.version}")
            return None
    
    def _parse_ocpp16_charging_profile(self, payload: Dict) -> Optional[Dict]:
        """
        Parse OCPP 1.6 SetChargingProfile payload
        
        OCPP 1.6 format:
        {
            "connectorId": 1,
            "csChargingProfiles": {
                "chargingProfileId": 1,
                "stackLevel": 0,
                "chargingProfilePurpose": "TxProfile",
                "chargingProfileKind": "Absolute",
                "chargingSchedule": {
                    "chargingRateUnit": "A",
                    "chargingSchedulePeriod": [
                        {"startPeriod": 0, "limit": 32.0}
                    ]
                }
            }
        }
        """
        logger.debug("Parsing OCPP 1.6 SetChargingProfile")
        
        if 'csChargingProfiles' in payload:
            return payload['csChargingProfiles']
        
        logger.warning("No csChargingProfiles found in OCPP 1.6 payload")
        return None
    
    def _parse_ocpp20_charging_profile(self, payload: Dict) -> Optional[Dict]:
        """
        Parse OCPP 2.0/2.0.1 SetChargingProfile payload
        
        OCPP 2.0/2.0.1 format:
        {
            "evseId": 1,
            "chargingProfile": {
                "id": 1,
                "stackLevel": 0,
                "chargingProfilePurpose": "TxProfile",
                "chargingProfileKind": "Absolute",
                "chargingSchedule": [
                    {
                        "id": 1,
                        "chargingRateUnit": "A",
                        "chargingSchedulePeriod": [
                            {"startPeriod": 0, "limit": 32.0}
                        ]
                    }
                ]
            }
        }
        """
        logger.debug(f"Parsing OCPP {self.version.value} SetChargingProfile")
        
        if 'chargingProfile' in payload:
            return payload['chargingProfile']
        
        logger.warning(f"No chargingProfile found in OCPP {self.version.value} payload")
        return None
    
    def get_charging_schedule(self, profile: Dict) -> Optional[Dict]:
        """
        Extract charging schedule from profile based on OCPP version
        
        Args:
            profile: Charging profile dictionary
            
        Returns:
            Charging schedule or None
        """
        if self.version == OCPPVersion.OCPP_16:
            # OCPP 1.6: chargingSchedule is a single object
            return profile.get('chargingSchedule')
        elif self.version in [OCPPVersion.OCPP_20, OCPPVersion.OCPP_201]:
            # OCPP 2.0/2.0.1: chargingSchedule is an array
            schedules = profile.get('chargingSchedule', [])
            return schedules[0] if schedules else None
        
        return None
    
    def get_charging_schedule_periods(self, schedule: Dict) -> list:
        """
        Extract charging schedule periods from schedule
        
        Args:
            schedule: Charging schedule dictionary
            
        Returns:
            List of charging schedule periods
        """
        return schedule.get('chargingSchedulePeriod', [])
    
    def get_action_name(self, version: OCPPVersion) -> str:
        """
        Get the SetChargingProfile action name for the given version
        
        Args:
            version: OCPP version
            
        Returns:
            Action name string
        """
        # Action name is the same across versions
        return "SetChargingProfile"
    
    def is_set_charging_profile_action(self, action: str) -> bool:
        """
        Check if action is SetChargingProfile for any OCPP version
        
        Args:
            action: Action name from OCPP message
            
        Returns:
            True if this is a SetChargingProfile action
        """
        return action in [
            "SetChargingProfile",
            "SetChargingProfileRequest"
        ]
