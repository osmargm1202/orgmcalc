#!/bin/bash
# Smoke test script for orgmcalc API
# Tests basic functionality after deployment

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"
echo "Testing orgmcalc API at: $BASE_URL"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Track results
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected=$3
    local description=$4
    local data=$5
    
    if [ -n "$data" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$endpoint" 2>/dev/null || echo "000")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" \
            "$BASE_URL$endpoint" 2>/dev/null || echo "000")
    fi
    
    if [ "$response" = "$expected" ]; then
        echo -e "${GREEN}✓${NC} $description ($method $endpoint -> $response)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $description ($method $endpoint -> $response, expected $expected)"
        ((TESTS_FAILED++))
    fi
}

echo "=== Health Check ==="
test_endpoint "GET" "/health" "200" "Health endpoint"
echo ""

echo "=== Documentation ==="
test_endpoint "GET" "/docs" "200" "Swagger UI"
test_endpoint "GET" "/redoc" "200" "ReDoc UI"
test_endpoint "GET" "/externo/api-md" "200" "API Documentation (Markdown)"
test_endpoint "GET" "/openapi.json" "200" "OpenAPI Schema"
echo ""

echo "=== Authentication (Public Reads) ==="
test_endpoint "GET" "/auth/google" "307" "OAuth redirect"
echo ""

echo "=== Projects (Proyectos) ==="
# GET should work (public)
test_endpoint "GET" "/proyectos" "200" "List proyectos (public)"
test_endpoint "GET" "/proyectos/99999" "404" "Get non-existent proyecto (public)"
# POST/PATCH/DELETE should require auth
test_endpoint "POST" "/proyectos" "403" "Create proyecto requires auth" '{"nombre": "Test"}'
test_endpoint "PATCH" "/proyectos/1" "403" "Update proyecto requires auth" '{"nombre": "Test"}'
test_endpoint "DELETE" "/proyectos/1" "403" "Delete proyecto requires auth"
echo ""

echo "=== Companies (Empresas) ==="
test_endpoint "GET" "/empresas" "200" "List empresas (public)"
test_endpoint "GET" "/empresas/99999" "404" "Get non-existent empresa (public)"
test_endpoint "POST" "/empresas" "403" "Create empresa requires auth" '{"nombre": "Test"}'
echo ""

echo "=== Engineers (Ingenieros) ==="
test_endpoint "GET" "/ingenieros" "200" "List ingenieros (public)"
test_endpoint "GET" "/ingenieros/99999" "404" "Get non-existent ingeniero (public)"
test_endpoint "POST" "/ingenieros" "403" "Create ingeniero requires auth" '{"nombre": "Test"}'
echo ""

echo "=== Calculos ==="
test_endpoint "GET" "/proyectos/99999/calculos" "404" "List calculos (project not found)"
test_endpoint "POST" "/proyectos/1/calculos" "403" "Create calculo requires auth" '{"codigo": "TEST", "nombre": "Test"}'
echo ""

echo "=== Documentos ==="
test_endpoint "GET" "/proyectos/99999/documentos" "404" "List documentos (project not found)"
test_endpoint "POST" "/proyectos/1/documentos" "403" "Create documento requires auth" '{"nombre_documento": "test.pdf"}'
echo ""

echo "=== Storage ==="
test_endpoint "POST" "/storage/status" "200" "Batch file status (public)" '{"keys": ["test/key"]}'
# File uploads should require auth
test_endpoint "POST" "/proyectos/1/logo" "403" "Upload logo requires auth"
test_endpoint "POST" "/empresas/1/logo" "403" "Upload empresa logo requires auth"
test_endpoint "POST" "/ingenieros/1/perfil" "403" "Upload perfil requires auth"
test_endpoint "POST" "/ingenieros/1/carnet" "403" "Upload carnet requires auth"
test_endpoint "POST" "/ingenieros/1/certificacion" "403" "Upload certificacion requires auth"
test_endpoint "POST" "/proyectos/1/documentos/1/file" "403" "Upload documento file requires auth"
echo ""

# Summary
echo "=== Summary ==="
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -gt 0 ]; then
    echo ""
    echo -e "${RED}Smoke tests failed!${NC}"
    exit 1
else
    echo ""
    echo -e "${GREEN}All smoke tests passed!${NC}"
    exit 0
fi
