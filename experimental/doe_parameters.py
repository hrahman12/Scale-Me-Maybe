"""
DOE Parameters for 96-Well Plate Experiment
First cycle: 12 wells (A1-A12) with 20μL cells + 180μL media
Future cycles: Can expand to full 96-well plate
"""

# First cycle: 12 wells (A1-A12) with standard parameters
# 20μL cells + 180μL media = 200μL total volume
DOE_PARAMETERS = {
    # First cycle: Row A (A1-A12) - Standard parameters for all wells
    # 20μL cells + 180μL media = 200μL total volume
    "A1": {"mix_reps": 5, "mix_volume": 100, "mix_height_mm": 2.5, "seed_volume": 20, "media_volume": 180},
    "A2": {"mix_reps": 5, "mix_volume": 100, "mix_height_mm": 2.5, "seed_volume": 20, "media_volume": 180},
    "A3": {"mix_reps": 5, "mix_volume": 100, "mix_height_mm": 2.5, "seed_volume": 20, "media_volume": 180},
    "A4": {"mix_reps": 5, "mix_volume": 100, "mix_height_mm": 2.5, "seed_volume": 20, "media_volume": 180},
    "A5": {"mix_reps": 5, "mix_volume": 100, "mix_height_mm": 2.5, "seed_volume": 20, "media_volume": 180},
    "A6": {"mix_reps": 5, "mix_volume": 100, "mix_height_mm": 2.5, "seed_volume": 20, "media_volume": 180},
    "A7": {"mix_reps": 5, "mix_volume": 100, "mix_height_mm": 2.5, "seed_volume": 20, "media_volume": 180},
    "A8": {"mix_reps": 5, "mix_volume": 100, "mix_height_mm": 2.5, "seed_volume": 20, "media_volume": 180},
    "A9": {"mix_reps": 5, "mix_volume": 100, "mix_height_mm": 2.5, "seed_volume": 20, "media_volume": 180},
    "A10": {"mix_reps": 5, "mix_volume": 100, "mix_height_mm": 2.5, "seed_volume": 20, "media_volume": 180},
    "A11": {"mix_reps": 5, "mix_volume": 100, "mix_height_mm": 2.5, "seed_volume": 20, "media_volume": 180},
    "A12": {"mix_reps": 5, "mix_volume": 100, "mix_height_mm": 2.5, "seed_volume": 20, "media_volume": 180}
    
    # Future cycles can expand to include more wells with different parameters
    # For now, we focus on the first 12 wells (A1-A12)
}

# Helper function to get parameters for a specific well
def get_well_parameters(well_id):
    """Get DOE parameters for a specific well"""
    return DOE_PARAMETERS.get(well_id, {
        "mix_reps": 5, 
        "mix_volume": 100, 
        "mix_height_mm": 2.5, 
        "seed_volume": 20,
        "media_volume": 180
    })

# Helper function to get all well IDs (first cycle: 12 wells)
def get_all_well_ids():
    """Get list of all well IDs for the first cycle"""
    return list(DOE_PARAMETERS.keys())

# Helper function to get parameters for multiple wells
def get_wells_parameters(well_ids):
    """Get parameters for multiple wells"""
    return {well_id: get_well_parameters(well_id) for well_id in well_ids}

# Helper function to get first cycle wells (A1-A12)
def get_first_cycle_wells():
    """Get the 12 wells for the first cycle"""
    return ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12"]