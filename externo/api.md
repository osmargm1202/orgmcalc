# API Documentation

## Overview

`orgmcalc` is a shared calculations API for project management. It provides endpoints for managing projects (`proyectos`), companies (`empresas`), engineers (`ingenieros`), calculations (`calculos`), documents (`documentos`), and file storage.

**Base URL**: `http://localhost:8000`

**OpenAPI Documentation**: 
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Markdown: `GET /externo/api-md`

## Getting Started

### Quick Start

```bash
# List all projects
curl -X GET http://localhost:8000/proyectos

# Create a project
curl -X POST http://localhost:8000/proyectos \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Proyecto Demo", "ubicacion": "Ciudad de Guatemala"}'
```

## Authentication

**IMPORTANT**: The API uses a "protected-write boundary" model:

- **GET endpoints** (all read operations): **Public access** - No authentication required
- **POST, PATCH, DELETE endpoints** (write operations): **Require authentication**
- **File uploads** (POST /storage/*): **Require authentication**

### Google OAuth Flow

1. **Initiate OAuth**: Visit `/auth/google` in your browser
2. **Google Consent**: User authenticates with Google
3. **Callback**: Google redirects to `/auth/google/callback?code=...`
4. **Session Created**: API returns a bearer token
5. **Use Token**: Include token in all write requests:
   ```
   Authorization: Bearer <token>
   ```

### Auth Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/auth/google` | No | Start OAuth flow (redirects to Google) |
| GET | `/auth/google/callback` | No | OAuth callback (exchanges code for session) |
| POST | `/auth/logout` | Yes | Revoke current session |
| GET | `/auth/me` | Yes | Get current user info |

## Projects (`/proyectos`)

Projects are the core entities in the system. Each project can have multiple calculations, documents, and be associated with companies and engineers.

### Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/proyectos` | No | List all projects |
| GET | `/proyectos/{id}` | No | Get project by ID |
| POST | `/proyectos` | Yes | Create new project |
| PATCH | `/proyectos/{id}` | Yes | Update project |
| DELETE | `/proyectos/{id}` | Yes | Delete project |

### Examples

#### List Projects

```bash
curl -X GET "http://localhost:8000/proyectos?limit=10&offset=0"
```

**Response**:
```json
[
  {
    "id": 1,
    "nombre": "Edificio Centro",
    "ubicacion": "Ciudad de Guatemala",
    "estado": "activo",
    "fecha": "2024-01-15",
    "id_empresa": 2,
    "id_ingeniero": 3,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "logo_available": false
  }
]
```

#### Get Project

```bash
curl -X GET http://localhost:8000/proyectos/1
```

**Response**:
```json
{
  "id": 1,
  "nombre": "Edificio Centro",
  "ubicacion": "Ciudad de Guatemala",
  "estado": "activo",
  "fecha": "2024-01-15",
  "id_empresa": 2,
  "id_ingeniero": 3,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "logo_available": true
}
```

#### Create Project (Requires Auth)

```bash
curl -X POST http://localhost:8000/proyectos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "nombre": "Nuevo Proyecto",
    "ubicacion": "Antigua Guatemala",
    "estado": "activo",
    "fecha": "2024-03-15",
    "id_empresa": 1,
    "id_ingeniero": 2
  }'
```

**Response** (201 Created):
```json
{
  "id": 42,
  "nombre": "Nuevo Proyecto",
  "ubicacion": "Antigua Guatemala",
  "estado": "activo",
  "fecha": "2024-03-15",
  "id_empresa": 1,
  "id_ingeniero": 2,
  "created_at": "2024-03-15T08:00:00",
  "updated_at": "2024-03-15T08:00:00",
  "logo_available": false
}
```

#### Update Project (Requires Auth)

```bash
curl -X PATCH http://localhost:8000/proyectos/42 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"estado": "completado", "ubicacion": "Quetzaltenango"}'
```

#### Delete Project (Requires Auth)

```bash
curl -X DELETE http://localhost:8000/proyectos/42 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response**: 204 No Content

### Project Logo

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/proyectos/{id}/logo` | No | Download logo (redirects to signed URL) |
| GET | `/proyectos/{id}/logo/status` | No | Check if logo exists |
| POST | `/proyectos/{id}/logo` | Yes | Upload/replace logo |

```bash
# Check logo status
curl -X GET http://localhost:8000/proyectos/1/logo/status

# Upload logo (Requires Auth)
curl -X POST http://localhost:8000/proyectos/1/logo \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@logo.png"
```

## Companies (`/empresas`)

Companies (empresas) can be associated with projects and calculations.

### Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/empresas` | No | List all companies |
| GET | `/empresas/{id}` | No | Get company by ID |
| POST | `/empresas` | Yes | Create company |
| PATCH | `/empresas/{id}` | Yes | Update company |
| DELETE | `/empresas/{id}` | Yes | Delete company |

### Examples

```bash
# List companies
curl -X GET http://localhost:8000/empresas

# Create company (Requires Auth)
curl -X POST http://localhost:8000/empresas \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "nombre": "Constructora ABC",
    "contacto": "Juan Pérez",
    "telefono": "5555-1234",
    "correo": "contacto@abc.com",
    "direccion": "Zona 10, Ciudad de Guatemala",
    "ciudad": "Ciudad de Guatemala"
  }'
```

### Company Logo

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/empresas/{id}/logo` | No | Download logo |
| GET | `/empresas/{id}/logo/status` | No | Check logo status |
| POST | `/empresas/{id}/logo` | Yes | Upload logo |

## Engineers (`/ingenieros`)

Engineers (ingenieros) can be associated with projects and calculations.

### Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/ingenieros` | No | List all engineers |
| GET | `/ingenieros/{id}` | No | Get engineer by ID |
| POST | `/ingenieros` | Yes | Create engineer |
| PATCH | `/ingenieros/{id}` | Yes | Update engineer |
| DELETE | `/ingenieros/{id}` | Yes | Delete engineer |

### Engineer Files

Engineers have three file types:
- **perfil**: Profile photo
- **carnet**: ID card
- **certificacion**: Certification document

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/ingenieros/{id}/perfil` | No | Download profile photo |
| GET | `/ingenieros/{id}/perfil/status` | No | Check profile status |
| POST | `/ingenieros/{id}/perfil` | Yes | Upload profile photo |
| GET | `/ingenieros/{id}/carnet` | No | Download ID card |
| GET | `/ingenieros/{id}/carnet/status` | No | Check ID status |
| POST | `/ingenieros/{id}/carnet` | Yes | Upload ID card |
| GET | `/ingenieros/{id}/certificacion` | No | Download certification |
| GET | `/ingenieros/{id}/certificacion/status` | No | Check cert status |
| POST | `/ingenieros/{id}/certificacion` | Yes | Upload certification |

## Calculations (`/proyectos/{id}/calculos`)

Calculations belong to projects. Each calculation can be linked to multiple companies and engineers.

### Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/proyectos/{id}/calculos` | No | List calculations for project |
| GET | `/proyectos/{id}/calculos/{calculo_id}` | No | Get specific calculation |
| POST | `/proyectos/{id}/calculos` | Yes | Create calculation |
| PATCH | `/proyectos/{id}/calculos/{calculo_id}` | Yes | Update calculation |
| DELETE | `/proyectos/{id}/calculos/{calculo_id}` | Yes | Delete calculation |

### Examples

```bash
# List calculations for project 1
curl -X GET http://localhost:8000/proyectos/1/calculos

# Create calculation (Requires Auth)
curl -X POST http://localhost:8000/proyectos/1/calculos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "codigo": "CALC-001",
    "nombre": "Cálculo de Cimentación",
    "descripcion": "Análisis estructural de cimentación",
    "estado": "borrador"
  }'
```

### Calculation-Company Links

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/proyectos/{id}/calculos/{cid}/empresas` | No | List linked companies |
| POST | `/proyectos/{id}/calculos/{cid}/empresas` | Yes | Link company |
| PATCH | `/proyectos/{id}/calculos/{cid}/empresas/{link_id}` | Yes | Update link |
| DELETE | `/proyectos/{id}/calculos/{cid}/empresas/{link_id}` | Yes | Unlink company |

```bash
# Link company to calculation (Requires Auth)
curl -X POST http://localhost:8000/proyectos/1/calculos/5/empresas \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "empresa_id": 2,
    "rol": "Constructora Principal",
    "orden": 1
  }'
```

### Calculation-Engineer Links

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/proyectos/{id}/calculos/{cid}/ingenieros` | No | List linked engineers |
| POST | `/proyectos/{id}/calculos/{cid}/ingenieros` | Yes | Link engineer |
| PATCH | `/proyectos/{id}/calculos/{cid}/ingenieros/{link_id}` | Yes | Update link |
| DELETE | `/proyectos/{id}/calculos/{cid}/ingenieros/{link_id}` | Yes | Unlink engineer |

## Documents (`/proyectos/{id}/documentos`)

Documents are attached to projects.

### Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/proyectos/{id}/documentos` | No | List documents |
| POST | `/proyectos/{id}/documentos` | Yes | Create document record |
| GET | `/proyectos/{id}/documentos/{doc_id}/file` | No | Download file |
| POST | `/proyectos/{id}/documentos/{doc_id}/file` | Yes | Upload file |

### Examples

```bash
# Create document record (Requires Auth)
curl -X POST http://localhost:8000/proyectos/1/documentos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "nombre_documento": "Plano Estructural.pdf",
    "descripcion": "Plano estructural aprobado"
  }'

# Upload file to document (Requires Auth)
curl -X POST http://localhost:8000/proyectos/1/documentos/10/file \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@plano.pdf"
```

## File Storage

### Supported File Types

- **Images**: `image/png`, `image/jpeg`, `image/webp`, `image/gif`
- **Documents**: `application/pdf`

Maximum file size is determined by your object storage provider.

### Batch Status Check

```bash
# Check multiple files at once
curl -X POST http://localhost:8000/storage/status \
  -H "Content-Type: application/json" \
  -d '{
    "keys": [
      "project/1/logo",
      "empresa/2/logo",
      "ingeniero/3/perfil"
    ]
  }'
```

**Response**:
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
      "storage_key": null
    },
    "ingeniero/3/perfil": {
      "available": true,
      "storage_key": "ingeniero/3/perfil",
      "filename": "perfil.jpg",
      "size_bytes": 15360,
      "content_type": "image/jpeg"
    }
  }
}
```

## Response Formats

### Success Responses

All successful responses return appropriate HTTP status codes:
- `200 OK` - GET, PATCH success
- `201 Created` - POST success (new resource created)
- `204 No Content` - DELETE success
- `302 Found` - Redirect to file download URL

### Error Responses

Errors follow a consistent format:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:

| Code | Meaning | When |
|------|---------|------|
| 400 | Bad Request | Invalid request body, missing required fields |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | Valid token but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error (invalid file type, etc.) |
| 503 | Service Unavailable | Storage service unavailable |

### Example Error Responses

**Validation Error (400)**:
```json
{
  "detail": "Nada que actualizar"
}
```

**Not Found (404)**:
```json
{
  "detail": "Proyecto 123 no encontrado"
}
```

**Unauthorized (401)**:
```json
{
  "detail": "Not authenticated"
}
```

**Invalid File Type (422)**:
```json
{
  "detail": "Tipo de archivo no permitido. Permitidos: imagen (png, jpeg, webp, gif) o PDF"
}
```

## Rate Limiting

Currently, no rate limiting is enforced. In production, consider implementing:
- Request rate limits per IP
- Per-user limits for authenticated endpoints
- File upload size and frequency limits

## API Versioning

This documentation applies to API version **0.1.0**.

The API is currently unversioned in the URL. Future versions may use:
- `/v1/...` prefix for breaking changes
- Header-based versioning: `Accept: application/vnd.orgmcalc.v1+json`

## Compatibility Notes

- Route names use Spanish naming (`/proyectos`, `/empresas`, `/ingenieros`) for compatibility with existing clients
- Field names use snake_case
- Dates use ISO 8601 format: `YYYY-MM-DD` for date fields, `YYYY-MM-DDTHH:MM:SS` for timestamps
- All endpoints support CORS for browser-based clients

## Support

For issues or questions:
- API Health Check: `GET /health`
- OpenAPI Schema: `GET /openapi.json`
