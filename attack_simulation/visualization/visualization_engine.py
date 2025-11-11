"""
Visualization Engine for generating plots and reports
"""

import logging
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server environments
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

logger = logging.getLogger(__name__)


class VisualizationEngine:
    """
    Generates plots and reports from simulation data
    """
    
    def __init__(self, metrics_collector):
        """
        Initialize with metrics data
        
        Args:
            metrics_collector: MetricsCollector instance with simulation data
        """
        self.metrics = metrics_collector
        self.output_dir = Path(metrics_collector.session_dir) / "plots"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure matplotlib for publication quality
        self._configure_matplotlib()
        
        logger.info(f"VisualizationEngine initialized: {self.output_dir}")
    
    def _configure_matplotlib(self) -> None:
        """
        Configure matplotlib for publication-quality plots
        """
        # Set publication-quality defaults
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['savefig.bbox'] = 'tight'
        plt.rcParams['savefig.pad_inches'] = 0.1
        
        # Font settings
        plt.rcParams['font.size'] = 11
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10
        
        # Line and marker settings
        plt.rcParams['lines.linewidth'] = 2
        plt.rcParams['lines.markersize'] = 6
        
        # Grid settings
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['grid.linestyle'] = '--'
        
        # Color cycle for professional appearance
        plt.rcParams['axes.prop_cycle'] = plt.cycler(
            color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                   '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        )
        
        logger.debug("Matplotlib configured for publication quality")
    
    def plot_soh_timeline(self, output_path: Optional[str] = None) -> None:
        """
        Generate SoH degradation timeline plot
        X-axis: Charging cycles or time
        Y-axis: State of Health (%)
        
        Args:
            output_path: Optional custom output path
        """
        logger.info("Generating SoH timeline plot")
        
        # Load degradation timeline data
        degradation_csv = Path(self.metrics.session_dir) / 'degradation_timeline.csv'
        
        if not degradation_csv.exists():
            logger.warning(f"Degradation timeline CSV not found: {degradation_csv}")
            return
        
        try:
            df = pd.read_csv(degradation_csv)
            
            if df.empty:
                logger.warning("No degradation data available for plotting")
                return
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(12, 7))
            
            # Plot SoH timeline
            ax.plot(df['cycle_num'], df['soh'], 
                   color='#1f77b4', linewidth=2.5, 
                   label='State of Health', marker='o', 
                   markersize=4, markevery=max(1, len(df)//20))
            
            # Add confidence interval (simulate with small variance for visualization)
            if len(df) > 1:
                # Calculate rolling standard deviation for confidence interval
                window_size = min(10, len(df) // 5)
                if window_size > 1:
                    rolling_std = df['soh'].rolling(window=window_size, center=True).std()
                    rolling_std = rolling_std.fillna(0.1)  # Fill NaN with small value
                    
                    ax.fill_between(df['cycle_num'], 
                                   df['soh'] - rolling_std, 
                                   df['soh'] + rolling_std,
                                   alpha=0.2, color='#1f77b4', 
                                   label='Confidence Interval')
            
            # Annotate significant degradation events (drops > 0.5%)
            if len(df) > 1:
                df['soh_change'] = df['soh'].diff().abs()
                significant_events = df[df['soh_change'] > 0.5]
                
                for idx, row in significant_events.iterrows():
                    if idx < len(df) - 1:  # Skip last point
                        ax.annotate(f"Δ{row['soh_change']:.2f}%",
                                  xy=(row['cycle_num'], row['soh']),
                                  xytext=(10, -10), textcoords='offset points',
                                  fontsize=8, color='red',
                                  bbox=dict(boxstyle='round,pad=0.3', 
                                          facecolor='yellow', alpha=0.3),
                                  arrowprops=dict(arrowstyle='->', 
                                                connectionstyle='arc3,rad=0',
                                                color='red', lw=1))
            
            # Add horizontal reference lines
            ax.axhline(y=90, color='orange', linestyle='--', 
                      linewidth=1.5, alpha=0.7, label='90% SoH Threshold')
            ax.axhline(y=80, color='red', linestyle='--', 
                      linewidth=1.5, alpha=0.7, label='80% SoH Threshold')
            
            # Formatting
            ax.set_xlabel('Charging Cycle Number', fontsize=13, fontweight='bold')
            ax.set_ylabel('State of Health (%)', fontsize=13, fontweight='bold')
            ax.set_title('Battery State of Health Degradation Over Time', 
                        fontsize=15, fontweight='bold', pad=20)
            
            # Set y-axis limits with some padding
            min_soh = df['soh'].min()
            max_soh = df['soh'].max()
            padding = (max_soh - min_soh) * 0.1 if max_soh > min_soh else 5
            ax.set_ylim(max(0, min_soh - padding), min(100, max_soh + padding))
            
            # Grid
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(loc='best', framealpha=0.9)
            
            # Tight layout
            plt.tight_layout()
            
            # Save in multiple formats
            if output_path:
                base_path = Path(output_path).with_suffix('')
            else:
                base_path = self.output_dir / 'soh_timeline'
            
            # Save as PNG
            png_path = base_path.with_suffix('.png')
            plt.savefig(png_path, dpi=300, bbox_inches='tight')
            logger.info(f"SoH timeline plot saved: {png_path}")
            
            # Save as PDF for publications
            pdf_path = base_path.with_suffix('.pdf')
            plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
            logger.info(f"SoH timeline plot saved: {pdf_path}")
            
            plt.close(fig)
            
        except Exception as e:
            logger.error(f"Error generating SoH timeline plot: {e}")
            raise
    
    def plot_baseline_comparison(self, baseline_data: pd.DataFrame,
                                 attack_data: pd.DataFrame,
                                 output_path: Optional[str] = None) -> None:
        """
        Generate comparison plot: baseline vs. attack scenarios
        Shows degradation acceleration
        
        Args:
            baseline_data: Baseline simulation data (degradation timeline DataFrame)
            attack_data: Attack simulation data (degradation timeline DataFrame)
            output_path: Optional custom output path
        """
        logger.info("Generating baseline comparison plot")
        
        if baseline_data.empty or attack_data.empty:
            logger.warning("Insufficient data for comparison plot")
            return
        
        try:
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(12, 7))
            
            # Plot baseline SoH
            ax.plot(baseline_data['cycle_num'], baseline_data['soh'],
                   color='#2ca02c', linewidth=2.5, linestyle='-',
                   label='Baseline (Normal Operation)', marker='o',
                   markersize=4, markevery=max(1, len(baseline_data)//20))
            
            # Plot attack SoH
            ax.plot(attack_data['cycle_num'], attack_data['soh'],
                   color='#d62728', linewidth=2.5, linestyle='-',
                   label='Attack (Poisoned Profiles)', marker='s',
                   markersize=4, markevery=max(1, len(attack_data)//20))
            
            # Add shaded area showing degradation difference
            # Interpolate to common cycle numbers for comparison
            max_cycles = min(baseline_data['cycle_num'].max(), 
                           attack_data['cycle_num'].max())
            common_cycles = np.linspace(0, max_cycles, 100)
            
            baseline_interp = np.interp(common_cycles, 
                                       baseline_data['cycle_num'], 
                                       baseline_data['soh'])
            attack_interp = np.interp(common_cycles, 
                                     attack_data['cycle_num'], 
                                     attack_data['soh'])
            
            # Fill between curves where attack is worse
            ax.fill_between(common_cycles, baseline_interp, attack_interp,
                          where=(attack_interp < baseline_interp),
                          alpha=0.3, color='red',
                          label='Accelerated Degradation')
            
            # Calculate and display statistical significance
            final_baseline_soh = baseline_data['soh'].iloc[-1]
            final_attack_soh = attack_data['soh'].iloc[-1]
            degradation_diff = final_baseline_soh - final_attack_soh
            
            # Add text box with statistics
            stats_text = (
                f"Final SoH Difference: {degradation_diff:.2f}%\n"
                f"Baseline: {final_baseline_soh:.2f}%\n"
                f"Attack: {final_attack_soh:.2f}%"
            )
            
            ax.text(0.02, 0.02, stats_text,
                   transform=ax.transAxes,
                   fontsize=10,
                   verticalalignment='bottom',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            # Add statistical significance indicator
            if degradation_diff > 1.0:  # Significant difference threshold
                ax.text(0.98, 0.98, '*** Statistically Significant',
                       transform=ax.transAxes,
                       fontsize=11, fontweight='bold',
                       verticalalignment='top',
                       horizontalalignment='right',
                       color='red',
                       bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
            
            # Add horizontal reference lines
            ax.axhline(y=90, color='orange', linestyle='--', 
                      linewidth=1.5, alpha=0.5, label='90% SoH Threshold')
            ax.axhline(y=80, color='darkred', linestyle='--', 
                      linewidth=1.5, alpha=0.5, label='80% SoH Threshold')
            
            # Formatting
            ax.set_xlabel('Charging Cycle Number', fontsize=13, fontweight='bold')
            ax.set_ylabel('State of Health (%)', fontsize=13, fontweight='bold')
            ax.set_title('Baseline vs. Attack: Battery Degradation Comparison', 
                        fontsize=15, fontweight='bold', pad=20)
            
            # Set y-axis limits
            all_soh = pd.concat([baseline_data['soh'], attack_data['soh']])
            min_soh = all_soh.min()
            max_soh = all_soh.max()
            padding = (max_soh - min_soh) * 0.1 if max_soh > min_soh else 5
            ax.set_ylim(max(0, min_soh - padding), min(100, max_soh + padding))
            
            # Grid
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(loc='best', framealpha=0.9, fontsize=10)
            
            # Tight layout
            plt.tight_layout()
            
            # Save in multiple formats
            if output_path:
                base_path = Path(output_path).with_suffix('')
            else:
                base_path = self.output_dir / 'baseline_comparison'
            
            # Save as PNG
            png_path = base_path.with_suffix('.png')
            plt.savefig(png_path, dpi=300, bbox_inches='tight')
            logger.info(f"Baseline comparison plot saved: {png_path}")
            
            # Save as PDF
            pdf_path = base_path.with_suffix('.pdf')
            plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
            logger.info(f"Baseline comparison plot saved: {pdf_path}")
            
            plt.close(fig)
            
        except Exception as e:
            logger.error(f"Error generating baseline comparison plot: {e}")
            raise
    
    def plot_parameter_deviations(self, output_path: Optional[str] = None) -> None:
        """
        Generate histogram of parameter manipulations
        Shows distribution of voltage/current deviations
        
        Args:
            output_path: Optional custom output path
        """
        logger.info("Generating parameter deviation plots")
        
        # Load manipulation data
        manipulations_csv = Path(self.metrics.session_dir) / 'manipulations.csv'
        
        if not manipulations_csv.exists():
            logger.warning(f"Manipulations CSV not found: {manipulations_csv}")
            return
        
        try:
            df = pd.read_csv(manipulations_csv)
            
            if df.empty:
                logger.warning("No manipulation data available for plotting")
                return
            
            # Separate voltage and current manipulations
            voltage_data = df[df['parameter_name'].str.contains('voltage', case=False, na=False)]
            current_data = df[df['parameter_name'].str.contains('current', case=False, na=False)]
            
            # Create figure with subplots
            fig, axes = plt.subplots(2, 1, figsize=(12, 10))
            
            # Plot voltage deviations
            if not voltage_data.empty:
                ax1 = axes[0]
                
                # Histogram
                n, bins, patches = ax1.hist(voltage_data['deviation_percent'], 
                                           bins=30, color='#1f77b4', 
                                           alpha=0.7, edgecolor='black', linewidth=1.2)
                
                # Calculate statistics
                mean_voltage = voltage_data['deviation_percent'].mean()
                std_voltage = voltage_data['deviation_percent'].std()
                
                # Add vertical lines for mean and std
                ax1.axvline(mean_voltage, color='red', linestyle='--', 
                          linewidth=2.5, label=f'Mean: {mean_voltage:.2f}%')
                ax1.axvline(mean_voltage + std_voltage, color='orange', 
                          linestyle=':', linewidth=2, 
                          label=f'±1 Std Dev: {std_voltage:.2f}%')
                ax1.axvline(mean_voltage - std_voltage, color='orange', 
                          linestyle=':', linewidth=2)
                
                # Annotations
                ax1.text(0.98, 0.98, 
                        f'Count: {len(voltage_data)}\n'
                        f'Mean: {mean_voltage:.2f}%\n'
                        f'Std Dev: {std_voltage:.2f}%\n'
                        f'Min: {voltage_data["deviation_percent"].min():.2f}%\n'
                        f'Max: {voltage_data["deviation_percent"].max():.2f}%',
                        transform=ax1.transAxes,
                        fontsize=10,
                        verticalalignment='top',
                        horizontalalignment='right',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
                
                ax1.set_xlabel('Voltage Deviation (%)', fontsize=12, fontweight='bold')
                ax1.set_ylabel('Frequency', fontsize=12, fontweight='bold')
                ax1.set_title('Voltage Parameter Deviation Distribution', 
                            fontsize=14, fontweight='bold', pad=15)
                ax1.grid(True, alpha=0.3, linestyle='--')
                ax1.legend(loc='upper left', framealpha=0.9)
            else:
                axes[0].text(0.5, 0.5, 'No voltage manipulation data available',
                           ha='center', va='center', fontsize=12)
                axes[0].set_title('Voltage Parameter Deviation Distribution',
                                fontsize=14, fontweight='bold')
            
            # Plot current deviations
            if not current_data.empty:
                ax2 = axes[1]
                
                # Histogram
                n, bins, patches = ax2.hist(current_data['deviation_percent'], 
                                           bins=30, color='#ff7f0e', 
                                           alpha=0.7, edgecolor='black', linewidth=1.2)
                
                # Calculate statistics
                mean_current = current_data['deviation_percent'].mean()
                std_current = current_data['deviation_percent'].std()
                
                # Add vertical lines for mean and std
                ax2.axvline(mean_current, color='red', linestyle='--', 
                          linewidth=2.5, label=f'Mean: {mean_current:.2f}%')
                ax2.axvline(mean_current + std_current, color='orange', 
                          linestyle=':', linewidth=2, 
                          label=f'±1 Std Dev: {std_current:.2f}%')
                ax2.axvline(mean_current - std_current, color='orange', 
                          linestyle=':', linewidth=2)
                
                # Annotations
                ax2.text(0.98, 0.98, 
                        f'Count: {len(current_data)}\n'
                        f'Mean: {mean_current:.2f}%\n'
                        f'Std Dev: {std_current:.2f}%\n'
                        f'Min: {current_data["deviation_percent"].min():.2f}%\n'
                        f'Max: {current_data["deviation_percent"].max():.2f}%',
                        transform=ax2.transAxes,
                        fontsize=10,
                        verticalalignment='top',
                        horizontalalignment='right',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
                
                ax2.set_xlabel('Current Deviation (%)', fontsize=12, fontweight='bold')
                ax2.set_ylabel('Frequency', fontsize=12, fontweight='bold')
                ax2.set_title('Current Parameter Deviation Distribution', 
                            fontsize=14, fontweight='bold', pad=15)
                ax2.grid(True, alpha=0.3, linestyle='--')
                ax2.legend(loc='upper left', framealpha=0.9)
            else:
                axes[1].text(0.5, 0.5, 'No current manipulation data available',
                           ha='center', va='center', fontsize=12)
                axes[1].set_title('Current Parameter Deviation Distribution',
                                fontsize=14, fontweight='bold')
            
            # Overall title
            fig.suptitle('Attack Parameter Deviation Analysis', 
                        fontsize=16, fontweight='bold', y=0.995)
            
            # Tight layout
            plt.tight_layout()
            
            # Save in multiple formats
            if output_path:
                base_path = Path(output_path).with_suffix('')
            else:
                base_path = self.output_dir / 'parameter_deviations'
            
            # Save as PNG
            png_path = base_path.with_suffix('.png')
            plt.savefig(png_path, dpi=300, bbox_inches='tight')
            logger.info(f"Parameter deviation plot saved: {png_path}")
            
            # Save as PDF
            pdf_path = base_path.with_suffix('.pdf')
            plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
            logger.info(f"Parameter deviation plot saved: {pdf_path}")
            
            plt.close(fig)
            
        except Exception as e:
            logger.error(f"Error generating parameter deviation plots: {e}")
            raise
    
    def plot_stress_factors(self, output_path: Optional[str] = None) -> None:
        """
        Generate stacked area chart of stress factor contributions
        Shows relative impact of voltage, current, SoC stresses
        
        Args:
            output_path: Optional custom output path
        """
        logger.info("Generating stress factor plots")
        
        # Load degradation timeline data
        degradation_csv = Path(self.metrics.session_dir) / 'degradation_timeline.csv'
        
        if not degradation_csv.exists():
            logger.warning(f"Degradation timeline CSV not found: {degradation_csv}")
            return
        
        try:
            df = pd.read_csv(degradation_csv)
            
            if df.empty:
                logger.warning("No degradation data available for stress factor plotting")
                return
            
            # Check if stress factor columns exist
            required_cols = ['voltage_stress', 'current_stress', 'soc_stress']
            if not all(col in df.columns for col in required_cols):
                logger.warning("Stress factor columns not found in degradation data")
                return
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 7))
            
            # Prepare data for stacked area chart
            cycles = df['cycle_num']
            voltage_stress = df['voltage_stress']
            current_stress = df['current_stress']
            soc_stress = df['soc_stress']
            
            # Create stacked area chart
            ax.fill_between(cycles, 0, voltage_stress, 
                          alpha=0.7, color='#d62728', label='Voltage Stress')
            ax.fill_between(cycles, voltage_stress, 
                          voltage_stress + current_stress,
                          alpha=0.7, color='#ff7f0e', label='Current Stress')
            ax.fill_between(cycles, voltage_stress + current_stress,
                          voltage_stress + current_stress + soc_stress,
                          alpha=0.7, color='#2ca02c', label='SoC Stress')
            
            # Add line for combined stress
            combined_stress = df['combined_stress']
            ax.plot(cycles, combined_stress, color='black', 
                   linewidth=2.5, linestyle='--', 
                   label='Combined Stress Factor', marker='o',
                   markersize=3, markevery=max(1, len(df)//20))
            
            # Calculate average contributions
            avg_voltage = voltage_stress.mean()
            avg_current = current_stress.mean()
            avg_soc = soc_stress.mean()
            total_avg = avg_voltage + avg_current + avg_soc
            
            # Add statistics text box
            if total_avg > 0:
                stats_text = (
                    f"Average Stress Contributions:\n"
                    f"Voltage: {avg_voltage:.3f} ({avg_voltage/total_avg*100:.1f}%)\n"
                    f"Current: {avg_current:.3f} ({avg_current/total_avg*100:.1f}%)\n"
                    f"SoC: {avg_soc:.3f} ({avg_soc/total_avg*100:.1f}%)"
                )
            else:
                stats_text = "No stress data available"
            
            ax.text(0.02, 0.98, stats_text,
                   transform=ax.transAxes,
                   fontsize=10,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            # Formatting
            ax.set_xlabel('Charging Cycle Number', fontsize=13, fontweight='bold')
            ax.set_ylabel('Stress Factor', fontsize=13, fontweight='bold')
            ax.set_title('Battery Stress Factor Contributions Over Time', 
                        fontsize=15, fontweight='bold', pad=20)
            
            # Grid
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(loc='best', framealpha=0.9)
            
            # Set y-axis to start at 0
            ax.set_ylim(bottom=0)
            
            # Tight layout
            plt.tight_layout()
            
            # Save in multiple formats
            if output_path:
                base_path = Path(output_path).with_suffix('')
            else:
                base_path = self.output_dir / 'stress_factors'
            
            # Save as PNG
            png_path = base_path.with_suffix('.png')
            plt.savefig(png_path, dpi=300, bbox_inches='tight')
            logger.info(f"Stress factors plot saved: {png_path}")
            
            # Save as PDF
            pdf_path = base_path.with_suffix('.pdf')
            plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
            logger.info(f"Stress factors plot saved: {pdf_path}")
            
            plt.close(fig)
            
        except Exception as e:
            logger.error(f"Error generating stress factor plots: {e}")
            raise
    
    def generate_latex_table(self, output_path: Optional[str] = None) -> None:
        """
        Generate LaTeX-formatted summary table for publications
        
        Args:
            output_path: Optional custom output path
        """
        logger.info("Generating LaTeX table")
        
        try:
            # Get summary data
            summary = self.metrics.generate_summary_report()
            
            # Create LaTeX table
            latex_lines = [
                "% LaTeX table for publication",
                "% Generated by EmuOCPP Attack Simulation",
                "\\begin{table}[htbp]",
                "\\centering",
                "\\caption{Attack Simulation Summary Statistics}",
                "\\label{tab:attack_simulation_summary}",
                "\\begin{tabular}{|l|r|}",
                "\\hline",
                "\\textbf{Metric} & \\textbf{Value} \\\\",
                "\\hline",
                "\\hline",
                f"Session ID & \\texttt{{{summary.session_id}}} \\\\",
                "\\hline",
                f"Total Charging Cycles & {summary.total_cycles} \\\\",
                f"Total Duration (hours) & {summary.total_duration_hours:.2f} \\\\",
                "\\hline",
                f"Initial SoH (\\%) & {summary.initial_soh:.2f} \\\\",
                f"Final SoH (\\%) & {summary.final_soh:.2f} \\\\",
                f"Total Degradation (\\%) & {summary.total_degradation:.4f} \\\\",
                f"Degradation Rate (\\%/cycle) & {summary.degradation_rate_per_cycle:.6f} \\\\",
                "\\hline",
                f"Avg. Voltage Deviation (\\%) & {summary.average_voltage_deviation:.2f} \\\\",
                f"Avg. Current Deviation (\\%) & {summary.average_current_deviation:.2f} \\\\",
                "\\hline",
                "\\end{tabular}",
                "\\end{table}",
                ""
            ]
            
            # Save LaTeX table
            if output_path:
                latex_path = Path(output_path)
            else:
                latex_path = self.output_dir / 'summary_table.tex'
            
            with open(latex_path, 'w') as f:
                f.write('\n'.join(latex_lines))
            
            logger.info(f"LaTeX table saved: {latex_path}")
            
        except Exception as e:
            logger.error(f"Error generating LaTeX table: {e}")
            raise
    
    def generate_html_report(self, output_path: Optional[str] = None) -> None:
        """
        Generate interactive HTML report with all plots and statistics
        
        Args:
            output_path: Optional custom output path
        """
        logger.info("Generating HTML report")
        
        try:
            # Get summary data
            summary = self.metrics.generate_summary_report()
            
            # Check for available plots
            plots_dir = self.output_dir
            soh_plot = plots_dir / 'soh_timeline.png'
            param_plot = plots_dir / 'parameter_deviations.png'
            stress_plot = plots_dir / 'stress_factors.png'
            
            # Create HTML content
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Attack Simulation Report - {summary.session_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .subtitle {{
            margin-top: 10px;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .section {{
            background: white;
            padding: 25px;
            margin-bottom: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h2 {{
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }}
        .stat-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }}
        .stat-unit {{
            font-size: 0.8em;
            color: #666;
        }}
        .plot-container {{
            margin: 20px 0;
            text-align: center;
        }}
        .plot-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .plot-title {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #555;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}
        .alert {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .alert-danger {{
            background-color: #f8d7da;
            border-left-color: #dc3545;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔋 Attack Simulation Report</h1>
        <div class="subtitle">Session ID: {summary.session_id}</div>
        <div class="subtitle">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    </div>

    <div class="section">
        <h2>📊 Summary Statistics</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Charging Cycles</div>
                <div class="stat-value">{summary.total_cycles}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Duration</div>
                <div class="stat-value">{summary.total_duration_hours:.2f} <span class="stat-unit">hours</span></div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Initial SoH</div>
                <div class="stat-value">{summary.initial_soh:.2f} <span class="stat-unit">%</span></div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Final SoH</div>
                <div class="stat-value">{summary.final_soh:.2f} <span class="stat-unit">%</span></div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Degradation</div>
                <div class="stat-value">{summary.total_degradation:.4f} <span class="stat-unit">%</span></div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Degradation Rate</div>
                <div class="stat-value">{summary.degradation_rate_per_cycle:.6f} <span class="stat-unit">%/cycle</span></div>
            </div>
        </div>
"""

            # Add attack manipulation statistics if available
            if summary.average_voltage_deviation > 0 or summary.average_current_deviation > 0:
                html_content += f"""
        <div class="alert alert-danger">
            <strong>⚠️ Attack Detected:</strong> This simulation includes malicious charging profile manipulations.
        </div>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Avg. Voltage Deviation</div>
                <div class="stat-value">{summary.average_voltage_deviation:.2f} <span class="stat-unit">%</span></div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg. Current Deviation</div>
                <div class="stat-value">{summary.average_current_deviation:.2f} <span class="stat-unit">%</span></div>
            </div>
        </div>
"""
            
            html_content += """
    </div>
"""

            # Add SoH timeline plot
            if soh_plot.exists():
                html_content += f"""
    <div class="section">
        <h2>📈 State of Health Timeline</h2>
        <div class="plot-container">
            <img src="plots/soh_timeline.png" alt="SoH Timeline">
        </div>
    </div>
"""

            # Add parameter deviation plots
            if param_plot.exists():
                html_content += f"""
    <div class="section">
        <h2>📉 Parameter Deviation Analysis</h2>
        <div class="plot-container">
            <img src="plots/parameter_deviations.png" alt="Parameter Deviations">
        </div>
    </div>
"""

            # Add stress factors plot
            if stress_plot.exists():
                html_content += f"""
    <div class="section">
        <h2>⚡ Stress Factor Contributions</h2>
        <div class="plot-container">
            <img src="plots/stress_factors.png" alt="Stress Factors">
        </div>
    </div>
"""

            # Add detailed metrics table
            html_content += f"""
    <div class="section">
        <h2>📋 Detailed Metrics</h2>
        <table>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Session ID</td>
                    <td><code>{summary.session_id}</code></td>
                </tr>
                <tr>
                    <td>Total Charging Cycles</td>
                    <td>{summary.total_cycles}</td>
                </tr>
                <tr>
                    <td>Total Duration (hours)</td>
                    <td>{summary.total_duration_hours:.2f}</td>
                </tr>
                <tr>
                    <td>Initial State of Health (%)</td>
                    <td>{summary.initial_soh:.2f}</td>
                </tr>
                <tr>
                    <td>Final State of Health (%)</td>
                    <td>{summary.final_soh:.2f}</td>
                </tr>
                <tr>
                    <td>Total Degradation (%)</td>
                    <td>{summary.total_degradation:.4f}</td>
                </tr>
                <tr>
                    <td>Degradation Rate (%/cycle)</td>
                    <td>{summary.degradation_rate_per_cycle:.6f}</td>
                </tr>
                <tr>
                    <td>Average Voltage Deviation (%)</td>
                    <td>{summary.average_voltage_deviation:.2f}</td>
                </tr>
                <tr>
                    <td>Average Current Deviation (%)</td>
                    <td>{summary.average_current_deviation:.2f}</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="footer">
        <p>Generated by EmuOCPP Attack Simulation Framework</p>
        <p>For research and educational purposes only</p>
    </div>
</body>
</html>
"""

            # Save HTML report
            if output_path:
                html_path = Path(output_path)
            else:
                html_path = Path(self.metrics.session_dir) / 'report.html'
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report saved: {html_path}")
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            raise
    
    def generate_all_visualizations(self) -> None:
        """
        Generate all standard visualizations and reports
        """
        logger.info("Generating all visualizations and reports...")
        
        try:
            # Generate plots
            self.plot_soh_timeline()
            self.plot_parameter_deviations()
            self.plot_stress_factors()
            
            # Generate reports
            self.generate_latex_table()
            self.generate_html_report()
            
            logger.info(f"All visualizations and reports generated successfully in {self.output_dir}")
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
            raise
