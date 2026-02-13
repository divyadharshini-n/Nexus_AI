import asyncio
from app.core.code_generation.structured_text_generator import st_generator, codegen_client

async def test():
    print(f"Testing code generation client...")
    print(f"API Key: {codegen_client.api_key[:20]}...")
    print(f"Model: {codegen_client.model}")
    
    stage_data = {
        "id": 1,
        "stage_number": 0,
        "stage_name": "Idle Stage",
        "stage_type": "idle",
        "description": "Safe baseline state",
        "original_logic": "Conveyor belt control",
        "edited_logic": "Turn OFF motor in idle stage"
    }
    
    try:
        result = await st_generator.generate_code(stage_data)
        print(f"\n✓ Code generated successfully!")
        print(f"Program blocks: {len(result.get('program_blocks', []))}")
        print(f"Global labels: {len(result.get('global_labels', []))}")
        
        if result.get('program_blocks'):
            block = result['program_blocks'][0]
            print(f"\nBlock name: {block.get('name')}")
            print(f"Code length: {len(block.get('code', ''))}")
            print(f"Code preview: {block.get('code', '')[:200]}")
        else:
            print("\n✗ No program blocks in result!")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
