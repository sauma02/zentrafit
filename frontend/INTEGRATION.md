# ZentraFit Storefront — integración Django

Este proyecto contiene el frontend React/Vite y se conecta a la API complementaria de Django bajo `/api/`. Las vistas HTML existentes se mantienen intactas.

## Auditoría realizada

Repositorio analizado: `sauma02/zentrafit`, rama `main`.

El backend actual contiene:

| Recurso | Estado actual | Uso desde el frontend |
| --- | --- | --- |
| Catálogo | `GET /api/catalog/` devuelve productos y variantes JSON; `GET /` sigue devolviendo HTML | El frontend usa la API JSON |
| Carrito | `GET/POST/PATCH/DELETE /api/cart/` opera sobre la sesión actual | Persistente en Django y protegido por CSRF en mutaciones |
| CSRF | `GET /api/csrf/` establece la cookie CSRF | El adaptador la solicita antes de mutar |
| Pedidos | `POST /api/orders/` crea pedido, detalles y pago pendiente, y vacía el carrito | Checkout real conectado desde el drawer |
| Admin | `/admin/` | No se expone en la tienda pública |
| Catálogo JSON | Implementado en `/api/catalog/` | Consumido por `djangoApi.ts` |
| Lectura/edición de carrito | Implementado en `/api/cart/` | Consumido por bolsa y controles de cantidad |
| Checkout / creación de pedido | Implementado en `/api/orders/` | Formulario conectado; pago queda pendiente |
| Autenticación | No hay flujo de login HTTP implementado para la tienda | No se inventa una sesión de usuario |
| Pagos | El modelo `Pago` existe, pero no hay endpoint de pago | No se simula checkout ni pago |
| Imágenes | Existe `ImagenProducto`, pero no hay endpoint/serving público documentado | El frontend usa visuales de marca hasta conectar URLs reales |
| Dashboard admin | `/admin-dashboard` consume `/api/admin/*` y requiere sesión staff de Django | Gestiona productos, variantes, categorías, movimientos de inventario y métricas |

## Variables de entorno

Copia `.env.example` como `.env.local` en la raíz del frontend:

```bash
VITE_DJANGO_BASE_URL=http://127.0.0.1:8000
VITE_CATALOG_ENDPOINT=
VITE_PREVIEW_MODE=true
```

- `VITE_DJANGO_BASE_URL`: origen del backend Django. No incluye la barra final.
- `VITE_CATALOG_ENDPOINT`: opcional. Si existe, debe responder JSON con una lista de productos o `{ "products": [...] }`. Si queda vacío, el adaptador solicita `/` y convierte el catálogo HTML actual a un formato común.
- `VITE_PREVIEW_MODE`: deja `true` para revisar el diseño sin backend; cambia a `false` en integración si quieres que la interfaz muestre errores de conexión en lugar de usar el dato seed de preview.

## Contrato JSON recomendado

El adaptador acepta nombres en inglés y los nombres actuales del dominio Django. La forma recomendada es:

```json
{
  "products": [
    {
      "id": "1",
      "name": "Creatina Monohidratada Nutrex",
      "description": "Creatina monohidratada Nutrex de 300 g.",
      "brand": "Nutrex",
      "category": "Creatina",
      "imageUrl": "https://...",
      "variants": [
        {
          "id": "1",
          "sku": "1234567",
          "flavor": "Sin sabor",
          "size": "300",
          "unit": "g",
          "price": 90000,
          "active": true
        }
      ]
    }
  ]
}
```

## Pendientes para producción

1. Reemplazar el método de pago informativo por una pasarela real y actualizar el estado de `Pago` mediante webhook.
2. Añadir autenticación de usuarios y asociar pedidos/carritos a `usuarioId` cuando exista sesión autenticada.
3. Configurar CORS/CSRF y cookies seguras para el dominio de producción.
4. Publicar las imágenes de `ImagenProducto` con URLs absolutas o un storage/CDN.

## Dashboard administrativo

Abre `/admin-dashboard` desde el frontend. El panel redirige a `/admin/login/` si no existe una sesión staff de Django. Después de iniciar sesión, permite crear categorías, productos y variantes, registrar entradas/salidas/ajustes de inventario y consultar métricas, stock bajo y pedidos recientes. Los movimientos se guardan en `MovimientoInventario` y el stock se calcula por entradas menos salidas.

## Estructura relevante

```text
client/src/pages/Home.tsx       # experiencia pública y bolsa de preview
client/src/lib/djangoApi.ts     # adaptador normalizador Django/JSON/HTML legacy
client/src/index.css             # identidad visual y responsive
client/index.html                # metadata y título
.env.example                     # configuración de conexión
```

## Comandos

```bash
pnpm install
pnpm check
pnpm build
pnpm dev
```

Para fusionarlo, copia la carpeta `client/`, los archivos de configuración de Vite/TypeScript y `INTEGRATION.md` según la estructura de tu aplicación. Mantén el backend fuera de este paquete.

## Asset de marca

`brand-assets/zentrafit-logo-original.png` contiene el logo extraído del plan de negocios. En el preview administrado se sirve desde `/manus-storage/zentrafit-000_87db05dc.png`. Al fusionar en otro hosting, sube este PNG al storage/CDN del proyecto y cambia la ruta en `client/src/pages/Home.tsx`.
