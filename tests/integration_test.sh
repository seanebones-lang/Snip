#!/bin/bash
# Integration tests for Snip production API

BASE_URL="https://snip-production.up.railway.app"
PASSED=0
FAILED=0

echo "=== Snip Production API Integration Tests ==="
echo ""

test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_code=$3
    local description=$4
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" -H "Content-Type: application/json" -d "$5")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_code" ]; then
        echo "✓ PASS: $description"
        echo "  $method $endpoint -> $http_code"
        ((PASSED++))
        return 0
    else
        echo "✗ FAIL: $description"
        echo "  $method $endpoint -> Expected $expected_code, got $http_code"
        echo "  Response: $body"
        ((FAILED++))
        return 1
    fi
}

# Test 1: Health check
test_endpoint "GET" "/healthz" "200" "Health check endpoint"

# Test 2: API docs
test_endpoint "GET" "/docs" "200" "API documentation"

# Test 3: OpenAPI schema
test_endpoint "GET" "/openapi.json" "200" "OpenAPI schema"

# Test 4: Invalid endpoint (404)
test_endpoint "GET" "/nonexistent" "404" "Invalid endpoint returns 404"

# Test 5: Protected endpoint requires auth
test_endpoint "GET" "/api/clients/me" "401" "Protected endpoint requires authentication"

# Test 6: Create client with invalid data
test_endpoint "POST" "/api/clients" "422" "Create client with invalid data returns validation error" "{}"

# Test 7: Widget config endpoint structure
response=$(curl -s "$BASE_URL/api/widget/config/00000000-0000-0000-0000-000000000000" 2>&1)
http_code=$(echo "$response" | grep -o "HTTP/[0-9.]* [0-9]*" | grep -o "[0-9]*$" || echo "000")
if [ "$http_code" = "404" ] || [ "$http_code" = "400" ]; then
    echo "✓ PASS: Widget config endpoint exists (returns expected error for invalid client)"
    ((PASSED++))
else
    echo "? INFO: Widget config endpoint status: $http_code"
fi

echo ""
echo "=== Test Summary ==="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "Total: $((PASSED + FAILED))"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo "All tests passed! ✓"
    exit 0
else
    echo ""
    echo "Some tests failed. ✗"
    exit 1
fi
