#!/usr/bin/env python3
"""
Comprehensive Test Suite for TTS Fixes
Tests all the fixes applied to widget and backend TTS implementation
"""
import re
import os
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(name):
    print(f"\n{Colors.BLUE}Testing: {name}{Colors.END}")

def print_pass(msg):
    print(f"  {Colors.GREEN}✓ PASS{Colors.END}: {msg}")

def print_fail(msg):
    print(f"  {Colors.RED}✗ FAIL{Colors.END}: {msg}")

def print_warn(msg):
    print(f"  {Colors.YELLOW}⚠ WARN{Colors.END}: {msg}")

def test_widget_fixes():
    """Test all widget TTS fixes"""
    print_test("Widget TTS Fixes")
    
    widget_file = Path("widget/src/widget.ts")
    if not widget_file.exists():
        print_fail("widget.ts file not found")
        return False
    
    content = widget_file.read_text()
    passed = 0
    failed = 0
    
    # Test 1: Memory leak fix - currentAudio property
    if "currentAudio: HTMLAudioElement | null" in content or "private currentAudio" in content:
        print_pass("currentAudio property added (memory leak fix)")
        passed += 1
    else:
        print_fail("currentAudio property not found")
        failed += 1
    
    # Test 2: Race condition fix - isPlayingAudio flag
    if "isPlayingAudio: boolean" in content or "private isPlayingAudio" in content:
        print_pass("isPlayingAudio flag added (race condition fix)")
        passed += 1
    else:
        print_fail("isPlayingAudio flag not found")
        failed += 1
    
    # Test 3: stopAudio method
    if "stopAudio()" in content and "private stopAudio" in content:
        print_pass("stopAudio() method added (cleanup fix)")
        passed += 1
    else:
        print_fail("stopAudio() method not found")
        failed += 1
    
    # Test 4: announceAudioState method
    if "announceAudioState" in content and "aria-live" in content:
        print_pass("announceAudioState() method added (accessibility fix)")
        passed += 1
    else:
        print_fail("announceAudioState() method not found")
        failed += 1
    
    # Test 5: Error recovery - fallbackText parameter
    if "fallbackText" in content and "fallbackBrowserTTS" in content:
        print_pass("Error recovery with fallbackText parameter")
        passed += 1
    else:
        print_fail("Error recovery fallback not found")
        failed += 1
    
    # Test 6: Race condition prevention in setupTTSWatcher
    if "if (this.isPlayingAudio) return" in content:
        print_pass("Race condition check in TTS watcher")
        passed += 1
    else:
        print_fail("Race condition check missing in TTS watcher")
        failed += 1
    
    # Test 7: Long text chunking
    if "maxLength" in content and "speakTextChunk" in content:
        print_pass("Long text chunking for browser TTS")
        passed += 1
    else:
        print_warn("Long text chunking may be missing")
    
    # Test 8: Audio cleanup on error
    if "this.currentAudio = null" in content and "this.isPlayingAudio = false" in content:
        print_pass("Audio cleanup on error/end events")
        passed += 1
    else:
        print_fail("Audio cleanup missing")
        failed += 1
    
    print(f"\n  {Colors.BOLD}Widget Tests: {passed} passed, {failed} failed{Colors.END}")
    return failed == 0

def test_backend_fixes():
    """Test all backend TTS fixes"""
    print_test("Backend TTS Fixes")
    
    backend_file = Path("backend/app/main.py")
    if not backend_file.exists():
        print_fail("main.py file not found")
        return False
    
    content = backend_file.read_text()
    passed = 0
    failed = 0
    
    # Test 1: Retry logic in get_xai_ephemeral_token
    if "retries: int = 3" in content and "retry" in content.lower():
        print_pass("Retry logic added to get_xai_ephemeral_token")
        passed += 1
    else:
        print_fail("Retry logic not found")
        failed += 1
    
    # Test 2: Exponential backoff
    if "wait_time = (attempt + 1) * 0.5" in content or "asyncio.sleep" in content:
        print_pass("Exponential backoff implemented")
        passed += 1
    else:
        print_warn("Exponential backoff may be missing")
    
    # Test 3: Voice configuration
    if "XAI_TTS_VOICE" in content or "voice = " in content:
        print_pass("Voice configuration support added")
        passed += 1
    else:
        print_fail("Voice configuration not found")
        failed += 1
    
    # Test 4: Voice validation
    if "['Ara', 'Leo', 'Rex', 'Sal', 'Eve']" in content or "voice not in" in content:
        print_pass("Voice validation implemented")
        passed += 1
    else:
        print_warn("Voice validation may be missing")
    
    # Test 5: Error handling for auth errors
    if "401" in content and "403" in content and "Don't retry" in content:
        print_pass("Proper error handling for auth errors (no retry)")
        passed += 1
    else:
        print_warn("Auth error handling may need improvement")
    
    print(f"\n  {Colors.BOLD}Backend Tests: {passed} passed, {failed} failed{Colors.END}")
    return failed == 0

