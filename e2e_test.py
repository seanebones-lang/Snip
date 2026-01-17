#!/usr/bin/env python3
"""
E2E Test for Snip Chatbot - Tests everything end-to-end
"""
import os
import sys
import requests
import json
import time
from typing import Optional, Dict, Any

# Configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("XAI_API_KEY", "")
CLIENT_ID = os.getenv("CLIENT_ID", "")

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name: str):
    print(f"\n{Colors.BLUE}Testing: {name}{Colors.END}")

def print_pass(msg: str):
    print(f"{Colors.GREEN}✓ PASS: {msg}{Colors.END}")

def print_fail(msg: str, error: Optional[str] = None):
    print(f"{Colors.RED}✗ FAIL: {msg}{Colors.END}")
    if error:
        print(f"  Error: {error}")

def print_warn(msg: str):
    print(f"{Colors.YELLOW}⚠ WARN: {msg}{Colors.END}")

def test_health_check() -> bool:
    """Test backend health check"""
    print_test("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/healthz", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                print_pass("Health check passed")
                return True
        print_fail(f"Health check failed: {response.status_code}")
        return False
    except Exception as e:
        print_fail("Health check failed", str(e))
        return False

def test_create_client() -> Optional[Dict]:
    """Test client creation"""
    print_test("Create Client")
    try:
        data = {
            "email": f"test_{int(time.time())}@example.com",
            "company_name": "Test Company"
        }
        response = requests.post(
            f"{BASE_URL}/api/clients",
            json=data,
            timeout=10
        )
        if response.status_code == 200:
            client_data = response.json()
            print_pass(f"Client created: {client_data.get('id')}")
            return client_data
        elif response.status_code == 400 and "already registered" in response.text:
            print_warn("Client already exists (may be from previous test)")
            return None
        else:
            print_fail(f"Client creation failed: {response.status_code}", response.text)
            return None
    except Exception as e:
        print_fail("Client creation failed", str(e))
        return None

def test_widget_config(client_id: str) -> bool:
    """Test widget config endpoint"""
    print_test("Widget Config")
    try:
        response = requests.get(
            f"{BASE_URL}/api/widget/config/{client_id}",
            timeout=5
        )
        if response.status_code == 200:
            config = response.json()
            required_fields = ["bot_name", "welcome_message", "colors"]
            if all(field in config for field in required_fields):
                print_pass("Widget config retrieved")
                return True
        print_fail(f"Widget config failed: {response.status_code}", response.text[:200])
        return False
    except Exception as e:
        print_fail("Widget config failed", str(e))
        return False

def test_chat(client_id: str, api_key: Optional[str] = None) -> Optional[Dict]:
    """Test chat endpoint with TTS"""
    print_test("Chat with TTS")
    try:
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "client_id": client_id,
            "message": "Hello! Say 'This is a test' in a cheerful voice."
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=data,
            headers=headers,
            timeout=60  # Longer timeout for TTS
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            # Check response text
            if "response" not in result:
                print_fail("No 'response' field in chat response")
                return None
            
            response_text = result.get("response", "")
            print_pass(f"Chat response received ({len(response_text)} chars, {elapsed:.2f}s)")
            print(f"  Response: {response_text[:100]}...")
            
            # Check TTS audio
            audio_url = result.get("audio_url")
            if audio_url:
                if audio_url.startswith("data:audio/wav;base64,"):
                    audio_data = audio_url[len("data:audio/wav;base64,"):]
                    audio_size = len(audio_data) * 3 // 4  # Approximate base64 decoded size
                    print_pass(f"TTS audio generated ({audio_size} bytes)")
                    print(f"  Audio URL: {audio_url[:50]}...")
                    return {
                        "response": response_text,
                        "audio_url": audio_url,
                        "has_audio": True
                    }
                else:
                    print_warn(f"Unexpected audio_url format: {audio_url[:50]}")
                    return {
                        "response": response_text,
                        "audio_url": audio_url,
                        "has_audio": False
                    }
            else:
                print_warn("No audio_url in response (TTS may have failed or been skipped)")
                return {
                    "response": response_text,
                    "audio_url": None,
                    "has_audio": False
                }
        else:
            print_fail(f"Chat failed: {response.status_code}", response.text[:500])
            return None
    except requests.exceptions.Timeout:
        print_fail("Chat request timed out (>60s)")
        return None
    except Exception as e:
        print_fail("Chat failed", str(e))
        return None

def test_audio_playback(audio_url: Optional[str]) -> bool:
    """Test if audio URL can be decoded"""
    print_test("Audio Playback (decode test)")
    if not audio_url:
        print_warn("No audio URL to test")
        return False
    
    try:
        import base64
        if audio_url.startswith("data:audio/wav;base64,"):
            base64_data = audio_url[len("data:audio/wav;base64,"):]
            audio_bytes = base64.b64decode(base64_data)
            
            # Check WAV header
            if audio_bytes[:4] == b'RIFF' and audio_bytes[8:12] == b'WAVE':
                print_pass(f"Audio is valid WAV format ({len(audio_bytes)} bytes)")
                return True
            else:
                print_fail("Audio does not have valid WAV header")
                return False
        else:
            print_fail(f"Audio URL has unexpected format")
            return False
    except Exception as e:
        print_fail("Audio decode failed", str(e))
        return False

def main():
    """Run all E2E tests"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  Snip Chatbot E2E Test Suite")
    print(f"{'='*60}{Colors.END}\n")
    print(f"Base URL: {BASE_URL}")
    print(f"API Key: {'Set' if API_KEY else 'Not set'}")
    print(f"Client ID: {CLIENT_ID if CLIENT_ID else 'Will create new'}\n")
    
    results = {
        "health": False,
        "client": False,
        "widget_config": False,
        "chat": False,
        "audio": False
    }
    
    # Test 1: Health check
    results["health"] = test_health_check()
    if not results["health"]:
        print_fail("\nBackend is not accessible. Cannot continue.")
        return False
    
    # Test 2: Create client (if needed)
    client_id = CLIENT_ID
    client_data = None
    
    if not client_id:
        client_data = test_create_client()
        if client_data:
            client_id = client_data.get("id")
            results["client"] = True
            print(f"\n{Colors.GREEN}Using client ID: {client_id}{Colors.END}\n")
        else:
            print_warn("Could not create client, but continuing...")
    else:
        results["client"] = True
        print(f"\n{Colors.GREEN}Using provided client ID: {client_id}{Colors.END}\n")
    
    if not client_id:
        print_fail("No client ID available. Cannot continue.")
        return False
    
    # Test 3: Widget config
    results["widget_config"] = test_widget_config(client_id)
    
    # Test 4: Chat with TTS
    api_key = API_KEY or (client_data.get("api_key") if client_data else None)
    chat_result = test_chat(client_id, api_key)
    results["chat"] = chat_result is not None
    
    # Test 5: Audio playback
    if chat_result and chat_result.get("has_audio"):
        results["audio"] = test_audio_playback(chat_result.get("audio_url"))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  Test Summary")
    print(f"{'='*60}{Colors.END}\n")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if result else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"  {test_name:20} {status}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{'='*60}")
        print(f"  ✓ ALL TESTS PASSED - READY FOR PRODUCTION")
        print(f"{'='*60}{Colors.END}\n")
        return True
    else:
        print(f"\n{Colors.RED}{'='*60}")
        print(f"  ✗ SOME TESTS FAILED - REVIEW ERRORS ABOVE")
        print(f"{'='*60}{Colors.END}\n")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
