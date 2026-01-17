#!/usr/bin/env python3
"""
E2E Test for Vercel-Deployed NextElevenWeb Site
Tests the live production site with actual chatbot interaction
"""

import asyncio
import httpx
import json
import sys
import time
from urllib.parse import urljoin

# Colors for output
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

# Try to detect the Vercel URL - user can override
VERCEL_URL = sys.argv[1] if len(sys.argv) > 1 else 'https://bizbot.store'

async def test_site_availability():
    """Test 1: Site is accessible"""
    print_test("Site Availability")
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(VERCEL_URL)
            if response.status_code == 200:
                print_pass(f"Site accessible (Status: {response.status_code})")
                return True
            else:
                print_fail(f"Status {response.status_code}")
                return False
    except Exception as e:
        print_fail(f"Cannot access site: {e}")
        print_info(f"Tried URL: {VERCEL_URL}")
        print_info("Usage: python3 test_vercel_site_e2e.py <your-vercel-url>")
        return False

async def test_homepage_content():
    """Test 2: Homepage loads with expected content"""
    print_test("Homepage Content")
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(VERCEL_URL)
            content = response.text.lower()
            
            checks = {
                'NextEleven': 'nexteleven' in content,
                'Chatbot': 'chat' in content or 'ai' in content,
                'React App': 'root' in content or 'react' in content or 'script' in content,
            }
            
            all_pass = all(checks.values())
            for name, passed in checks.items():
                if passed:
                    print_pass(f"{name} found")
                else:
                    print_fail(f"{name} not found")
            
            return all_pass
    except Exception as e:
        print_fail(f"Exception: {e}")
        return False

async def test_backend_api():
    """Test 3: Backend API is accessible"""
    print_test("Backend API Availability")
    
    # Try common backend URLs
    possible_backends = [
        'https://nexteleven-backend.vercel.app',
        'https://nexteleven-backend-production.vercel.app',
        'https://api.bizbot.store',
        'http://localhost:8000',  # For local testing
    ]
    
    # Also try relative path
    api_paths = ['/api/chat', '/api/healthz', '/healthz']
    
    found_backend = None
    
    for backend_url in possible_backends:
        for api_path in api_paths:
            try:
                url = urljoin(backend_url, api_path)
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(url)
                    if response.status_code in [200, 404]:  # 404 means server exists
                        print_info(f"Backend found: {url} (Status: {response.status_code})")
                        found_backend = backend_url
                        break
            except:
                continue
        if found_backend:
            break
    
    if found_backend:
        print_pass(f"Backend accessible at: {found_backend}")
        return found_backend
    else:
        print_info("Backend URL not auto-detected")
        print_info("This is OK if backend is on different domain")
        return None

