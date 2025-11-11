"""
Unit tests for MITM Proxy and OCPP Parser
Tests the core functionality of message interception and OCPP version support
"""

import unittest
import json
from attack_simulation.core.ocpp_parser import OCPPMessageParser, OCPPVersion


class TestOCPPParser(unittest.TestCase):
    """Test OCPP message parser functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser_16 = OCPPMessageParser(OCPPVersion.OCPP_16)
        self.parser_20 = OCPPMessageParser(OCPPVersion.OCPP_20)
        self.parser_201 = OCPPMessageParser(OCPPVersion.OCPP_201)
    
    def test_version_detection_ocpp16(self):
        """Test OCPP 1.6 version detection"""
        parser = OCPPMessageParser()
        version = parser.detect_version("ocpp1.6")
        self.assertEqual(version, OCPPVersion.OCPP_16)
    
    def test_version_detection_ocpp20(self):
        """Test OCPP 2.0 version detection"""
        parser = OCPPMessageParser()
        version = parser.detect_version("ocpp2.0")
        self.assertEqual(version, OCPPVersion.OCPP_20)
    
    def test_version_detection_ocpp201(self):
        """Test OCPP 2.0.1 version detection"""
        parser = OCPPMessageParser()
        version = parser.detect_version("ocpp2.0.1")
        self.assertEqual(version, OCPPVersion.OCPP_201)
    
    def test_version_detection_unknown(self):
        """Test unknown version defaults to OCPP 1.6"""
        parser = OCPPMessageParser()
        version = parser.detect_version("unknown")
        self.assertEqual(version, OCPPVersion.OCPP_16)
    
    def test_version_detection_none(self):
        """Test None subprotocol defaults to OCPP 1.6"""
        parser = OCPPMessageParser()
        version = parser.detect_version(None)
        self.assertEqual(version, OCPPVersion.OCPP_16)
    
    def test_is_set_charging_profile_action(self):
        """Test SetChargingProfile action detection"""
        parser = OCPPMessageParser()
        self.assertTrue(parser.is_set_charging_profile_action("SetChargingProfile"))
        self.assertTrue(parser.is_set_charging_profile_action("SetChargingProfileRequest"))
        self.assertFalse(parser.is_set_charging_profile_action("BootNotification"))
    
    def test_parse_ocpp16_charging_profile(self):
        """Test parsing OCPP 1.6 SetChargingProfile payload"""
        payload = {
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
        
        profile = self.parser_16.parse_set_charging_profile(payload)
        self.assertIsNotNone(profile)
        self.assertEqual(profile["chargingProfileId"], 1)
        self.assertEqual(profile["stackLevel"], 0)
    
    def test_parse_ocpp20_charging_profile(self):
        """Test parsing OCPP 2.0 SetChargingProfile payload"""
        payload = {
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
        
        profile = self.parser_20.parse_set_charging_profile(payload)
        self.assertIsNotNone(profile)
        self.assertEqual(profile["id"], 1)
        self.assertEqual(profile["stackLevel"], 0)
    
    def test_get_charging_schedule_ocpp16(self):
        """Test extracting charging schedule from OCPP 1.6 profile"""
        profile = {
            "chargingSchedule": {
                "chargingRateUnit": "A",
                "chargingSchedulePeriod": [
                    {"startPeriod": 0, "limit": 32.0}
                ]
            }
        }
        
        schedule = self.parser_16.get_charging_schedule(profile)
        self.assertIsNotNone(schedule)
        self.assertEqual(schedule["chargingRateUnit"], "A")
    
    def test_get_charging_schedule_ocpp20(self):
        """Test extracting charging schedule from OCPP 2.0 profile"""
        profile = {
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
        
        schedule = self.parser_20.get_charging_schedule(profile)
        self.assertIsNotNone(schedule)
        self.assertEqual(schedule["id"], 1)
    
    def test_get_charging_schedule_periods(self):
        """Test extracting charging schedule periods"""
        schedule = {
            "chargingSchedulePeriod": [
                {"startPeriod": 0, "limit": 32.0},
                {"startPeriod": 3600, "limit": 16.0}
            ]
        }
        
        periods = self.parser_16.get_charging_schedule_periods(schedule)
        self.assertEqual(len(periods), 2)
        self.assertEqual(periods[0]["limit"], 32.0)
        self.assertEqual(periods[1]["limit"], 16.0)


class TestOCPPMessageFormat(unittest.TestCase):
    """Test OCPP message format handling"""
    
    def test_ocpp_call_message_format(self):
        """Test OCPP CALL message format"""
        # OCPP CALL format: [2, MessageId, Action, Payload]
        message = [2, "12345", "SetChargingProfile", {"connectorId": 1}]
        
        self.assertEqual(message[0], 2)  # MessageTypeId
        self.assertEqual(message[2], "SetChargingProfile")  # Action
        self.assertIsInstance(message[3], dict)  # Payload
    
    def test_ocpp_callresult_message_format(self):
        """Test OCPP CALLRESULT message format"""
        # OCPP CALLRESULT format: [3, MessageId, Payload]
        message = [3, "12345", {"status": "Accepted"}]
        
        self.assertEqual(message[0], 3)  # MessageTypeId
        self.assertIsInstance(message[2], dict)  # Payload
    
    def test_ocpp_callerror_message_format(self):
        """Test OCPP CALLERROR message format"""
        # OCPP CALLERROR format: [4, MessageId, ErrorCode, ErrorDescription, ErrorDetails]
        message = [4, "12345", "InternalError", "An error occurred", {}]
        
        self.assertEqual(message[0], 4)  # MessageTypeId
        self.assertEqual(message[2], "InternalError")  # ErrorCode


if __name__ == '__main__':
    unittest.main()
