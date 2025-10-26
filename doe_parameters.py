"""
DOE Parameters for 96-Well Plate Experiment
Each well gets a unique combination of passage parameters
"""

# 96 different parameter combinations (one per well)
DOE_PARAMETERS = {
    # Row A (A1-A12)
    "A1": {"mix_reps": 3, "mix_volume": 80, "mix_height_mm": 1.5, "seed_volume": 30},
    "A2": {"mix_reps": 4, "mix_volume": 90, "mix_height_mm": 1.8, "seed_volume": 35},
    "A3": {"mix_reps": 5, "mix_volume": 100, "mix_height_mm": 2.0, "seed_volume": 40},
    "A4": {"mix_reps": 6, "mix_volume": 110, "mix_height_mm": 2.2, "seed_volume": 45},
    "A5": {"mix_reps": 7, "mix_volume": 120, "mix_height_mm": 2.5, "seed_volume": 50},
    "A6": {"mix_reps": 8, "mix_volume": 130, "mix_height_mm": 2.8, "seed_volume": 55},
    "A7": {"mix_reps": 3, "mix_volume": 140, "mix_height_mm": 3.0, "seed_volume": 60},
    "A8": {"mix_reps": 4, "mix_volume": 150, "mix_height_mm": 3.2, "seed_volume": 65},
    "A9": {"mix_reps": 5, "mix_volume": 160, "mix_height_mm": 3.5, "seed_volume": 70},
    "A10": {"mix_reps": 6, "mix_volume": 170, "mix_height_mm": 3.8, "seed_volume": 75},
    "A11": {"mix_reps": 7, "mix_volume": 180, "mix_height_mm": 4.0, "seed_volume": 80},
    "A12": {"mix_reps": 8, "mix_volume": 190, "mix_height_mm": 4.2, "seed_volume": 85},
    
    # Row B (B1-B12)
    "B1": {"mix_reps": 4, "mix_volume": 85, "mix_height_mm": 1.6, "seed_volume": 32},
    "B2": {"mix_reps": 5, "mix_volume": 95, "mix_height_mm": 1.9, "seed_volume": 37},
    "B3": {"mix_reps": 6, "mix_volume": 105, "mix_height_mm": 2.1, "seed_volume": 42},
    "B4": {"mix_reps": 7, "mix_volume": 115, "mix_height_mm": 2.3, "seed_volume": 47},
    "B5": {"mix_reps": 8, "mix_volume": 125, "mix_height_mm": 2.6, "seed_volume": 52},
    "B6": {"mix_reps": 3, "mix_volume": 135, "mix_height_mm": 2.9, "seed_volume": 57},
    "B7": {"mix_reps": 4, "mix_volume": 145, "mix_height_mm": 3.1, "seed_volume": 62},
    "B8": {"mix_reps": 5, "mix_volume": 155, "mix_height_mm": 3.3, "seed_volume": 67},
    "B9": {"mix_reps": 6, "mix_volume": 165, "mix_height_mm": 3.6, "seed_volume": 72},
    "B10": {"mix_reps": 7, "mix_volume": 175, "mix_height_mm": 3.9, "seed_volume": 77},
    "B11": {"mix_reps": 8, "mix_volume": 185, "mix_height_mm": 4.1, "seed_volume": 82},
    "B12": {"mix_reps": 3, "mix_volume": 195, "mix_height_mm": 4.3, "seed_volume": 87},
    
    # Row C (C1-C12)
    "C1": {"mix_reps": 5, "mix_volume": 88, "mix_height_mm": 1.7, "seed_volume": 33},
    "C2": {"mix_reps": 6, "mix_volume": 98, "mix_height_mm": 2.0, "seed_volume": 38},
    "C3": {"mix_reps": 7, "mix_volume": 108, "mix_height_mm": 2.2, "seed_volume": 43},
    "C4": {"mix_reps": 8, "mix_volume": 118, "mix_height_mm": 2.4, "seed_volume": 48},
    "C5": {"mix_reps": 3, "mix_volume": 128, "mix_height_mm": 2.7, "seed_volume": 53},
    "C6": {"mix_reps": 4, "mix_volume": 138, "mix_height_mm": 3.0, "seed_volume": 58},
    "C7": {"mix_reps": 5, "mix_volume": 148, "mix_height_mm": 3.2, "seed_volume": 63},
    "C8": {"mix_reps": 6, "mix_volume": 158, "mix_height_mm": 3.4, "seed_volume": 68},
    "C9": {"mix_reps": 7, "mix_volume": 168, "mix_height_mm": 3.7, "seed_volume": 73},
    "C10": {"mix_reps": 8, "mix_volume": 178, "mix_height_mm": 4.0, "seed_volume": 78},
    "C11": {"mix_reps": 3, "mix_volume": 188, "mix_height_mm": 4.2, "seed_volume": 83},
    "C12": {"mix_reps": 4, "mix_volume": 198, "mix_height_mm": 4.4, "seed_volume": 88},
    
    # Row D (D1-D12)
    "D1": {"mix_reps": 6, "mix_volume": 92, "mix_height_mm": 1.8, "seed_volume": 34},
    "D2": {"mix_reps": 7, "mix_volume": 102, "mix_height_mm": 2.1, "seed_volume": 39},
    "D3": {"mix_reps": 8, "mix_volume": 112, "mix_height_mm": 2.3, "seed_volume": 44},
    "D4": {"mix_reps": 3, "mix_volume": 122, "mix_height_mm": 2.5, "seed_volume": 49},
    "D5": {"mix_reps": 4, "mix_volume": 132, "mix_height_mm": 2.8, "seed_volume": 54},
    "D6": {"mix_reps": 5, "mix_volume": 142, "mix_height_mm": 3.1, "seed_volume": 59},
    "D7": {"mix_reps": 6, "mix_volume": 152, "mix_height_mm": 3.3, "seed_volume": 64},
    "D8": {"mix_reps": 7, "mix_volume": 162, "mix_height_mm": 3.5, "seed_volume": 69},
    "D9": {"mix_reps": 8, "mix_volume": 172, "mix_height_mm": 3.8, "seed_volume": 74},
    "D10": {"mix_reps": 3, "mix_volume": 182, "mix_height_mm": 4.1, "seed_volume": 79},
    "D11": {"mix_reps": 4, "mix_volume": 192, "mix_height_mm": 4.3, "seed_volume": 84},
    "D12": {"mix_reps": 5, "mix_volume": 200, "mix_height_mm": 4.5, "seed_volume": 89},
    
    # Row E (E1-E12)
    "E1": {"mix_reps": 7, "mix_volume": 95, "mix_height_mm": 1.9, "seed_volume": 35},
    "E2": {"mix_reps": 8, "mix_volume": 105, "mix_height_mm": 2.2, "seed_volume": 40},
    "E3": {"mix_reps": 3, "mix_volume": 115, "mix_height_mm": 2.4, "seed_volume": 45},
    "E4": {"mix_reps": 4, "mix_volume": 125, "mix_height_mm": 2.6, "seed_volume": 50},
    "E5": {"mix_reps": 5, "mix_volume": 135, "mix_height_mm": 2.9, "seed_volume": 55},
    "E6": {"mix_reps": 6, "mix_volume": 145, "mix_height_mm": 3.2, "seed_volume": 60},
    "E7": {"mix_reps": 7, "mix_volume": 155, "mix_height_mm": 3.4, "seed_volume": 65},
    "E8": {"mix_reps": 8, "mix_volume": 165, "mix_height_mm": 3.6, "seed_volume": 70},
    "E9": {"mix_reps": 3, "mix_volume": 175, "mix_height_mm": 3.9, "seed_volume": 75},
    "E10": {"mix_reps": 4, "mix_volume": 185, "mix_height_mm": 4.2, "seed_volume": 80},
    "E11": {"mix_reps": 5, "mix_volume": 195, "mix_height_mm": 4.4, "seed_volume": 85},
    "E12": {"mix_reps": 6, "mix_volume": 200, "mix_height_mm": 4.6, "seed_volume": 90},
    
    # Row F (F1-F12)
    "F1": {"mix_reps": 8, "mix_volume": 98, "mix_height_mm": 2.0, "seed_volume": 36},
    "F2": {"mix_reps": 3, "mix_volume": 108, "mix_height_mm": 2.3, "seed_volume": 41},
    "F3": {"mix_reps": 4, "mix_volume": 118, "mix_height_mm": 2.5, "seed_volume": 46},
    "F4": {"mix_reps": 5, "mix_volume": 128, "mix_height_mm": 2.7, "seed_volume": 51},
    "F5": {"mix_reps": 6, "mix_volume": 138, "mix_height_mm": 3.0, "seed_volume": 56},
    "F6": {"mix_reps": 7, "mix_volume": 148, "mix_height_mm": 3.3, "seed_volume": 61},
    "F7": {"mix_reps": 8, "mix_volume": 158, "mix_height_mm": 3.5, "seed_volume": 66},
    "F8": {"mix_reps": 3, "mix_volume": 168, "mix_height_mm": 3.7, "seed_volume": 71},
    "F9": {"mix_reps": 4, "mix_volume": 178, "mix_height_mm": 4.0, "seed_volume": 76},
    "F10": {"mix_reps": 5, "mix_volume": 188, "mix_height_mm": 4.3, "seed_volume": 81},
    "F11": {"mix_reps": 6, "mix_volume": 198, "mix_height_mm": 4.5, "seed_volume": 86},
    "F12": {"mix_reps": 7, "mix_volume": 200, "mix_height_mm": 4.7, "seed_volume": 91},
    
    # Row G (G1-G12)
    "G1": {"mix_reps": 3, "mix_volume": 102, "mix_height_mm": 2.1, "seed_volume": 37},
    "G2": {"mix_reps": 4, "mix_volume": 112, "mix_height_mm": 2.4, "seed_volume": 42},
    "G3": {"mix_reps": 5, "mix_volume": 122, "mix_height_mm": 2.6, "seed_volume": 47},
    "G4": {"mix_reps": 6, "mix_volume": 132, "mix_height_mm": 2.8, "seed_volume": 52},
    "G5": {"mix_reps": 7, "mix_volume": 142, "mix_height_mm": 3.1, "seed_volume": 57},
    "G6": {"mix_reps": 8, "mix_volume": 152, "mix_height_mm": 3.4, "seed_volume": 62},
    "G7": {"mix_reps": 3, "mix_volume": 162, "mix_height_mm": 3.6, "seed_volume": 67},
    "G8": {"mix_reps": 4, "mix_volume": 172, "mix_height_mm": 3.8, "seed_volume": 72},
    "G9": {"mix_reps": 5, "mix_volume": 182, "mix_height_mm": 4.1, "seed_volume": 77},
    "G10": {"mix_reps": 6, "mix_volume": 192, "mix_height_mm": 4.4, "seed_volume": 82},
    "G11": {"mix_reps": 7, "mix_volume": 200, "mix_height_mm": 4.6, "seed_volume": 87},
    "G12": {"mix_reps": 8, "mix_volume": 200, "mix_height_mm": 4.8, "seed_volume": 92},
    
    # Row H (H1-H12)
    "H1": {"mix_reps": 4, "mix_volume": 105, "mix_height_mm": 2.2, "seed_volume": 38},
    "H2": {"mix_reps": 5, "mix_volume": 115, "mix_height_mm": 2.5, "seed_volume": 43},
    "H3": {"mix_reps": 6, "mix_volume": 125, "mix_height_mm": 2.7, "seed_volume": 48},
    "H4": {"mix_reps": 7, "mix_volume": 135, "mix_height_mm": 2.9, "seed_volume": 53},
    "H5": {"mix_reps": 8, "mix_volume": 145, "mix_height_mm": 3.2, "seed_volume": 58},
    "H6": {"mix_reps": 3, "mix_volume": 155, "mix_height_mm": 3.5, "seed_volume": 63},
    "H7": {"mix_reps": 4, "mix_volume": 165, "mix_height_mm": 3.7, "seed_volume": 68},
    "H8": {"mix_reps": 5, "mix_volume": 175, "mix_height_mm": 3.9, "seed_volume": 73},
    "H9": {"mix_reps": 6, "mix_volume": 185, "mix_height_mm": 4.2, "seed_volume": 78},
    "H10": {"mix_reps": 7, "mix_volume": 195, "mix_height_mm": 4.5, "seed_volume": 83},
    "H11": {"mix_reps": 8, "mix_volume": 200, "mix_height_mm": 4.7, "seed_volume": 88},
    "H12": {"mix_reps": 3, "mix_volume": 200, "mix_height_mm": 4.9, "seed_volume": 93}
}

# Helper function to get parameters for a specific well
def get_well_parameters(well_id):
    """Get DOE parameters for a specific well"""
    return DOE_PARAMETERS.get(well_id, {
        "mix_reps": 5, 
        "mix_volume": 120, 
        "mix_height_mm": 2.5, 
        "seed_volume": 50
    })

# Helper function to get all well IDs
def get_all_well_ids():
    """Get list of all 96 well IDs"""
    return list(DOE_PARAMETERS.keys())

# Helper function to get parameters for multiple wells
def get_wells_parameters(well_ids):
    """Get parameters for multiple wells"""
    return {well_id: get_well_parameters(well_id) for well_id in well_ids}
