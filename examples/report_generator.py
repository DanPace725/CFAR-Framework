#!/usr/bin/env python3
"""
CFAR Framework Report Generator

Generate comprehensive PDF and HTML reports with interpretive analysis
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import argparse
from datetime import datetime
from typing import Dict, Any, List
import numpy as np

# Try to import reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Note: reportlab not installed. PDF export will be unavailable.")
    print("Install with: pip install reportlab")

# Set plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class CFARReportGenerator:
    """Generate comprehensive reports for CFAR Framework simulation results"""
    
    def __init__(self, results_file: str):
        """Initialize with simulation results"""
        self.results_file = Path(results_file)
        
        with open(self.results_file, 'r') as f:
            self.results = json.load(f)
        
        self.df = pd.DataFrame(self.results['simulation_data'])
        self.metadata = self.results['metadata']
        self.summary = self.results['summary']
        
        # Create output directory
        self.output_dir = Path(f"reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.output_dir.mkdir(exist_ok=True)
        
        # Generate interpretive analysis
        self.analysis = self.generate_interpretive_analysis()
    
    def generate_interpretive_analysis(self) -> Dict[str, Any]:
        """Generate interpretive analysis of the simulation results"""
        
        # Extract time series data
        state_data = {}
        control_data = {}
        param_data = {}
        
        for var in ['Y', 'N', 'A', 'C', 'B']:
            state_data[var] = [day['state'][var] for day in self.df.to_dict('records')]
        
        for var in ['uC', 'uA', 'uF']:
            control_data[var] = [day['control'][var] for day in self.df.to_dict('records')]
        
        for var in ['NA_eff', 'lambda_eff', 'k1', 'delta_Y_min']:
            param_data[var] = [day['parameters'][var] for day in self.df.to_dict('records')]
        
        days = list(range(len(state_data['Y'])))
        
        # Performance analysis
        performance = self.analyze_performance(state_data, days)
        
        # Control strategy analysis
        control_strategy = self.analyze_control_strategy(control_data, days)
        
        # System dynamics analysis
        dynamics = self.analyze_system_dynamics(state_data, control_data, param_data, days)
        
        # Key insights
        insights = self.generate_key_insights(performance, control_strategy, dynamics)
        
        # Recommendations
        recommendations = self.generate_recommendations(performance, control_strategy, dynamics, insights)
        
        return {
            'performance': performance,
            'control_strategy': control_strategy,
            'dynamics': dynamics,
            'insights': insights,
            'recommendations': recommendations
        }
    
    def analyze_performance(self, state_data: Dict, days: List[int]) -> Dict[str, Any]:
        """Analyze system performance metrics"""
        
        Y_values = state_data['Y']
        target = self.metadata['target_Y']
        
        # Performance metrics
        final_Y = Y_values[-1]
        max_Y = max(Y_values)
        min_Y = min(Y_values)
        
        # Time to target
        time_to_target = None
        for i, y in enumerate(Y_values):
            if y >= target:
                time_to_target = i
                break
        
        # Stability analysis
        if len(Y_values) > 20:
            recent_std = np.std(Y_values[-20:])
            overall_std = np.std(Y_values)
            stability_ratio = recent_std / overall_std if overall_std > 0 else 1.0
        else:
            stability_ratio = 1.0
        
        # Performance phases
        phases = self.identify_performance_phases(Y_values, target)
        
        return {
            'final_performance': final_Y,
            'peak_performance': max_Y,
            'performance_range': max_Y - min_Y,
            'target_achievement': final_Y >= target * 0.95,  # Within 5% of target
            'time_to_target': time_to_target,
            'stability_ratio': stability_ratio,
            'phases': phases,
            'performance_grade': self.calculate_performance_grade(final_Y, target, time_to_target)
        }
    
    def analyze_control_strategy(self, control_data: Dict, days: List[int]) -> Dict[str, Any]:
        """Analyze control strategy effectiveness"""
        
        uC_values = control_data['uC']
        uA_values = control_data['uA']
        uF_values = control_data['uF']
        
        # Control mode analysis
        control_modes = [day['control']['control_mode'] for day in self.df.to_dict('records')]
        precision_days = sum(1 for mode in control_modes if mode == 'precision')
        fluctuation_days = len(control_modes) - precision_days
        
        # Fluctuation pulse analysis
        fluctuation_pulses = [(i, uF) for i, uF in enumerate(uF_values) if uF > 0.01]
        
        # Control effort analysis
        total_control_effort = sum(abs(uC) + abs(uA) + abs(uF) for uC, uA, uF in zip(uC_values, uA_values, uF_values))
        
        # Strategy effectiveness
        strategy_effectiveness = self.evaluate_strategy_effectiveness(control_data, fluctuation_pulses)
        
        return {
            'precision_percentage': precision_days / len(control_modes) * 100,
            'fluctuation_percentage': fluctuation_days / len(control_modes) * 100,
            'total_fluctuation_pulses': len(fluctuation_pulses),
            'pulse_frequency': len(fluctuation_pulses) / len(days) * 100,  # pulses per 100 days
            'total_control_effort': total_control_effort,
            'average_control_effort': total_control_effort / len(days),
            'strategy_effectiveness': strategy_effectiveness,
            'control_pattern': self.identify_control_patterns(control_modes, fluctuation_pulses)
        }
    
    def analyze_system_dynamics(self, state_data: Dict, control_data: Dict, param_data: Dict, days: List[int]) -> Dict[str, Any]:
        """Analyze system dynamics and parameter evolution"""
        
        # Constraint evolution
        C_values = state_data['C']
        constraint_trend = 'declining' if C_values[-1] < C_values[0] else 'stable' if abs(C_values[-1] - C_values[0]) < 0.1 else 'increasing'
        
        # Attention dynamics
        A_values = state_data['A']
        attention_saturation = max(A_values) > 0.9
        
        # Resolution parameter analysis
        delta_Y_min_values = param_data['delta_Y_min']
        avg_resolution = np.mean(delta_Y_min_values)
        resolution_trend = 'improving' if delta_Y_min_values[-1] < delta_Y_min_values[0] else 'degrading'
        
        # System phase identification
        system_phases = self.identify_system_phases(state_data, control_data)
        
        return {
            'constraint_trend': constraint_trend,
            'attention_saturation': attention_saturation,
            'max_attention': max(A_values),
            'average_resolution': avg_resolution,
            'resolution_trend': resolution_trend,
            'system_phases': system_phases,
            'dominant_dynamics': self.identify_dominant_dynamics(state_data)
        }
    
    def generate_key_insights(self, performance: Dict, control_strategy: Dict, dynamics: Dict) -> List[str]:
        """Generate key insights from the analysis"""
        
        insights = []
        
        # Performance insights
        if performance['target_achievement']:
            insights.append(f"🎯 **Target Achievement**: System successfully reached {performance['final_performance']:.1%} of target performance.")
        else:
            gap = self.metadata['target_Y'] - performance['final_performance']
            insights.append(f"⚠️ **Performance Gap**: System fell short of target by {gap:.1%}.")
        
        # Control strategy insights
        if control_strategy['fluctuation_percentage'] > 80:
            insights.append(f"🌊 **Fluctuation-Dominant**: System operated in fluctuation mode {control_strategy['fluctuation_percentage']:.0f}% of the time, indicating resolution limits were frequently encountered.")
        elif control_strategy['precision_percentage'] > 60:
            insights.append(f"🎛️ **Precision-Capable**: System operated in precision mode {control_strategy['precision_percentage']:.0f}% of the time, suggesting good resolution capacity.")
        
        # Fluctuation pulse insights
        if control_strategy['total_fluctuation_pulses'] > 10:
            insights.append(f"⚡ **Active Gradient Engineering**: {control_strategy['total_fluctuation_pulses']} fluctuation pulses created alternative pathways when precision was blocked.")
        
        # System dynamics insights
        if dynamics['attention_saturation']:
            insights.append(f"🔥 **Attention Saturation**: System reached maximum attention levels, indicating high engagement but potential for attention traps.")
        
        if dynamics['constraint_trend'] == 'declining':
            insights.append(f"📉 **Constraint Decay**: System constraints declined over time, requiring increased reliance on fluctuation control.")
        
        # Resolution insights
        if dynamics['resolution_trend'] == 'improving':
            insights.append(f"🔍 **Improving Resolution**: System resolution capacity improved over time, enabling more precise control.")
        
        return insights
    
    def generate_recommendations(self, performance: Dict, control_strategy: Dict, dynamics: Dict, insights: List[str]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        
        recommendations = []
        
        # Based on control strategy
        if control_strategy['fluctuation_percentage'] > 80:
            recommendations.append("🔧 **Improve Resolution**: Consider increasing sensing features, reducing intervention cadence, or improving operational precision to enable more precision mode operation.")
        
        # Based on performance
        if not performance['target_achievement']:
            if control_strategy['total_fluctuation_pulses'] < 5:
                recommendations.append("⚡ **Increase Fluctuation Control**: Consider lowering attention threshold or reducing cooldown to enable more gradient engineering.")
            else:
                recommendations.append("🎯 **Adjust Target**: Current target may be beyond system capacity given current constraints.")
        
        # Based on system dynamics
        if dynamics['constraint_trend'] == 'declining':
            recommendations.append("🏗️ **Strengthen Constraints**: Implement measures to maintain beneficial structural elements while allowing adaptive flexibility.")
        
        if dynamics['attention_saturation']:
            recommendations.append("💡 **Attention Management**: Consider attention allocation strategies to prevent traps and maintain sustainable engagement.")
        
        # Based on stability
        if performance['stability_ratio'] > 1.5:
            recommendations.append("📊 **Improve Stability**: System shows increasing volatility. Consider tuning PID parameters or adjusting fluctuation control sensitivity.")
        
        return recommendations
    
    def identify_performance_phases(self, Y_values: List[float], target: float) -> List[Dict]:
        """Identify distinct performance phases in the simulation"""
        
        phases = []
        current_phase = None
        phase_start = 0
        
        for i, y in enumerate(Y_values):
            # Determine current state
            if y < target * 0.8:
                state = 'building'
            elif y < target * 0.95:
                state = 'approaching'
            elif y >= target:
                state = 'achieved'
            else:
                state = 'near_target'
            
            # Check for phase change
            if current_phase != state:
                if current_phase is not None:
                    phases.append({
                        'phase': current_phase,
                        'start_day': phase_start,
                        'end_day': i - 1,
                        'duration': i - phase_start
                    })
                current_phase = state
                phase_start = i
        
        # Add final phase
        if current_phase is not None:
            phases.append({
                'phase': current_phase,
                'start_day': phase_start,
                'end_day': len(Y_values) - 1,
                'duration': len(Y_values) - phase_start
            })
        
        return phases
    
    def calculate_performance_grade(self, final_Y: float, target: float, time_to_target: int) -> str:
        """Calculate an overall performance grade"""
        
        # Performance score (0-100)
        performance_score = min(100, (final_Y / target) * 100)
        
        # Time bonus/penalty
        if time_to_target is not None:
            if time_to_target <= 10:
                time_bonus = 10
            elif time_to_target <= 30:
                time_bonus = 5
            else:
                time_bonus = 0
        else:
            time_bonus = -20  # Penalty for not reaching target
        
        total_score = performance_score + time_bonus
        
        if total_score >= 90:
            return 'A'
        elif total_score >= 80:
            return 'B'
        elif total_score >= 70:
            return 'C'
        elif total_score >= 60:
            return 'D'
        else:
            return 'F'
    
    def evaluate_strategy_effectiveness(self, control_data: Dict, fluctuation_pulses: List) -> str:
        """Evaluate the effectiveness of the control strategy"""
        
        # Simple heuristic based on control patterns
        uF_values = control_data['uF']
        pulse_count = len(fluctuation_pulses)
        
        if pulse_count > 15:
            return 'highly_active'
        elif pulse_count > 8:
            return 'moderately_active'
        elif pulse_count > 3:
            return 'selective'
        else:
            return 'minimal'
    
    def identify_control_patterns(self, control_modes: List[str], fluctuation_pulses: List) -> str:
        """Identify the dominant control pattern"""
        
        precision_count = sum(1 for mode in control_modes if mode == 'precision')
        fluctuation_count = len(control_modes) - precision_count
        
        if fluctuation_count > precision_count * 3:
            return 'fluctuation_dominant'
        elif precision_count > fluctuation_count * 2:
            return 'precision_dominant'
        else:
            return 'balanced'
    
    def identify_system_phases(self, state_data: Dict, control_data: Dict) -> List[str]:
        """Identify major system phases"""
        
        phases = []
        
        # Check for initial buildup
        Y_values = state_data['Y']
        if Y_values[10] > Y_values[0] * 1.2:  # 20% improvement in first 10 days
            phases.append('rapid_initial_growth')
        
        # Check for plateau
        if len(Y_values) > 30:
            mid_section = Y_values[20:40]
            if max(mid_section) - min(mid_section) < 0.05:  # Low variance in middle section
                phases.append('plateau')
        
        # Check for decline
        if Y_values[-1] < max(Y_values) * 0.9:
            phases.append('performance_decline')
        
        return phases if phases else ['steady_state']
    
    def identify_dominant_dynamics(self, state_data: Dict) -> str:
        """Identify the dominant system dynamics"""
        
        # Analyze which state variable shows most change
        changes = {}
        for var in ['Y', 'N', 'A', 'C', 'B']:
            values = state_data[var]
            changes[var] = max(values) - min(values)
        
        dominant_var = max(changes, key=changes.get)
        
        dynamics_map = {
            'Y': 'outcome_driven',
            'N': 'norm_evolution',
            'A': 'attention_dynamics',
            'C': 'constraint_evolution',
            'B': 'burden_management'
        }
        
        return dynamics_map.get(dominant_var, 'balanced')
    
    def generate_plots(self) -> Dict[str, str]:
        """Generate all plots and return file paths"""
        
        plot_files = {}
        
        # 1. Performance overview
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # State evolution
        days = list(range(len(self.df)))
        for var, color in zip(['Y', 'N', 'A', 'C', 'B'], ['blue', 'green', 'orange', 'red', 'purple']):
            values = [day['state'][var] for day in self.df.to_dict('records')]
            ax1.plot(days, values, label=var, color=color, linewidth=2)
        ax1.axhline(y=self.metadata['target_Y'], color='black', linestyle='--', alpha=0.7, label='Target')
        ax1.set_title('State Variables Over Time')
        ax1.set_xlabel('Day')
        ax1.set_ylabel('Value')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Control actions
        uC_values = [day['control']['uC'] for day in self.df.to_dict('records')]
        uA_values = [day['control']['uA'] for day in self.df.to_dict('records')]
        uF_values = [day['control']['uF'] for day in self.df.to_dict('records')]
        
        ax2.plot(days, uC_values, label='Structural (uC)', color='red', linewidth=2)
        ax2.plot(days, uA_values, label='Attention (uA)', color='blue', linewidth=2)
        ax2.plot(days, uF_values, label='Fluctuation (uF)', color='purple', linewidth=2)
        
        # Highlight fluctuation pulses
        pulse_days = [i for i, uF in enumerate(uF_values) if uF > 0.01]
        pulse_values = [uF_values[i] for i in pulse_days]
        ax2.scatter(pulse_days, pulse_values, color='orange', s=50, zorder=5, label='Fluctuation Pulses')
        
        ax2.set_title('Control Actions Over Time')
        ax2.set_xlabel('Day')
        ax2.set_ylabel('Control Signal')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Resolution parameters
        delta_Y_min_values = [day['parameters']['delta_Y_min'] for day in self.df.to_dict('records')]
        ax3.plot(days, delta_Y_min_values, color='brown', linewidth=2)
        ax3.set_title('Resolution Limit (ΔY_min) Over Time')
        ax3.set_xlabel('Day')
        ax3.set_ylabel('Minimum Resolvable Change')
        ax3.grid(True, alpha=0.3)
        
        # Control mode timeline
        control_modes = [day['control']['control_mode'] for day in self.df.to_dict('records')]
        precision_y = [1 if mode == 'precision' else 0 for mode in control_modes]
        fluctuation_y = [0 if mode == 'precision' else 1 for mode in control_modes]
        
        ax4.fill_between(days, precision_y, alpha=0.7, color='blue', label='Precision Mode')
        ax4.fill_between(days, fluctuation_y, alpha=0.7, color='purple', label='Fluctuation Mode')
        
        # Mark fluctuation pulses
        for day in pulse_days:
            ax4.axvline(x=day, color='orange', linestyle='--', alpha=0.8)
        
        ax4.set_title('Control Mode Timeline')
        ax4.set_xlabel('Day')
        ax4.set_ylabel('Mode Active')
        ax4.set_ylim(-0.1, 1.1)
        ax4.legend()
        
        plt.tight_layout()
        overview_path = self.output_dir / 'performance_overview.png'
        plt.savefig(overview_path, dpi=300, bbox_inches='tight')
        plt.close()
        plot_files['overview'] = str(overview_path)
        
        return plot_files
    
    def export_html_report(self) -> str:
        """Generate comprehensive HTML report"""
        
        plots = self.generate_plots()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CFAR Framework Simulation Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 30px 0; }}
                .metric {{ background: #e9f5ff; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .insight {{ background: #f0f8e9; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .recommendation {{ background: #fff3cd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .plot {{ text-align: center; margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .grade {{ font-size: 2em; font-weight: bold; color: #2e7d32; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 CFAR Framework Simulation Report</h1>
                <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Configuration:</strong> {self.metadata['config_file']}</p>
                <p><strong>Simulation Period:</strong> {self.metadata['horizon_days']} days</p>
            </div>
            
            <div class="section">
                <h2>📊 Executive Summary</h2>
                <div class="metric">
                    <h3>Overall Performance Grade: <span class="grade">{self.analysis['performance']['performance_grade']}</span></h3>
                    <p><strong>Target:</strong> {self.metadata['target_Y']:.1%} | <strong>Achieved:</strong> {self.analysis['performance']['final_performance']:.1%}</p>
                    <p><strong>Peak Performance:</strong> {self.analysis['performance']['peak_performance']:.1%}</p>
                    <p><strong>Target Achievement:</strong> {'✅ Yes' if self.analysis['performance']['target_achievement'] else '❌ No'}</p>
                </div>
            </div>
            
            <div class="section">
                <h2>🎛️ Control Strategy Analysis</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th><th>Interpretation</th></tr>
                    <tr>
                        <td>Precision Mode Usage</td>
                        <td>{self.analysis['control_strategy']['precision_percentage']:.1f}%</td>
                        <td>{'High precision capability' if self.analysis['control_strategy']['precision_percentage'] > 50 else 'Resolution-limited system'}</td>
                    </tr>
                    <tr>
                        <td>Fluctuation Mode Usage</td>
                        <td>{self.analysis['control_strategy']['fluctuation_percentage']:.1f}%</td>
                        <td>{'Frequent gradient engineering needed' if self.analysis['control_strategy']['fluctuation_percentage'] > 70 else 'Moderate fluctuation reliance'}</td>
                    </tr>
                    <tr>
                        <td>Fluctuation Pulses</td>
                        <td>{self.analysis['control_strategy']['total_fluctuation_pulses']}</td>
                        <td>{'Highly active gradient creation' if self.analysis['control_strategy']['total_fluctuation_pulses'] > 10 else 'Selective intervention'}</td>
                    </tr>
                    <tr>
                        <td>Control Effort</td>
                        <td>{self.analysis['control_strategy']['average_control_effort']:.3f}</td>
                        <td>Average daily control signal magnitude</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h2>🔍 Key Insights</h2>
        """
        
        for insight in self.analysis['insights']:
            html_content += f'<div class="insight">{insight}</div>\n'
        
        html_content += f"""
            </div>
            
            <div class="section">
                <h2>💡 Recommendations</h2>
        """
        
        for rec in self.analysis['recommendations']:
            html_content += f'<div class="recommendation">{rec}</div>\n'
        
        html_content += f"""
            </div>
            
            <div class="section">
                <h2>📈 Performance Visualization</h2>
                <div class="plot">
                    <img src="{Path(plots['overview']).name}" alt="Performance Overview" style="max-width: 100%; height: auto;">
                </div>
            </div>
            
            <div class="section">
                <h2>🔬 Technical Details</h2>
                <h3>System Dynamics</h3>
                <ul>
                    <li><strong>Constraint Trend:</strong> {self.analysis['dynamics']['constraint_trend'].title()}</li>
                    <li><strong>Attention Saturation:</strong> {'Yes' if self.analysis['dynamics']['attention_saturation'] else 'No'} (Max: {self.analysis['dynamics']['max_attention']:.1%})</li>
                    <li><strong>Average Resolution:</strong> {self.analysis['dynamics']['average_resolution']:.3f}</li>
                    <li><strong>Resolution Trend:</strong> {self.analysis['dynamics']['resolution_trend'].title()}</li>
                    <li><strong>Dominant Dynamics:</strong> {self.analysis['dynamics']['dominant_dynamics'].replace('_', ' ').title()}</li>
                </ul>
                
                <h3>Performance Phases</h3>
                <table>
                    <tr><th>Phase</th><th>Start Day</th><th>Duration</th><th>Description</th></tr>
        """
        
        phase_descriptions = {
            'building': 'Building toward target performance',
            'approaching': 'Approaching target range',
            'achieved': 'Target performance achieved',
            'near_target': 'Near target but not fully achieved'
        }
        
        for phase in self.analysis['performance']['phases']:
            desc = phase_descriptions.get(phase['phase'], phase['phase'].replace('_', ' ').title())
            html_content += f"""
                    <tr>
                        <td>{phase['phase'].replace('_', ' ').title()}</td>
                        <td>{phase['start_day']}</td>
                        <td>{phase['duration']} days</td>
                        <td>{desc}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>📋 Simulation Configuration</h2>
                <table>
                    <tr><th>Parameter</th><th>Value</th></tr>
        """
        
        # Add key configuration parameters
        config_items = [
            ('Target Y', f"{self.metadata['target_Y']:.1%}"),
            ('Initial Y', f"{self.metadata['initial_state']['Y']:.1%}"),
            ('Horizon Days', str(self.metadata['horizon_days'])),
            ('PID Gains', f"Kp={self.results['parameters']['pid']['kp']}, Ki={self.results['parameters']['pid']['ki']}, Kd={self.results['parameters']['pid']['kd']}"),
            ('Fluctuation Max uF', str(self.results['parameters']['fluctuation']['max_uF'])),
            ('Attention Threshold', f"{self.results['parameters']['fluctuation']['A_threshold']:.1%}"),
        ]
        
        for param, value in config_items:
            html_content += f"<tr><td>{param}</td><td>{value}</td></tr>\n"
        
        html_content += """
                </table>
            </div>
            
            <footer style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
                <p>Generated by CFAR Framework Report Generator</p>
                <p>For more information, visit the project documentation.</p>
            </footer>
        </body>
        </html>
        """
        
        # Save HTML report
        html_file = self.output_dir / 'simulation_report.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(html_file)
    
    def export_json_summary(self) -> str:
        """Export structured analysis summary as JSON"""
        
        summary_data = {
            'metadata': self.metadata,
            'analysis': self.analysis,
            'generated_at': datetime.now().isoformat(),
            'source_file': str(self.results_file)
        }
        
        json_file = self.output_dir / 'analysis_summary.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2)
        
        return str(json_file)
    
    def export_csv_data(self) -> str:
        """Export processed data as CSV"""
        
        # Flatten the nested data structure
        flattened_data = []
        
        for day_data in self.df.to_dict('records'):
            row = {'day': day_data['day']}
            
            # Add state variables
            for var in ['Y', 'N', 'A', 'C', 'B']:
                row[f'state_{var}'] = day_data['state'][var]
            
            # Add control variables
            for var in ['uC', 'uA', 'uF', 'control_mode', 'arm_name']:
                row[f'control_{var}'] = day_data['control'][var]
            
            # Add parameters
            for var in ['NA_eff', 'lambda_eff', 'k1', 'delta_Y_min']:
                row[f'param_{var}'] = day_data['parameters'][var]
            
            flattened_data.append(row)
        
        # Create DataFrame and save
        df_flat = pd.DataFrame(flattened_data)
        csv_file = self.output_dir / 'simulation_data.csv'
        df_flat.to_csv(csv_file, index=False)
        
        return str(csv_file)


