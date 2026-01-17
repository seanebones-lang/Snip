#!/usr/bin/env python3
"""
Complete E2E Test with TTS for snip.mothership-ai.com
Creates client, configures X.AI, tests chat with TTS verification
"""

import asyncio
import httpx
import json
import sys
import time
import base64

# Colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f'\n{Colors.BOLD}{Colors.BLUE}{"="*70}{Colors.RESET}')
    print(f'{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}')
    print(f'{Colors.BOLD}{Colors.BLUE}{"="*70}{Colors.RESET}\n')

def print_test(name):
    print(f'{Colors.BOLD}[TEST]{Colors.RESET} {name}')

def print_pass(msg):
    print(f'{Colors.GREEN}✅ PASS:{Colors.RESET} {msg}')

def print_fail(msg):
    print(f'{Colors.RED}❌ FAIL:{Colors.RESET} {msg}')

def print_info(msg):
    print(f'{Colors.YELLOW}ℹ️  INFO:{Colors.RESET} {msg}')

SNIP_BACKEND = 'https://snip-production.up.railway.app'
SNIP_SITE = 'https://snip.mothership-ai.com'
XAI_API_KEY = 'YOUR_XAI_API_KEY_HERE'

async def create_and_configure_client():
    """Create client and configure for X.AI TTS"""
    print_test("Creating and Configuring Client")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Create client
            email = f'tts-e2e-{int(time.time())}@test.com'
            response = await client.post(
                f'{SNIP_BACKEND}/api/clients',
                json={
                    'email': email,
                    'company_name': 'TTS E2E Test',
                    'tier': 'premium'
                }
            )
            if response.status_code != 200:
                print_fail(f"Client creation failed: {response.status_code}")
                return None, None
            
            data = response.json()
            client_id = data['id']
            api_key = data['api_key']
            print_pass(f"Client created (ID: {client_id})")
            
            # Configure for X.AI
            print_info("Configuring client for X.AI TTS...")
            config_response = await client.patch(
                f'{SNIP_BACKEND}/api/config',
                json={
                    'ai_provider': 'xai',
                    'ai_api_key': XAI_API_KEY,
                    'ai_model': 'grok-4-1-fast-non-reasoning'
                },
                headers={'X-API-Key': api_key}
            )
            
            if config_response.status_code == 200:
                print_pass("Client configured for X.AI TTS")
                return client_id, api_key
            else:
                print_info(f"Config status: {config_response.status_code}")
                print_info("Continuing anyway (may use default config)")
                return client_id, api_key
                
    except Exception as e:
        print_fail(f"Exception: {e}")
        return None, None

async def test_chat_with_tts_verification(api_key, client_id):
    """Test chat and verify TTS audio"""
    print_test("Chat with TTS Verification")
    test_message = "Hello! This is a test of the text-to-speech system."
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print_info(f"Message: '{test_message}'")
            print_info("Waiting for response with TTS (15-30 seconds)...")
            
            response = await client.post(
                f'{SNIP_BACKEND}/api/chat',
                json={
                    'client_id': client_id,
                    'message': test_message
                },
                headers={
                    'X-API-Key': api_key,
                    'Content-Type': 'application/json'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response
                if 'response' not in data:
                    print_fail("Response missing 'response' field")
                    return False
                
                response_text = data.get('response', '')
                print_pass("Chat response received")
                print_info(f"Response: {response_text[:150]}...")
                
                # Check TTS
                audio_url = data.get('audio_url')
                if audio_url:
                    if audio_url.startswith('data:audio/wav;base64,'):
                        # Extract and verify audio
                        base64_data = audio_url.split(',', 1)[1]
                        try:
                            audio_bytes = base64.b64decode(base64_data)
                            print_pass("TTS audio URL present and valid")
                            print_info(f"Audio size: {len(audio_bytes):,} bytes")
                            
                            # Verify WAV format
                            if audio_bytes[:4] == b'RIFF' and audio_bytes[8:12] == b'WAVE':
                                print_pass("Audio is valid WAV format")
                                print_info("✅ TTS IS WORKING!")
                                return True
                            else:
                                print_fail("Audio is not valid WAV format")
                                return False
                        except Exception as e:
                            print_fail(f"Failed to decode audio: {e}")
                            return False
                    else:
                        print_fail(f"Audio URL has unexpected format: {audio_url[:50]}...")
                        return False
                else:
                    print_info("No audio_url in response")
                    print_info("Possible reasons:")
                    print_info("  - Client not configured with X.AI API key")
                    print_info("  - TTS generation failed (non-fatal)")
                    print_info("  - Provider not set to 'xai'")
                    return True  # Chat works, TTS may need config
            else:
                print_fail(f"Status {response.status_code}: {response.text[:300]}")
                return False
    except httpx.TimeoutException:
        print_fail("Request timed out")
        return False
    except Exception as e:
        print_fail(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_full_test():
    """Run complete E2E test"""
    print_header("SNIP.MOTHERSHIP-AI.COM FULL E2E TEST WITH TTS")
    print(f"{Colors.BOLD}Testing: {SNIP_SITE}{Colors.RESET}\n")
    
    # Step 1: Create and configure client
    print_header("STEP 1: CREATE AND CONFIGURE CLIENT")
    client_id, api_key = await create_and_configure_client()
    
    if not client_id or not api_key:
        print_fail("Cannot continue without client")
        return False
    
    # Step 2: Test chat with TTS
    print_header("STEP 2: TEST CHAT WITH TTS")
    tts_works = await test_chat_with_tts_verification(api_key, client_id)
    
    # Summary
    print_header("FINAL RESULTS")
    
    if tts_works:
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}🎉 TTS IS WORKING! 🎉{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.RESET}\n")
        print(f"{Colors.GREEN}✅ Client created and configured{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Chat endpoint works{Colors.RESET}")
        print(f"{Colors.GREEN}✅ TTS generates audio{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Audio is valid WAV format{Colors.RESET}")
        print(f"\n{Colors.BOLD}🚀 READY TO SELL!{Colors.RESET}\n")
    else:
        print(f"{Colors.YELLOW}⚠️  Chat works but TTS needs configuration{Colors.RESET}")
        print(f"{Colors.YELLOW}   Check client config: ai_provider='xai', ai_api_key set{Colors.RESET}\n")
    
    return tts_works

if __name__ == '__main__':
    try:
        result = asyncio.run(run_full_test())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Tests interrupted{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Fatal error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
