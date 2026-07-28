# CLAUDE.md

Contexto operativo del proyecto para Claude Code. El usuario (Fer) trabaja en español.

---

## Regla #1 — División de trabajo

**Fer es dueño de todo `app/` (backend). Claude NO escribe código de backend salvo petición explícita.**

Esto incluye `app/`, `alembic/`, `app/seed.py` y los tests de Python.

**Por qué:** el propósito declarado del proyecto es que Fer aprenda backend. Si Claude lo escribe, el proyecto pierde su razón de ser.

**Rol de Claude:**
- **Dueño de `frontend/`** — ahí avanza sin pedir permiso.
- **Guía en el backend** — da el *qué* y el *porqué* (decisiones de diseño, trade-offs, orden de ataque, revisión de código), no el *cómo* tecleado. Al detectar un bug: señalar `archivo:línea`, explicar el concepto detrás, y dejar que Fer lo arregle.

**Contrato entre capas:** el OpenAPI en `http://127.0.0.1:8000/openapi.json`. Cuando Fer cambia un schema o endpoint, se **regenera** el cliente TypeScript (`npm run gen:api`), nunca se escriben tipos a mano. **Nunca construir UI contra un endpoint que aún no existe en el OpenAPI.**

---

## Qué es el proyecto

API REST para gestión de una panadería: inventario de materia prima (ingredients), recetas con costeo dinámico, y catálogo de productos terminados. Proyecto personal, con ambición de **portafolio serio / usable de verdad**.

Historia: 49 commits entre 2026-04-30 y 2026-05-20, luego ~9 semanas parado. Reactivado el 2026-07-24 con un plan por fases.

---

## Stack

**Backend (existe):** FastAPI · SQLAlchemy 2.0 async · asyncpg · PostgreSQL 15 · Pydantic v2 · Docker Compose (solo la BD).

**Frontend (existe):** Vite 8 + React 19 + TypeScript 5.9 + Tailwind 4 + TanStack Query + TanStack Router, con cliente generado vía `openapi-typescript` + `openapi-fetch`. Vive en `frontend/` **en este mismo repo** (monorepo).

⚠️ TypeScript va fijado a `~5.9`: `openapi-typescript` aún declara `peer typescript@^5.x` y la plantilla de Vite trae TS 6. Subirlo rompe `npm install`.

---

## Comandos

```bash
docker compose up -d      # levanta Postgres (host:5433 → contenedor:5432)
fastapi dev               # API en http://127.0.0.1:8000, docs en /docs
make reset-db             # alembic downgrade base → upgrade head → python -m app.seed

alembic revision --autogenerate -m "..."   # nueva migración (revisar SIEMPRE el archivo generado)
alembic upgrade head                       # aplicar
alembic current                            # en qué revisión está la BD

cd frontend && npm run dev   # http://localhost:5173
cd frontend && npm run gen:api   # regenera el cliente TS (requiere la API corriendo)
```

Entorno: `.venv/` en la raíz. Variables en `.env` (ver `.env.example`): `DB_USER`, `DB_PASSWORD`, `DATABASE_URL`, `DB_ECHO`, `CORS_ORIGINS` (opcional, separado por comas).

`DB_USER`/`DB_PASSWORD` las lee **solo `docker-compose.yml`**, para crear el usuario de Postgres; `app/` nunca las toca, le basta `DATABASE_URL`. Por eso `Settings` lleva `extra="ignore"`: el `.env` es un archivo compartido por dos consumidores. Efecto secundario a tener presente: un typo en una variable **con default** (`DB_ECH0=true`) se descarta en silencio. Las que no tienen default siguen fallando ruidosamente.

---

## Arquitectura del backend

Arquitectura en capas, sin repositorios (los servicios hablan directo con SQLAlchemy):

```
app/api/v1/routers/   → HTTP, validación de existencia, HTTPException
app/services/         → clases con @staticmethod async, reciben db: AsyncSession
app/models/           → SQLAlchemy (estilo Column() legacy, no Mapped[])
app/schemas/          → Pydantic v2 (usan class Config, no model_config)
app/core/config.py    → Settings (pydantic-settings), instancia única `settings`
app/db/database.py    → engine, AsyncSessionLocal, Base, get_db()
alembic/versions/     → migraciones; env.py importa app.models explícito y lee la URL de settings
```

**Convenciones tácitas** (viven solo en el código, del commit `fb568ce`):
- Schemas de entrada como parámetro: `ingredient_in`, `recipe_in`
- Objetos ORM: `db_ingredient`, `db_recipe`
- Argumentos opcionales siempre por keyword: `get_by_id(db, id, include_inactive=True)`

