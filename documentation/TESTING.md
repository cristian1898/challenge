# Testing & Error Handling

## Descripción
Este módulo implementa una suite de tests completa usando pytest con soporte async,
fixtures reutilizables, y factories para generación de datos de prueba.

## Estructura de Tests

```
tests/
├── __init__.py
├── conftest.py          # Fixtures compartidas y configuración
├── test_users.py        # Tests de integración para endpoints
├── test_services.py     # Tests unitarios para service layer
├── test_health.py       # Tests para health endpoints
└── test_schemas.py      # Tests de validación de schemas
```

## Configuración de Testing

### pytest.ini
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
addopts = -v --tb=short --strict-markers
```

### Dependencias
```
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
pytest-mock==3.12.0
factory-boy==3.3.0
faker==22.0.0
```

## Fixtures Principales

### Database Fixtures
- `test_engine`: Motor de base de datos en memoria (SQLite)
- `db_session`: Sesión de base de datos aislada por test
- `client`: Cliente HTTP async para tests de integración

### Factory Fixtures
- `user_factory`: Factory para crear usuarios de prueba
- `sample_user`: Usuario regular pre-creado
- `admin_user`: Usuario admin pre-creado
- `inactive_user`: Usuario inactivo pre-creado

### Data Fixtures
- `valid_user_data`: Datos válidos para creación de usuario
- `invalid_user_data_samples`: Ejemplos de datos inválidos

## Tipos de Tests

### Tests de Integración (`test_users.py`)
Prueban el flujo completo request → response

| Test Class | Endpoints Cubiertos |
|------------|---------------------|
| TestCreateUser | POST /users |
| TestGetUser | GET /users/{id}, /by-username, /by-email |
| TestListUsers | GET /users (paginación, filtros, orden) |
| TestUpdateUser | PUT /users/{id}, PATCH /users/{id} |
| TestDeleteUser | DELETE /users/{id} |
| TestUserActivation | POST /users/{id}/activate, /deactivate |
| TestUserStatistics | GET /users/statistics |

### Tests Unitarios (`test_services.py`)
Prueban la lógica de negocio aislada

| Test Class | Métodos Cubiertos |
|------------|-------------------|
| TestUserServiceCreate | create_user() |
| TestUserServiceGet | get_user(), get_by_username(), get_by_email() |
| TestUserServiceList | list_users() con paginación y filtros |
| TestUserServiceUpdate | update_user() |
| TestUserServiceDelete | delete_user() |
| TestUserServiceActivation | activate_user(), deactivate_user() |
| TestUserServiceStatistics | get_user_statistics() |

### Tests de Validación (`test_schemas.py`)
Prueban las reglas de validación de Pydantic

| Test Class | Validaciones |
|------------|--------------|
| TestUserCreateValidation | username, email, names, role, defaults |
| TestUserUpdateValidation | partial updates, campo requerido |

## Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=app --cov-report=html

# Solo tests específicos
pytest tests/test_users.py

# Tests con output verbose
pytest -v --tb=long

# Ejecutar test específico
pytest tests/test_users.py::TestCreateUser::test_create_user_success
```

## Cobertura de Código

Meta de cobertura: **>80%**

Áreas cubiertas:
- ✅ Endpoints CRUD completos
- ✅ Service layer business logic
- ✅ Schema validation rules
- ✅ Error handling
- ✅ Health checks
- ✅ Edge cases (duplicates, not found, validation errors)

## Patrón de Testing

### Arrange-Act-Assert (AAA)
```python
@pytest.mark.asyncio
async def test_create_user_success(self, client, valid_user_data):
    # Arrange - datos ya preparados en fixture
    
    # Act
    response = await client.post("/api/v1/users", json=valid_user_data)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["username"] == valid_user_data["username"]
```

### Factory Pattern
```python
# Crear un usuario
user = await user_factory.create(
    username="custom",
    role=UserRole.ADMIN,
)

# Crear múltiples usuarios
users = await user_factory.create_batch(10)
```

## Manejo de Base de Datos en Tests

- Cada test usa una base de datos SQLite en memoria
- Las tablas se crean antes de cada test
- Las transacciones se hacen rollback después de cada test
- Aislamiento completo entre tests

## Casos de Error Cubiertos

| Código | Escenario | Test |
|--------|-----------|------|
| 404 | Usuario no encontrado | test_get_user_not_found |
| 409 | Username duplicado | test_create_user_duplicate_username |
| 409 | Email duplicado | test_create_user_duplicate_email |
| 422 | Email inválido | test_create_user_invalid_email |
| 422 | Username muy corto | test_create_user_username_too_short |

