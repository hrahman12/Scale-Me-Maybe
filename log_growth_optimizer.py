#!/usr/bin/env python3
"""
Scale Me Maybe - Vibrio natriegens Growth Optimization Analysis
FOCUSED ON LOG GROWTH PHASE OPTIMIZATION
"""

import csv
import json
import os
from datetime import datetime
import math

class LogGrowthOptimizer:
    def __init__(self, data_dir="data/Individual_wells_data", params_dir="passaging_workcell_params"):
        self.data_dir = data_dir
        self.params_dir = params_dir
        self.well_data = {}
        self.parameter_data = {}
        self.log_growth_analysis = {}
        
    def load_csv(self, filepath):
        """Load CSV file and return as list of dictionaries"""
        data = []
        try:
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            print(f"  ❌ File not found: {filepath}")
        return data
    
    def load_all_data(self):
        """Load all well data and parameter files"""
        print("🧬 Loading experimental data...")
        
        # Load parameter files
        param_files = [
            "passaging_parameters.csv",
            f"{self.params_dir}/passaging_parameters_2.csv",
            f"{self.params_dir}/passaging_parameters_3.csv", 
            f"{self.params_dir}/passaging_parameters_4.csv"
        ]
        
        for i, file in enumerate(param_files, 1):
            if os.path.exists(file):
                df = self.load_csv(file)
                self.parameter_data[f"experiment_{i}"] = df
                print(f"  ✅ Loaded {file}: {len(df)} rows")
        
        # Load well data
        if os.path.exists(self.data_dir):
            well_files = [f for f in os.listdir(self.data_dir) if f.startswith('well_') and f.endswith('.csv')]
            
            for file in well_files:
                well_id = file.replace('well_', '').replace('_absorbance.csv', '')
                df = self.load_csv(f"{self.data_dir}/{file}")
                
                # Sort by timestamp (oldest first)
                df.sort(key=lambda x: x['timestamp'])
                self.well_data[well_id] = df
                print(f"    Data range: {df[0]['timestamp']} to {df[-1]['timestamp']}")
                print(f"  ✅ Loaded {well_id}: {len(df)} measurements")
                
        print(f"📊 Total wells loaded: {len(self.well_data)}")
        return self.well_data, self.parameter_data
    
    def identify_log_growth_phase(self, data_points):
        """
        Identify the Log Growth phase by finding the steepest exponential growth period
        This is the circled section in your graph - the exponential growth phase
        """
        if len(data_points) < 10:
            return None
        
        # Convert to numeric and filter valid data
        valid_points = []
        for point in data_points:
            try:
                timestamp = datetime.fromisoformat(point['timestamp'].replace('Z', '+00:00'))
                od = float(point['absorbance_od600'])
                if od > 0.05:  # Filter very low noise
                    valid_points.append((timestamp, od))
            except (ValueError, KeyError):
                continue
        
        if len(valid_points) < 10:
            return None
        
        # Sort by time
        valid_points.sort(key=lambda x: x[0])
        
        # Convert to hours from start
        start_time = valid_points[0][0]
        hours_data = []
        od_data = []
        
        for timestamp, od in valid_points:
            hours = (timestamp - start_time).total_seconds() / 3600
            hours_data.append(hours)
            od_data.append(od)
        
        # Find the LOG GROWTH PHASE around OD 0.4 (optimal growth range)
        # This is the exponential growth period in the optimal OD range
        best_log_growth = None
        best_slope = 0
        best_r_squared = 0
        
        # Look for exponential growth windows around OD 0.4
        for window_size in [2, 4, 6, 8, 12]:  # Different window sizes in hours
            window_hours = window_size * 12  # Convert to 5-minute intervals
            
            for i in range(len(hours_data) - window_hours):
                end_idx = i + window_hours
                window_hours_data = hours_data[i:end_idx]
                window_od_data = od_data[i:end_idx]
                
                # Check if this window contains the optimal OD range (around 0.4)
                min_od = min(window_od_data)
                max_od = max(window_od_data)
                avg_od = sum(window_od_data) / len(window_od_data)
                
                # 1. Should contain OD values around 0.4 (optimal range)
                if not (0.2 <= avg_od <= 0.6):  # Focus on OD range 0.2-0.6
                    continue
                
                # 2. Should be increasing overall
                if window_od_data[-1] <= window_od_data[0]:
                    continue
                
                # 3. Should have significant increase (>15% increase)
                increase_ratio = window_od_data[-1] / window_od_data[0]
                if increase_ratio < 1.15:  # Less than 15% increase
                    continue
                
                # 3. Calculate exponential growth slope (log transformation)
                log_od = [math.log(od) for od in window_od_data if od > 0]
                if len(log_od) < 5:
                    continue
                
                # Linear regression on log-transformed data
                n = len(window_hours_data)
                sum_x = sum(window_hours_data)
                sum_y = sum(log_od)
                sum_xy = sum(x * y for x, y in zip(window_hours_data, log_od))
                sum_x2 = sum(x * x for x in window_hours_data)
                
                # Calculate slope and R²
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                
                # R² calculation
                y_mean = sum_y / n
                ss_tot = sum((y - y_mean) ** 2 for y in log_od)
                ss_res = sum((y - (slope * x + (sum_y - slope * sum_x) / n)) ** 2 
                            for x, y in zip(window_hours_data, log_od))
                r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                
                # This is a good LOG GROWTH phase if:
                # - Positive slope (exponential growth)
                # - Good R² (reasonable exponential fit)
                # - Significant growth (at least 15% increase)
                # - OD range around 0.4 (optimal growth range)
                od_score = 1.0 - abs(avg_od - 0.4) / 0.4  # Higher score closer to 0.4
                combined_score = slope * r_squared * od_score
                
                if slope > 0 and r_squared > 0.6 and increase_ratio > 1.15 and combined_score > best_slope:
                    best_slope = slope
                    best_r_squared = r_squared
                    best_log_growth = {
                        'start_hour': window_hours_data[0],
                        'end_hour': window_hours_data[-1],
                        'slope': slope,
                        'r_squared': r_squared,
                        'max_od': max(window_od_data),
                        'min_od': min(window_od_data),
                        'increase_ratio': increase_ratio,
                        'doubling_time': math.log(2) / slope if slope > 0 else None,
                        'phase_type': 'log_growth'
                    }
        
        return best_log_growth
    
    def analyze_log_growth_phases(self):
        """Analyze Log Growth phases for all wells"""
        print("📈 Analyzing LOG GROWTH phases...")
        
        for well_id, data in self.well_data.items():
            print(f"\n  🔍 Analyzing {well_id}...")
            log_growth = self.identify_log_growth_phase(data)
            if log_growth:
                self.log_growth_analysis[well_id] = log_growth
                print(f"  ✅ {well_id}: LOG GROWTH slope={log_growth['slope']:.4f}, R²={log_growth['r_squared']:.3f}, "
                      f"doubling_time={log_growth['doubling_time']:.1f}h, increase={log_growth['increase_ratio']:.1f}x, "
                      f"OD_range={log_growth['min_od']:.3f}-{log_growth['max_od']:.3f}")
            else:
                print(f"  ❌ {well_id}: No clear LOG GROWTH phase detected")
                # Debug: show some data points
                if len(data) > 5:
                    od_values = [float(point['absorbance_od600']) for point in data[:5]]
                    print(f"    Debug: First 5 OD values: {od_values}")
        
        return self.log_growth_analysis
    
    def create_parameter_mapping(self):
        """Map wells to their experimental parameters"""
        print("🔗 Mapping wells to parameters...")
        
        well_to_params = {}
        
        # Experiment 1: A1→A2,B2,C2, B1→D2,E2,F2
        exp1 = self.parameter_data.get('experiment_1', [])
        for row in exp1:
            dest_well = row['destination_well']
            well_to_params[dest_well] = {
                'mix_cycles': int(row['mix_reps']),
                'mix_volume': int(row['mix_volume_uL']),
                'mix_height': 3,  # Default
                'experiment': 1
            }
        
        # Experiment 2: A2→A3,B3,C3, B2→D3,E3,F3
        exp2 = self.parameter_data.get('experiment_2', [])
        for row in exp2:
            dest_well = row['destination_well']
            well_to_params[dest_well] = {
                'mix_cycles': int(row['mix_reps']),
                'mix_volume': int(row['mix_volume_uL']),
                'mix_height': int(row['mix_height_mm']),
                'experiment': 2
            }
        
        # Experiment 3: A2→A3,B3,C3, B2→D3,E3,F3
        exp3 = self.parameter_data.get('experiment_3', [])
        for row in exp3:
            dest_well = row['destination_well']
            well_to_params[dest_well] = {
                'mix_cycles': int(row['mix_reps']),
                'mix_volume': int(row['mix_volume_uL']),
                'mix_height': int(row['mix_height_mm']),
                'experiment': 3
            }
        
        # Experiment 4: A4→A5,B5,C5, B4→D5,E5,F5
        exp4 = self.parameter_data.get('experiment_4', [])
        for row in exp4:
            dest_well = row['destination_well']
            well_to_params[dest_well] = {
                'mix_cycles': int(row['mix_reps']),
                'mix_height': int(row['mix_height_mm']),
                'mix_volume': int(row['mix_volume_uL']),
                'experiment': 4
            }
        
        self.well_to_params = well_to_params
        print(f"  ✅ Mapped {len(well_to_params)} wells to parameters")
        return well_to_params
    
    def optimize_for_log_growth(self):
        """Find optimal parameters for LOG GROWTH phase"""
        print("🎯 Optimizing for LOG GROWTH phase...")
        
        if not self.log_growth_analysis or not hasattr(self, 'well_to_params'):
            print("  ❌ No log growth analysis or parameter mapping available")
            return None
        
        # Create dataset focusing on LOG GROWTH performance
        data_points = []
        for well_id, log_growth_data in self.log_growth_analysis.items():
            if well_id in self.well_to_params:
                params = self.well_to_params[well_id]
                data_points.append({
                    'well_id': well_id,
                    'mix_cycles': params['mix_cycles'],
                    'mix_volume': params['mix_volume'],
                    'mix_height': params['mix_height'],
                    'log_growth_slope': log_growth_data['slope'],
                    'doubling_time': log_growth_data['doubling_time'],
                    'increase_ratio': log_growth_data['increase_ratio'],
                    'r_squared': log_growth_data['r_squared']
                })
        
        if not data_points:
            print("  ❌ No valid log growth data points found")
            return None
        
        # Find best performing wells for LOG GROWTH
        data_points.sort(key=lambda x: x['log_growth_slope'], reverse=True)
        best_wells = data_points[:5]  # Top 5
        
        print("  🏆 Best LOG GROWTH performing wells:")
        for well in best_wells:
            print(f"     {well['well_id']}: slope={well['log_growth_slope']:.4f}, "
                  f"doubling_time={well['doubling_time']:.1f}h, "
                  f"cycles={well['mix_cycles']}, vol={well['mix_volume']}, height={well['mix_height']}")
        
        # Find optimal parameter combination for LOG GROWTH
        param_groups = {}
        for point in data_points:
            key = (point['mix_cycles'], point['mix_volume'], point['mix_height'])
            if key not in param_groups:
                param_groups[key] = []
            param_groups[key].append(point['log_growth_slope'])
        
        # Find best parameter combination
        best_combo = None
        best_avg_slope = 0
        
        for combo, slopes in param_groups.items():
            avg_slope = sum(slopes) / len(slopes)
            if avg_slope > best_avg_slope:
                best_avg_slope = avg_slope
                best_combo = combo
        
        if best_combo:
            optimal_params = {
                'mix_cycles': best_combo[0],
                'mix_volume': best_combo[1],
                'mix_height': best_combo[2],
                'predicted_log_growth_slope': best_avg_slope,
                'predicted_doubling_time': math.log(2) / best_avg_slope if best_avg_slope > 0 else None,
                'confidence': len(param_groups[best_combo]),
                'optimization_target': 'log_growth_phase'
            }
            
            print(f"  ✅ Optimal parameters for LOG GROWTH:")
            print(f"     Mix Cycles: {optimal_params['mix_cycles']}")
            print(f"     Mix Volume: {optimal_params['mix_volume']} μL")
            print(f"     Mix Height: {optimal_params['mix_height']} mm")
            print(f"     Predicted LOG GROWTH Slope: {optimal_params['predicted_log_growth_slope']:.4f}")
            print(f"     Predicted Doubling Time: {optimal_params['predicted_doubling_time']:.1f} hours")
            
            return optimal_params
        
        return None
    
    def generate_optimized_website_data(self):
        """Generate data for website integration focused on LOG GROWTH"""
        print("🌐 Generating LOG GROWTH optimized website data...")
        
        website_data = {
            'best_log_growth_wells': [],
            'parameter_ranges': {
                'mix_cycles': {'min': 1, 'max': 10},
                'mix_volume': {'min': 50, 'max': 150},
                'mix_height': {'min': 1, 'max': 4}
            },
            'log_growth_optimization_results': None,
            'real_data_samples': {}
        }
        
        # Add best LOG GROWTH wells
        if self.log_growth_analysis:
            sorted_wells = sorted(self.log_growth_analysis.items(), 
                                key=lambda x: x[1]['slope'], reverse=True)
            
            for well_id, log_growth_data in sorted_wells[:5]:
                if well_id in self.well_to_params:
                    params = self.well_to_params[well_id]
                    well_info = {
                        'well_id': well_id,
                        'parameters': params,
                        'log_growth_slope': log_growth_data['slope'],
                        'doubling_time': log_growth_data['doubling_time'],
                        'increase_ratio': log_growth_data['increase_ratio'],
                        'r_squared': log_growth_data['r_squared'],
                        'time_range': f"{log_growth_data['start_hour']:.1f}-{log_growth_data['end_hour']:.1f}h",
                        'phase_type': 'log_growth'
                    }
                    website_data['best_log_growth_wells'].append(well_info)
        
        # Add LOG GROWTH optimization results
        optimal_params = self.optimize_for_log_growth()
        if optimal_params:
            website_data['log_growth_optimization_results'] = optimal_params
        
        # Save to JSON
        with open('log_growth_website_data.json', 'w') as f:
            json.dump(website_data, f, indent=2)
        
        print(f"  ✅ Generated LOG GROWTH data for {len(website_data['best_log_growth_wells'])} best wells")
        return website_data
    
    def run_log_growth_optimization(self):
        """Run the complete LOG GROWTH optimization pipeline"""
        print("🚀 Starting LOG GROWTH Phase Optimization...")
        
        # Load data
        self.load_all_data()
        
        # Analyze LOG GROWTH phases
        self.analyze_log_growth_phases()
        
        # Map parameters
        self.create_parameter_mapping()
        
        # Generate optimized website data
        website_data = self.generate_optimized_website_data()
        
        print("✅ LOG GROWTH optimization complete!")
        return website_data

if __name__ == "__main__":
    optimizer = LogGrowthOptimizer()
    results = optimizer.run_log_growth_optimization()
    
    if results:
        print("\n🎯 LOG GROWTH OPTIMIZATION RESULTS:")
        print(f"Best LOG GROWTH wells: {[w['well_id'] for w in results['best_log_growth_wells']]}")
        if results['log_growth_optimization_results']:
            opt = results['log_growth_optimization_results']
            print(f"Optimal parameters: {opt['mix_cycles']} cycles, {opt['mix_volume']}μL, {opt['mix_height']}mm")
            print(f"Predicted LOG GROWTH slope: {opt['predicted_log_growth_slope']:.4f}")
            print(f"Predicted doubling time: {opt['predicted_doubling_time']:.1f} hours")
