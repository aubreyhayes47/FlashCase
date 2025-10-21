#!/bin/bash
# FlashCase Smoke Tests
# Run these tests after deployment to verify basic functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
print_test() {
    echo -e "\n${YELLOW}► $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    ((TESTS_PASSED++))
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    ((TESTS_FAILED++))
}

print_summary() {
    echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Test Summary${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "Tests Passed: ${GREEN}${TESTS_PASSED}${NC}"
    echo -e "Tests Failed: ${RED}${TESTS_FAILED}${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}All smoke tests passed! ✓${NC}"
        exit 0
    else
        echo -e "\n${RED}Some smoke tests failed! ✗${NC}"
        exit 1
    fi
}

# Test functions
test_backend_health() {
    print_test "Testing backend health endpoint..."
    
    response=$(curl -s -w "\n%{http_code}" "$BACKEND_URL/api/v1/health")
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 200 ]; then
        if echo "$body" | grep -q "healthy"; then
            print_success "Backend health check passed"
        else
            print_error "Backend health check returned unexpected response"
        fi
    else
        print_error "Backend health check failed (HTTP $http_code)"
    fi
}

test_ai_health() {
    print_test "Testing AI health endpoint..."
    
    response=$(curl -s -w "\n%{http_code}" "$BACKEND_URL/api/v1/ai/health")
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 200 ]; then
        if echo "$body" | grep -q "status"; then
            print_success "AI health check passed"
        else
            print_error "AI health check returned unexpected response"
        fi
    else
        print_error "AI health check failed (HTTP $http_code)"
    fi
}

test_ai_usage() {
    print_test "Testing AI usage monitoring endpoint..."
    
    response=$(curl -s -w "\n%{http_code}" "$BACKEND_URL/api/v1/ai/usage")
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 200 ]; then
        if echo "$body" | grep -q "usage"; then
            print_success "AI usage endpoint working"
            # Print token stats
            total_tokens=$(echo "$body" | grep -o '"total_tokens":[0-9]*' | cut -d: -f2)
            echo "  Total tokens used: $total_tokens"
        else
            print_error "AI usage endpoint returned unexpected response"
        fi
    else
        print_error "AI usage endpoint failed (HTTP $http_code)"
    fi
}

test_api_docs() {
    print_test "Testing API documentation endpoint..."
    
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/docs")
    
    if [ "$http_code" -eq 200 ]; then
        print_success "API documentation accessible"
    else
        print_error "API documentation not accessible (HTTP $http_code)"
    fi
}

test_cors() {
    print_test "Testing CORS configuration..."
    
    response=$(curl -s -H "Origin: http://localhost:3000" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: Content-Type" \
        -X OPTIONS \
        -I "$BACKEND_URL/api/v1/health")
    
    if echo "$response" | grep -q "Access-Control-Allow-Origin"; then
        print_success "CORS configured correctly"
    else
        print_error "CORS headers not found"
    fi
}

test_frontend() {
    print_test "Testing frontend accessibility..."
    
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Frontend is accessible"
    else
        print_error "Frontend not accessible (HTTP $http_code)"
    fi
}

test_database_connection() {
    print_test "Testing database connection (via health check)..."
    
    response=$(curl -s "$BACKEND_URL/api/v1/health")
    
    if echo "$response" | grep -q "database"; then
        db_status=$(echo "$response" | grep -o '"database":"[^"]*"' | cut -d: -f2 | tr -d '"')
        if [ "$db_status" = "connected" ]; then
            print_success "Database connection verified"
        else
            print_error "Database not connected (status: $db_status)"
        fi
    else
        print_error "Could not verify database connection"
    fi
}

test_rate_limiting() {
    print_test "Testing rate limiting configuration..."
    
    # Make multiple rapid requests
    for i in {1..3}; do
        curl -s "$BACKEND_URL/api/v1/health" > /dev/null
    done
    
    # Check if rate limiting info is available
    response=$(curl -s "$BACKEND_URL/api/v1/ai/health")
    
    if echo "$response" | grep -q "rate_limiting"; then
        enabled=$(echo "$response" | grep -o '"enabled":[^,}]*' | head -1 | cut -d: -f2)
        if [ "$enabled" = "true" ]; then
            print_success "Rate limiting is enabled"
        else
            print_success "Rate limiting is disabled (may be intentional)"
        fi
    else
        print_error "Could not verify rate limiting configuration"
    fi
}

test_response_time() {
    print_test "Testing backend response time..."
    
    start_time=$(date +%s%N)
    curl -s "$BACKEND_URL/api/v1/health" > /dev/null
    end_time=$(date +%s%N)
    
    response_time=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
    
    if [ $response_time -lt 1000 ]; then
        print_success "Response time acceptable ($response_time ms)"
    else
        print_error "Response time too high ($response_time ms)"
    fi
}

test_docker_containers() {
    print_test "Testing Docker containers (if running locally)..."
    
    if command -v docker &> /dev/null; then
        backend_running=$(docker ps --filter "name=flashcase-backend" --format "{{.Names}}" 2>/dev/null)
        frontend_running=$(docker ps --filter "name=flashcase-frontend" --format "{{.Names}}" 2>/dev/null)
        
        if [ -n "$backend_running" ]; then
            print_success "Backend container is running"
        else
            echo "  ℹ Backend container not found (may not be using Docker)"
        fi
        
        if [ -n "$frontend_running" ]; then
            print_success "Frontend container is running"
        else
            echo "  ℹ Frontend container not found (may not be using Docker)"
        fi
    else
        echo "  ℹ Docker not available, skipping container checks"
    fi
}

# Main execution
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "FlashCase Deployment Smoke Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Backend URL:  $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"

# Run all tests
test_backend_health
test_ai_health
test_ai_usage
test_api_docs
test_cors
test_database_connection
test_rate_limiting
test_response_time
test_frontend
test_docker_containers

# Print summary
print_summary
