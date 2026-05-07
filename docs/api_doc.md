# Documentación de API para aplicaciones cliente

## Propósito

`orgmcalc` es una API HTTP para gestionar proyectos, empresas, ingenieros, cálculos, documentos y archivos asociados. La implementación actual usa FastAPI, nombres de rutas en español y un modelo de **lecturas públicas / escrituras protegidas**.

## Base URL

- Local: `http://localhost:8000`
- Ejemplo desplegado: `https://tu-api.ejemplo.com`

Ejemplos completos:

- `http://localhost:8000/proyectos`
- `https://tu-api.ejemplo.com/proyectos`

## Autenticación

### Regla general

- Los endpoints **públicos** no requieren autenticación.
- Los endpoints **protegidos** requieren header:

```http
Authorization: Bearer <access_token>
```

### Contrato real de autenticación

La implementación actual valida tokens bearer **solamente en endpoints protegidos** usando JWKS obtenido desde:

```text
{AUTH_API_URL}/.well-known/jwks.json
```

El token esperado es un **access token JWT RS256** con `kid` y claim `type = access`.

Importante:

- `orgmcalc` **no** expone login, logout, refresh ni callbacks OAuth.
- Los endpoints públicos siguen siendo públicos aunque mandes un `Authorization` inválido.
- No existen rutas legacy como `/auth/google`, `/auth/google/callback`, `/auth/me` o `/auth/logout`.

### Errores de auth en endpoints protegidos

- Sin bearer token: `401 {"detail": "Missing bearer token"}`
- Token inválido, expirado, con firma incorrecta, `kid` desconocido, `alg` no soportado o `type != access`: `401 {"detail": "Invalid token"}`

## Convenciones útiles para clientes

- Las respuestas JSON exitosas usan objetos o listas según el recurso.
- `GET` de archivos devuelve `302 Found` hacia una URL firmada de descarga.
- `DELETE` exitoso devuelve `204 No Content`.
- Las validaciones automáticas de FastAPI/Pydantic devuelven `422` y el detalle puede variar según el campo inválido.
- Algunos mensajes de error vienen de lógica de negocio y otros del framework; cuando el shape puede variar, se indica explícitamente.

Ejemplo típico de `422` de validación:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "nombre"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

## Inventario rápido

### Endpoints públicos

- `GET /health`
- `GET /docs`
- `GET /redoc`
- `GET /openapi.json`
- `GET /externo/api-md`
- `GET /proyectos`
- `GET /proyectos/{project_id}`
- `GET /clientes`
- `GET /clientes/{cliente_id}`
- `GET /empresas`
- `GET /empresas/{empresa_id}`
- `GET /ingenieros`
- `GET /ingenieros/{ingeniero_id}`
- `GET /tipo-calculos`
- `GET /tipo-calculos/{tipo_id}`
- `GET /tipo-calculos/by-codigo/{codigo}`
- `GET /proyectos/{project_id}/calculos`
- `GET /proyectos/{project_id}/calculos/{calculo_id}`
- `GET /proyectos/{project_id}/calculos/{calculo_id}/empresas` _(obsoleto, responde 410)_
- `GET /proyectos/{project_id}/calculos/{calculo_id}/ingenieros` _(obsoleto, responde 410)_
- `GET /proyectos/{project_id}/documentos`
- `GET /proyectos/{project_id}/documentos/{document_id}`
- `GET /proyectos/{project_id}/logo`
- `GET /proyectos/{project_id}/logo/status`
- `GET /proyectos/{project_id}/cliente/logo`
- `GET /proyectos/{project_id}/cliente/logo/status`
- `GET /clientes/{cliente_id}/logo`
- `GET /clientes/{cliente_id}/logo/status`
- `GET /empresas/{empresa_id}/logo`
- `GET /empresas/{empresa_id}/logo/status`
- `GET /ingenieros/{ingeniero_id}/perfil`
- `GET /ingenieros/{ingeniero_id}/perfil/status`
- `GET /ingenieros/{ingeniero_id}/carnet`
- `GET /ingenieros/{ingeniero_id}/carnet/status`
- `GET /ingenieros/{ingeniero_id}/certificacion`
- `GET /ingenieros/{ingeniero_id}/certificacion/status`
- `GET /proyectos/{project_id}/documentos/{document_id}/file`
- `POST /storage/status` _(público aunque sea POST)_

### Endpoints protegidos

- `POST /proyectos`
- `PATCH /proyectos/{project_id}`
- `DELETE /proyectos/{project_id}`
- `POST /clientes`
- `PATCH /clientes/{cliente_id}`
- `DELETE /clientes/{cliente_id}`
- `POST /empresas`
- `PATCH /empresas/{empresa_id}`
- `DELETE /empresas/{empresa_id}`
- `POST /ingenieros`
- `PATCH /ingenieros/{ingeniero_id}`
- `DELETE /ingenieros/{ingeniero_id}`
- `POST /proyectos/{project_id}/calculos`
- `PATCH /proyectos/{project_id}/calculos/{calculo_id}`
- `DELETE /proyectos/{project_id}/calculos/{calculo_id}`
- `POST /proyectos/{project_id}/documentos`
- `DELETE /proyectos/{project_id}/documentos/{document_id}`
- `POST /proyectos/{project_id}/logo`
- `POST /proyectos/{project_id}/cliente/logo`
- `POST /clientes/{cliente_id}/logo`
- `POST /empresas/{empresa_id}/logo`
- `POST /ingenieros/{ingeniero_id}/perfil`
- `POST /ingenieros/{ingeniero_id}/carnet`
- `POST /ingenieros/{ingeniero_id}/certificacion`
- `POST /proyectos/{project_id}/documentos/{document_id}/file`

---

## 1. Salud y documentación

### GET /health
- **Propósito:** verificar que la API está arriba.
- **Auth:** no requerida.
- **Parámetros:** ninguno.
- **Ejemplo:** `curl http://localhost:8000/health`
- **Respuestas:**
  - `200 OK`
    ```json
    {"status": "ok", "version": "0.1.0"}
    ```

### GET /docs
- **Propósito:** interfaz Swagger UI generada por FastAPI.
- **Auth:** no requerida.
- **Parámetros:** ninguno.
- **Ejemplo:** abrir `http://localhost:8000/docs`
- **Respuestas:**
  - `200 OK` con HTML.

### GET /redoc
- **Propósito:** interfaz ReDoc generada por FastAPI.
- **Auth:** no requerida.
- **Parámetros:** ninguno.
- **Ejemplo:** abrir `http://localhost:8000/redoc`
- **Respuestas:**
  - `200 OK` con HTML.