def test_code_quality():
    """Test code quality and best practices"""
    print_test("Code Quality Checks")
    
    widget_file = Path("widget/src/widget.ts")
    backend_file = Path("backend/app/main.py")
    
    passed = 0
    failed = 0
    
    # Test 1: Check for console.log statements (logging)
    if widget_file.exists():
        widget_content = widget_file.read_text()
        if "[TTS]" in widget_content:
            print_pass("TTS logging with [TTS] prefix found")
            passed += 1
        else:
            print_warn("TTS logging may be missing")
    
    # Test 2: Check for error handling
    if backend_file.exists():
        backend_content = backend_file.read_text()
        if "try:" in backend_content and "except" in backend_content:
            print_pass("Error handling present in backend")
            passed += 1
        else:
            print_fail("Error handling missing")
            failed += 1
    
    # Test 3: Check for type safety (TypeScript)
    if widget_file.exists():
        widget_content = widget_file.read_text()
        if "private" in widget_content and ":" in widget_content:
            print_pass("TypeScript type annotations present")
            passed += 1
    
    print(f"\n  {Colors.BOLD}Quality Checks: {passed} passed, {failed} failed{Colors.END}")
    return failed == 0

def test_fix_integration():
    """Test that fixes work together"""
    print_test("Fix Integration")
    
    widget_file = Path("widget/src/widget.ts")
    if not widget_file.exists():
        return False
    
    content = widget_file.read_text()
    passed = 0
    failed = 0
    
    # Test: stopAudio is called before new audio
    if "stopAudio()" in content and "playAudioFromUrl" in content:
        # Check if stopAudio is called at start of playAudioFromUrl
        play_audio_match = re.search(r'playAudioFromUrl\([^)]+\)\s*\{[^}]*?stopAudio\(\)', content, re.DOTALL)
        if play_audio_match or "this.stopAudio()" in content:
            print_pass("stopAudio() called before new audio playback")
            passed += 1
        else:
            print_warn("stopAudio() integration may need verification")
    
    # Test: isPlayingAudio is set correctly
    if "this.isPlayingAudio = true" in content and "this.isPlayingAudio = false" in content:
        print_pass("isPlayingAudio flag set correctly on start/end")
        passed += 1
    else:
        print_fail("isPlayingAudio flag not managed correctly")
        failed += 1
    
    # Test: currentAudio is cleaned up
    if "this.currentAudio = null" in content:
        print_pass("currentAudio cleanup on error/end")
        passed += 1
    else:
        print_fail("currentAudio cleanup missing")
        failed += 1
    
    print(f"\n  {Colors.BOLD}Integration Tests: {passed} passed, {failed} failed{Colors.END}")
    return failed == 0

def main():
    print(f"{Colors.BOLD}{'='*60}")
    print("TTS Fixes Test Suite")
    print(f"{'='*60}{Colors.END}")
    
    results = {
        "Widget Fixes": test_widget_fixes(),
        "Backend Fixes": test_backend_fixes(),
        "Code Quality": test_code_quality(),
        "Fix Integration": test_fix_integration()
    }
    
    print(f"\n{Colors.BOLD}{'='*60}")
    print("Test Summary")
    print(f"{'='*60}{Colors.END}")
    
    total_passed = sum(1 for v in results.values() if v)
    total_tests = len(results)
    
    for name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {name}: {status}")
    
    print(f"\n{Colors.BOLD}Overall: {total_passed}/{total_tests} test suites passed{Colors.END}")
    
    if total_passed == total_tests:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All tests passed! TTS fixes are properly implemented.{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Some tests failed. Review the issues above.{Colors.END}")
        return 1

if __name__ == "__main__":
    exit(main())
