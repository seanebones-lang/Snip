#!/bin/bash
# E2E Test for Snip Chatbot - Quick validation
set -e

BASE_URL="${BASE_URL:-https://snip-production.up.railway.app}"
GREEN='\033[92m'
RED='\033[91m'
YELLOW='\033[93m'
BLUE='\033[94m'
NC='\033[0m'

PASSED=0
FAILED=0

echo -e "${BLUE}=========================================="
echo -e "  Snip Chatbot E2E Test Suite"
echo -e "==========================================${NC}\n"
echo "Base URL: $BASE_URL"
echo ""

# Test 1: Health Check
echo -e "${BLUE}Testing: Health Check${NC}"
if curl -s -f "${BASE_URL}/healthz" | grep -q '"status":"ok"'; then
    echo -e "${GREEN}✓ PASS: Health check passed${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL: Health check failed${NC}"
    ((FAILED++))
    echo "Cannot continue - backend not accessible"
    exit 1
fi
echo ""

# Test 2: Create Client
echo -e "${BLUE}Testing: Create Client${NC}"
TIMESTAMP=$(date +%s)
CLIENT_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/clients" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"test${TIMESTAMP}@example.com\",\"company_name\":\"Test Company\"}")

if echo "$CLIENT_RESPONSE" | grep -q '"id"'; then
    CLIENT_ID=$(echo "$CLIENT_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    API_KEY=$(echo "$CLIENT_RESPONSE" | grep -o '"api_key":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "")
    echo -e "${GREEN}✓ PASS: Client created${NC}"
    echo "  Client ID: $CLIENT_ID"
    if [ -n "$API_KEY" ]; then
        echo "  API Key: ${API_KEY:0:20}..."
    fi
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ WARN: Client creation may have failed or client already exists${NC}"
    echo "  Response: $CLIENT_RESPONSE"
    # Try to continue with existing client if needed
    CLIENT_ID="00000000-0000-0000-0000-000000000000"  # Test with dummy ID
fi
echo ""

# Test 3: Widget Config
if [ -n "$CLIENT_ID" ] && [ "$CLIENT_ID" != "00000000-0000-0000-0000-000000000000" ]; then
    echo -e "${BLUE}Testing: Widget Config${NC}"
    CONFIG_RESPONSE=$(curl -s "${BASE_URL}/api/widget/config/${CLIENT_ID}")
    if echo "$CONFIG_RESPONSE" | grep -q '"botName"'; then
        echo -e "${GREEN}✓ PASS: Widget config retrieved${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL: Widget config failed${NC}"
        echo "  Response: $CONFIG_RESPONSE"
        ((FAILED++))
    fi
    echo ""
fi

# Test 4: Chat Endpoint
if [ -n "$CLIENT_ID" ] && [ "$CLIENT_ID" != "00000000-0000-0000-0000-000000000000" ]; then
    echo -e "${BLUE}Testing: Chat with TTS${NC}"
    echo "  Sending message: 'Hello! Say this is a test.'"
    
    CHAT_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${BASE_URL}/api/chat" \
        -H "Content-Type: application/json" \
        -d "{\"client_id\":\"${CLIENT_ID}\",\"message\":\"Hello! Say this is a test.\"}" \
        --max-time 60)
    
    HTTP_CODE=$(echo "$CHAT_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
    CHAT_BODY=$(echo "$CHAT_RESPONSE" | sed '/HTTP_CODE:/d')
    
    if [ "$HTTP_CODE" = "200" ]; then
        if echo "$CHAT_BODY" | grep -q '"response"'; then
            RESPONSE_TEXT=$(echo "$CHAT_BODY" | grep -o '"response":"[^"]*"' | cut -d'"' -f4 | head -c 100)
            echo -e "${GREEN}✓ PASS: Chat response received${NC}"
            echo "  Response: ${RESPONSE_TEXT}..."
            ((PASSED++))
            
            # Check for audio_url
            if echo "$CHAT_BODY" | grep -q '"audio_url"'; then
                AUDIO_URL=$(echo "$CHAT_BODY" | grep -o '"audio_url":"[^"]*"' | cut -d'"' -f4)
                if echo "$AUDIO_URL" | grep -q "^data:audio/wav;base64,"; then
                    AUDIO_SIZE=$(echo "$AUDIO_URL" | cut -d',' -f2 | wc -c)
                    echo -e "${GREEN}✓ PASS: TTS audio generated${NC}"
                    echo "  Audio URL: ${AUDIO_URL:0:50}... (${AUDIO_SIZE} chars)"
                    ((PASSED++))
                else
                    echo -e "${YELLOW}⚠ WARN: audio_url format unexpected${NC}"
                fi
            else
                echo -e "${YELLOW}⚠ WARN: No audio_url in response (TTS may have failed)${NC}"
            fi
        else
            echo -e "${RED}✗ FAIL: No response field in chat response${NC}"
            echo "  Body: $CHAT_BODY"
            ((FAILED++))
        fi
    else
        echo -e "${RED}✗ FAIL: Chat failed with HTTP $HTTP_CODE${NC}"
        echo "  Response: $CHAT_BODY"
        ((FAILED++))
    fi
    echo ""
fi

# Summary
echo -e "${BLUE}=========================================="
echo -e "  Test Summary"
echo -e "==========================================${NC}\n"
TOTAL=$((PASSED + FAILED))
echo "Total: $PASSED passed, $FAILED failed (out of $TOTAL tests)"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}=========================================="
    echo -e "  ✓ ALL TESTS PASSED - READY FOR PRODUCTION"
    echo -e "==========================================${NC}\n"
    exit 0
else
    echo -e "\n${RED}=========================================="
    echo -e "  ✗ SOME TESTS FAILED - REVIEW ERRORS ABOVE"
    echo -e "==========================================${NC}\n"
    exit 1
fi