### GET /openapi.json
- **Propósito:** esquema OpenAPI actual de la aplicación.
- **Auth:** no requerida.
- **Parámetros:** ninguno.
- **Ejemplo:** `curl http://localhost:8000/openapi.json`
- **Respuestas:**
  - `200 OK` con JSON OpenAPI. El shape exacto puede variar si cambian rutas o esquemas.

### GET /externo/api-md
- **Propósito:** servir la documentación Markdown publicada en `externo/api.md`.
- **Auth:** no requerida.
- **Parámetros:** ninguno.
- **Ejemplo:** `curl http://localhost:8000/externo/api-md`
- **Respuestas:**
  - `200 OK` con `text/plain`/Markdown.
  - `503 Service Unavailable`
    ```json
    {"detail": "Documentation not available"}
    ```

---

## 2. Proyectos

### GET /proyectos
- **Propósito:** listar proyectos.
- **Auth:** no requerida.
- **Query params:** `offset` (default `0`), `limit` (default `100`, máximo `500`).
- **Ejemplo:** `curl "http://localhost:8000/proyectos?offset=0&limit=2"`
- **Respuestas:**
  - `200 OK`
    ```json
    [
      {
        "id": "proj-uuid",
        "nombre": "Edificio Centro Comercial",
        "cliente_id": "cli-uuid",
        "cliente": {
          "id": "cli-uuid",
          "empresa_id": "emp-uuid",
          "empresa": {"id": "emp-uuid", "nombre": "Constructora ABC S.A."},
          "nombre": "Obra Torre Norte",
          "ubicacion": "Ciudad de Guatemala, Zona 10",
          "telefono": "+502 5555-1234",
          "created_at": "2026-03-29T10:30:00",
          "updated_at": "2026-03-29T10:30:00"
        },
        "ubicacion": "Ciudad de Guatemala, Zona 10",
        "fecha": "2024-03-15",
        "estado": "activo",
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-03-20T14:45:00",
        "logo_available": true,
        "cliente_logo_available": false
      }
    ]
    ```
  - `422` si `offset` o `limit` no cumplen validación.

### GET /proyectos/{project_id}
- **Propósito:** obtener un proyecto por ID.
- **Auth:** no requerida.
- **Path params:** `project_id`.
- **Ejemplo:** `curl http://localhost:8000/proyectos/proj-uuid`
- **Respuestas:**
  - `200 OK` con el mismo shape de `ProjectResponse`.
  - `404 Not Found`
    ```json
    {"detail": "Proyecto proj-uuid no encontrado"}
    ```

### POST /proyectos
- **Propósito:** crear un proyecto.
- **Auth:** requerida.
- **Body:**
  - `nombre` (requerido)
  - `cliente_id` (opcional, referencia a `/clientes/{id}`)
  - `ubicacion` (opcional)
  - `fecha` (opcional, `YYYY-MM-DD`)
  - `estado` (opcional, default `activo`)
- **Ejemplo:**
  ```bash
  curl -X POST http://localhost:8000/proyectos \
    -H "Authorization: Bearer TU_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "nombre": "Proyecto Demo",
      "cliente_id": "cli-uuid",
      "ubicacion": "Santo Domingo",
      "fecha": "2026-03-28",
      "estado": "activo"
    }'
  ```
- **Respuestas:**
  - `201 Created` con `ProjectResponse`.
  - `401` (`Missing bearer token` / `Invalid token`).
  - `422` por body inválido.

### PATCH /proyectos/{project_id}
- **Propósito:** actualizar parcialmente un proyecto.
- **Auth:** requerida.
- **Path params:** `project_id`.
- **Body:** cualquiera de `nombre`, `cliente_id`, `ubicacion`, `fecha`, `estado`.
- **Ejemplo:**
  ```bash
  curl -X PATCH http://localhost:8000/proyectos/proj-uuid \
    -H "Authorization: Bearer TU_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"estado": "completado"}'
  ```
- **Respuestas:**
  - `200 OK` con `ProjectResponse` actualizado.
  - `400 Bad Request`
    ```json
    {"detail": "Nada que actualizar"}
    ```
  - `401` por auth.
  - `404 Not Found`
    ```json
    {"detail": "Proyecto proj-uuid no encontrado"}
    ```

### DELETE /proyectos/{project_id}
- **Propósito:** eliminar un proyecto.
- **Auth:** requerida.
- **Path params:** `project_id`.
- **Ejemplo:**
  ```bash
  curl -X DELETE http://localhost:8000/proyectos/proj-uuid \
    -H "Authorization: Bearer TU_TOKEN"
  ```
- **Respuestas:**
  - `204 No Content`
  - `401` por auth.
  - `404 Not Found`
    ```json
    {"detail": "Proyecto proj-uuid no encontrado"}
    ```

---

## 3. Clientes de proyecto

Un cliente se puede modelar de tres formas:

1. **Cliente empresa**: `empresa_id` definido, sin fallback manual.
2. **Cliente persona**: sin `empresa_id`, usando `nombre`/`ubicacion`/`telefono`.
3. **Cliente mixto**: `empresa_id` + campos fallback manuales.

### GET /clientes
- **Propósito:** listar clientes reutilizables para proyectos.
- **Auth:** no requerida.
- **Query params:** `offset`, `limit`.
- **Respuestas:**
  - `200 OK`
    ```json
    [
      {
        "id": "cli-uuid",
        "empresa_id": "emp-uuid",
        "empresa": {"id": "emp-uuid", "nombre": "Constructora ABC S.A."},
        "nombre": "Obra Torre Norte",
        "ubicacion": "Ciudad de Guatemala, Zona 10",
        "telefono": "+502 5555-1234",
        "created_at": "2026-03-29T10:30:00",
        "updated_at": "2026-03-29T10:30:00"
      }
    ]
    ```

### GET /clientes/{cliente_id}
- **Propósito:** obtener un cliente por ID.
- **Auth:** no requerida.
- **Respuestas:**
  - `200 OK` con `ClienteResponse`.
  - `404 Not Found` con `{"detail": "Cliente cli-uuid no encontrado"}`.

