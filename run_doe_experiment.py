"""
DOE Experiment Execution Script
Runs 96-well parameter testing with 10-minute OD600 monitoring
"""

import asyncio
import sys
import os

# Add the current directory to the path to import the parameter file
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from doe_parameters import get_well_parameters, get_all_well_ids, get_wells_parameters

async def run_doe_experiment():
    """
    Execute the DOE experiment with 96 different parameter combinations
    """
    
    print("🧪 Starting DOE Experiment: 96-Well Parameter Testing")
    print("=" * 60)
    
    # Step 1: Check available plates
    print("🔍 Checking available plates...")
    try:
        available_plates = await list_culture_plates(is_checked_in=True, exclude_in_workflows=True)
        
        if not available_plates:
            print("❌ No plates available. Please check in a plate first.")
            return None
        
        plate_barcode = available_plates[0]["barcode"]
        print(f"✅ Using plate: {plate_barcode}")
        
    except Exception as e:
        print(f"❌ Error checking plates: {e}")
        return None
    
    # Step 2: Check plate availability
    print("🔍 Checking plate availability...")
    try:
        plate_status = await check_plate_availability(plate_barcode)
        if not plate_status.is_available:
            print(f"❌ Plate not available: {plate_status.reason}")
            return None
        print(f"✅ Plate {plate_barcode} is available")
        
    except Exception as e:
        print(f"❌ Error checking plate availability: {e}")
        return None
    
    # Step 3: Display parameter information
    print("\n📊 Parameter Configuration:")
    print("-" * 40)
    all_wells = get_all_well_ids()
    print(f"Total wells: {len(all_wells)}")
    print(f"Parameter combinations: {len(all_wells)}")
    print(f"Monitoring frequency: Every 10 minutes")
    print(f"Experiment duration: 24+ hours")
    
    # Show sample parameters
    print("\n🔬 Sample Parameters (first 5 wells):")
    for well_id in all_wells[:5]:
        params = get_well_parameters(well_id)
        print(f"  {well_id}: Mix reps={params['mix_reps']}, Volume={params['mix_volume']}μL, Height={params['mix_height_mm']}mm, Seed={params['seed_volume']}μL")
    
    # Step 4: Execute the workflow
    print(f"\n🚀 Starting workflow execution...")
    try:
        result = await instantiate_workflow(
            definition_id=11,  # DOE 96-Well Continuous Growth Monitoring workflow
            inputs={"plate_barcode": plate_barcode},
            start_after_minutes=0,  # Start immediately after approval
            reason=f"DOE Experiment: 96-well continuous growth monitoring with 10-minute OD600 readings on plate {plate_barcode}"
        )
        
        print(f"✅ Workflow created successfully!")
        print(f"📋 Workflow UUID: {result.uuid}")
        print(f"📊 Status: {result.status}")
        print(f"⏳ Requires operator approval: {result.requires_approval}")
        
        if result.requires_approval:
            print("\n⚠️  IMPORTANT: This workflow requires operator approval before execution.")
            print("   Please check the Workflow Instances UI to approve the workflow.")
        
        return result
        
    except Exception as e:
        print(f"❌ Error creating workflow: {e}")
        return None

async def monitor_experiment(workflow_uuid):
    """
    Monitor the progress of the DOE experiment
    """
    print(f"\n📈 Monitoring experiment: {workflow_uuid}")
    print("-" * 40)
    
    try:
        # Get workflow details
        details = await get_workflow_instance_details(workflow_uuid)
        print(f"Workflow status: {details.get('status', 'Unknown')}")
        
        # List workflow routines
        routines = await list_workflow_routines(workflow_uuid)
        print(f"Total routines: {len(routines)}")
        
        # Show sample routines
        print("\nSample routines:")
        for routine in routines[:5]:
            print(f"  - {routine.get('node_key', 'Unknown')}: {routine.get('status', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error monitoring experiment: {e}")

async def main():
    """
    Main execution function
    """
    print("🧪 DOE Experiment Runner")
    print("=" * 60)
    
    # Run the experiment
    result = await run_doe_experiment()
    
    if result:
        print(f"\n✅ Experiment started successfully!")
        print(f"Workflow UUID: {result.uuid}")
        
        # Monitor the experiment
        await monitor_experiment(result.uuid)
        
        print(f"\n📋 Next Steps:")
        print(f"1. Check the Workflow Instances UI to approve the workflow")
        print(f"2. Monitor progress through the UI or using the monitoring functions")
        print(f"3. The experiment will run continuously with 10-minute OD600 readings")
        print(f"4. Pure growth monitoring - no passaging, just growth curve data collection")
        print(f"5. To stop the experiment, cancel the workflow in the UI when you're ready")
        
    else:
        print(f"\n❌ Failed to start experiment")

if __name__ == "__main__":
    # Note: This script requires the MCP tools to be available
    # In practice, you would run this through the MCP interface
    print("⚠️  This script requires MCP tools to be available.")
    print("   Please run this through the MCP interface with the following functions:")
    print("   - list_culture_plates()")
    print("   - check_plate_availability()")
    print("   - instantiate_workflow()")
    print("   - get_workflow_instance_details()")
    print("   - list_workflow_routines()")
