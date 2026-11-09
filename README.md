# ZentraFit

Tienda virtual ZentraFit con backend Django y frontend React/Vite. El frontend consume el catálogo, carrito, CSRF y pedidos mediante la API Django. El pago se registra como `Pendiente` porque no hay pasarela conectada todavía.

## 1. Configurar Codespaces

Abre el repositorio en GitHub Codespaces y ejecuta una sola vez:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

### Secretos

No guardes `SECRET_KEY` en GitHub. Crea un secreto de Codespaces llamado `DJANGO_SECRET_KEY` desde:

`GitHub → Settings → Codespaces → Secrets → New secret`

También puedes definirlo temporalmente en la terminal, sin escribirlo en ningún archivo versionado:

```bash
export DJANGO_SECRET_KEY='genera-aqui-una-clave-larga-y-aleatoria'
```

La aplicación lee `DJANGO_SECRET_KEY` desde el entorno. El valor de fallback solo sirve para desarrollo local y no debe usarse en producción.

Para generar una clave segura sin instalar herramientas adicionales:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

> La clave que estuvo anteriormente en `settings.py` debe considerarse comprometida y debe rotarse. No reutilices ese valor.

## 2. Arrancar Django

En la primera terminal:

```bash
source .venv/bin/activate
export DJANGO_SECRET_KEY='tu-secreto-de-Codespaces'
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

En la pestaña **PORTS**, busca el puerto `8000` y copia su URL pública, por ejemplo:

```text
https://fictional-space-guide-7g4r6xww9x4fv9g-8000.app.github.dev
```

## 3. Arrancar el frontend

En una segunda terminal:

```bash
cd frontend
pnpm install
export VITE_DJANGO_BASE_URL="https://fictional-space-guide-7g4r6xww9x4fv9g-8000.app.github.dev"
export VITE_PREVIEW_MODE=false
pnpm dev --host 0.0.0.0
```

En **PORTS**, abre el puerto `3000` con la URL similar a:

```text
https://fictional-space-guide-7g4r6xww9x4fv9g-3000.app.github.dev
```

## 4. Cómo se ve el dashboard

El dashboard usa una estética ZentraFit oscura, con negro carbón, verde `#A2FF00`, tipografía deportiva y tarjetas redondeadas. La pantalla principal muestra:

- Métricas de productos, variantes, categorías y pedidos pendientes.
- Ventas completadas.
- Pedidos recientes con estado y total.
- Alertas de stock bajo.
- Navegación lateral para productos, inventario y categorías.

La ruta es:

```text
https://TU-URL-3000.app.github.dev/admin-dashboard
```

Si no has iniciado sesión, verás una pantalla protegida con un botón para entrar al Django Admin.

## 5. Abrir el dashboard paso a paso

1. Abre la URL pública del puerto `8000` y entra en `/admin/`.
2. Si no tienes usuario administrativo, detén Django y ejecuta:

   ```bash
   python manage.py createsuperuser
   ```

3. Reinicia Django y entra con ese usuario en:

   ```text
   https://TU-URL-8000.app.github.dev/admin/
   ```

4. Abre la URL pública del puerto `3000` y añade:

   ```text
   /admin-dashboard
   ```

5. En **Productos** crea un producto y luego una variante.
6. En **Inventario** registra una entrada para esa variante.
7. Regresa a **Resumen** y verifica las métricas y el stock bajo.
8. En **Categorías** crea nuevas categorías para organizar el catálogo.

## 6. Probar una compra completa

Desde la portada de la tienda:

1. Confirma que el producto aparece desde `/api/catalog/`.
2. Pulsa **Añadir**.
3. Abre la bolsa y cambia la cantidad.
4. Pulsa **Continuar compra**.
5. Completa los datos de entrega.
6. Pulsa **Crear pedido**.
7. Revisa el pedido desde el dashboard o desde `/admin/`.

El pedido crea sus detalles, registra un pago pendiente y vacía el carrito de la sesión.

## 7. Validaciones

Backend:

```bash
source .venv/bin/activate
python manage.py check
python manage.py test tienda.test_api
```

Frontend:

```bash
cd frontend
pnpm check
pnpm build
```

## Rutas principales

| Ruta | Uso |
| --- | --- |
| `/` | Tienda pública |
| `/admin-dashboard` | Dashboard visual ZentraFit |
| `/admin/` | Administración nativa de Django |
| `/api/catalog/` | Catálogo JSON |
| `/api/cart/` | Carrito por sesión |
| `/api/orders/` | Creación de pedidos |
| `/api/admin/overview/` | Métricas protegidas |
| `/api/admin/products/` | Gestión de productos |
| `/api/admin/variants/` | Gestión de variantes |
| `/api/admin/inventory/` | Movimientos de inventario |
| `/api/admin/categories/` | Gestión de categorías |

## Nota de seguridad

Nunca hagas commit de `.env`, claves de Django, contraseñas, tokens de pago ni credenciales. Si una clave fue subida alguna vez al repositorio, considérala comprometida, rótala y configura una nueva mediante GitHub Codespaces Secrets.
