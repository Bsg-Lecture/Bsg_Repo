"""
Detection Performance Evaluation with ROC curves, AUC, and confusion matrix
"""

import logging
from typing import List, Tuple, Dict, Any
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import matplotlib, but make it optional
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("matplotlib not available, visualization features will be disabled")


@dataclass
class ROCPoint:
    """Single point on ROC curve"""
    threshold: float
    true_positive_rate: float
    false_positive_rate: float
    precision: float
    recall: float


class DetectionPerformanceEvaluator:
    """
    Evaluates detection performance with ROC curves, AUC, and confusion matrix
    """
    
    def __init__(self, output_dir: str = "./output"):
        """
        Initialize performance evaluator
        
        Args:
            output_dir: Directory for saving plots
        """
        self.output_dir = output_dir
        
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("Matplotlib not available, plots will not be generated")
    
    def calculate_roc_curve(self, 
                           predictions: List[Tuple[float, bool]]) -> Tuple[List[ROCPoint], float]:
        """
        Calculate ROC curve points and AUC
        
        Args:
            predictions: List of (confidence_score, is_actually_anomalous) tuples
            
        Returns:
            Tuple of (ROC points list, AUC value)
        """
        if not predictions:
            logger.warning("No predictions provided for ROC calculation")
            return [], 0.0
        
        # Sort predictions by confidence score (descending)
        sorted_predictions = sorted(predictions, key=lambda x: x[0], reverse=True)
        
        # Count total positives and negatives
        total_positives = sum(1 for _, is_anomaly in predictions if is_anomaly)
        total_negatives = len(predictions) - total_positives
        
        if total_positives == 0 or total_negatives == 0:
            logger.warning("Need both positive and negative samples for ROC curve")
            return [], 0.0
        
        # Calculate ROC points at different thresholds
        roc_points = []
        true_positives = 0
        false_positives = 0
        
        # Add point at threshold = 1.0 (no detections)
        roc_points.append(ROCPoint(
            threshold=1.0,
            true_positive_rate=0.0,
            false_positive_rate=0.0,
            precision=0.0,
            recall=0.0
        ))
        
        # Calculate points for each unique threshold
        prev_score = None
        for confidence_score, is_actually_anomalous in sorted_predictions:
            # Only create new point when threshold changes
            if prev_score is not None and confidence_score == prev_score:
                if is_actually_anomalous:
                    true_positives += 1
                else:
                    false_positives += 1
                continue
            
            # Update counts
            if is_actually_anomalous:
                true_positives += 1
            else:
                false_positives += 1
            
            # Calculate rates
            tpr = true_positives / total_positives if total_positives > 0 else 0.0
            fpr = false_positives / total_negatives if total_negatives > 0 else 0.0
            
            # Calculate precision and recall
            total_predicted_positive = true_positives + false_positives
            precision = true_positives / total_predicted_positive if total_predicted_positive > 0 else 0.0
            recall = tpr
            
            roc_points.append(ROCPoint(
                threshold=confidence_score,
                true_positive_rate=tpr,
                false_positive_rate=fpr,
                precision=precision,
                recall=recall
            ))
            
            prev_score = confidence_score
        
        # Add point at threshold = 0.0 (all detections)
        if roc_points[-1].threshold > 0.0:
            roc_points.append(ROCPoint(
                threshold=0.0,
                true_positive_rate=1.0,
                false_positive_rate=1.0,
                precision=total_positives / len(predictions),
                recall=1.0
            ))
        
        # Calculate AUC using trapezoidal rule
        auc = self._calculate_auc(roc_points)
        
        logger.info(f"ROC curve calculated: {len(roc_points)} points, AUC = {auc:.4f}")
        
        return roc_points, auc
    
    def _calculate_auc(self, roc_points: List[ROCPoint]) -> float:
        """
        Calculate Area Under Curve using trapezoidal rule
        
        Args:
            roc_points: List of ROC points
            
        Returns:
            AUC value
        """
        if len(roc_points) < 2:
            return 0.0
        
        auc = 0.0
        for i in range(len(roc_points) - 1):
            # Trapezoidal area between two points
            x1, y1 = roc_points[i].false_positive_rate, roc_points[i].true_positive_rate
            x2, y2 = roc_points[i+1].false_positive_rate, roc_points[i+1].true_positive_rate
            
            width = abs(x2 - x1)
            height = (y1 + y2) / 2.0
            auc += width * height
        
        return auc
    
    def plot_roc_curve(self, 
                      roc_points: List[ROCPoint], 
                      auc: float,
                      output_path: str,
                      title: str = "ROC Curve - Anomaly Detection") -> None:
        """
        Generate ROC curve plot
        
        Args:
            roc_points: List of ROC points
            auc: Area Under Curve value
            output_path: Path to save plot
            title: Plot title
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("Matplotlib not available, skipping ROC plot")
            return
        
        if not roc_points:
            logger.warning("No ROC points to plot")
            return
        
        # Extract FPR and TPR values
        fpr = [point.false_positive_rate for point in roc_points]
        tpr = [point.true_positive_rate for point in roc_points]
        
        # Create plot
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, 'b-', linewidth=2, label=f'ROC Curve (AUC = {auc:.4f})')
        plt.plot([0, 1], [0, 1], 'r--', linewidth=1, label='Random Classifier')
        
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend(loc='lower right', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        
        # Add annotations for key points
        if len(roc_points) > 2:
            # Find point closest to top-left corner (optimal point)
            distances = [(point.false_positive_rate**2 + (1-point.true_positive_rate)**2, i) 
                        for i, point in enumerate(roc_points)]
            _, optimal_idx = min(distances)
            optimal_point = roc_points[optimal_idx]
            
            plt.plot(optimal_point.false_positive_rate, 
                    optimal_point.true_positive_rate, 
                    'go', markersize=10, label='Optimal Point')
            plt.annotate(f'Threshold: {optimal_point.threshold:.2f}',
                        xy=(optimal_point.false_positive_rate, optimal_point.true_positive_rate),
                        xytext=(10, -10), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                        fontsize=9)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"ROC curve saved to: {output_path}")
    
    def plot_precision_recall_curve(self,
                                    roc_points: List[ROCPoint],
                                    output_path: str,
                                    title: str = "Precision-Recall Curve") -> None:
        """
        Generate Precision-Recall curve plot
        
        Args:
            roc_points: List of ROC points (contains precision and recall)
            output_path: Path to save plot
            title: Plot title
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("Matplotlib not available, skipping PR plot")
            return
        
        if not roc_points:
            logger.warning("No points to plot")
            return
        
        # Extract precision and recall values
        recall = [point.recall for point in roc_points]
        precision = [point.precision for point in roc_points]
        
        # Create plot
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, 'b-', linewidth=2, label='PR Curve')
        
        plt.xlabel('Recall', fontsize=12)
        plt.ylabel('Precision', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend(loc='upper right', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Precision-Recall curve saved to: {output_path}")
    
    def plot_confusion_matrix(self,
                             true_positives: int,
                             false_positives: int,
                             true_negatives: int,
                             false_negatives: int,
                             output_path: str,
                             title: str = "Confusion Matrix") -> None:
        """
        Generate confusion matrix visualization
        
        Args:
            true_positives: Number of true positives
            false_positives: Number of false positives
            true_negatives: Number of true negatives
            false_negatives: Number of false negatives
            output_path: Path to save plot
            title: Plot title
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("Matplotlib not available, skipping confusion matrix plot")
            return
        
        # Create confusion matrix
        confusion_matrix = np.array([
            [true_negatives, false_positives],
            [false_negatives, true_positives]
        ])
        
        # Create plot
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Display matrix as image
        im = ax.imshow(confusion_matrix, cmap='Blues', aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['Predicted Normal', 'Predicted Anomaly'], fontsize=11)
        ax.set_yticklabels(['Actually Normal', 'Actually Anomaly'], fontsize=11)
        
        # Rotate x labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Add text annotations
        for i in range(2):
            for j in range(2):
                value = confusion_matrix[i, j]
                text = ax.text(j, i, str(value),
                             ha="center", va="center", color="black", fontsize=20, fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Count', fontsize=11)
        
        # Set title
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Calculate and display metrics
        total = true_positives + false_positives + true_negatives + false_negatives
        accuracy = (true_positives + true_negatives) / total if total > 0 else 0.0
        
        metrics_text = f"Accuracy: {accuracy:.2%}\n"
        metrics_text += f"Total Samples: {total}"
        
        plt.figtext(0.5, 0.02, metrics_text, ha='center', fontsize=10,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Confusion matrix saved to: {output_path}")
    
    def plot_threshold_analysis(self,
                               roc_points: List[ROCPoint],
                               output_path: str,
                               title: str = "Detection Threshold Analysis") -> None:
        """
        Plot how different metrics vary with detection threshold
        
        Args:
            roc_points: List of ROC points
            output_path: Path to save plot
            title: Plot title
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("Matplotlib not available, skipping threshold analysis plot")
            return
        
        if not roc_points:
            logger.warning("No points to plot")
            return
        
        # Extract data
        thresholds = [point.threshold for point in roc_points]
        tpr = [point.true_positive_rate for point in roc_points]
        fpr = [point.false_positive_rate for point in roc_points]
        precision = [point.precision for point in roc_points]
        
        # Calculate F1 scores
        f1_scores = []
        for point in roc_points:
            if point.precision + point.recall > 0:
                f1 = 2 * (point.precision * point.recall) / (point.precision + point.recall)
            else:
                f1 = 0.0
            f1_scores.append(f1)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(thresholds, tpr, 'b-', linewidth=2, label='True Positive Rate (Recall)')
        ax.plot(thresholds, fpr, 'r-', linewidth=2, label='False Positive Rate')
        ax.plot(thresholds, precision, 'g-', linewidth=2, label='Precision')
        ax.plot(thresholds, f1_scores, 'm-', linewidth=2, label='F1 Score')
        
        ax.set_xlabel('Detection Threshold', fontsize=12)
        ax.set_ylabel('Metric Value', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        
        # Find and mark optimal threshold (max F1 score)
        if f1_scores:
            max_f1_idx = f1_scores.index(max(f1_scores))
            optimal_threshold = thresholds[max_f1_idx]
            optimal_f1 = f1_scores[max_f1_idx]
            
            ax.axvline(x=optimal_threshold, color='k', linestyle='--', linewidth=1, alpha=0.5)
            ax.annotate(f'Optimal: {optimal_threshold:.2f}\nF1: {optimal_f1:.3f}',
                       xy=(optimal_threshold, optimal_f1),
                       xytext=(10, 10), textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                       fontsize=9)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Threshold analysis saved to: {output_path}")
    
    def generate_performance_report(self,
                                   detection_metrics: Any,
                                   roc_points: List[ROCPoint],
                                   auc: float,
                                   output_dir: str) -> Dict[str, Any]:
        """
        Generate comprehensive performance evaluation report
        
        Args:
            detection_metrics: DetectionMetrics object
            roc_points: List of ROC points
            auc: Area Under Curve value
            output_dir: Directory to save plots
            
        Returns:
            Dictionary with performance metrics
        """
        import os
        from pathlib import Path
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate plots
        roc_path = os.path.join(output_dir, 'roc_curve.png')
        self.plot_roc_curve(roc_points, auc, roc_path)
        
        pr_path = os.path.join(output_dir, 'precision_recall_curve.png')
        self.plot_precision_recall_curve(roc_points, pr_path)
        
        cm_path = os.path.join(output_dir, 'confusion_matrix.png')
        self.plot_confusion_matrix(
            detection_metrics.true_positives,
            detection_metrics.false_positives,
            detection_metrics.true_negatives,
            detection_metrics.false_negatives,
            cm_path
        )
        
        threshold_path = os.path.join(output_dir, 'threshold_analysis.png')
        self.plot_threshold_analysis(roc_points, threshold_path)
        
        # Compile report
        report = {
            'auc': auc,
            'accuracy': detection_metrics.get_accuracy(),
            'precision': detection_metrics.get_precision(),
            'recall': detection_metrics.get_recall(),
            'f1_score': detection_metrics.get_f1_score(),
            'false_positive_rate': detection_metrics.get_false_positive_rate(),
            'true_positives': detection_metrics.true_positives,
            'false_positives': detection_metrics.false_positives,
            'true_negatives': detection_metrics.true_negatives,
            'false_negatives': detection_metrics.false_negatives,
            'total_detections': detection_metrics.total_detections,
            'plots': {
                'roc_curve': roc_path,
                'precision_recall_curve': pr_path,
                'confusion_matrix': cm_path,
                'threshold_analysis': threshold_path
            }
        }
        
        logger.info(f"Performance report generated in: {output_dir}")
        logger.info(f"AUC: {auc:.4f}, Accuracy: {report['accuracy']:.2%}, "
                   f"F1: {report['f1_score']:.2%}")
        
        return report