### POST /clientes
- **Propósito:** crear cliente.
- **Auth:** requerida.
- **Body (flexible):** `empresa_id`, `nombre`, `ubicacion`, `telefono` (todos opcionales según el modo de cliente).
- **Ejemplos de body:**
  - Cliente empresa: `{"empresa_id": "emp-uuid"}`
  - Cliente persona: `{"nombre": "Juan Pérez", "ubicacion": "Santo Domingo", "telefono": "+1 809-555-1122"}`
  - Cliente mixto: `{"empresa_id": "emp-uuid", "nombre": "Obra Punta Cana", "telefono": "+1 829-555-0000"}`
- **Respuestas:**
  - `201 Created` con `ClienteResponse`.
  - `400 Bad Request` con `{"detail": "Empresa con ID 'emp-uuid' no existe"}`.
  - `401` por auth.
  - `422` por body inválido.

### PATCH /clientes/{cliente_id}
- **Propósito:** actualizar cliente.
- **Auth:** requerida.
- **Body:** cualquier subconjunto de `empresa_id`, `nombre`, `ubicacion`, `telefono`.
- **Respuestas:**
  - `200 OK` con `ClienteResponse`.
  - `400 Bad Request` con `{"detail": "Nada que actualizar"}` o error de `empresa_id` inválido.
  - `401` por auth.
  - `404 Not Found` con `{"detail": "Cliente cli-uuid no encontrado"}`.

### DELETE /clientes/{cliente_id}
- **Propósito:** eliminar cliente.
- **Auth:** requerida.
- **Respuestas:**
  - `204 No Content`
  - `401` por auth.
  - `404 Not Found` con `{"detail": "Cliente cli-uuid no encontrado"}`.

---

## 4. Empresas

### GET /empresas
- **Propósito:** listar empresas.
- **Auth:** no requerida.
- **Query params:** `offset`, `limit`.
- **Ejemplo:** `curl "http://localhost:8000/empresas?offset=0&limit=2"`
- **Respuestas:**
  - `200 OK`
    ```json
    [
      {
        "id": "emp-uuid",
        "nombre": "Constructora ABC S.A.",
        "url": "https://www.abc.com",
        "contacto": "Juan Pérez",
        "telefono": "+502 5555-1234",
        "correo": "contacto@abc.com",
        "direccion": "12 Calle 5-45, Zona 10",
        "ciudad": "Ciudad de Guatemala",
        "created_at": "2024-01-10T09:00:00",
        "updated_at": "2024-03-15T16:30:00",
        "logo_available": true
      }
    ]
    ```
  - `422` por query inválida.

### GET /empresas/{empresa_id}
- **Propósito:** obtener una empresa por ID.
- **Auth:** no requerida.
- **Path params:** `empresa_id`.
- **Ejemplo:** `curl http://localhost:8000/empresas/emp-uuid`
- **Respuestas:**
  - `200 OK` con `EmpresaResponse`.
  - `404 Not Found`
    ```json
    {"detail": "Empresa emp-uuid no encontrada"}
    ```

### POST /empresas
- **Propósito:** crear una empresa.
- **Auth:** requerida.
- **Body:** `nombre` requerido; `url`, `contacto`, `telefono`, `correo`, `direccion`, `ciudad` opcionales.
- **Ejemplo:**
  ```bash
  curl -X POST http://localhost:8000/empresas \
    -H "Authorization: Bearer TU_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"nombre": "Constructora ABC S.A.", "correo": "contacto@abc.com"}'
  ```
- **Respuestas:**
  - `201 Created` con `EmpresaResponse`.
  - `401` por auth.
  - `422` por body inválido.

### PATCH /empresas/{empresa_id}
- **Propósito:** actualizar una empresa.
- **Auth:** requerida.
- **Path params:** `empresa_id`.
- **Body:** cualquier subconjunto de los campos del recurso.
- **Ejemplo:**
  ```bash
  curl -X PATCH http://localhost:8000/empresas/emp-uuid \
    -H "Authorization: Bearer TU_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"telefono": "+502 5555-5678"}'
  ```
- **Respuestas:**
  - `200 OK` con `EmpresaResponse`.
  - `400 Bad Request` con `{"detail": "Nada que actualizar"}`.
  - `401` por auth.
  - `404 Not Found` con `{"detail": "Empresa emp-uuid no encontrada"}`.

### DELETE /empresas/{empresa_id}
- **Propósito:** eliminar una empresa.
- **Auth:** requerida.
- **Path params:** `empresa_id`.
- **Ejemplo:**
  ```bash
  curl -X DELETE http://localhost:8000/empresas/emp-uuid \
    -H "Authorization: Bearer TU_TOKEN"
  ```
- **Respuestas:**
  - `204 No Content`
  - `401` por auth.
  - `404 Not Found` con `{"detail": "Empresa emp-uuid no encontrada"}`.

---

## 5. Ingenieros

### GET /ingenieros
- **Propósito:** listar ingenieros.
- **Auth:** no requerida.
- **Query params:** `offset`, `limit`, `empresa_id` (opcional para filtrar).
- **Ejemplo:** `curl "http://localhost:8000/ingenieros?empresa_id=emp-uuid"`
- **Respuestas:**
  - `200 OK`
    ```json
    [
      {
        "id": "ing-uuid",
        "nombre": "Ing. María González",
        "email": "maria.gonzalez@email.com",
        "codia": "12345",
        "perfil_available": true,
        "carnet_available": false,
        "certificacion_available": false
      }
    ]
    ```
  - `422` por query inválida.

### GET /ingenieros/{ingeniero_id}
- **Propósito:** obtener un ingeniero por ID.
- **Auth:** no requerida.
- **Path params:** `ingeniero_id`.
- **Ejemplo:** `curl http://localhost:8000/ingenieros/ing-uuid`
- **Respuestas:**
  - `200 OK`
    ```json
    {
      "id": "ing-uuid",
      "nombre": "Ing. María González",
      "email": "maria.gonzalez@email.com",
      "telefono": "+502 5555-9876",
      "codia": "12345",
      "created_at": "2024-01-05T08:00:00",
      "updated_at": "2024-03-10T15:20:00",
      "perfil_available": true,
      "carnet_available": true,
      "certificacion_available": false
    }
    ```
  - `404 Not Found` con `{"detail": "Ingeniero ing-uuid no encontrado"}`.

### POST /ingenieros
- **Propósito:** crear un ingeniero.
- **Auth:** requerida.
- **Body:** `nombre` requerido; `email`, `telefono`, `codia` opcionales.
- **Ejemplo:**
  ```bash
  curl -X POST http://localhost:8000/ingenieros \
    -H "Authorization: Bearer TU_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"nombre": "Ing. María González", "codia": "12345"}'
  ```
