# Frontend — Panadería

Vite + React 19 + TypeScript + Tailwind 4 + TanStack Query/Router.

## Arranque

```bash
docker compose up -d      # Postgres, desde la raíz del repo
fastapi dev               # API en http://127.0.0.1:8000, desde la raíz del repo
cd frontend && npm install && npm run dev   # http://localhost:5173
```

`VITE_API_URL` (ver `.env.example`) apunta a la API. El origen del front tiene que
estar en `CORS_ORIGINS` del backend, o el navegador bloquea las respuestas.

## Contrato con la API

Los tipos de `src/api/schema.d.ts` son **generados**. Nunca se editan a mano:

```bash
npm run gen:api    # openapi-typescript contra http://127.0.0.1:8000/openapi.json
```

Hay que regenerar cada vez que el backend cambia un schema o un endpoint —
con la API corriendo. Si el cambio rompe algo, `npm run typecheck` lo dice.

Los enums del backend tienen sus etiquetas en `src/api/enums.ts`, tipadas como
`Record<Enum, string>`: si el backend agrega, quita o renombra un miembro, el
error de compilación sale ahí y en ningún otro lado.

## Estructura

```
src/api/          cliente generado, hooks de TanStack Query, un módulo por entidad
src/components/   layout y kit de UI reutilizable
src/features/     una carpeta por pantalla (ingredients, recipes, products)
src/lib/          formateo de moneda/cantidad/porcentaje y utilidades
src/router.tsx    rutas (definidas en código, no por archivos)
```

## Comandos

```bash
npm run dev        # servidor de desarrollo
npm run typecheck  # tsc sin emitir
npm run lint       # oxlint
npm run build      # typecheck + build de producción
```
