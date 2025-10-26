#!/usr/bin/env python3
"""
Scale Me Maybe - Vibrio natriegens Growth Optimization Analysis
Simplified analysis using only standard library for hackathon speed.
"""

import csv
import json
import os
from datetime import datetime
import math

class SimpleVibrioAnalyzer:
    def __init__(self, data_dir="data/Individual_wells_data", params_dir="passaging_workcell_params"):
        self.data_dir = data_dir
        self.params_dir = params_dir
        self.well_data = {}
        self.parameter_data = {}
        self.slope_analysis = {}
        
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
                
                # Sort by timestamp
                df.sort(key=lambda x: x['timestamp'])
                self.well_data[well_id] = df
                print(f"  ✅ Loaded {well_id}: {len(df)} measurements")
                
        print(f"📊 Total wells loaded: {len(self.well_data)}")
        return self.well_data, self.parameter_data
    
    def calculate_simple_slope(self, data_points, time_window_hours=6):
        """Calculate slope using simple linear regression"""
        if len(data_points) < 5:
            return None
        
        # Convert to numeric and filter valid data
        valid_points = []
        for point in data_points:
            try:
                timestamp = datetime.fromisoformat(point['timestamp'].replace('Z', '+00:00'))
                od = float(point['absorbance_od600'])
                if od > 0.1:  # Filter noise
                    valid_points.append((timestamp, od))
            except (ValueError, KeyError):
                continue
        
        if len(valid_points) < 5:
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
        
        # Find best exponential growth window (Log Growth phase)
        best_slope = 0
        best_r_squared = 0
        best_window = None
        
        window_size = min(time_window_hours * 12, len(hours_data) // 2)  # 5min intervals
        
        for i in range(len(hours_data) - window_size):
            end_idx = i + window_size
            window_hours = hours_data[i:end_idx]
            window_od = od_data[i:end_idx]
            
            # Log transform for exponential growth (Log Growth phase)
            log_od = [math.log(od) for od in window_od if od > 0]
            if len(log_od) < 5:
                continue
            
            # Simple linear regression
            n = len(window_hours)
            sum_x = sum(window_hours)
            sum_y = sum(log_od)
            sum_xy = sum(x * y for x, y in zip(window_hours, log_od))
            sum_x2 = sum(x * x for x in window_hours)
            sum_y2 = sum(y * y for y in log_od)
            
            # Calculate slope and R²
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # R² calculation
            y_mean = sum_y / n
            ss_tot = sum((y - y_mean) ** 2 for y in log_od)
            ss_res = sum((y - (slope * x + (sum_y - slope * sum_x) / n)) ** 2 
                        for x, y in zip(window_hours, log_od))
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            if slope > best_slope and r_squared > 0.7:
                best_slope = slope
                best_r_squared = r_squared
                best_window = {
                    'start_hour': window_hours[0],
                    'end_hour': window_hours[-1],
                    'slope': slope,
                    'r_squared': r_squared,
                    'max_od': max(window_od),
                    'min_od': min(window_od)
                }
        
        return best_window
    
    def analyze_all_slopes(self):
        """Calculate slopes for all wells"""
        print("📈 Calculating growth slopes...")
        
        for well_id, data in self.well_data.items():
            slope_data = self.calculate_simple_slope(data)
            if slope_data:
                self.slope_analysis[well_id] = slope_data
                print(f"  ✅ {well_id}: slope={slope_data['slope']:.4f}, R²={slope_data['r_squared']:.3f}")
            else:
                print(f"  ❌ {well_id}: No valid exponential growth detected")
        
        return self.slope_analysis
    
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
    
    def find_optimal_parameters(self):
        """Find optimal parameters using simple analysis"""
        print("🎯 Finding optimal parameters...")
        
        if not self.slope_analysis or not hasattr(self, 'well_to_params'):
            print("  ❌ No slope analysis or parameter mapping available")
            return None
        
        # Create dataset
        data_points = []
        for well_id, slope_data in self.slope_analysis.items():
            if well_id in self.well_to_params:
                params = self.well_to_params[well_id]
                data_points.append({
                    'well_id': well_id,
                    'mix_cycles': params['mix_cycles'],
                    'mix_volume': params['mix_volume'],
                    'mix_height': params['mix_height'],
                    'slope': slope_data['slope'],
                    'r_squared': slope_data['r_squared']
                })
        
        if not data_points:
            print("  ❌ No valid data points found")
            return None
        
        # Find best performing wells
        data_points.sort(key=lambda x: x['slope'], reverse=True)
        best_wells = data_points[:3]
        
        print("  🏆 Best performing wells:")
        for well in best_wells:
            print(f"     {well['well_id']}: slope={well['slope']:.4f}, "
                  f"cycles={well['mix_cycles']}, vol={well['mix_volume']}, height={well['mix_height']}")
        
        # Simple optimization: find parameter combinations that work well
        # Group by parameter combinations
        param_groups = {}
        for point in data_points:
            key = (point['mix_cycles'], point['mix_volume'], point['mix_height'])
            if key not in param_groups:
                param_groups[key] = []
            param_groups[key].append(point['slope'])
        
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
                'predicted_slope': best_avg_slope,
                'confidence': len(param_groups[best_combo])
            }
            
            print(f"  ✅ Optimal parameters:")
            print(f"     Mix Cycles: {optimal_params['mix_cycles']}")
            print(f"     Mix Volume: {optimal_params['mix_volume']} μL")
            print(f"     Mix Height: {optimal_params['mix_height']} mm")
            print(f"     Predicted Slope: {optimal_params['predicted_slope']:.4f}")
            
            return optimal_params
        
        return None
    
    def generate_website_data(self):
        """Generate data for website integration"""
        print("🌐 Generating website data...")
        
        website_data = {
            'best_wells': [],
            'parameter_ranges': {
                'mix_cycles': {'min': 1, 'max': 10},
                'mix_volume': {'min': 50, 'max': 150},
                'mix_height': {'min': 1, 'max': 4}
            },
            'optimization_results': None,
            'real_data_samples': {}
        }
        
        # Add best wells
        if self.slope_analysis:
            sorted_wells = sorted(self.slope_analysis.items(), 
                                key=lambda x: x[1]['slope'], reverse=True)
            
            for well_id, slope_data in sorted_wells[:3]:
                if well_id in self.well_to_params:
                    params = self.well_to_params[well_id]
                    well_info = {
                        'well_id': well_id,
                        'parameters': params,
                        'growth_slope': slope_data['slope'],
                        'r_squared': slope_data['r_squared'],
                        'time_range': f"{slope_data['start_hour']:.1f}-{slope_data['end_hour']:.1f}h"
                    }
                    website_data['best_wells'].append(well_info)
        
        # Add optimization results
        optimal_params = self.find_optimal_parameters()
        if optimal_params:
            website_data['optimization_results'] = optimal_params
        
        # Add sample real data for website
        for well_id, data in list(self.well_data.items())[:2]:  # First 2 wells
            sample_data = []
            for i, point in enumerate(data[::5]):  # Every 5th point
                try:
                    timestamp = datetime.fromisoformat(point['timestamp'].replace('Z', '+00:00'))
                    od = float(point['absorbance_od600'])
                    sample_data.append({
                        'time': i * 5,  # Minutes
                        'absorbance': od
                    })
                except (ValueError, KeyError):
                    continue
            
            website_data['real_data_samples'][well_id] = sample_data[:20]  # First 20 points
        
        # Save to JSON
        with open('website_data.json', 'w') as f:
            json.dump(website_data, f, indent=2)
        
        print(f"  ✅ Generated data for {len(website_data['best_wells'])} best wells")
        return website_data
    
    def run_complete_analysis(self):
        """Run the complete analysis pipeline"""
        print("🚀 Starting Scale Me Maybe Analysis...")
        
        # Load data
        self.load_all_data()
        
        # Analyze slopes
        self.analyze_all_slopes()
        
        # Map parameters
        self.create_parameter_mapping()
        
        # Generate website data
        website_data = self.generate_website_data()
        
        print("✅ Analysis complete!")
        return website_data

if __name__ == "__main__":
    analyzer = SimpleVibrioAnalyzer()
    results = analyzer.run_complete_analysis()
    
    if results:
        print("\n🎯 KEY FINDINGS:")
        print(f"Best performing wells: {[w['well_id'] for w in results['best_wells']]}")
        if results['optimization_results']:
            opt = results['optimization_results']
            print(f"Optimal parameters: {opt['mix_cycles']} cycles, {opt['mix_volume']}μL, {opt['mix_height']}mm")
            print(f"Predicted slope: {opt['predicted_slope']:.4f}")