- **Respuestas:**
  - `201 Created` con `IngenieroResponse`.
  - `401` por auth.
  - `422` por body inválido.

### PATCH /ingenieros/{ingeniero_id}
- **Propósito:** actualizar un ingeniero.
- **Auth:** requerida.
- **Path params:** `ingeniero_id`.
- **Body:** cualquier subconjunto de `nombre`, `email`, `telefono`, `codia`.
- **Ejemplo:**
  ```bash
  curl -X PATCH http://localhost:8000/ingenieros/ing-uuid \
    -H "Authorization: Bearer TU_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"telefono": "+502 5555-1111"}'
  ```
- **Respuestas:**
  - `200 OK` con `IngenieroResponse`.
  - `400 Bad Request` con `{"detail": "Nada que actualizar"}`.
  - `401` por auth.
  - `404 Not Found` con `{"detail": "Ingeniero ing-uuid no encontrado"}`.

### DELETE /ingenieros/{ingeniero_id}
- **Propósito:** eliminar un ingeniero.
- **Auth:** requerida.
- **Path params:** `ingeniero_id`.
- **Ejemplo:**
  ```bash
  curl -X DELETE http://localhost:8000/ingenieros/ing-uuid \
    -H "Authorization: Bearer TU_TOKEN"
  ```
- **Respuestas:**
  - `204 No Content`
  - `401` por auth.
  - `404 Not Found` con `{"detail": "Ingeniero ing-uuid no encontrado"}`.

---

## 6. Tipos de cálculo

### GET /tipo-calculos
- **Propósito:** listar tipos de cálculo predefinidos.
- **Auth:** no requerida.
- **Query params:**
  - `categoria` (opcional)
  - `solo_activos` (default `true`)
- **Ejemplo:** `curl "http://localhost:8000/tipo-calculos?categoria=electricidad&solo_activos=true"`
- **Respuestas:**
  - `200 OK`
    ```json
    [
      {
        "id": "abc-123",
        "codigo": "BT",
        "nombre": "Cálculo de Baja Tensión",
        "descripcion": "Cálculo de instalaciones eléctricas de baja tensión",
        "categoria": "electricidad",
        "icono": "⚡",
        "color": "#FFD700",
        "orden": 1,
        "activo": true
      }
    ]
    ```

### GET /tipo-calculos/{tipo_id}
- **Propósito:** obtener un tipo de cálculo por ID.
- **Auth:** no requerida.
- **Path params:** `tipo_id`.
- **Ejemplo:** `curl http://localhost:8000/tipo-calculos/abc-123`
- **Respuestas:**
  - `200 OK` con `TipoCalculoResponse`.
  - `404 Not Found`
    ```json
    {"detail": "Tipo de cálculo con ID abc-123 no encontrado"}
    ```
  - `500 Internal Server Error` si falla la obtención de columnas.

### GET /tipo-calculos/by-codigo/{codigo}
- **Propósito:** obtener un tipo de cálculo por código corto.
- **Auth:** no requerida.
- **Path params:** `codigo` (la implementación lo normaliza a mayúsculas).
- **Ejemplo:** `curl http://localhost:8000/tipo-calculos/by-codigo/bt`
- **Respuestas:**
  - `200 OK` con `TipoCalculoResponse`.
  - `404 Not Found`
    ```json
    {"detail": "Tipo de cálculo con código 'bt' no encontrado"}
    ```
  - `500 Internal Server Error` si falla la obtención de columnas.

---

## 7. Cálculos por proyecto

### GET /proyectos/{project_id}/calculos
- **Propósito:** listar cálculos de un proyecto.
- **Auth:** no requerida.
- **Path params:** `project_id`.
- **Query params:** `offset`, `limit`.
- **Ejemplo:** `curl "http://localhost:8000/proyectos/proj-uuid/calculos?limit=10"`
- **Respuestas:**
  - `200 OK`
    ```json
    [
      {
        "id": "calc-uuid",
        "codigo": "CALC-2024-001",
        "nombre": "Cálculo Baja Tensión Edificio A",
        "estado": "borrador",
        "empresa_nombre": "ORGM",
        "ingeniero_nombre": "Osmar Garcia",
        "fecha_creacion": "2024-03-15"
      }
    ]
    ```
  - `404 Not Found` con `{"detail": "Proyecto proj-uuid no encontrado"}`.

### GET /proyectos/{project_id}/calculos/{calculo_id}
- **Propósito:** obtener un cálculo puntual con empresa e ingeniero embebidos.
- **Auth:** no requerida.
- **Path params:** `project_id`, `calculo_id`.
- **Ejemplo:** `curl http://localhost:8000/proyectos/proj-uuid/calculos/calc-uuid`
- **Respuestas:**
  - `200 OK`
    ```json
    {
      "id": "calc-uuid",
      "project_id": "proj-uuid",
      "tipo_calculo_id": "tipo-bt-uuid",
      "codigo": "CALC-2024-001",
      "nombre": "Cálculo Baja Tensión Edificio A",
      "descripcion": "Cálculo de instalación eléctrica",
      "estado": "borrador",
      "empresa": {"id": "emp-uuid", "nombre": "ORGM"},
      "ingeniero": {"id": "ing-uuid", "nombre": "Osmar Garcia", "profesion": "CODIA: 36467"},
      "fecha_creacion": "2024-03-15",
      "created_at": "2024-03-15T09:00:00",
      "updated_at": "2024-03-20T16:45:00"
    }
    ```
  - `404 Not Found` si no existe proyecto o cálculo.

### POST /proyectos/{project_id}/calculos
- **Propósito:** crear un cálculo dentro de un proyecto.
- **Auth:** requerida.
- **Path params:** `project_id`.
- **Body requerido:** `codigo`, `nombre`, `tipo_calculo_id`, `empresa_id`, `ingeniero_id`.
- **Body opcional:** `descripcion`, `estado`.
- **Reglas de negocio actuales:**
  - la empresa debe existir,
  - el ingeniero debe existir,
  - el ingeniero debe poder trabajar para esa empresa,
  - el `codigo` debe ser único dentro del proyecto.
- **Ejemplo:**
  ```bash
  curl -X POST http://localhost:8000/proyectos/proj-uuid/calculos \
    -H "Authorization: Bearer TU_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "codigo": "CALC-2024-001",
      "nombre": "Cálculo BT",
      "descripcion": "Primera versión",
      "estado": "borrador",
      "tipo_calculo_id": "tipo-bt-uuid",
      "empresa_id": "emp-uuid",
      "ingeniero_id": "ing-uuid"
    }'
  ```
