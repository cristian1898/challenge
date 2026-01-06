# Core Infrastructure

## Descripción
Este módulo establece los cimientos del proyecto, incluyendo la configuración del entorno, 
conexión a base de datos, modelos ORM, esquemas de validación y el patrón repositorio para 
acceso a datos.

## Estructura Creada

```
app/
├── __init__.py              # Package initialization
├── config.py                # Environment configuration with Pydantic Settings
├── database.py              # SQLAlchemy async engine and session management
├── models/
│   ├── __init__.py
│   └── user.py              # User SQLAlchemy model with validations
├── schemas/
│   ├── __init__.py
│   └── user.py              # Pydantic schemas for request/response
├── repositories/
│   ├── __init__.py
│   └── user_repository.py   # Data access layer with Repository pattern
└── utils/
    ├── __init__.py
    ├── exceptions.py        # Custom exception hierarchy
    └── logger.py            # Structured logging configuration
```

## Decisiones de Arquitectura

### 1. Configuración con Pydantic Settings
- **Por qué**: Permite validación de tipos en tiempo de carga y valores por defecto seguros
- **Beneficios**: 
  - Soporte nativo para `.env` files
  - Validación automática de tipos
  - Cache con `lru_cache` para singleton
  - Separación clara de ambientes (dev/staging/prod)

### 2. SQLAlchemy 2.0 Async
- **Por qué**: Máximo rendimiento con operaciones I/O non-blocking
- **Beneficios**:
  - Connection pooling configurable
  - Soporte para PostgreSQL y SQLite
  - Migrations con Alembic
  - Type hints completos con `Mapped`

### 3. UUID como Primary Key
- **Por qué**: Mejor distribución en índices y seguridad
- **Beneficios**:
  - No expone el orden de creación
  - Permite generación client-side
  - Mejor para sistemas distribuidos

### 4. Repository Pattern
- **Por qué**: Abstracción del acceso a datos
- **Beneficios**:
  - Facilita testing con mocks
  - Desacopla lógica de negocio de persistencia
  - Centraliza queries complejas
  - Permite cambiar ORM sin afectar servicios

### 5. Validación en Múltiples Capas
- **Model Level**: Validaciones de integridad (SQLAlchemy `@validates`)
- **Schema Level**: Validaciones de formato (Pydantic validators)
- **Beneficio**: Defense in depth

## Campos del Usuario

| Campo | Tipo | Restricciones |
|-------|------|---------------|
| id | UUID (string) | Primary Key, auto-generated |
| username | String(50) | Unique, indexed, 3-50 chars, lowercase |
| email | String(255) | Unique, indexed, valid email format |
| first_name | String(100) | Required, 1-100 chars |
| last_name | String(100) | Required, 1-100 chars |
| role | Enum | admin, user, guest (default: user) |
| created_at | DateTime | Auto-set on creation |
| updated_at | DateTime | Auto-updated on modification |
| active | Boolean | Default: True |

## Índices de Base de Datos

```sql
-- Índices simples
CREATE INDEX ix_users_id ON users(id);
CREATE INDEX ix_users_username ON users(username);
CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_role ON users(role);
CREATE INDEX ix_users_active ON users(active);

-- Índices compuestos para queries comunes
CREATE INDEX ix_users_role_active ON users(role, active);
CREATE INDEX ix_users_created_at ON users(created_at);
CREATE INDEX ix_users_last_name_first_name ON users(last_name, first_name);
```

## Validaciones Implementadas

### Username
- Longitud: 3-50 caracteres
- Caracteres permitidos: letras, números, guiones, underscores
- Debe iniciar y terminar con letra o número
- No permite caracteres especiales consecutivos
- Normalizado a lowercase

### Email
- Validación con `email-validator`
- Normalizado a lowercase
- Formato estándar RFC 5322

### Nombres
- Longitud: 1-100 caracteres
- Caracteres permitidos: letras (incluyendo acentos), espacios, guiones, apóstrofes
- Soporta nombres como "O'Brien" o "Mary-Jane"
- Normalizado a Title Case

## Dependencias Principales

```
fastapi==0.109.0
sqlalchemy==2.0.25
pydantic==2.5.3
pydantic-settings==2.1.0
structlog==24.1.0
```

## Configuración de Entorno

Variables requeridas en `.env`:
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname
SECRET_KEY=your-secret-key-min-32-chars
ENVIRONMENT=development
LOG_LEVEL=INFO
```

