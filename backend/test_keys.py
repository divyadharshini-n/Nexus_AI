import httpx

key1 = 'AIzaSyA9Z5bYFxaBAfTyHCnjZCAaH9RaC7yTTbY'
key2 = 'AIzaSyARYgZlu9pZ8u8kOqUQzTftKs7ahYbGEN4'
model = 'gemini-flash-lite-latest'
payload = {'contents': [{'role': 'user', 'parts': [{'text': 'Hi'}]}]}

print('Testing Key 1 (AI Dude)...')
r1 = httpx.post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key1}', json=payload, timeout=10)
print(f'Key 1: {r1.status_code}')
if r1.status_code != 200:
    print(f'Error: {r1.json().get("error", {}).get("message", "Unknown")[:100]}')

print('\nTesting Key 2 (Code Gen)...')
r2 = httpx.post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key2}', json=payload, timeout=10)
print(f'Key 2: {r2.status_code}')
if r2.status_code != 200:
    print(f'Error: {r2.json().get("error", {}).get("message", "Unknown")[:100]}')

print('\n=== SUMMARY ===')
print(f'Key 1 (AIzaSyA9Z5b...): {"✅ WORKING" if r1.status_code == 200 else "❌ FAILED"}')
print(f'Key 2 (AIzaSyARYgZ...): {"✅ WORKING" if r2.status_code == 200 else "❌ FAILED"}')