- **Respuestas:**
  - `201 Created` con `CalculoResponse`.
  - `400 Bad Request`, por ejemplo:
    ```json
    {"detail": "Empresa con ID 'emp-uuid' no existe"}
    ```
    o
    ```json
    {"detail": "Ingeniero con ID 'ing-uuid' no existe"}
    ```
    o
    ```json
    {"detail": "El ingeniero 'ing-uuid' no está autorizado a trabajar para la empresa 'emp-uuid'"}
    ```
  - `401` por auth.
  - `404 Not Found` con `{"detail": "Proyecto proj-uuid no encontrado"}`.
  - `409 Conflict`
    ```json
    {"detail": "Ya existe un cálculo con el código 'CALC-2024-001' en este proyecto"}
    ```
  - `422` por body inválido.

### PATCH /proyectos/{project_id}/calculos/{calculo_id}
- **Propósito:** actualizar un cálculo.
- **Auth:** requerida.
- **Path params:** `project_id`, `calculo_id`.
- **Body:** cualquier subconjunto de `codigo`, `nombre`, `descripcion`, `estado`, `empresa_id`, `ingeniero_id`.
- **Ejemplo:**
  ```bash
  curl -X PATCH http://localhost:8000/proyectos/proj-uuid/calculos/calc-uuid \
    -H "Authorization: Bearer TU_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"estado": "en_progreso"}'
  ```
- **Respuestas:**
  - `200 OK` con `CalculoResponse`.
  - `400 Bad Request` con `{"detail": "Nada que actualizar"}` o con errores de validación de empresa/ingeniero.
  - `401` por auth.
  - `404 Not Found` si no existe proyecto o cálculo.
  - `409 Conflict` si el nuevo código colisiona dentro del proyecto.

### DELETE /proyectos/{project_id}/calculos/{calculo_id}
- **Propósito:** eliminar un cálculo.
- **Auth:** requerida.
- **Path params:** `project_id`, `calculo_id`.
- **Ejemplo:**
  ```bash
  curl -X DELETE http://localhost:8000/proyectos/proj-uuid/calculos/calc-uuid \
    -H "Authorization: Bearer TU_TOKEN"
  ```
- **Respuestas:**
  - `204 No Content`
  - `401` por auth.
  - `404 Not Found` si no existe proyecto o cálculo.

### GET /proyectos/{project_id}/calculos/{calculo_id}/empresas
- **Propósito:** endpoint obsoleto.
- **Auth:** no requerida.
- **Ejemplo:** `curl http://localhost:8000/proyectos/proj-uuid/calculos/calc-uuid/empresas`
- **Respuestas:**
  - `410 Gone`
    ```json
    {"detail": "Este endpoint está obsoleto. La empresa está disponible directamente en el objeto cálculo (campo empresa)."}
    ```

### GET /proyectos/{project_id}/calculos/{calculo_id}/ingenieros
- **Propósito:** endpoint obsoleto.
- **Auth:** no requerida.
- **Ejemplo:** `curl http://localhost:8000/proyectos/proj-uuid/calculos/calc-uuid/ingenieros`
- **Respuestas:**
  - `410 Gone`
    ```json
    {"detail": "Este endpoint está obsoleto. El ingeniero está disponible directamente en el objeto cálculo (campo ingeniero)."}
    ```

---

## 8. Documentos por proyecto

### GET /proyectos/{project_id}/documentos
- **Propósito:** listar documentos de un proyecto.
- **Auth:** no requerida.
- **Path params:** `project_id`.
- **Query params:** `offset`, `limit`.
- **Ejemplo:** `curl http://localhost:8000/proyectos/proj-uuid/documentos`
- **Respuestas:**
  - `200 OK`
    ```json
    [
      {
        "id": 1,
        "nombre_documento": "Plano Estructural Rev A.pdf",
        "descripcion": "Plano estructural aprobado",
        "file_available": true,
        "created_at": "2024-02-01T10:00:00"
      }
    ]
    ```
  - `404 Not Found` con `{"detail": "Proyecto proj-uuid no encontrado"}`.

### GET /proyectos/{project_id}/documentos/{document_id}
- **Propósito:** obtener metadata de un documento.
- **Auth:** no requerida.
- **Path params:** `project_id`, `document_id`.
- **Ejemplo:** `curl http://localhost:8000/proyectos/proj-uuid/documentos/1`
- **Respuestas:**
  - `200 OK`
    ```json
    {
      "id": 1,
      "project_id": 5,
      "nombre_documento": "Plano Estructural Rev A.pdf",
      "descripcion": "Plano estructural aprobado",
      "file_available": true,
      "created_at": "2024-02-01T10:00:00",
      "updated_at": "2024-02-15T14:30:00"
    }
    ```
  - `404 Not Found` si no existe proyecto o documento.

### POST /proyectos/{project_id}/documentos
- **Propósito:** crear el registro de un documento. El archivo se sube aparte.
- **Auth:** requerida.
- **Path params:** `project_id`.
- **Body:** `nombre_documento` requerido, `descripcion` opcional.
- **Ejemplo:**
  ```bash
  curl -X POST http://localhost:8000/proyectos/proj-uuid/documentos \
    -H "Authorization: Bearer TU_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"nombre_documento": "Plano Estructural Rev A.pdf", "descripcion": "Aprobado"}'
  ```
- **Respuestas:**
  - `201 Created` con `DocumentoResponse`.
  - `401` por auth.
  - `404 Not Found` con `{"detail": "Proyecto proj-uuid no encontrado"}`.
  - `422` por body inválido.

### DELETE /proyectos/{project_id}/documentos/{document_id}
- **Propósito:** eliminar un documento.
- **Auth:** requerida.
- **Path params:** `project_id`, `document_id`.
- **Ejemplo:**
  ```bash
  curl -X DELETE http://localhost:8000/proyectos/proj-uuid/documentos/1 \
    -H "Authorization: Bearer TU_TOKEN"
  ```
- **Respuestas:**
  - `204 No Content`
  - `401` por auth.
  - `404 Not Found` si no existe proyecto o documento.

---

## 9. Archivos y storage

### Formato general de uploads

Los uploads usan `multipart/form-data` con un campo llamado **`file`**.

Tipos MIME permitidos:

- `image/png`
- `image/jpeg`
- `image/webp`
- `image/gif`
- `application/pdf`

Si el tipo no está permitido:

```json
{
  "detail": "Tipo de archivo no permitido. Permitidos: imagen (png, jpeg, webp, gif) o PDF"
}
```

Respuesta exitosa de upload (shape actual):

```json
{
  "storage_key": "ingenieros/osmar-garcia-d2c2d3d/carnet.jpg",
  "url": "https://storage.example.com/...",
  "filename": "osmar-garcia_36467.jpg",
  "content_type": "image/jpeg"
}
```

`url` puede venir `null` o variar según el backend de almacenamiento.

### Convención de nombre y reemplazo

- La API genera un `filename` amigable (ej: `osmar-garcia_36467.jpg`) y también expone `content_type`.
- La app cliente debe usar ese `filename` para guardar el archivo local y `content_type` para decidir preview/visor.
- Al subir una nueva versión del mismo asset (`logo`, `perfil`, `carnet`, etc.), la API deja una sola metadata activa y elimina el objeto físico anterior cuando cambia la key (por ejemplo, al cambiar de `.jpg` a `.pdf`).
- Convención de carpetas en storage:
  - Ingenieros: `ingenieros/{nombre-slug}-{id8}/{documento}.{ext}`
  - Empresas: `empresas/{nombre-slug}-{id8}/logo.{ext}`
  - Clientes: `clientes/{nombre-slug}-{id8}/logo.{ext}`

### Modelo `FileStatus`

```json
{
  "available": true,
  "storage_key": "project/1/logo",
  "filename": "logo.png",
  "size_bytes": 20480,
  "content_type": "image/png"
}
```

Cuando no existe archivo, la respuesta puede ser:

```json
{
  "available": false,
  "storage_key": null,
  "filename": null,
  "size_bytes": null,
  "content_type": null
}
```

### GET /proyectos/{project_id}/logo
- **Propósito:** descargar logo del proyecto.
- **Auth:** no requerida.
- **Path params:** `project_id`.
- **Ejemplo:** `curl -i http://localhost:8000/proyectos/proj-uuid/logo`
- **Respuestas:**
  - `302 Found` sin body JSON; el header `Location` apunta a la URL firmada.
  - `404 Not Found`
    ```json
    {"detail": "Proyecto proj-uuid no encontrado"}
    ```
    o
    ```json
    {"detail": "Logo no encontrado"}
    ```

### GET /proyectos/{project_id}/logo/status
- **Propósito:** consultar estado del logo del proyecto.
- **Auth:** no requerida.
- **Path params:** `project_id`.
- **Ejemplo:** `curl http://localhost:8000/proyectos/proj-uuid/logo/status`
- **Respuestas:**
  - `200 OK`
    ```json
    {
      "available": true,
      "storage_key": "project/proj-uuid/logo",
      "filename": "logo.png",
      "size_bytes": 20480,
      "content_type": "image/png"
    }
    ```
  - `404 Not Found`
    ```json
    {"detail": "Proyecto proj-uuid no encontrado"}
    ```

### POST /proyectos/{project_id}/logo
- **Propósito:** subir o reemplazar logo del proyecto.
- **Auth:** requerida.
- **Path params:** `project_id`.
- **Body:** multipart con `file`.
- **Ejemplo:**
  ```bash
  curl -X POST http://localhost:8000/proyectos/proj-uuid/logo \
    -H "Authorization: Bearer TU_TOKEN" \
    -F "file=@logo.png"
  ```
- **Respuestas:**
  - `200 OK`
    ```json
    {"storage_key": "project/proj-uuid/logo", "url": "https://storage.example.com/..."}
    ```
  - `401` por auth.
  - `404 Not Found`
    ```json
    {"detail": "Proyecto proj-uuid no encontrado"}
    ```
  - `422 Unprocessable Entity`
    ```json
    {"detail": "Tipo de archivo no permitido. Permitidos: imagen (png, jpeg, webp, gif) o PDF"}
    ```
  - `503 Service Unavailable`
    ```json
    {"detail": "Almacenamiento no disponible"}
    ```

### GET /proyectos/{project_id}/cliente/logo
- **Propósito:** descargar logo del cliente del proyecto.
- **Auth:** no requerida.
- **Path params:** `project_id`.
- **Ejemplo:** `curl -i http://localhost:8000/proyectos/proj-uuid/cliente/logo`
- **Respuestas:**
  - `302 Found` sin body JSON.
  - `404 Not Found`
    ```json
    {"detail": "Proyecto proj-uuid no encontrado"}
    ```
    o
    ```json
    {"detail": "Logo de cliente no encontrado"}
    ```

### GET /proyectos/{project_id}/cliente/logo/status
- **Propósito:** estado del logo del cliente del proyecto.
- **Auth:** no requerida.
- **Path params:** `project_id`.
- **Ejemplo:** `curl http://localhost:8000/proyectos/proj-uuid/cliente/logo/status`
- **Respuestas:**
  - `200 OK` con el mismo shape de `FileStatus`.
  - `404 Not Found`
    ```json
    {"detail": "Proyecto proj-uuid no encontrado"}
    ```

### POST /proyectos/{project_id}/cliente/logo
- **Propósito:** subir o reemplazar logo del cliente del proyecto.
- **Auth:** requerida.
- **Path params:** `project_id`.
- **Body:** multipart con `file`.
- **Ejemplo:**
  ```bash
  curl -X POST http://localhost:8000/proyectos/proj-uuid/cliente/logo \
    -H "Authorization: Bearer TU_TOKEN" \
    -F "file=@cliente.png"
  ```
- **Respuestas:**
  - `200 OK`
    ```json
    {
      "storage_key": "projects/proj-uuid/cliente/logo.png",
      "url": "https://storage.example.com/...",
      "filename": "obra-punta-cana_logo.png",
      "content_type": "image/png"
    }
    ```
  - `401`, `404`, `422`, `503` con el mismo patrón del upload anterior.

### GET /clientes/{cliente_id}/logo
- **Propósito:** descargar logo de cliente.
- **Auth:** no requerida.
- **Path params:** `cliente_id`.
- **Ejemplo:** `curl -i http://localhost:8000/clientes/cli-uuid/logo`
- **Respuestas:**
  - `302 Found` sin body JSON.
  - `404 Not Found`
    ```json
    {"detail": "Cliente cli-uuid no encontrado"}
    ```
    o
    ```json
    {"detail": "Logo no encontrado"}
    ```

