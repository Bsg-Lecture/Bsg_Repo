"""
OCPP data models and structures
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class ChargingSchedulePeriod:
    """Individual period in charging schedule"""
    start_period: int  # seconds from schedule start
    limit: float       # power/current limit
    number_phases: int = 3
    
    def to_dict(self):
        """Convert to dictionary for OCPP message"""
        return {
            'startPeriod': self.start_period,
            'limit': self.limit,
            'numberPhases': self.number_phases
        }


@dataclass
class ChargingProfile:
    """OCPP 2.0.1 ChargingProfile structure"""
    id: int
    stack_level: int
    charging_profile_purpose: str
    charging_profile_kind: str
    charging_schedule: List[ChargingSchedulePeriod]
    recurrency_kind: Optional[str] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary for OCPP message"""
        profile = {
            'id': self.id,
            'stackLevel': self.stack_level,
            'chargingProfilePurpose': self.charging_profile_purpose,
            'chargingProfileKind': self.charging_profile_kind,
            'chargingSchedule': [period.to_dict() for period in self.charging_schedule]
        }
        
        if self.recurrency_kind:
            profile['recurrencyKind'] = self.recurrency_kind
        if self.valid_from:
            profile['validFrom'] = self.valid_from
        if self.valid_to:
            profile['validTo'] = self.valid_to
            
        return profile
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create ChargingProfile from OCPP message dictionary"""
        schedule_data = data.get('chargingSchedule', [])
        schedule = [
            ChargingSchedulePeriod(
                start_period=period.get('startPeriod', 0),
                limit=period.get('limit', 0.0),
                number_phases=period.get('numberPhases', 3)
            )
            for period in schedule_data
        ]
        
        return cls(
            id=data.get('id', 0),
            stack_level=data.get('stackLevel', 0),
            charging_profile_purpose=data.get('chargingProfilePurpose', ''),
            charging_profile_kind=data.get('chargingProfileKind', ''),
            charging_schedule=schedule,
            recurrency_kind=data.get('recurrencyKind'),
            valid_from=data.get('validFrom'),
            valid_to=data.get('validTo')
        )


@dataclass
class ManipulationEvent:
    """Record of a single manipulation"""
    timestamp: datetime
    message_id: str
    parameter_name: str
    original_value: float
    modified_value: float
    deviation_percent: float
    
    def to_dict(self):
        """Convert to dictionary for logging"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'message_id': self.message_id,
            'parameter_name': self.parameter_name,
            'original_value': self.original_value,
            'modified_value': self.modified_value,
            'deviation_percent': self.deviation_percent
        }
