# Docker & Cloud Deployment

## Descripción
Este módulo implementa la containerización con Docker y la configuración de CI/CD 
para despliegue en Google Cloud Platform usando Cloud Build y Cloud Run.

## Archivos Creados

```
├── Dockerfile           # Multi-stage build optimizado
├── docker-compose.yml   # Orquestación local con PostgreSQL
├── .dockerignore        # Exclusiones para build
├── cloudbuild.yaml      # Pipeline CI/CD para GCP
└── API_README.md        # Documentación completa del proyecto
```

## Dockerfile

### Características
- **Multi-stage build**: Separa construcción de runtime
- **Non-root user**: Ejecución segura sin privilegios
- **Health checks**: Verificación de salud integrada
- **Cache optimization**: Capas ordenadas para mejor cache
- **Minimal image**: Solo dependencias de runtime

### Stages
1. **Builder**: Instala dependencias en virtualenv
2. **Runtime**: Imagen final optimizada (~150MB)

### Build Manual
```bash
docker build -t user-management-api:latest .
docker run -p 8000:8000 user-management-api:latest
```

## Docker Compose

### Servicios
| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| db | 5432 | PostgreSQL 15 |
| api | 8000 | FastAPI Application |
| pgadmin | 5050 | Admin UI (perfil dev) |

### Comandos
```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Detener servicios
docker-compose down

# Incluir pgAdmin (desarrollo)
docker-compose --profile dev up -d
```

## Cloud Build Pipeline

### Steps
1. **build**: Construye imagen Docker
2. **push**: Sube imagen a Container Registry
3. **test**: Ejecuta tests dentro del container
4. **deploy**: Despliega a Cloud Run

### Configuración Cloud Run
- **Memory**: 512Mi
- **CPU**: 1
- **Min instances**: 0 (scale to zero)
- **Max instances**: 10
- **Concurrency**: 80 requests
- **Timeout**: 300s

### Variables de Sustitución
```yaml
_SERVICE_NAME: user-management-api
_REGION: us-central1
```

### Secrets Requeridos
Crear en Secret Manager:
- `database-url`: URL de conexión PostgreSQL
- `secret-key`: Clave secreta de la aplicación

## Despliegue Manual

### Prerequisitos GCP
```bash
# Habilitar APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### Crear Secrets
```bash
# Database URL
echo -n "postgresql+asyncpg://user:pass@/dbname?host=/cloudsql/project:region:instance" | \
  gcloud secrets create database-url --data-file=-

# Secret Key
echo -n "your-production-secret-key-min-32-chars" | \
  gcloud secrets create secret-key --data-file=-
```

### Ejecutar Build
```bash
# Desde el directorio del proyecto
gcloud builds submit --config cloudbuild.yaml

# Con sustituciones personalizadas
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_SERVICE_NAME=my-api,_REGION=us-east1
```

### Deploy Directo a Cloud Run
```bash
gcloud run deploy user-management-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

## Arquitectura de Despliegue

```
┌─────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                      │
│                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐   │
│  │   Cloud     │───▶│  Container  │───▶│    Cloud Run    │   │
│  │   Build     │    │  Registry   │    │   (Auto-scale)  │   │
│  └─────────────┘    └─────────────┘    └────────┬────────┘   │
│         │                                        │            │
│         │                                        │            │
│         ▼                                        ▼            │
│  ┌─────────────┐                        ┌─────────────────┐   │
│  │   Secret    │                        │    Cloud SQL    │   │
│  │  Manager    │                        │   PostgreSQL    │   │
│  └─────────────┘                        └─────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Health Checks en Producción

Cloud Run utiliza los endpoints de health:
- **Startup**: `/health/ready` (determina cuando está listo)
- **Liveness**: `/health/live` (verifica que sigue vivo)

## Monitoreo

### Logs
```bash
# Ver logs de Cloud Run
gcloud run services logs read user-management-api --region us-central1

# Seguir logs en tiempo real
gcloud run services logs tail user-management-api --region us-central1
```

### Métricas
- Request count
- Request latency
- Container instance count
- Memory utilization
- CPU utilization

## Costos Estimados

Cloud Run cobra por:
- Tiempo de CPU durante requests
- Memoria durante requests
- Requests (primer millón gratis/mes)

Con scale-to-zero, no hay costos cuando no hay tráfico.

## Seguridad

- Imagen ejecuta como usuario non-root
- Secrets manejados por Secret Manager
- HTTPS automático en Cloud Run
- Headers de seguridad implementados
- Sin exposición de errores internos en producción
