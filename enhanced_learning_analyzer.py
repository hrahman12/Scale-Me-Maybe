#!/usr/bin/env python3
"""
Enhanced Learning Analyzer for Scale Me Maybe
Analyzes correlations between mix parameters and OD growth
Focuses on consider_data=True entries with B2 as preferred reference
"""

import os
import json
import math
from datetime import datetime, timedelta
from collections import defaultdict

class EnhancedLearningAnalyzer:
    def __init__(self, base_path='.'):
        self.base_path = base_path
        self.parameter_files = {
            1: os.path.join(base_path, 'passaging_workcell_params', 'ScaleMeMaybe_Plate', 'passaging_parameters.csv'),
            2: os.path.join(base_path, 'passaging_workcell_params', 'ScaleMeMaybe_Plate', 'passaging_parameters_2.csv'),
            3: os.path.join(base_path, 'passaging_workcell_params', 'ScaleMeMaybe_Plate', 'passaging_parameters_3.csv'),
            4: os.path.join(base_path, 'passaging_workcell_params', 'ScaleMeMaybe_Plate', 'passaging_parameters_4.csv'),
        }
        self.well_data_path = os.path.join(base_path, 'data', 'Individual_wells_data')
        self.parameter_data = {}
        self.well_data = {}
        self.learning_analysis = {}
        self.correlation_analysis = {}
        
    def load_csv(self, file_path):
        """Load CSV file with proper error handling"""
        data = []
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                headers = [h.strip() for h in lines[0].split(',')]
                for line in lines[1:]:
                    values = [v.strip() for v in line.split(',')]
                    row = {}
                    for i, header in enumerate(headers):
                        if header == 'timestamp':
                            row[header] = datetime.fromisoformat(values[i].replace('Z', '+00:00'))
                        elif header in ['absorbance_od600', 'cell_concentration_cells_per_ml']:
                            row[header] = float(values[i])
                        elif header == 'consider_data':
                            row[header] = values[i].lower() == 'true'
                        else:
                            row[header] = values[i]
                    data.append(row)
        except FileNotFoundError:
            print(f"  ❌ File not found: {file_path}")
        except Exception as e:
            print(f"  ❌ Error loading {file_path}: {e}")
        return data

    def load_all_data(self):
        """Load all parameter and well data"""
        print("🔬 Loading Enhanced Learning Data...")
        
        # Load parameter files
        print("  Loading parameter files...")
        for exp_num, file_path in self.parameter_files.items():
            df = self.load_csv(file_path)
            if df:
                self.parameter_data[exp_num] = df
                print(f"    ✅ Loaded {os.path.basename(file_path)}: {len(df)} rows")

        # Load well data with consider_data filtering
        print("  Loading well data (consider_data=True only)...")
        well_files = [f for f in os.listdir(self.well_data_path) if f.endswith('_absorbance.csv')]
        
        total_consider_points = 0
        for file in well_files:
            well_id = file.replace('well_', '').replace('_absorbance.csv', '')
            df = self.load_csv(f"{self.well_data_path}/{file}")
            
            if df:
                # Filter to only consider_data=True entries
                consider_data = [row for row in df if row.get('consider_data', False)]
                consider_count = len(consider_data)
                total_consider_points += consider_count
                
                if consider_count > 0:
                    # Sort by timestamp
                    consider_data.sort(key=lambda x: x['timestamp'])
                    self.well_data[well_id] = consider_data
                    print(f"    ✅ {well_id}: {consider_count} consider_data=True points")
                else:
                    print(f"    ⚠️  {well_id}: No consider_data=True points")
        
        print(f"📊 Total consider_data=True points: {total_consider_points}")
        return self.well_data, self.parameter_data

    def map_wells_to_parameters(self):
        """Map wells to their experimental parameters"""
        well_to_params = {}
        
        for exp_num, params in self.parameter_data.items():
            for param_row in params:
                dest_well = param_row.get('destination_well', '')
                if dest_well:
                    well_to_params[dest_well] = {
                        'experiment': exp_num,
                        'mix_cycles': int(param_row.get('mix_reps', 0)),
                        'mix_volume': int(param_row.get('mix_volume_uL', 0)),
                        'mix_height': int(param_row.get('mix_height_mm', 0)),
                        'cell_volume': int(param_row.get('cell_volume_uL', 0)),
                        'media_volume': int(param_row.get('media_volume_uL', 0)),
                        'total_volume': int(param_row.get('total_volume_uL', 0))
                    }
        
        return well_to_params

    def analyze_growth_characteristics(self, well_id, data):
        """Analyze growth characteristics for a specific well"""
        if len(data) < 10:
            return None
            
        # Convert to hours and OD
        start_time = data[0]['timestamp']
        hours_data = []
        od_data = []
        
        for point in data:
            if point['absorbance_od600'] > 0:
                hours = (point['timestamp'] - start_time).total_seconds() / 3600
                hours_data.append(hours)
                od_data.append(point['absorbance_od600'])
        
        if len(hours_data) < 10:
            return None
            
        # Find optimal growth phase (exponential growth)
        best_growth = self.find_optimal_growth_phase(hours_data, od_data)
        
        if best_growth:
            return {
                'well_id': well_id,
                'total_points': len(data),
                'time_span_hours': hours_data[-1] - hours_data[0],
                'max_od': max(od_data),
                'min_od': min(od_data),
                'od_range': max(od_data) - min(od_data),
                'growth_phase': best_growth
            }
        return None

    def find_optimal_growth_phase(self, hours_data, od_data):
        """Find the optimal exponential growth phase"""
        best_growth = None
        best_score = 0
        
        # Look for exponential growth windows
        for window_size in [3, 6, 9, 12]:  # Different window sizes in hours
            window_points = min(window_size * 4, len(hours_data) // 2)  # ~4 points per hour
            
            for i in range(len(hours_data) - window_points):
                end_idx = i + window_points
                window_hours = hours_data[i:end_idx]
                window_od = od_data[i:end_idx]
                
                if len(window_od) < 5:
                    continue
                
                # Check if this is exponential growth
                min_od = min(window_od)
                max_od = max(window_od)
                avg_od = sum(window_od) / len(window_od)
                
                # Should be in optimal OD range (0.2-0.8)
                if not (0.2 <= avg_od <= 0.8):
                    continue
                
                # Should be increasing
                if window_od[-1] <= window_od[0]:
                    continue
                
                # Calculate exponential growth slope
                log_od = [math.log(od) for od in window_od if od > 0]
                if len(log_od) < 5:
                    continue
                
                # Linear regression on log-transformed data
                slope, r_squared = self.calculate_log_regression(window_hours, log_od)
                
                if slope > 0 and r_squared > 0.7:
                    # Calculate growth efficiency score
                    od_efficiency = 1.0 - abs(avg_od - 0.4) / 0.4  # Prefer OD around 0.4
                    growth_rate = slope
                    consistency = r_squared
                    
                    # Combined score
                    score = growth_rate * consistency * od_efficiency
                    
                    if score > best_score:
                        best_score = score
                        doubling_time = math.log(2) / slope if slope > 0 else float('inf')
                        
                        best_growth = {
                            'slope': slope,
                            'r_squared': r_squared,
                            'doubling_time': doubling_time,
                            'start_hour': window_hours[0],
                            'end_hour': window_hours[-1],
                            'min_od': min_od,
                            'max_od': max_od,
                            'avg_od': avg_od,
                            'growth_score': score,
                            'od_efficiency': od_efficiency
                        }
        
        return best_growth

    def calculate_log_regression(self, x_data, y_data):
        """Calculate linear regression on log-transformed data"""
        n = len(x_data)
        sum_x = sum(x_data)
        sum_y = sum(y_data)
        sum_xy = sum(x * y for x, y in zip(x_data, y_data))
        sum_x2 = sum(x ** 2 for x in x_data)
        
        try:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        except ZeroDivisionError:
            return 0, 0
        
        # Calculate R-squared
        y_mean = sum_y / n
        ss_tot = sum((y - y_mean) ** 2 for y in y_data)
        ss_res = sum((y - (slope * x + (sum_y - slope * sum_x) / n)) ** 2 
                    for x, y in zip(x_data, y_data))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return slope, r_squared

    def analyze_correlations(self, well_to_params):
        """Analyze correlations between mix parameters and growth performance"""
        print("\n🔍 Analyzing Parameter Correlations...")
        
        correlations = {
            'mix_cycles': [],
            'mix_volume': [],
            'mix_height': [],
            'growth_scores': [],
            'doubling_times': [],
            'od_efficiency': []
        }
        
        well_performance = []
        
        for well_id, data in self.well_data.items():
            if well_id not in well_to_params:
                continue
                
            params = well_to_params[well_id]
            growth_analysis = self.analyze_growth_characteristics(well_id, data)
            
            if growth_analysis and growth_analysis['growth_phase']:
                correlations['mix_cycles'].append(params['mix_cycles'])
                correlations['mix_volume'].append(params['mix_volume'])
                correlations['mix_height'].append(params['mix_height'])
                correlations['growth_scores'].append(growth_analysis['growth_phase']['growth_score'])
                correlations['doubling_times'].append(growth_analysis['growth_phase']['doubling_time'])
                correlations['od_efficiency'].append(growth_analysis['growth_phase']['od_efficiency'])
                
                well_performance.append({
                    'well_id': well_id,
                    'parameters': params,
                    'growth_analysis': growth_analysis,
                    'is_b2': well_id == 'B2'
                })
        
        # Calculate correlation coefficients
        correlation_matrix = self.calculate_correlation_matrix(correlations)
        
        # Find optimal parameters based on correlations
        optimal_params = self.find_optimal_parameters(correlations, well_performance)
        
        return {
            'correlations': correlation_matrix,
            'well_performance': well_performance,
            'optimal_parameters': optimal_params,
            'b2_analysis': self.get_b2_analysis(well_performance)
        }

    def calculate_correlation_matrix(self, correlations):
        """Calculate correlation matrix between parameters and performance"""
        matrix = {}
        
        params = ['mix_cycles', 'mix_volume', 'mix_height']
        metrics = ['growth_scores', 'doubling_times', 'od_efficiency']
        
        for param in params:
            matrix[param] = {}
            for metric in metrics:
                if len(correlations[param]) > 1 and len(correlations[metric]) > 1:
                    corr = self.calculate_correlation(correlations[param], correlations[metric])
                    matrix[param][metric] = corr
                else:
                    matrix[param][metric] = 0
        
        return matrix

    def calculate_correlation(self, x, y):
        """Calculate Pearson correlation coefficient"""
        n = len(x)
        if n != len(y) or n < 2:
            return 0
        
        # Convert to floats and filter out invalid values
        x_clean = []
        y_clean = []
        
        for i in range(n):
            try:
                x_val = float(x[i])
                y_val = float(y[i])
                if not (math.isnan(x_val) or math.isnan(y_val)):
                    x_clean.append(x_val)
                    y_clean.append(y_val)
            except (ValueError, TypeError):
                continue
        
        if len(x_clean) < 2:
            return 0
        
        # Calculate means
        mean_x = sum(x_clean) / len(x_clean)
        mean_y = sum(y_clean) / len(y_clean)
        
        # Calculate correlation
        numerator = sum((x_clean[i] - mean_x) * (y_clean[i] - mean_y) for i in range(len(x_clean)))
        denominator_x = sum((x_clean[i] - mean_x) ** 2 for i in range(len(x_clean)))
        denominator_y = sum((y_clean[i] - mean_y) ** 2 for i in range(len(y_clean)))
        
        if denominator_x == 0 or denominator_y == 0:
            return 0
        
        correlation = numerator / math.sqrt(denominator_x * denominator_y)
        return correlation

    def find_optimal_parameters(self, correlations, well_performance):
        """Find optimal parameters based on performance analysis"""
        # Sort wells by growth score
        sorted_wells = sorted(well_performance, 
                            key=lambda x: x['growth_analysis']['growth_phase']['growth_score'], 
                            reverse=True)
        
        # Get top performers
        top_performers = sorted_wells[:5]  # Top 5 wells
        
        # Calculate optimal parameters
        optimal = {
            'mix_cycles': sum([w['parameters']['mix_cycles'] for w in top_performers]) / len(top_performers),
            'mix_volume': sum([w['parameters']['mix_volume'] for w in top_performers]) / len(top_performers),
            'mix_height': sum([w['parameters']['mix_height'] for w in top_performers]) / len(top_performers),
            'confidence': len(top_performers) / len(well_performance) if well_performance else 0
        }
        
        return optimal

    def get_b2_analysis(self, well_performance):
        """Get specific analysis for B2 well"""
        b2_data = [w for w in well_performance if w['well_id'] == 'B2']
        if b2_data:
            return {
                'found': True,
                'performance': b2_data[0],
                'rank': next((i+1 for i, w in enumerate(sorted(well_performance, 
                    key=lambda x: x['growth_analysis']['growth_phase']['growth_score'], 
                    reverse=True)) if w['well_id'] == 'B2'), None)
            }
        return {'found': False}

    def generate_learning_model(self, analysis_results):
        """Generate enhanced learning model based on analysis"""
        print("\n🧠 Generating Enhanced Learning Model...")
        
        correlations = analysis_results['correlations']
        optimal_params = analysis_results['optimal_parameters']
        b2_analysis = analysis_results['b2_analysis']
        
        # Create learning model
        learning_model = {
            'model_type': 'correlation_based_optimization',
            'created_at': datetime.now().isoformat(),
            'data_summary': {
                'total_wells_analyzed': len(analysis_results['well_performance']),
                'consider_data_points': sum(len(data) for data in self.well_data.values()),
                'b2_preference': b2_analysis['found']
            },
            'correlation_insights': {
                'mix_cycles_vs_growth': correlations['mix_cycles']['growth_scores'],
                'mix_volume_vs_growth': correlations['mix_volume']['growth_scores'],
                'mix_height_vs_growth': correlations['mix_height']['growth_scores'],
                'mix_cycles_vs_doubling': correlations['mix_cycles']['doubling_times'],
                'mix_volume_vs_doubling': correlations['mix_volume']['doubling_times'],
                'mix_height_vs_doubling': correlations['mix_height']['doubling_times']
            },
            'optimal_parameters': {
                'mix_cycles': round(optimal_params['mix_cycles'], 1),
                'mix_volume': round(optimal_params['mix_volume'], 1),
                'mix_height': round(optimal_params['mix_height'], 1),
                'confidence': round(optimal_params['confidence'], 3)
            },
            'b2_analysis': b2_analysis,
            'top_performing_wells': [
                {
                    'well_id': w['well_id'],
                    'mix_cycles': w['parameters']['mix_cycles'],
                    'mix_volume': w['parameters']['mix_volume'],
                    'mix_height': w['parameters']['mix_height'],
                    'growth_score': round(w['growth_analysis']['growth_phase']['growth_score'], 4),
                    'doubling_time': round(w['growth_analysis']['growth_phase']['doubling_time'], 2),
                    'is_b2': w['is_b2']
                }
                for w in sorted(analysis_results['well_performance'], 
                              key=lambda x: x['growth_analysis']['growth_phase']['growth_score'], 
                              reverse=True)[:10]
            ],
            'parameter_ranges': {
                'mix_cycles': {
                    'min': min([w['parameters']['mix_cycles'] for w in analysis_results['well_performance']]),
                    'max': max([w['parameters']['mix_cycles'] for w in analysis_results['well_performance']]),
                    'optimal': round(optimal_params['mix_cycles'], 1)
                },
                'mix_volume': {
                    'min': min([w['parameters']['mix_volume'] for w in analysis_results['well_performance']]),
                    'max': max([w['parameters']['mix_volume'] for w in analysis_results['well_performance']]),
                    'optimal': round(optimal_params['mix_volume'], 1)
                },
                'mix_height': {
                    'min': min([w['parameters']['mix_height'] for w in analysis_results['well_performance']]),
                    'max': max([w['parameters']['mix_height'] for w in analysis_results['well_performance']]),
                    'optimal': round(optimal_params['mix_height'], 1)
                }
            }
        }
        
        return learning_model

    def run_complete_analysis(self):
        """Run the complete enhanced learning analysis"""
        print("🚀 Starting Enhanced Learning Analysis...")
        print("=" * 60)
        
        # Load data
        self.load_all_data()
        
        # Map wells to parameters
        well_to_params = self.map_wells_to_parameters()
        
        # Analyze correlations
        analysis_results = self.analyze_correlations(well_to_params)
        
        # Generate learning model
        learning_model = self.generate_learning_model(analysis_results)
        
        # Save results
        output_file = 'enhanced_learning_model.json'
        with open(output_file, 'w') as f:
            json.dump(learning_model, f, indent=2)
        
        print(f"\n✅ Enhanced Learning Model saved to: {output_file}")
        print("=" * 60)
        
        # Print summary
        self.print_analysis_summary(learning_model)
        
        return learning_model

    def print_analysis_summary(self, model):
        """Print analysis summary"""
        print("\n📊 ANALYSIS SUMMARY:")
        print(f"  • Total wells analyzed: {model['data_summary']['total_wells_analyzed']}")
        print(f"  • Consider data points: {model['data_summary']['consider_data_points']}")
        print(f"  • B2 preference: {'Yes' if model['b2_analysis']['found'] else 'No'}")
        
        print("\n🎯 OPTIMAL PARAMETERS:")
        opt = model['optimal_parameters']
        print(f"  • Mix Cycles: {opt['mix_cycles']} (confidence: {opt['confidence']:.1%})")
        print(f"  • Mix Volume: {opt['mix_volume']} μL")
        print(f"  • Mix Height: {opt['mix_height']} mm")
        
        print("\n🔗 KEY CORRELATIONS:")
        corr = model['correlation_insights']
        print(f"  • Mix Cycles vs Growth: {corr['mix_cycles_vs_growth']:.3f}")
        print(f"  • Mix Volume vs Growth: {corr['mix_volume_vs_growth']:.3f}")
        print(f"  • Mix Height vs Growth: {corr['mix_height_vs_growth']:.3f}")
        
        if model['b2_analysis']['found']:
            print(f"\n⭐ B2 PERFORMANCE:")
            b2_perf = model['b2_analysis']['performance']
            print(f"  • Growth Score: {b2_perf['growth_analysis']['growth_phase']['growth_score']:.4f}")
            print(f"  • Doubling Time: {b2_perf['growth_analysis']['growth_phase']['doubling_time']:.2f} hours")
            print(f"  • Rank: #{model['b2_analysis']['rank']}")

if __name__ == "__main__":
    analyzer = EnhancedLearningAnalyzer()
    model = analyzer.run_complete_analysis()