**Patrones establecidos:**
- **Soft delete** en las 3 entidades (`is_active=False`) + endpoint `PATCH /{id}/reactivate`
- `include_inactive: bool = False` como query param en los `GET`
- Costeo de recetas **sin N+1**: `ProductService._get_recipe_costs` hace un `SUM(quantity * current_unit_price)` con `GROUP BY` para todos los ids de golpe (`app/services/product_service.py:16`). Respetar este patrón.
- `Product.cost` **no es columna**: se asigna en runtime sobre la instancia ORM y `ProductResponse` lo lee vía `from_attributes`.
- **Toda la config pasa por `settings`** (`app/core/config.py`). Nada de `os.getenv` disperso. Regla: lo que rompe si falta va sin default (`database_url`); lo que tiene un valor sensato de desarrollo va con default (`db_echo`, `cors_origins`).

**Git:** rama `dev` → PR a `main`. Conventional Commits (`feat:`, `fix:`, `chore:`, `refactor:`), muy consistentes. Mantener el estilo; para el front usar scope: `feat(front): ...`.

---

## Estado actual (2026-07-27, pausado aquí)

**Fase 0 cerrada. Fase 1 arrancada: Alembic hecho.** Todo lo que sigue se comprobó contra el servidor corriendo, no solo por lectura de código.

**Backend — funciona:** 20 operaciones en 11 paths. CRUD completo de `ingredients`, `recipes` (con ingredientes anidados y eager loading) y `products` (con `cost` calculado). Cero mock data.

**Frontend:** existe desde el 2026-07-27. Scaffold + cliente generado + las 3 pantallas (Ingredientes, Recetas, Productos) con alta/edición/soft delete/reactivación. `npm run build` y `npm run typecheck` pasan. Ver `frontend/README.md`.

### Lo que cerró la Fase 0 (2026-07-26/27)

- **CORS** (`app/main.py:33`) — orígenes desde `settings.cors_origins`, no hardcodeados. Permite `localhost:5173` y `127.0.0.1:5173` (son orígenes distintos para el navegador aunque sean la misma máquina; el segundo faltaba y devolvía 400). `allow_credentials=True`, métodos explícitos. Verificado: origen no permitido → 400.
- **`app/core/config.py`** — `Settings(BaseSettings)` con `database_url`, `db_echo`, `cors_origins`. Adiós al `os.getenv` de `database.py`.
  - ⚠️ **Detalle que hay que recordar:** `cors_origins` es `Annotated[list[str], NoDecode]` + `field_validator(mode="before")`. `NoDecode` es **obligatorio**: pydantic-settings aplica `json.loads()` a los tipos complejos *antes* de correr validadores, así que sin esa anotación el split por comas nunca se ejecuta y arranca con `SettingsError`. El validador maneja string (del entorno) y lista (el default). Mismo patrón para cualquier futuro campo de tipo lista.
- **`GET /health`** (`app/api/v1/routers/health.py`, sin prefijo `/api/v1`) — hace `SELECT 1`. 200 `{"status":"ok","database":"ok"}` / 503 `{"status":"error","database":"unavailable"}`. Sin BD esta API no sirve nada, por eso `"error"` y no `"degraded"`. Único sitio del proyecto con `logging` (`logger.exception` en el `except`).
- **Bug arreglado** en `ingredient_service.py:76` — `query = query.where(...)`. Verificado que el patrón está bien en los 8 bloques `if not include_inactive` de los 3 servicios.
- `app/core/__init__.py` y `app/services/__init__.py` creados.

Todo esto ya está commiteado en `dev` (hasta `bad2cff`).

### Lo hecho de la Fase 1 (2026-07-27) — ⚠️ SIN COMMITEAR

En el working tree, pendiente de commit:

- **Alembic** (`alembic/`, `alembic.ini`). Migración inicial `c2fec39bed13_initial_schema`, aplicada (`alembic_version` = `c2fec39bed13`). `env.py` importa `app.models` explícito (línea 12) — muere así la dependencia accidental por la que los modelos se registraban solo porque los routers importaban los servicios — y lee la URL de `settings`, no del `.ini`.
- **`create_all` fuera del lifespan** (`app/main.py`). Va en el mismo commit que la migración inicial: si se separan, queda un commit intermedio donde nadie crea el esquema.
- **`make reset-db` reescrito**: `alembic downgrade base → upgrade head → seed`. Sin la pausa interactiva ni el `psql -U admin` hardcodeado.
- **`extra="ignore"`** en `Settings` (`app/core/config.py`), que es lo que impedía arrancar la API.

Mensajes sugeridos:
```
feat: add alembic with initial schema migration and drop create_all
chore: rewrite reset-db target to use alembic migrations
fix: ignore extra env vars in Settings so docker-compose vars don't break startup
```

### Huecos conocidos (todos verificados)

