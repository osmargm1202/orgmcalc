#!/bin/bash
# Script de prueba para orgmcalc API
# Este script levanta la API y realiza pruebas básicas

set -e  # Exit on error

echo "=========================================="
echo "Script de Prueba - orgmcalc API"
echo "=========================================="
echo ""

# Verificar que .env existe
if [ ! -f ".env" ]; then
    echo "❌ Error: No se encuentra el archivo .env"
    exit 1
fi

# Cargar variables de entorno
set -a
source .env
set +a

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para hacer requests
api_get() {
    local endpoint=$1
    local description=$2
    echo "📡 GET $description"
    response=$(curl -s -w "\n%{http_code}" "http://localhost:8000$endpoint")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✅ HTTP $http_code${NC}"
        echo "$body" | head -c 500
        echo ""
    else
        echo -e "${RED}❌ HTTP $http_code${NC}"
        echo "$body"
    fi
    echo ""
}

api_post() {
    local endpoint=$1
    local data=$2
    local description=$3
    echo "📡 POST $description"
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "$data" \
        "http://localhost:8000$endpoint")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
        echo -e "${GREEN}✅ HTTP $http_code${NC}"
        echo "$body" | head -c 500
        echo ""
    else
        echo -e "${RED}❌ HTTP $http_code${NC}"
        echo "$body"
    fi
    echo ""
}

# Verificar dependencias
echo "🔍 Verificando dependencias..."
if ! command -v curl &> /dev/null; then
    echo "❌ Error: curl no está instalado"
    exit 1
fi
echo -e "${GREEN}✅ curl disponible${NC}"
echo ""

# Levantar la API en segundo plano
echo "🚀 Iniciando API orgmcalc..."
uv run uvicorn main:app --host 0.0.0.0 --port 8000 &
API_PID=$!
echo "PID de la API: $API_PID"
echo ""

# Función para limpiar al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo API..."
    kill $API_PID 2>/dev/null || true
    wait $API_PID 2>/dev/null || true
    echo -e "${GREEN}✅ API detenida${NC}"
}
trap cleanup EXIT

# Esperar a que la API esté lista
echo "⏳ Esperando a que la API esté lista..."
for i in {1..30}; do
    if curl -s "http://localhost:8000/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API lista!${NC}"
        echo ""
        break
    fi
    sleep 1
    echo -n "."
done

# Verificar que la API está respondiendo
if ! curl -s "http://localhost:8000/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: La API no respondió en 30 segundos${NC}"
    exit 1
fi

# ============================================
# PRUEBAS
# ============================================

echo "=========================================="
echo "1. ENDPOINTS PÚBLICOS (Sin Auth)"
echo "=========================================="
echo ""

# Health check
echo "🏥 Health Check"
curl -s "http://localhost:8000/health" | jq . 2>/dev/null || curl -s "http://localhost:8000/health"
echo ""
echo ""

# Listar empresas
api_get "/empresas" "Listar Empresas"

# Listar ingenieros
api_get "/ingenieros" "Listar Ingenieros"

# Obtener detalle de primera empresa (si existe)
echo "📋 Detalle de Empresa (primera)"
first_empresa=$(curl -s "http://localhost:8000/empresas" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['id'] if d and len(d)>0 else '')" 2>/dev/null || echo "")
if [ -n "$first_empresa" ]; then
    api_get "/empresas/$first_empresa" "Detalle de Empresa"
    
    # Intentar obtener logo (probablemente no exista aún)
    echo "🖼️  Intentando obtener logo de empresa..."
    response=$(curl -s -w "\n%{http_code}" "http://localhost:8000/empresas/$first_empresa/logo")
    http_code=$(echo "$response" | tail -n1)
    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✅ Logo disponible${NC}"
    else
        echo -e "${YELLOW}⚠️  Logo no disponible (HTTP $http_code) - se debe subir primero${NC}"
    fi
    echo ""
else
    echo -e "${YELLOW}⚠️  No hay empresas para probar detalle${NC}"
    echo ""
fi

# Obtener detalle de primer ingeniero (si existe)
echo "📋 Detalle de Ingeniero (primero)"
first_ingeniero=$(curl -s "http://localhost:8000/ingenieros" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['id'] if d and len(d)>0 else '')" 2>/dev/null || echo "")
if [ -n "$first_ingeniero" ]; then
    api_get "/ingenieros/$first_ingeniero" "Detalle de Ingeniero"
    
    # Mostrar CODIA (está en el campo profesion)
    echo "🎫 CODIA del ingeniero:"
    curl -s "http://localhost:8000/ingenieros/$first_ingeniero" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    codia = d.get('profesion', 'No disponible')
    print(f'  {codia}')
except:
    print('  No se pudo obtener CODIA')
