# ZentraFit

Tienda virtual de suplementación deportiva con storefront en React/Vite y backend en Django. El proyecto mantiene una arquitectura MVC en el backend: las vistas/API reciben la petición, los servicios aplican las reglas de negocio y las entidades representan los datos persistidos.

## Estado actual

La aplicación ya integra el frontend con el backend para consultar el catálogo real, categorías, variantes, precios e inventario; mostrar imágenes y galerías; abrir el detalle en `/producto/:id`; administrar catálogo e inventario desde el dashboard; crear pedidos reales con pago pendiente y estado inicial **Por confirmar**; redirigir al WhatsApp oficial con los datos del pedido; y consultar o actualizar pedidos desde la pestaña **Pedidos**.

También se muestran las acciones **Generar factura** y **Enviar al correo** como preparación para los endpoints Django que todavía debe implementar el propietario. La factura inicial será un documento interno básico con datos del pedido y total. No representa todavía una factura electrónica legal ni un documento validado por DIAN.

## Tecnologías

### Backend

- Python y Django 6.1.x.
- SQLite para desarrollo local.
- Django ORM, `ImageField` y Pillow.
- API JSON y endpoints multipart para imágenes.
- Sesiones Django, cookies CSRF y permisos de usuario `staff`.
- Arquitectura MVC por entidades, servicios y vistas/API.

### Frontend

- React 19, TypeScript y Vite.
- Tailwind CSS, componentes reutilizables y `lucide-react`.
- `pnpm` como gestor de paquetes.
- Cliente centralizado en `frontend/client/src/lib/djangoApi.ts`.
- Identidad visual neon green, blanco y negro.

## Estructura importante

```text
zentrafit-git/
├── tienda/
│   ├── entidades/              # Modelos Django del dominio
│   ├── servicios/              # Reglas de negocio MVC
│   ├── api_views.py            # API pública de catálogo, carrito y pedidos
│   ├── admin_api.py            # API protegida del dashboard
│   └── migrations/
├── zentrafit_project/
│   ├── settings.py             # CORS, CSRF, media y configuración
│   └── urls.py
├── frontend/
│   ├── client/src/lib/djangoApi.ts
│   ├── client/src/pages/Home.tsx
│   ├── client/src/pages/ProductDetail.tsx
│   ├── client/src/pages/AdminDashboard.tsx
│   └── client/public/zentrafit-logo-original.png
├── docs/
│   ├── manual-usuario-zentrafit.md
│   └── reporte-final-2026-11-26.md
└── requirements.txt
```

## Instalación local

### Backend

```bash
git clone https://github.com/sauma02/zentrafit.git
cd zentrafit
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

En Codespaces, el puerto 8000 debe estar reenviado y ser accesible desde el frontend. El administrador nativo de Django se encuentra en `/admin/`.

### Frontend

```bash
cd frontend
pnpm install
pnpm dev --host 0.0.0.0 --port 3000
```

El storefront se abre en la URL pública del puerto 3000. El dashboard visual está en `/admin` de esa misma URL; no debe confundirse con `/admin/` del backend Django.

## Variables de entorno del frontend

Crear `frontend/.env.local` (no subirlo a GitHub):

```env
VITE_DJANGO_BASE_URL=https://TU-URL-DEL-PUERTO-8000.app.github.dev
VITE_PREVIEW_MODE=false
VITE_WHATSAPP_NUMBER=573001234567
```

`VITE_DJANGO_BASE_URL` es la URL pública del backend; `VITE_PREVIEW_MODE` debe ser `false` para catálogo, carrito y pedidos reales; `VITE_WHATSAPP_NUMBER` usa formato internacional, solo dígitos y sin `+`, espacios ni guiones.

No guardar contraseñas, `SECRET_KEY`, tokens ni bases de datos con información real en GitHub. La `SECRET_KEY` debe configurarse mediante los Secrets del entorno donde se ejecuta Django.

## URLs principales

| Función | URL |
|---|---|
| Storefront | `https://TU-URL-3000/` |
| Detalle de producto | `https://TU-URL-3000/producto/<id>` |
| Dashboard visual | `https://TU-URL-3000/admin` |
| Django Admin | `https://TU-URL-8000/admin/` |
| Catálogo público | `GET /api/catalog/` |
| Carrito | `GET/POST/PATCH/DELETE /api/cart/` |
| Crear pedido | `POST /api/orders/` |
| CSRF | `GET /api/csrf/` |

## Catálogo, imágenes y galerías

El backend serializa cada producto incluyendo `imageUrl` e `images`. Las URLs de media se construyen de forma absoluta para que el navegador del frontend pueda solicitar imágenes al puerto de Django.

Desde el dashboard se selecciona un producto, se elige un archivo, se marca opcionalmente como principal y se define el orden. La petición usa `multipart/form-data` y termina en `POST /api/admin/images/`. La vista valida transporte y permisos; `ProductoServicio.asociarImagenes` mantiene la lógica de negocio y asociación.