def main():
    parser = argparse.ArgumentParser(description="Generate comprehensive CFAR Framework simulation reports")
    parser.add_argument("results_file", help="Path to simulation results JSON file")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--json", action="store_true", help="Generate JSON analysis summary")
    parser.add_argument("--csv", action="store_true", help="Generate CSV data export")
    parser.add_argument("--all", action="store_true", help="Generate all report formats")
    
    args = parser.parse_args()
    
    # Create report generator
    generator = CFARReportGenerator(args.results_file)
    
    generated_files = []
    
    # Generate requested formats
    if args.html or args.all:
        html_file = generator.export_html_report()
        generated_files.append(f"HTML Report: {html_file}")
    
    if args.json or args.all:
        json_file = generator.export_json_summary()
        generated_files.append(f"JSON Summary: {json_file}")
    
    if args.csv or args.all:
        csv_file = generator.export_csv_data()
        generated_files.append(f"CSV Data: {csv_file}")
    
    if not any([args.html, args.json, args.csv, args.all]):
        # Default to HTML if no format specified
        html_file = generator.export_html_report()
        generated_files.append(f"HTML Report: {html_file}")
    
    print("🎯 CFAR Framework Report Generation Complete!")
    print(f"📁 Output Directory: {generator.output_dir}")
    print("\n📄 Generated Files:")
    for file_info in generated_files:
        print(f"  • {file_info}")
    
    print(f"\n🔍 Key Insights:")
    for insight in generator.analysis['insights'][:3]:  # Show top 3 insights
        print(f"  • {insight}")
    
    print(f"\n💡 Top Recommendations:")
    for rec in generator.analysis['recommendations'][:2]:  # Show top 2 recommendations
        print(f"  • {rec}")


if __name__ == "__main__":
    main()
