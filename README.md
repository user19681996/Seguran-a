# ORION – FASE 7 (Production)

Inclui:
- PostgreSQL real (docker-compose)
- Alembic migrations
- RBAC (roles + permissions)
- Rate limit (antifraude básico)
- Audit logs (ações críticas)
- Manifests Kubernetes em /k8s/orion.yaml

## Subir local
```bash
docker compose up --build
```

API:  http://localhost:8000
Docs: http://localhost:8000/docs

PGAdmin: http://localhost:5050
- admin@orion.local / admin123!

Master seed:
- tenant: orion-master
- email: master@orion.local
- senha: admin123!