### GET /clientes/{cliente_id}/logo/status
- **Propósito:** estado del logo de cliente.
- **Auth:** no requerida.
- **Path params:** `cliente_id`.
- **Ejemplo:** `curl http://localhost:8000/clientes/cli-uuid/logo/status`
- **Respuestas:**
  - `200 OK` con `FileStatus`.
  - `404 Not Found`
    ```json
    {"detail": "Cliente cli-uuid no encontrado"}
    ```

### POST /clientes/{cliente_id}/logo
- **Propósito:** subir o reemplazar logo de cliente.
- **Auth:** requerida.
- **Path params:** `cliente_id`.
- **Body:** multipart con `file`.
- **Ejemplo:**
  ```bash
  curl -X POST http://localhost:8000/clientes/cli-uuid/logo \
    -H "Authorization: Bearer TU_TOKEN" \
    -F "file=@cliente.png"
  ```
- **Respuestas:**
  - `200 OK`
    ```json
    {
      "storage_key": "clientes/obra-punta-cana-2a9f87c1/logo.png",
      "url": "https://storage.example.com/...",
      "filename": "obra-punta-cana_logo.png",
      "content_type": "image/png"
    }
    ```
  - `401`, `404`, `422`, `503`.

### GET /empresas/{empresa_id}/logo
- **Propósito:** descargar logo de empresa.
- **Auth:** no requerida.
- **Path params:** `empresa_id`.
- **Ejemplo:** `curl -i http://localhost:8000/empresas/emp-uuid/logo`
- **Respuestas:**
  - `302 Found` sin body JSON.
  - `404 Not Found`
    ```json
    {"detail": "Empresa emp-uuid no encontrada"}
    ```
    o
    ```json
    {"detail": "Logo no encontrado"}
    ```

### GET /empresas/{empresa_id}/logo/status
- **Propósito:** estado del logo de empresa.
- **Auth:** no requerida.
- **Path params:** `empresa_id`.
- **Ejemplo:** `curl http://localhost:8000/empresas/emp-uuid/logo/status`
- **Respuestas:**
  - `200 OK` con `FileStatus`.
  - `404 Not Found`
    ```json
    {"detail": "Empresa emp-uuid no encontrada"}
    ```

### POST /empresas/{empresa_id}/logo
- **Propósito:** subir o reemplazar logo de empresa.
- **Auth:** requerida.
- **Path params:** `empresa_id`.
- **Body:** multipart con `file`.
- **Ejemplo:**
  ```bash
  curl -X POST http://localhost:8000/empresas/emp-uuid/logo \
    -H "Authorization: Bearer TU_TOKEN" \
    -F "file=@logo.png"
  ```
- **Respuestas:**
  - `200 OK`
    ```json
    {
      "storage_key": "empresas/orgm-57a21c18/logo.png",
      "url": "https://storage.example.com/...",
      "filename": "orgm_logo.png",
      "content_type": "image/png"
    }
    ```
  - `401`, `404`, `422`, `503`.

### GET /ingenieros/{ingeniero_id}/perfil
- **Propósito:** descargar foto de perfil.
- **Auth:** no requerida.
- **Path params:** `ingeniero_id`.
- **Ejemplo:** `curl -i http://localhost:8000/ingenieros/ing-uuid/perfil`
- **Respuestas:**
  - `302 Found` sin body JSON.
  - `404 Not Found`
    ```json
    {"detail": "Ingeniero ing-uuid no encontrado"}
    ```
    o
    ```json
    {"detail": "Perfil no encontrado"}
    ```

### GET /ingenieros/{ingeniero_id}/perfil/status
- **Propósito:** estado del perfil.
- **Auth:** no requerida.
- **Path params:** `ingeniero_id`.
- **Ejemplo:** `curl http://localhost:8000/ingenieros/ing-uuid/perfil/status`
- **Respuestas:**
  - `200 OK` con `FileStatus`.
  - `404 Not Found`
    ```json
    {"detail": "Ingeniero ing-uuid no encontrado"}
    ```

### POST /ingenieros/{ingeniero_id}/perfil
- **Propósito:** subir o reemplazar foto de perfil.
- **Auth:** requerida.
- **Path params:** `ingeniero_id`.
- **Body:** multipart con `file`.
- **Ejemplo:**
  ```bash
  curl -X POST http://localhost:8000/ingenieros/ing-uuid/perfil \
    -H "Authorization: Bearer TU_TOKEN" \
    -F "file=@perfil.jpg"
  ```
- **Respuestas:**
  - `200 OK`
    ```json
    {
      "storage_key": "ingenieros/osmar-garcia-d2c2d3d3/perfil.jpg",
      "url": "https://storage.example.com/...",
      "filename": "osmar-garcia_perfil.jpg",
      "content_type": "image/jpeg"
    }
    ```
  - `401`, `404`, `422`, `503`.

### GET /ingenieros/{ingeniero_id}/carnet
- **Propósito:** descargar carnet del ingeniero.
- **Auth:** no requerida.
- **Path params:** `ingeniero_id`.
- **Ejemplo:** `curl -i http://localhost:8000/ingenieros/ing-uuid/carnet`
- **Respuestas:**
  - `302 Found` sin body JSON.
  - `404 Not Found`
    ```json
    {"detail": "Ingeniero ing-uuid no encontrado"}
    ```
    o
    ```json
    {"detail": "Carnet no encontrado"}
    ```

### GET /ingenieros/{ingeniero_id}/carnet/status
- **Propósito:** estado del carnet.
- **Auth:** no requerida.
- **Path params:** `ingeniero_id`.
- **Ejemplo:** `curl http://localhost:8000/ingenieros/ing-uuid/carnet/status`
- **Respuestas:**
  - `200 OK` con `FileStatus`.
  - `404 Not Found`
    ```json
    {"detail": "Ingeniero ing-uuid no encontrado"}
    ```

### POST /ingenieros/{ingeniero_id}/carnet
- **Propósito:** subir o reemplazar carnet.
- **Auth:** requerida.
- **Path params:** `ingeniero_id`.
- **Body:** multipart con `file`.
- **Ejemplo:**
  ```bash
  curl -X POST http://localhost:8000/ingenieros/ing-uuid/carnet \
    -H "Authorization: Bearer TU_TOKEN" \
    -F "file=@carnet.pdf"
  ```
- **Respuestas:**
  - `200 OK`
    ```json
    {
      "storage_key": "ingenieros/osmar-garcia-d2c2d3d3/carnet.jpg",
      "url": "https://storage.example.com/...",
      "filename": "osmar-garcia_36467.jpg",
      "content_type": "image/jpeg"
    }
    ```
  - `401`, `404`, `422`, `503`.

