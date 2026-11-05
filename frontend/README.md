# ZentraFit Storefront

Frontend React + TypeScript + Vite para la tienda virtual ZentraFit. La dirección visual sigue el plan de negocio: neon green `#A2FF00`, blanco y negro, con una estética editorial deportiva y foco en conversión.

## Importante

El frontend consume la API complementaria del backend Django en `/api/catalog/`, `/api/cart/`, `/api/csrf/` y `/api/orders/`. La auditoría y los pendientes de producción están en [INTEGRATION.md](./INTEGRATION.md).

## Preview

El preview usa el único producto seed que existe en `db.sqlite3` del repositorio analizado. No se presenta como inventario inventado: es un dato de demostración obtenido del backend local. Al integrar, configura `VITE_DJANGO_BASE_URL` y desactiva `VITE_PREVIEW_MODE` si ya tienes endpoints disponibles.

## Ejecutar

```bash
pnpm install
export VITE_DJANGO_BASE_URL=http://127.0.0.1:8000
export VITE_PREVIEW_MODE=false
pnpm dev
```

Validaciones usadas antes de entregar:

```bash
pnpm check
pnpm build
```
