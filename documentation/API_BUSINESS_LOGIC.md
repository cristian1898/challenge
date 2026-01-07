# API & Business Logic

## Descripción
Este módulo implementa la capa de servicios con lógica de negocio, los endpoints REST completos,
y la aplicación principal FastAPI con middleware personalizado.

## Estructura Creada

```
app/
├── main.py                  # Application entry point and configuration
├── middleware.py            # Custom middleware (logging, security headers)
├── services/
│   ├── __init__.py
│   └── user_service.py      # Business logic layer
└── routers/
    ├── __init__.py
    ├── users.py             # User CRUD endpoints
    └── health.py            # Health check endpoints
```

## Endpoints Implementados

### Users API (`/api/v1/users`)

| Method | Endpoint | Descripción | Status Codes |
|--------|----------|-------------|--------------|
| POST | `/users` | Crear nuevo usuario | 201, 409, 422 |
| GET | `/users` | Listar usuarios (paginado) | 200 |
| GET | `/users/statistics` | Estadísticas de usuarios | 200 |
| GET | `/users/by-username/{username}` | Buscar por username | 200, 404 |
| GET | `/users/by-email/{email}` | Buscar por email | 200, 404 |
| GET | `/users/{id}` | Obtener usuario por ID | 200, 404 |
| PUT | `/users/{id}` | Actualizar usuario | 200, 404, 409, 422 |
| PATCH | `/users/{id}` | Actualización parcial | 200, 404, 409, 422 |
| DELETE | `/users/{id}` | Eliminar usuario | 204, 404 |
| POST | `/users/{id}/deactivate` | Desactivar usuario | 200, 404 |
| POST | `/users/{id}/activate` | Activar usuario | 200, 404 |

### Health API

| Method | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Health check básico |
| GET | `/health/live` | Kubernetes liveness probe |
| GET | `/health/ready` | Kubernetes readiness probe |
| GET | `/health/detailed` | Health check detallado |

## Parámetros de Query (GET /users)

### Paginación
- `page`: Número de página (default: 1)
- `page_size`: Items por página (default: 20, max: 100)

### Filtros
- `username`: Filtro parcial por username
- `email`: Filtro parcial por email
- `first_name`: Filtro parcial por nombre
- `last_name`: Filtro parcial por apellido
- `role`: Filtro exacto por rol (admin/user/guest)
- `active`: Filtro por estado activo (true/false)
- `search`: Búsqueda global en todos los campos de texto

### Ordenamiento
- `sort_by`: Campo para ordenar (default: created_at)
- `sort_desc`: Orden descendente (default: true)

## Ejemplos de API Calls

### Crear Usuario
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "active": true
  }'
```

### Listar Usuarios con Filtros
```bash
curl "http://localhost:8000/api/v1/users?page=1&page_size=10&role=user&active=true&sort_by=username"
```

### Actualizar Usuario
```bash
curl -X PUT http://localhost:8000/api/v1/users/{user_id} \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Johnny",
    "role": "admin"
  }'
```

### Eliminar Usuario
```bash
curl -X DELETE http://localhost:8000/api/v1/users/{user_id}
```

## Middleware Implementado

### RequestLoggingMiddleware
- Genera/extrae Correlation ID para trazabilidad
- Registra método, path, IP del cliente
- Calcula tiempo de procesamiento
- Agrega headers `X-Correlation-ID` y `X-Process-Time`

### SecurityHeadersMiddleware
Headers de seguridad OWASP:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Cache-Control: no-store, no-cache, must-revalidate`

## Manejo de Errores

### Códigos de Error
| Código | HTTP Status | Descripción |
|--------|-------------|-------------|
| NOT_FOUND | 404 | Recurso no encontrado |
| CONFLICT | 409 | Username/email duplicado |
| VALIDATION_ERROR | 422 | Error de validación |
| INTERNAL_ERROR | 500 | Error interno del servidor |

### Formato de Respuesta de Error
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "User with ID 'xxx' not found",
    "details": {
      "resource": "User",
      "resource_id": "xxx"
    }
  }
}
```

## Service Layer Pattern

### Responsabilidades del UserService
1. **Validación de Negocio**: Verificar unicidad de username/email
2. **Orquestación**: Coordinar operaciones del repositorio
3. **Logging**: Registrar operaciones para auditoría
4. **Transformación**: Convertir entidades a DTOs (schemas)

### Flujo de una Solicitud
```
Request → Router → Service → Repository → Database
         ↓           ↓           ↓
      Validation  Business    Data Access
                  Logic
```

## Configuración CORS
```python
origins = ["http://localhost:3000", "http://localhost:8080"]
allow_credentials = True
allow_methods = ["*"]
allow_headers = ["*"]
```

## Documentación OpenAPI
- Swagger UI: `/docs` (solo en modo debug)
- ReDoc: `/redoc` (solo en modo debug)
- OpenAPI JSON: `/openapi.json`

## Ejecutar la Aplicación
```bash
# Desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Producción
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

