"""
Anomaly Detection Framework for charging profile manipulation detection
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import statistics
import yaml

logger = logging.getLogger(__name__)


class DetectionMethod(Enum):
    """Detection method types"""
    STATISTICAL = "statistical"  # Statistical threshold-based detection
    RANGE_BASED = "range_based"  # Parameter range violation detection
    PATTERN_BASED = "pattern_based"  # Pattern anomaly detection


@dataclass
class DetectionConfig:
    """Configuration for anomaly detection"""
    enabled: bool = True
    method: DetectionMethod = DetectionMethod.STATISTICAL
    
    # Statistical detection thresholds
    voltage_threshold_percent: float = 10.0  # % deviation from baseline
    current_threshold_percent: float = 15.0  # % deviation from baseline
    power_threshold_percent: float = 12.0    # % deviation from baseline
    
    # Range-based detection (absolute limits)
    voltage_min: float = 3.0   # Minimum safe voltage (V)
    voltage_max: float = 4.2   # Maximum safe voltage (V)
    current_min: float = 0.0   # Minimum current (A)
    current_max: float = 60.0  # Maximum safe current (A)
    
    # Pattern-based detection
    enable_curve_analysis: bool = True
    curve_smoothness_threshold: float = 0.3  # Threshold for curve irregularity
    
    # Confidence scoring
    confidence_weight_statistical: float = 0.4
    confidence_weight_range: float = 0.3
    confidence_weight_pattern: float = 0.3
    
    # Baseline parameters (learned from normal operation)
    baseline_voltage_mean: float = 3.7
    baseline_voltage_std: float = 0.2
    baseline_current_mean: float = 30.0
    baseline_current_std: float = 5.0
    baseline_power_mean: float = 7.0
    baseline_power_std: float = 1.5
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'DetectionConfig':
        """
        Load detection configuration from YAML file
        
        Args:
            yaml_path: Path to YAML configuration file
            
        Returns:
            DetectionConfig instance
        """
        with open(yaml_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        detection_cfg = config_data.get('detection_config', {})
        thresholds = detection_cfg.get('thresholds', {})
        ranges = detection_cfg.get('ranges', {})
        pattern = detection_cfg.get('pattern', {})
        baseline = detection_cfg.get('baseline', {})
        
        # Parse detection method
        method_str = detection_cfg.get('method', 'statistical')
        try:
            method = DetectionMethod(method_str)
        except ValueError:
            logger.warning(f"Invalid detection method '{method_str}', defaulting to STATISTICAL")
            method = DetectionMethod.STATISTICAL
        
        return cls(
            enabled=detection_cfg.get('enabled', True),
            method=method,
            voltage_threshold_percent=thresholds.get('voltage_percent', 10.0),
            current_threshold_percent=thresholds.get('current_percent', 15.0),
            power_threshold_percent=thresholds.get('power_percent', 12.0),
            voltage_min=ranges.get('voltage_min', 3.0),
            voltage_max=ranges.get('voltage_max', 4.2),
            current_min=ranges.get('current_min', 0.0),
            current_max=ranges.get('current_max', 60.0),
            enable_curve_analysis=pattern.get('enable_curve_analysis', True),
            curve_smoothness_threshold=pattern.get('curve_smoothness_threshold', 0.3),
            baseline_voltage_mean=baseline.get('voltage_mean', 3.7),
            baseline_voltage_std=baseline.get('voltage_std', 0.2),
            baseline_current_mean=baseline.get('current_mean', 30.0),
            baseline_current_std=baseline.get('current_std', 5.0),
            baseline_power_mean=baseline.get('power_mean', 7.0),
            baseline_power_std=baseline.get('power_std', 1.5)
        )


@dataclass
class DetectionEvent:
    """Record of a single detection event"""
    timestamp: datetime
    message_id: str
    parameter_name: str
    observed_value: float
    expected_value: float
    deviation_percent: float
    confidence_score: float
    is_anomaly: bool
    detection_method: str
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'message_id': self.message_id,
            'parameter_name': self.parameter_name,
            'observed_value': self.observed_value,
            'expected_value': self.expected_value,
            'deviation_percent': self.deviation_percent,
            'confidence_score': self.confidence_score,
            'is_anomaly': self.is_anomaly,
            'detection_method': self.detection_method,
            'details': self.details
        }


@dataclass
class DetectionResult:
    """Result of anomaly detection on a charging profile"""
    is_anomalous: bool
    confidence_score: float
    detected_anomalies: List[DetectionEvent]
    total_parameters_checked: int
    anomalous_parameters: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'is_anomalous': self.is_anomalous,
            'confidence_score': self.confidence_score,
            'detected_anomalies': [event.to_dict() for event in self.detected_anomalies],
            'total_parameters_checked': self.total_parameters_checked,
            'anomalous_parameters': self.anomalous_parameters
        }


@dataclass
class DetectionMetrics:
    """Metrics for detection performance evaluation"""
    true_positives: int = 0
    false_positives: int = 0
    true_negatives: int = 0
    false_negatives: int = 0
    total_detections: int = 0
    
    def add_detection(self, predicted_anomaly: bool, actual_anomaly: bool) -> None:
        """
        Record a detection result
        
        Args:
            predicted_anomaly: Whether detector predicted an anomaly
            actual_anomaly: Whether there was actually an anomaly
        """
        self.total_detections += 1
        
        if predicted_anomaly and actual_anomaly:
            self.true_positives += 1
        elif predicted_anomaly and not actual_anomaly:
            self.false_positives += 1
        elif not predicted_anomaly and actual_anomaly:
            self.false_negatives += 1
        else:  # not predicted_anomaly and not actual_anomaly
            self.true_negatives += 1
    
    def get_accuracy(self) -> float:
        """Calculate detection accuracy"""
        if self.total_detections == 0:
            return 0.0
        return (self.true_positives + self.true_negatives) / self.total_detections
    
    def get_precision(self) -> float:
        """Calculate precision (positive predictive value)"""
        denominator = self.true_positives + self.false_positives
        if denominator == 0:
            return 0.0
        return self.true_positives / denominator
    
    def get_recall(self) -> float:
        """Calculate recall (sensitivity, true positive rate)"""
        denominator = self.true_positives + self.false_negatives
        if denominator == 0:
            return 0.0
        return self.true_positives / denominator
    
    def get_f1_score(self) -> float:
        """Calculate F1 score (harmonic mean of precision and recall)"""
        precision = self.get_precision()
        recall = self.get_recall()
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    def get_false_positive_rate(self) -> float:
        """Calculate false positive rate"""
        denominator = self.false_positives + self.true_negatives
        if denominator == 0:
            return 0.0
        return self.false_positives / denominator
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'true_positives': self.true_positives,
            'false_positives': self.false_positives,
            'true_negatives': self.true_negatives,
            'false_negatives': self.false_negatives,
            'total_detections': self.total_detections,
            'accuracy': self.get_accuracy(),
            'precision': self.get_precision(),
            'recall': self.get_recall(),
            'f1_score': self.get_f1_score(),
            'false_positive_rate': self.get_false_positive_rate()
        }


class AnomalyDetector:
    """
    Statistical anomaly detection for charging profile manipulation
    """
    
    def __init__(self, config: DetectionConfig, metrics_collector=None):
        """
        Initialize anomaly detector with configuration
        
        Args:
            config: Detection configuration
            metrics_collector: Optional metrics collector for logging
        """
        self.config = config
        self.metrics_collector = metrics_collector
        self.detection_metrics = DetectionMetrics()
        self.detection_history: List[DetectionEvent] = []
        
        logger.info(f"AnomalyDetector initialized with method: {config.method.value}")
        logger.info(f"Detection enabled: {config.enabled}")
        logger.info(f"Voltage threshold: {config.voltage_threshold_percent}%")
        logger.info(f"Current threshold: {config.current_threshold_percent}%")
    
    def detect_anomaly(self, profile: Dict[str, Any], 
                      message_id: str = "unknown",
                      is_manipulated: bool = False) -> DetectionResult:
        """
        Detect anomalies in a charging profile
        
        Args:
            profile: Charging profile to analyze
            message_id: Message identifier
            is_manipulated: Ground truth - whether profile was actually manipulated
            
        Returns:
            DetectionResult with anomaly detection results
        """
        if not self.config.enabled:
            logger.debug("Detection disabled, skipping")
            return DetectionResult(
                is_anomalous=False,
                confidence_score=0.0,
                detected_anomalies=[],
                total_parameters_checked=0,
                anomalous_parameters=0
            )
        
        timestamp = datetime.now()
        detected_anomalies: List[DetectionEvent] = []
        
        # Extract parameters from profile
        parameters = self._extract_parameters(profile)
        total_parameters = len(parameters)
        
        # Apply detection methods
        if self.config.method == DetectionMethod.STATISTICAL:
            detected_anomalies.extend(
                self._detect_statistical_anomalies(parameters, message_id, timestamp)
            )
        
        if self.config.method == DetectionMethod.RANGE_BASED:
            detected_anomalies.extend(
                self._detect_range_violations(parameters, message_id, timestamp)
            )
        
        if self.config.method == DetectionMethod.PATTERN_BASED:
            detected_anomalies.extend(
                self._detect_pattern_anomalies(profile, message_id, timestamp)
            )
        
        # Calculate overall confidence score
        confidence_score = self._calculate_confidence_score(detected_anomalies)
        
        # Determine if profile is anomalous
        is_anomalous = len(detected_anomalies) > 0 and confidence_score > 0.5
        
        # Record detection metrics
        self.detection_metrics.add_detection(is_anomalous, is_manipulated)
        
        # Store detection events
        self.detection_history.extend(detected_anomalies)
        
        # Log detection event
        if self.metrics_collector and detected_anomalies:
            self._log_detection_events(detected_anomalies)
        
        result = DetectionResult(
            is_anomalous=is_anomalous,
            confidence_score=confidence_score,
            detected_anomalies=detected_anomalies,
            total_parameters_checked=total_parameters,
            anomalous_parameters=len(detected_anomalies)
        )
        
        if is_anomalous:
            logger.info(
                f"Anomaly detected in message {message_id}: "
                f"{len(detected_anomalies)} anomalous parameters, "
                f"confidence: {confidence_score:.2f}"
            )
        
        return result
    
    def _extract_parameters(self, profile: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract relevant parameters from charging profile
        
        Args:
            profile: Charging profile dictionary
            
        Returns:
            Dictionary of parameter name to value
        """
        parameters = {}
        
        # Parse charging schedule
        schedule = self._parse_charging_schedule(profile)
        if not schedule:
            return parameters
        
        periods = schedule.get('chargingSchedulePeriod', [])
        
        # Extract limits from periods
        for i, period in enumerate(periods):
            if 'limit' in period:
                parameters[f'limit_period_{i}'] = period['limit']
        
        # Calculate aggregate statistics
        if periods:
            limits = [p.get('limit', 0) for p in periods if 'limit' in p]
            if limits:
                parameters['limit_mean'] = statistics.mean(limits)
                parameters['limit_max'] = max(limits)
                parameters['limit_min'] = min(limits)
                if len(limits) > 1:
                    parameters['limit_std'] = statistics.stdev(limits)
        
        return parameters
    
    def _parse_charging_schedule(self, profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse charging schedule from profile
        
        Args:
            profile: Charging profile dictionary
            
        Returns:
            Charging schedule dictionary or None
        """
        if 'chargingSchedule' in profile:
            schedule = profile['chargingSchedule']
            if isinstance(schedule, list):
                return schedule[0] if schedule else None
            return schedule
        return None
    
    def _detect_statistical_anomalies(self, parameters: Dict[str, float],
                                     message_id: str,
                                     timestamp: datetime) -> List[DetectionEvent]:
        """
        Detect anomalies using statistical thresholds
        
        Args:
            parameters: Extracted parameters
            message_id: Message identifier
            timestamp: Detection timestamp
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Check mean limit against baseline
        if 'limit_mean' in parameters:
            observed = parameters['limit_mean']
            expected = self.config.baseline_current_mean
            
            # Calculate z-score
            if self.config.baseline_current_std > 0:
                z_score = abs((observed - expected) / self.config.baseline_current_std)
                deviation_percent = abs((observed - expected) / expected) * 100.0
                
                # Check if deviation exceeds threshold
                if deviation_percent > self.config.current_threshold_percent:
                    confidence = min(1.0, z_score / 3.0)  # Normalize z-score to confidence
                    
                    anomalies.append(DetectionEvent(
                        timestamp=timestamp,
                        message_id=message_id,
                        parameter_name='limit_mean',
                        observed_value=observed,
                        expected_value=expected,
                        deviation_percent=deviation_percent,
                        confidence_score=confidence,
                        is_anomaly=True,
                        detection_method='statistical',
                        details={'z_score': z_score}
                    ))
        
        # Check maximum limit
        if 'limit_max' in parameters:
            observed = parameters['limit_max']
            expected = self.config.baseline_current_mean * 1.5  # Expected max is 1.5x mean
            deviation_percent = abs((observed - expected) / expected) * 100.0
            
            if deviation_percent > self.config.current_threshold_percent:
                confidence = min(1.0, deviation_percent / 50.0)  # Normalize to confidence
                
                anomalies.append(DetectionEvent(
                    timestamp=timestamp,
                    message_id=message_id,
                    parameter_name='limit_max',
                    observed_value=observed,
                    expected_value=expected,
                    deviation_percent=deviation_percent,
                    confidence_score=confidence,
                    is_anomaly=True,
                    detection_method='statistical',
                    details={}
                ))
        
        return anomalies
    
    def _detect_range_violations(self, parameters: Dict[str, float],
                                message_id: str,
                                timestamp: datetime) -> List[DetectionEvent]:
        """
        Detect anomalies based on parameter range violations
        
        Args:
            parameters: Extracted parameters
            message_id: Message identifier
            timestamp: Detection timestamp
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Check if any limit exceeds safe maximum
        for param_name, value in parameters.items():
            if 'limit' in param_name:
                # Check against current max (assuming limits are in Amperes)
                if value > self.config.current_max:
                    deviation_percent = ((value - self.config.current_max) / 
                                       self.config.current_max) * 100.0
                    confidence = min(1.0, deviation_percent / 20.0)
                    
                    anomalies.append(DetectionEvent(
                        timestamp=timestamp,
                        message_id=message_id,
                        parameter_name=param_name,
                        observed_value=value,
                        expected_value=self.config.current_max,
                        deviation_percent=deviation_percent,
                        confidence_score=confidence,
                        is_anomaly=True,
                        detection_method='range_based',
                        details={'violation_type': 'exceeds_maximum'}
                    ))
                
                # Check against minimum
                elif value < self.config.current_min:
                    deviation_percent = ((self.config.current_min - value) / 
                                       self.config.current_min) * 100.0
                    confidence = min(1.0, deviation_percent / 20.0)
                    
                    anomalies.append(DetectionEvent(
                        timestamp=timestamp,
                        message_id=message_id,
                        parameter_name=param_name,
                        observed_value=value,
                        expected_value=self.config.current_min,
                        deviation_percent=deviation_percent,
                        confidence_score=confidence,
                        is_anomaly=True,
                        detection_method='range_based',
                        details={'violation_type': 'below_minimum'}
                    ))
        
        return anomalies
    
    def _detect_pattern_anomalies(self, profile: Dict[str, Any],
                                  message_id: str,
                                  timestamp: datetime) -> List[DetectionEvent]:
        """
        Detect anomalies based on charging curve patterns
        
        Args:
            profile: Charging profile dictionary
            message_id: Message identifier
            timestamp: Detection timestamp
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        if not self.config.enable_curve_analysis:
            return anomalies
        
        schedule = self._parse_charging_schedule(profile)
        if not schedule:
            return anomalies
        
        periods = schedule.get('chargingSchedulePeriod', [])
        if len(periods) < 3:
            return anomalies  # Need at least 3 points for pattern analysis
        
        # Extract limits
        limits = [p.get('limit', 0) for p in periods if 'limit' in p]
        if len(limits) < 3:
            return anomalies
        
        # Calculate curve smoothness (variance of differences)
        differences = [limits[i+1] - limits[i] for i in range(len(limits)-1)]
        
        if len(differences) > 1:
            # Check for irregular patterns (high variance in differences)
            try:
                diff_variance = statistics.variance(differences)
                mean_limit = statistics.mean(limits)
                
                # Normalize variance by mean to get relative irregularity
                if mean_limit > 0:
                    irregularity = diff_variance / (mean_limit ** 2)
                    
                    if irregularity > self.config.curve_smoothness_threshold:
                        confidence = min(1.0, irregularity / self.config.curve_smoothness_threshold)
                        
                        anomalies.append(DetectionEvent(
                            timestamp=timestamp,
                            message_id=message_id,
                            parameter_name='charging_curve',
                            observed_value=irregularity,
                            expected_value=self.config.curve_smoothness_threshold,
                            deviation_percent=(irregularity / self.config.curve_smoothness_threshold - 1) * 100.0,
                            confidence_score=confidence,
                            is_anomaly=True,
                            detection_method='pattern_based',
                            details={
                                'irregularity_score': irregularity,
                                'diff_variance': diff_variance,
                                'num_periods': len(periods)
                            }
                        ))
            except statistics.StatisticsError:
                pass  # Not enough data for variance calculation
        
        return anomalies
    
    def _calculate_confidence_score(self, anomalies: List[DetectionEvent]) -> float:
        """
        Calculate overall confidence score from detected anomalies
        
        Args:
            anomalies: List of detected anomalies
            
        Returns:
            Overall confidence score (0.0 to 1.0)
        """
        if not anomalies:
            return 0.0
        
        # Weight confidence scores by detection method
        weighted_scores = []
        
        for anomaly in anomalies:
            weight = 1.0
            if anomaly.detection_method == 'statistical':
                weight = self.config.confidence_weight_statistical
            elif anomaly.detection_method == 'range_based':
                weight = self.config.confidence_weight_range
            elif anomaly.detection_method == 'pattern_based':
                weight = self.config.confidence_weight_pattern
            
            weighted_scores.append(anomaly.confidence_score * weight)
        
        # Return average weighted confidence
        return min(1.0, sum(weighted_scores) / len(weighted_scores))
    
    def _log_detection_events(self, events: List[DetectionEvent]) -> None:
        """
        Log detection events to metrics collector
        
        Args:
            events: List of detection events to log
        """
        if not self.metrics_collector:
            return
        
        for event in events:
            # Log as a special detection event
            if hasattr(self.metrics_collector, 'log_detection_event'):
                self.metrics_collector.log_detection_event(event)
            else:
                logger.debug(f"Metrics collector does not support detection event logging")
    
    def get_detection_metrics(self) -> DetectionMetrics:
        """
        Get current detection performance metrics
        
        Returns:
            DetectionMetrics object
        """
        return self.detection_metrics
    
    def get_detection_history(self) -> List[DetectionEvent]:
        """
        Get history of all detection events
        
        Returns:
            List of DetectionEvent objects
        """
        return self.detection_history
    
    def reset_metrics(self) -> None:
        """Reset detection metrics"""
        self.detection_metrics = DetectionMetrics()
        self.detection_history = []
        logger.info("Detection metrics reset")