1. **Dinero en `Float`**, debería ser `Numeric(10,2)` + `Decimal`. El cambio más caro de hacer tarde: toca modelos, schemas y el `SUM` de `_get_recipe_costs`. **Es lo siguiente de la Fase 1.** El `--autogenerate` de esto sale con `ALTER COLUMN ... TYPE`; en Postgres con datos puede necesitar `postgresql_using`. Revisar el archivo generado a mano, siempre.
2. **Cero validación**: ningún `Field(...)` con constraints ni validators → acepta precios y stock negativos. Lo que más rinde por línea escrita y no requiere migración.
3. **Integridad solo en el router**: `Recipe.name` sin `unique=True` en la tabla; `RecipeIngredient` sin `UniqueConstraint(recipe_id, ingredient_id)`; ningún servicio captura `IntegrityError` → choques de constraint salen como **500 en vez de 409**. El chequeo "¿ya existe?" en el router es una carrera; solo la BD lo garantiza. (Mientras tanto, el formulario de recetas del front bloquea ingredientes duplicados del lado del cliente — parche, no garantía.)
4. Sin paginación ni filtros en los `GET /`. ⚠️ Añadirla cambia la respuesta de `list[X]` a `{items, total}` → **avisar a Claude antes de mergearlo**, hay que regenerar el cliente TS y ajustar pantallas. Idealmente al final de la Fase 1, en un solo golpe.
5. Sin tests (0%), sin CI, sin linters, sin `pyproject.toml`, sin `Dockerfile` para la API.
6. Logging sin configurar globalmente: solo `health.py` tiene logger, el resto del proyecto no loguea nada. Fase 4.
7. Sin auth/usuarios. Sin dominio de producción/ventas/movimientos de stock.
8. **Los tres `PATCH /{id}/reactivate` exigen un body** (`ingredient_in: IngredientUpdate`) que no necesitan — copiado del handler de update. Obliga al cliente a mandar `{}`. Como usan `exclude_unset=True`, funciona, pero el contrato miente: el OpenAPI lo marca `required: true`.
9. Menores:
   - typo `"Postes Individuales"` → `"Postres"` en `ProductCategory` (`app/schemas/product.py:6`). El cliente TS **ya está generado con el typo**; al arreglarlo, correr `npm run gen:api` y TypeScript señalará el único punto a tocar (`frontend/src/api/enums.ts`).
   - `app/models/product.py:13` importa del schema (inversión de capas).
   - `alembic` quedó **sin pinnear** en `requirements.txt`, único caso en un archivo donde todo lo demás lleva versión exacta.
   - `app/main.py:10` importa `Base`, que ya no se usa desde que salió el `create_all`.
   - El `.gitignore` de la raíz es el estándar de Python y su regla `lib/` **no está anclada**, así que atrapa cualquier `lib/` del repo. Ya mordió a `frontend/src/lib/` (resuelto con una re-inclusión en `frontend/.gitignore`). El arreglo de fondo es anclarla como `/lib/`. Ojo: `dist/` sin anclar sí conviene, es lo que ignora `frontend/dist/`.

---

## Plan por fases

Documento completo: `/Users/fersoriano/.claude/plans/este-proyecto-personal-lo-cuddly-liskov.md`

```
Fase 0  ✅ HECHA (2026-07-27): CORS · app/core/config.py · GET /health · fix ingredient_service.py:76
Fase 1  Cimientos (Fer): Alembic ✅ · Numeric ← AQUÍ · validación · constraints · paginación
     ‖  Frontend v1 (Claude) ✅ HECHO (2026-07-27): scaffold + cliente OpenAPI + 3 pantallas
Fase 2  Dominio (Fer): ProductionOrder · StockMovement · Sale/SaleItem · transacciones
     ‖  Órdenes de producción, POS y dashboard (Claude)
Fase 3  Auth: User · JWT · RBAC ‖ login + guards
Fase 4  Calidad: pytest-asyncio · ruff/mypy · GitHub Actions · Dockerfile · deploy
```

Las dos preguntas de diseño que hay que discutir **antes** de codificar la Fase 2:
- ¿`Product` tiene stock propio? (hoy solo hay stock de materia prima)
- ¿El costo se congela en la venta? (`unit_cost_at_sale` en `SaleItem`) — es el concepto que separa un CRUD de un sistema real.

---

## Siguiente acción (al retomar)

**Primero: `git status`.** El trabajo de Alembic sigue sin commitear (ver "Lo hecho de la Fase 1"). Los 3 commits del frontend sí están en `dev` (`c43e79a`, `bc3dd50`, `2553b7f`) y nada está pusheado.

Para volver a arrancar todo:

```bash
docker compose up -d && alembic upgrade head
fastapi dev                    # raíz del repo, si no no encuentra el .env
cd frontend && npm run dev
```

Luego, las dos pistas siguen en paralelo:

- **Fer → hueco 1 (`Numeric`)**, la primera migración de verdad. Después: validación → constraints → paginación, **en ese orden**. El hueco 8 (body de `reactivate`) es de minutos y limpia el contrato; buen calentamiento.
- **Claude → frontend.** La v1 está entregada y verificada. Lo siguiente depende de lo que abra la Fase 2; mientras tanto, reaccionar a lo que cambie el contrato.

Coordinación obligatoria en dos momentos, porque ambos rompen el cliente TS generado:
- cuando entre **paginación** (hueco 4): `list[X]` → `{items, total}`.
- cuando se arregle el **typo del enum** (hueco 9): hay que correr `npm run gen:api`.

En los dos casos el orden es: backend → `npm run gen:api` → `npm run typecheck` → arreglar lo que TypeScript señale.