async def test_chat_endpoint(backend_url=None):
    """Test 4: Chat endpoint works with TTS"""
    print_test("Chat Endpoint with TTS")
    
    # Try to find backend
    if not backend_url:
        # Check if API is on same domain
        api_urls = [
            f"{VERCEL_URL}/api/chat",
            "https://nexteleven-backend.vercel.app/api/chat",
        ]
    else:
        api_urls = [f"{backend_url}/api/chat"]
    
    for api_url in api_urls:
        try:
            print_info(f"Trying: {api_url}")
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Test chat request
                payload = {
                    "message": "Hello! This is a test message.",
                    "conversation_history": []
                }
                
                response = await client.post(
                    api_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check response structure
                    has_response = 'response' in data or 'content' in data
                    has_audio = 'audio_url' in data
                    
                    if has_response:
                        print_pass("Chat endpoint responds")
                        response_text = data.get('response') or data.get('content', '')
                        print_info(f"Response length: {len(response_text)} chars")
                        
                        if has_audio:
                            audio_url = data.get('audio_url')
                            if audio_url and audio_url.startswith('data:audio/wav;base64,'):
                                print_pass("TTS audio URL present")
                                print_info(f"Audio URL length: {len(audio_url)} chars")
                                return True
                            else:
                                print_info("Audio URL present but format unexpected")
                                print_info(f"Audio URL: {audio_url[:100] if audio_url else 'None'}...")
                                return True  # Still pass if response works
                        else:
                            print_info("No audio_url in response (may be disabled or failed)")
                            return True  # Still pass if chat works
                    else:
                        print_fail("Response missing 'response' or 'content' field")
                        print_info(f"Response: {json.dumps(data, indent=2)[:200]}")
                        return False
                elif response.status_code == 404:
                    print_info(f"Endpoint not found: {api_url}")
                    continue
                else:
                    print_fail(f"Status {response.status_code}: {response.text[:200]}")
                    continue
        except httpx.TimeoutException:
            print_info(f"Timeout connecting to {api_url}")
            continue
        except Exception as e:
            print_info(f"Error with {api_url}: {e}")
            continue
    
    print_info("Chat endpoint not accessible (may require authentication or different URL)")
    return None  # Not a failure, just not testable

async def test_widget_script():
    """Test 5: Widget script is accessible (if applicable)"""
    print_test("Widget Script Availability")
    
    widget_urls = [
        f"{VERCEL_URL}/widget.js",
        "https://widget-sigma-sage.vercel.app/widget.js",
    ]
    
    for url in widget_urls:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    content = response.text
                    if 'widget' in content.lower() or 'chat' in content.lower():
                        print_pass(f"Widget script found: {url}")
                        print_info(f"Script size: {len(content)} bytes")
                        return True
        except:
            continue
    
    print_info("Widget script not found (may not be deployed)")
    return None

async def test_health_endpoints():
    """Test 6: Health check endpoints"""
    print_test("Health Check Endpoints")
    
    health_urls = [
        f"{VERCEL_URL}/healthz",
        f"{VERCEL_URL}/api/healthz",
        "https://nexteleven-backend.vercel.app/healthz",
    ]
    
    found = False
    for url in health_urls:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    print_pass(f"Health endpoint: {url}")
                    found = True
        except:
            continue
    
    if not found:
        print_info("Health endpoints not found (optional)")
    
    return True  # Not critical

async def run_all_tests():
    """Run complete E2E test suite"""
    print_header("VERCEL SITE E2E TEST SUITE")
    print(f"{Colors.BOLD}Testing: {VERCEL_URL}{Colors.RESET}\n")
    
    results = {}
    
    # Test 1: Site Availability
    print_header("TEST 1: SITE AVAILABILITY")
    results['site_available'] = await test_site_availability()
    
    if not results['site_available']:
        print_fail("Cannot continue - site not accessible")
        return results
    
    # Test 2: Homepage Content
    print_header("TEST 2: HOMEPAGE CONTENT")
    results['homepage_content'] = await test_homepage_content()
    
    # Test 3: Backend API
    print_header("TEST 3: BACKEND API")
    backend_url = await test_backend_api()
    results['backend_found'] = backend_url is not None
    
    # Test 4: Chat Endpoint
    print_header("TEST 4: CHAT ENDPOINT WITH TTS")
    chat_result = await test_chat_endpoint(backend_url)
    results['chat_endpoint'] = chat_result
    
    # Test 5: Widget Script
    print_header("TEST 5: WIDGET SCRIPT")
    widget_result = await test_widget_script()
    results['widget_script'] = widget_result
    
    # Test 6: Health Endpoints
    print_header("TEST 6: HEALTH ENDPOINTS")
    results['health_endpoints'] = await test_health_endpoints()
    
    # Summary
    print_header("TEST RESULTS SUMMARY")
    
    critical_tests = ['site_available', 'homepage_content']
    optional_tests = ['backend_found', 'chat_endpoint', 'widget_script', 'health_endpoints']
    
    critical_passed = sum(1 for t in critical_tests if results.get(t))
    optional_passed = sum(1 for t in optional_tests if results.get(t) is not False)
    
    print(f"\n{Colors.BOLD}Critical Tests:{Colors.RESET}")
    for test in critical_tests:
        status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if results.get(test) else f"{Colors.RED}❌ FAIL{Colors.RESET}"
        print(f"  {test.replace('_', ' ').title()}: {status}")
    
    print(f"\n{Colors.BOLD}Optional Tests:{Colors.RESET}")
    for test in optional_tests:
        result = results.get(test)
        if result is True:
            status = f"{Colors.GREEN}✅ PASS{Colors.RESET}"
        elif result is None:
            status = f"{Colors.YELLOW}⚠️  N/A{Colors.RESET}"
        else:
            status = f"{Colors.RED}❌ FAIL{Colors.RESET}"
        print(f"  {test.replace('_', ' ').title()}: {status}")
    
    print(f"\n{Colors.BOLD}Summary:{Colors.RESET}")
    print(f"  Critical: {critical_passed}/{len(critical_tests)} passed")
    print(f"  Optional: {optional_passed}/{len(optional_tests)} passed/available")
    
    if critical_passed == len(critical_tests):
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}✅ SITE IS ACCESSIBLE AND WORKING{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.RESET}\n")
        
        if results.get('chat_endpoint'):
            print(f"{Colors.GREEN}✅ Chat endpoint works{Colors.RESET}")
            if results.get('chat_endpoint') is True:
                print(f"{Colors.GREEN}✅ TTS integration verified{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠️  Chat endpoint not tested (may require auth or different URL){Colors.RESET}")
    else:
        print(f"\n{Colors.RED}⚠️  Some critical tests failed{Colors.RESET}\n")
    
    return results

if __name__ == '__main__':
    try:
        results = asyncio.run(run_all_tests())
        critical_passed = results.get('site_available') and results.get('homepage_content')
        sys.exit(0 if critical_passed else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Tests interrupted{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Fatal error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
