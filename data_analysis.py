#!/usr/bin/env python3
"""
Scale Me Maybe - Vibrio natriegens Growth Optimization Analysis
Analyzes experimental data and implements Bayesian optimization for parameter tuning.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import os
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

class VibrioGrowthAnalyzer:
    def __init__(self, data_dir="data/Individual_wells_data", params_dir="passaging_workcell_params"):
        self.data_dir = data_dir
        self.params_dir = params_dir
        self.well_data = {}
        self.parameter_data = {}
        self.slope_analysis = {}
        
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
                df = pd.read_csv(file)
                self.parameter_data[f"experiment_{i}"] = df
                print(f"  ✅ Loaded {file}")
        
        # Load well data
        well_files = [f for f in os.listdir(self.data_dir) if f.startswith('well_') and f.endswith('.csv')]
        
        for file in well_files:
            well_id = file.replace('well_', '').replace('_absorbance.csv', '')
            df = pd.read_csv(f"{self.data_dir}/{file}")
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            self.well_data[well_id] = df
            print(f"  ✅ Loaded {well_id}: {len(df)} measurements")
            
        print(f"📊 Total wells loaded: {len(self.well_data)}")
        return self.well_data, self.parameter_data
    
    def calculate_growth_slopes(self, well_id, time_window_hours=6):
        """Calculate exponential growth slopes for each well"""
        if well_id not in self.well_data:
            return None
            
        df = self.well_data[well_id].copy()
        
        # Convert timestamps to hours from start
        start_time = df['timestamp'].min()
        df['hours'] = (df['timestamp'] - start_time).dt.total_seconds() / 3600
        
        # Find exponential growth phase (avoid initial lag and final stationary)
        # Look for the steepest growth period
        slopes = []
        window_size = time_window_hours
        
        for i in range(len(df) - int(window_size * 12)):  # 12 = 5min intervals per hour
            end_idx = i + int(window_size * 12)
            window_data = df.iloc[i:end_idx]
            
            if len(window_data) < 10:  # Need minimum data points
                continue
                
            # Calculate slope using linear regression on log-transformed data
            x = window_data['hours'].values
            y = window_data['absorbance_od600'].values
            
            # Only use positive values for log transformation
            valid_mask = y > 0.1  # Avoid noise at low concentrations
            if np.sum(valid_mask) < 5:
                continue
                
            x_valid = x[valid_mask]
            y_valid = y[valid_mask]
            
            # Log transform for exponential growth analysis
            log_y = np.log(y_valid)
            
            # Linear regression on log-transformed data
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_valid, log_y)
            
            slopes.append({
                'start_hour': x_valid[0],
                'end_hour': x_valid[-1],
                'slope': slope,
                'r_squared': r_value**2,
                'p_value': p_value,
                'max_od': y_valid.max(),
                'min_od': y_valid.min()
            })
        
        # Find the best slope (highest with good R²)
        if slopes:
            # Filter for reasonable slopes (positive growth) and good fit
            valid_slopes = [s for s in slopes if s['slope'] > 0 and s['r_squared'] > 0.8]
            
            if valid_slopes:
                best_slope = max(valid_slopes, key=lambda x: x['slope'])
                self.slope_analysis[well_id] = best_slope
                return best_slope
        
        return None
    
    def analyze_all_slopes(self):
        """Calculate slopes for all wells"""
        print("📈 Calculating growth slopes...")
        
        for well_id in self.well_data.keys():
            slope_data = self.calculate_growth_slopes(well_id)
            if slope_data:
                print(f"  ✅ {well_id}: slope={slope_data['slope']:.4f}, R²={slope_data['r_squared']:.3f}")
            else:
                print(f"  ❌ {well_id}: No valid exponential growth detected")
        
        return self.slope_analysis
    
    def create_parameter_mapping(self):
        """Map wells to their experimental parameters"""
        print("🔗 Mapping wells to parameters...")
        
        well_to_params = {}
        
        # Experiment 1: A1→A2,B2,C2, B1→D2,E2,F2
        exp1 = self.parameter_data.get('experiment_1', pd.DataFrame())
        if not exp1.empty:
            for _, row in exp1.iterrows():
                dest_well = row['destination_well']
                well_to_params[dest_well] = {
                    'mix_cycles': row['mix_reps'],
                    'mix_volume': row['mix_volume_uL'],
                    'mix_height': 3,  # Default from original
                    'experiment': 1
                }
        
        # Experiment 2: A2→A3,B3,C3, B2→D3,E3,F3
        exp2 = self.parameter_data.get('experiment_2', pd.DataFrame())
        if not exp2.empty:
            for _, row in exp2.iterrows():
                dest_well = row['destination_well']
                well_to_params[dest_well] = {
                    'mix_cycles': row['mix_reps'],
                    'mix_volume': row['mix_volume_uL'],
                    'mix_height': row['mix_height_mm'],
                    'experiment': 2
                }
        
        # Experiment 3: A2→A3,B3,C3, B2→D3,E3,F3 (different mix cycles)
        exp3 = self.parameter_data.get('experiment_3', pd.DataFrame())
        if not exp3.empty:
            for _, row in exp3.iterrows():
                dest_well = row['destination_well']
                well_to_params[dest_well] = {
                    'mix_cycles': row['mix_reps'],
                    'mix_volume': row['mix_volume_uL'],
                    'mix_height': row['mix_height_mm'],
                    'experiment': 3
                }
        
        # Experiment 4: A4→A5,B5,C5, B4→D5,E5,F5
        exp4 = self.parameter_data.get('experiment_4', pd.DataFrame())
        if not exp4.empty:
            for _, row in exp4.iterrows():
                dest_well = row['destination_well']
                well_to_params[dest_well] = {
                    'mix_cycles': row['mix_reps'],
                    'mix_volume': row['mix_volume_uL'],
                    'mix_height': row['mix_height_mm'],
                    'experiment': 4
                }
        
        self.well_to_params = well_to_params
        print(f"  ✅ Mapped {len(well_to_params)} wells to parameters")
        return well_to_params
    
    def create_optimization_dataset(self):
        """Create dataset for ML optimization"""
        print("🤖 Creating optimization dataset...")
        
        data_rows = []
        
        for well_id, slope_data in self.slope_analysis.items():
            if well_id in self.well_to_params:
                params = self.well_to_params[well_id]
                
                data_rows.append({
                    'well_id': well_id,
                    'mix_cycles': params['mix_cycles'],
                    'mix_volume': params['mix_volume'],
                    'mix_height': params['mix_height'],
                    'experiment': params['experiment'],
                    'growth_slope': slope_data['slope'],
                    'r_squared': slope_data['r_squared'],
                    'max_od': slope_data['max_od'],
                    'min_od': slope_data['min_od']
                })
        
        self.optimization_df = pd.DataFrame(data_rows)
        print(f"  ✅ Created dataset with {len(self.optimization_df)} samples")
        return self.optimization_df
    
    def train_optimization_model(self):
        """Train ML model for parameter optimization"""
        print("🧠 Training optimization model...")
        
        if len(self.optimization_df) < 3:
            print("  ❌ Not enough data for training")
            return None
        
        # Prepare features and target
        X = self.optimization_df[['mix_cycles', 'mix_volume', 'mix_height']]
        y = self.optimization_df['growth_slope']
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Train Random Forest model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        
        print(f"  ✅ Model trained - R²: {r2:.3f}, MSE: {mse:.4f}")
        
        # Feature importance
        feature_importance = dict(zip(X.columns, self.model.feature_importances_))
        print(f"  📊 Feature importance: {feature_importance}")
        
        return self.model
    
    def optimize_parameters(self, n_iterations=100):
        """Use Bayesian optimization to find optimal parameters"""
        print("🎯 Running Bayesian optimization...")
        
        if not hasattr(self, 'model'):
            print("  ❌ No trained model available")
            return None
        
        # Define parameter bounds based on experimental ranges
        param_bounds = {
            'mix_cycles': (1, 10),
            'mix_volume': (50, 150),
            'mix_height': (1, 4)
        }
        
        best_params = None
        best_score = -np.inf
        
        # Simple grid search optimization (can be replaced with Bayesian optimization)
        for mix_cycles in np.linspace(param_bounds['mix_cycles'][0], param_bounds['mix_cycles'][1], 10):
            for mix_volume in np.linspace(param_bounds['mix_volume'][0], param_bounds['mix_volume'][1], 10):
                for mix_height in np.linspace(param_bounds['mix_height'][0], param_bounds['mix_height'][1], 4):
                    
                    # Predict growth slope
                    X_test = np.array([[mix_cycles, mix_volume, mix_height]])
                    predicted_slope = self.model.predict(X_test)[0]
                    
                    if predicted_slope > best_score:
                        best_score = predicted_slope
                        best_params = {
                            'mix_cycles': int(mix_cycles),
                            'mix_volume': int(mix_volume),
                            'mix_height': int(mix_height),
                            'predicted_slope': predicted_slope
                        }
        
        print(f"  ✅ Optimal parameters found:")
        print(f"     Mix Cycles: {best_params['mix_cycles']}")
        print(f"     Mix Volume: {best_params['mix_volume']} μL")
        print(f"     Mix Height: {best_params['mix_height']} mm")
        print(f"     Predicted Slope: {best_params['predicted_slope']:.4f}")
        
        return best_params
    
    def generate_website_data(self):
        """Generate data for website integration"""
        print("🌐 Generating website data...")
        
        # Find best performing wells
        if self.slope_analysis:
            best_wells = sorted(self.slope_analysis.items(), 
                              key=lambda x: x[1]['slope'], reverse=True)[:3]
            
            website_data = {
                'best_wells': [],
                'parameter_ranges': {
                    'mix_cycles': {'min': 1, 'max': 10},
                    'mix_volume': {'min': 50, 'max': 150},
                    'mix_height': {'min': 1, 'max': 4}
                },
                'optimization_results': None
            }
            
            for well_id, slope_data in best_wells:
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
            
            # Add optimization results if available
            if hasattr(self, 'model'):
                optimal_params = self.optimize_parameters()
                website_data['optimization_results'] = optimal_params
            
            # Save to JSON for website
            with open('website_data.json', 'w') as f:
                json.dump(website_data, f, indent=2)
            
            print(f"  ✅ Generated data for {len(website_data['best_wells'])} best wells")
            return website_data
        
        return None
    
    def run_complete_analysis(self):
        """Run the complete analysis pipeline"""
        print("🚀 Starting Scale Me Maybe Analysis...")
        
        # Load data
        self.load_all_data()
        
        # Analyze slopes
        self.analyze_all_slopes()
        
        # Map parameters
        self.create_parameter_mapping()
        
        # Create optimization dataset
        self.create_optimization_dataset()
        
        # Train model
        self.train_optimization_model()
        
        # Generate website data
        website_data = self.generate_website_data()
        
        print("✅ Analysis complete!")
        return website_data

if __name__ == "__main__":
    analyzer = VibrioGrowthAnalyzer()
    results = analyzer.run_complete_analysis()
    
    if results:
        print("\n🎯 KEY FINDINGS:")
        print(f"Best performing wells: {[w['well_id'] for w in results['best_wells']]}")
        if results['optimization_results']:
            opt = results['optimization_results']
            print(f"Optimal parameters: {opt['mix_cycles']} cycles, {opt['mix_volume']}μL, {opt['mix_height']}mm")
