"""
Simple Script to Schedule Measure Absorbance Routine
Reads OD600 every 5 minutes for plate "ScaleMeMaybe"
"""

import asyncio

async def schedule_absorbance_monitoring():
    """
    Schedule OD600 measurements every 5 minutes for plate ScaleMeMaybe
    """
    
    print("🧪 Scheduling Absorbance Monitoring")
    print("=" * 50)
    
    # Plate information
    plate_barcode = "ScaleMeMaybe"
    print(f"📋 Plate: {plate_barcode}")
    print(f"⏱️  Frequency: Every 5 minutes")
    print(f"📊 Routine: Measure Absorbance")
    
    # Step 1: Check if plate is available
    print(f"\n🔍 Checking plate availability...")
    try:
        plate_status = await check_plate_availability(plate_barcode)
        if not plate_status.is_available:
            print(f"❌ Plate not available: {plate_status.reason}")
            return None
        print(f"✅ Plate {plate_barcode} is available")
        
    except Exception as e:
        print(f"❌ Error checking plate availability: {e}")
        return None
    
    # Step 2: Create a simple workflow for 5-minute monitoring
    print(f"\n🚀 Creating workflow...")
    try:
        result = await instantiate_workflow(
            definition_id=19,  # 5-Minute Absorbance Monitoring workflow
            inputs={"plate_barcode": plate_barcode},
            start_after_minutes=0,  # Start immediately after approval
            reason=f"Simple OD600 monitoring every 5 minutes for plate {plate_barcode}"
        )
        
        print(f"✅ Workflow created successfully!")
        print(f"📋 Workflow UUID: {result.uuid}")
        print(f"📊 Status: {result.status}")
        print(f"⏳ Requires operator approval: {result.requires_approval}")
        
        if result.requires_approval:
            print(f"\n⚠️  IMPORTANT: This workflow requires operator approval before execution.")
            print(f"   Please check the Workflow Instances UI to approve the workflow.")
        
        return result
        
    except Exception as e:
        print(f"❌ Error creating workflow: {e}")
        return None

async def main():
    """
    Main execution function
    """
    print("📊 Absorbance Monitoring Scheduler")
    print("=" * 50)
    
    # Schedule the monitoring
    result = await schedule_absorbance_monitoring()
    
    if result:
        print(f"\n✅ Monitoring scheduled successfully!")
        print(f"Workflow UUID: {result.uuid}")
        
        print(f"\n📋 Next Steps:")
        print(f"1. Check the Workflow Instances UI to approve the workflow")
        print(f"2. The workcell will start reading OD600 every 5 minutes")
        print(f"3. Monitor progress through the UI")
        print(f"4. To stop, cancel the workflow in the UI when ready")
        
    else:
        print(f"\n❌ Failed to schedule monitoring")

if __name__ == "__main__":
    # Note: This script requires the MCP tools to be available
    print("⚠️  This script requires MCP tools to be available.")
    print("   Please run this through the MCP interface with the following functions:")
    print("   - check_plate_availability()")
    print("   - instantiate_workflow()")
    print("   - get_workflow_instance_details()")
