import asyncio
import httpx

async def test_codegen_key():
    api_key = "AIzaSyARYgZlu9pZ8u8kOqUQzTftKs7ahYbGEN4"
    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"
    
    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": "Say hello"}]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 100
        }
    }
    
    params = {"key": api_key}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(endpoint, params=params, json=payload)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code == 200:
                print("\n✓ Code generation API key is WORKING!")
            else:
                print(f"\n✗ API Error: {response.status_code}")
                
    except Exception as e:
        print(f"✗ Error: {e}")

asyncio.run(test_codegen_key())