### GET /ingenieros/{ingeniero_id}/certificacion
- **Propósito:** descargar certificación del ingeniero.
- **Auth:** no requerida.
- **Path params:** `ingeniero_id`.
- **Ejemplo:** `curl -i http://localhost:8000/ingenieros/ing-uuid/certificacion`
- **Respuestas:**
  - `302 Found` sin body JSON.
  - `404 Not Found`
    ```json
    {"detail": "Ingeniero ing-uuid no encontrado"}
    ```
    o
    ```json
    {"detail": "Certificacion no encontrada"}
    ```

### GET /ingenieros/{ingeniero_id}/certificacion/status
- **Propósito:** estado de la certificación.
- **Auth:** no requerida.
- **Path params:** `ingeniero_id`.
- **Ejemplo:** `curl http://localhost:8000/ingenieros/ing-uuid/certificacion/status`
- **Respuestas:**
  - `200 OK` con `FileStatus`.
  - `404 Not Found`
    ```json
    {"detail": "Ingeniero ing-uuid no encontrado"}
    ```

### POST /ingenieros/{ingeniero_id}/certificacion
- **Propósito:** subir o reemplazar certificación.
- **Auth:** requerida.
- **Path params:** `ingeniero_id`.
- **Body:** multipart con `file`.
- **Ejemplo:**
  ```bash
  curl -X POST http://localhost:8000/ingenieros/ing-uuid/certificacion \
    -H "Authorization: Bearer TU_TOKEN" \
    -F "file=@certificacion.pdf"
  ```
- **Respuestas:**
  - `200 OK`
    ```json
    {
      "storage_key": "ingenieros/osmar-garcia-d2c2d3d3/certificacion.pdf",
      "url": "https://storage.example.com/...",
      "filename": "osmar-garcia_certificacion.pdf",
      "content_type": "application/pdf"
    }
    ```
  - `401`, `404`, `422`, `503`.

### GET /proyectos/{project_id}/documentos/{document_id}/file
- **Propósito:** descargar el archivo físico asociado a un documento.
- **Auth:** no requerida.
- **Ejemplo:** `curl -i http://localhost:8000/proyectos/proj-uuid/documentos/1/file`
- **Respuestas:**
  - `302 Found` hacia URL firmada.
  - `404 Not Found` con `{"detail": "Proyecto proj-uuid no encontrado"}` o `{"detail": "Archivo no encontrado"}`.

### POST /proyectos/{project_id}/documentos/{document_id}/file
- **Propósito:** subir o reemplazar el archivo de un documento.
- **Auth:** requerida.
- **Body:** multipart con `file`.
- **Ejemplo:**
  ```bash
  curl -X POST http://localhost:8000/proyectos/proj-uuid/documentos/1/file \
    -H "Authorization: Bearer TU_TOKEN" \
    -F "file=@plano.pdf"
  ```
- **Respuestas:**
  - `200 OK` con `{storage_key, url}`.
  - `401` por auth.
  - `404 Not Found` con `{"detail": "Proyecto proj-uuid no encontrado"}`.
  - `422` por archivo inválido o por faltar el campo `file`.
  - `503 Service Unavailable` con `{"detail": "Almacenamiento no disponible"}`.

### POST /storage/status
- **Propósito:** consultar disponibilidad de múltiples archivos en lote.
- **Auth:** no requerida.
- **Nota:** aunque es `POST`, hoy es un endpoint público.
- **Body:**
  ```json
  {
    "keys": ["project/1/logo", "empresa/2/logo", "ingeniero/3/perfil"]
  }
  ```
- **Ejemplo:**
  ```bash
  curl -X POST http://localhost:8000/storage/status \
    -H "Content-Type: application/json" \
    -d '{"keys": ["project/1/logo", "empresa/2/logo"]}'
  ```
- **Respuestas:**
  - `200 OK`
    ```json
    {
      "statuses": {
        "project/1/logo": {
          "available": true,
          "storage_key": "project/1/logo",
          "filename": "logo.png",
          "size_bytes": 20480,
          "content_type": "image/png"
        },
        "empresa/2/logo": {
          "available": false,
          "storage_key": null,
          "filename": null,
          "size_bytes": null,
          "content_type": null
        }
      }
    }
    ```
  - `422` si `keys` viene vacío o supera el límite del schema.

---

## 10. Resumen de errores comunes para apps cliente

### Auth

```json
{"detail": "Missing bearer token"}
```

```json
{"detail": "Invalid token"}
```

### No encontrado

```json
{"detail": "Proyecto proj-uuid no encontrado"}
```

```json
{"detail": "Cliente cli-uuid no encontrado"}
```

```json
{"detail": "Empresa emp-uuid no encontrada"}
```

```json
{"detail": "Ingeniero ing-uuid no encontrado"}
```

### Nada que actualizar

```json
{"detail": "Nada que actualizar"}
```

### Validaciones de negocio en cálculos

```json
{"detail": "Empresa con ID 'emp-uuid' no existe"}
```

```json
{"detail": "Ingeniero con ID 'ing-uuid' no existe"}
```

```json
{"detail": "El ingeniero 'ing-uuid' no está autorizado a trabajar para la empresa 'emp-uuid'"}
```

```json
{"detail": "Ya existe un cálculo con el código 'CALC-2024-001' en este proyecto"}
```

### Uploads / almacenamiento

```json
{"detail": "Tipo de archivo no permitido. Permitidos: imagen (png, jpeg, webp, gif) o PDF"}
```

```json
{"detail": "Almacenamiento no disponible"}
```

### Validación automática del framework

La respuesta exacta puede variar según el campo y el tipo de error, pero el formato general es:

```json
{
  "detail": [
    {
      "type": "string_too_long",
      "loc": ["body", "nombre"],
      "msg": "String should have at most 255 characters",
      "input": "..."
    }
  ]
}
```

---

## 11. Notas finales para integradores

- Si tu app solo consume información, podés trabajar con los `GET` públicos sin token.
- Si tu app crea, edita, elimina o sube archivos, necesitás un bearer access token válido.
- Para archivos, tratá los `302` como parte del flujo normal de descarga.
- Para validaciones `422`, no hardcodees un único mensaje: procesá el array `detail` cuando exista.
- El shape de `openapi.json` y de la documentación HTML puede cambiar con la evolución de la API; tomalos como endpoints auxiliares, no como contrato funcional principal.