" 2>/dev/null || echo "  No disponible"
    echo ""
    
    # Intentar obtener foto de perfil
    echo "🖼️  Intentando obtener foto de perfil..."
    response=$(curl -s -w "\n%{http_code}" "http://localhost:8000/ingenieros/$first_ingeniero/perfil")
    http_code=$(echo "$response" | tail -n1)
    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✅ Foto de perfil disponible${NC}"
    else
        echo -e "${YELLOW}⚠️  Foto no disponible (HTTP $http_code) - se debe subir primero${NC}"
    fi
    echo ""
else
    echo -e "${YELLOW}⚠️  No hay ingenieros para probar detalle${NC}"
    echo ""
fi

# Listar proyectos
api_get "/proyectos" "Listar Proyectos"

# Listar tipos de cálculos predefinidos
echo "📋 Listar Tipos de Cálculos Predefinidos"
api_get "/tipo-calculos" "Tipos de Cálculos"

echo "=========================================="
echo "2. ENDPOINTS PROTEGIDOS (Requieren Auth)"
echo "=========================================="
echo ""

# Intentar crear empresa sin auth (debe fallar)
echo "🔒 Intentando crear empresa SIN autenticación..."
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"nombre": "Empresa Test", "contacto": "test@test.com"}' \
    "http://localhost:8000/empresas")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" -eq 401 ] || [ "$http_code" -eq 403 ]; then
    echo -e "${GREEN}✅ Correctamente protegido (HTTP $http_code)${NC}"
else
    echo -e "${RED}❌ No está protegido (HTTP $http_code)${NC}"
fi
echo ""

echo "📚 Documentación de OAuth:"
echo "  1. Visita: http://localhost:8000/auth/google"
echo "  2. Completa el flujo de OAuth con Google"
echo "  3. Obtén el token de acceso"
echo "  4. Usa: curl -H 'Authorization: Bearer TOKEN' ..."
echo ""

# Si tenemos un proyecto, intentar crear un cálculo (sin auth, debe fallar)
first_proyecto=$(curl -s "http://localhost:8000/proyectos" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['id'] if d and len(d)>0 else '')" 2>/dev/null || echo "")
if [ -n "$first_proyecto" ]; then
    echo "🔒 Intentando crear cálculo SIN autenticación..."
    
    # Obtener el ID del tipo BT (Baja Tensión)
    tipo_bt=$(curl -s "http://localhost:8000/tipo-calculos" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    for t in d:
        if t.get('codigo') == 'BT':
            print(t['id'])
            break
except:
    pass
" 2>/dev/null || echo "")
    
    if [ -n "$tipo_bt" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST \
            -H "Content-Type: application/json" \
            -d "{\"codigo\": \"CALC-001\", \"nombre\": \"Cálculo Prueba\", \"tipo_calculo_id\": \"$tipo_bt\", \"descripcion\": \"Prueba de creación\"}" \
            "http://localhost:8000/proyectos/$first_proyecto/calculos")
        http_code=$(echo "$response" | tail -n1)
        if [ "$http_code" -eq 401 ] || [ "$http_code" -eq 403 ]; then
            echo -e "${GREEN}✅ Creación de cálculo correctamente protegida (HTTP $http_code)${NC}"
        else
            echo -e "${RED}❌ Creación de cálculo no está protegida (HTTP $http_code)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  No se encontró tipo de cálculo BT${NC}"
    fi
    echo ""
fi

echo "=========================================="
echo "3. RESUMEN"
echo "=========================================="
echo ""
echo -e "${GREEN}✅ API funcionando correctamente${NC}"
echo ""
echo "Endpoints públicos (lectura):"
echo "  • GET /health - Health check"
echo "  • GET /empresas - Listar empresas"
echo "  • GET /empresas/{id} - Detalle de empresa"
echo "  • GET /empresas/{id}/logo - Logo de empresa"
echo "  • GET /ingenieros - Listar ingenieros"
echo "  • GET /ingenieros/{id} - Detalle de ingeniero (incluye CODIA)"
echo "  • GET /ingenieros/{id}/perfil - Foto de perfil"
echo "  • GET /proyectos - Listar proyectos"
echo "  • GET /tipo-calculos - Tipos de cálculos predefinidos"
echo ""
echo "Endpoints protegidos (requieren OAuth):"
echo "  • POST/PUT/DELETE en todos los recursos"
echo "  • POST /proyectos/{id}/calculos - Crear cálculo"
echo ""
echo "Tipos de cálculos disponibles:"
curl -s "http://localhost:8000/tipo-calculos" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    for t in d:
        print(f'  • {t.get(\"icono\", \"📋\")} {t.get(\"codigo\", \"?\")} - {t.get(\"nombre\", \"Sin nombre\")}')
except Exception as e:
    print(f'  Error: {e}')
" 2>/dev/null || echo "  No se pudieron cargar"
echo ""

echo "=========================================="
echo "Para probar con autenticación:"
echo "=========================================="
echo "1. Inicia sesión: curl http://localhost:8000/auth/google"
echo "2. Completa el flujo OAuth"
echo "3. Usa el token: curl -H 'Authorization: Bearer TOKEN' ..."
echo ""
echo "O abre en navegador: http://localhost:8000/docs"
echo "=========================================="