En desarrollo, Django sirve `MEDIA_URL` desde `MEDIA_ROOT`. En producción se debe configurar almacenamiento y servidor de media apropiados.

## Flujo de carrito y WhatsApp

1. El cliente añade una variante al carrito.
2. El frontend sincroniza la operación con el carrito de sesión Django.
3. En **Continuar compra**, el cliente diligencia nombre, contacto, correo, dirección, ciudad y medio de pago previsto.
4. `POST /api/orders/` crea el pedido real, calcula el total en backend, registra detalles, crea un pago pendiente y vacía el carrito.
5. El frontend construye un mensaje con número de pedido, cliente, dirección, productos, cantidades, total y estado.
6. El navegador redirige a `https://wa.me/<numero>`.
7. El negocio revisa la solicitud y confirma manualmente el pedido y el medio de pago por WhatsApp.

WhatsApp comunica la solicitud; no sustituye la creación del pedido ni confirma automáticamente el pago.

## Dashboard visual

El dashboard `/admin` consume endpoints administrativos protegidos por sesión Django y CSRF. Incluye resumen, categorías, productos, variantes, inventario, imágenes, pedidos y acciones de factura preparadas.

La API administrativa comprueba que el usuario esté autenticado y tenga `is_staff=True`. Un error 403 normalmente significa que hace falta iniciar sesión en el Django Admin del puerto 8000 o que la cookie no está llegando por una configuración incorrecta de CORS/CSRF.

## Facturación: integración pendiente

El frontend está preparado para consumir:

```text
POST /api/admin/orders/<id>/invoice/
POST /api/admin/orders/<id>/invoice/send/
```

Estos endpoints todavía no están implementados en el backend. El propietario implementará modelo, servicio y vistas manteniendo MVC. El primer documento puede incluir número de pedido, fecha, cliente, productos, cantidades, subtotal, envío, total y datos de contacto. Antes de usarlo como documento fiscal se deben validar los requisitos contables y legales aplicables.

## API principal

```text
GET    /api/catalog/
GET    /api/cart/
POST   /api/cart/
PATCH  /api/cart/
DELETE /api/cart/
POST   /api/orders/
GET    /api/csrf/
```

Las operaciones que modifican datos usan cookies de sesión y protección CSRF. El cliente solicita `/api/csrf/` antes de `POST`, `PATCH` o `DELETE`.

## API administrativa

| Endpoint | Método | Función |
|---|---|---|
| `/api/admin/overview/` | `GET` | Métricas, pedidos recientes y stock bajo |
| `/api/admin/categories/` | `GET/POST` | Listar o crear categorías |
| `/api/admin/products/` | `GET/POST` | Listar o crear productos |
| `/api/admin/variants/` | `POST` | Crear variante/SKU |
| `/api/admin/inventory/` | `GET/POST` | Consultar o registrar movimientos |
| `/api/admin/images/` | `POST` | Subir imagen multipart |
| `/api/admin/orders/` | `GET/PATCH` | Listar o actualizar pedidos |

## Debugging rápido

### `Failed to fetch`

1. Confirmar que Django esté activo en el puerto 8000.
2. Confirmar `VITE_DJANGO_BASE_URL` y reiniciar Vite después de cambiar `.env.local`.
3. Abrir `/api/catalog/` directamente para comprobar conectividad.
4. Verificar `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` y la URL exacta del puerto 3000.
5. Confirmar que el usuario sea `staff` para el dashboard.
6. Revisar la terminal de Django: un 400/403/500 es distinto de un bloqueo CORS.

### Imágenes que no aparecen

Confirmar que exista el archivo en `media/`, que la URL `MEDIA_URL` sea accesible, que `MEDIA_ROOT` esté configurado y que `/api/catalog/` tenga `imageUrl` o `images`. No guardar rutas locales del computador del administrador en la base de datos.

### Catálogo vacío

El frontend no inventa productos. Revisar que existan productos activos con variantes activas y que `GET /api/catalog/` responda correctamente.

## Validaciones

```bash
python manage.py check
python manage.py test tienda.test_api
cd frontend
pnpm check
pnpm build
cd ..
git diff --check
```

## Respaldos

Respaldar conjuntamente `db.sqlite3` y `media/`. Ambos están excluidos del repositorio para evitar que un `pull` sobrescriba datos locales. En producción se recomienda una base de datos administrada y almacenamiento de archivos con copias de seguridad.

## Documentación adicional

- [Manual de usuario](docs/manual-usuario-zentrafit.md)
- [Reporte final de la sesión](docs/reporte-final-2026-11-26.md)
- [Documentación técnica del frontend](frontend/README.md)
- [Guía de integración](frontend/INTEGRATION.md)
