# ZentraFit

ZentraFit es una tienda virtual de suplementación deportiva con un storefront en React/Vite y un backend Django. La aplicación permite consultar productos, gestionar un carrito por sesión, crear pedidos y administrar catálogo e inventario desde un dashboard interno.

## Funcionalidades principales

### Tienda pública

La tienda muestra productos activos, variantes, precios, marcas y categorías. El usuario puede buscar productos, añadir variantes a la bolsa, modificar cantidades y completar sus datos de entrega.

El carrito se guarda en la sesión de Django, por lo que sus cantidades se conservan mientras la sesión siga activa.

### Creación de pedidos

El checkout solicita:

- Nombre y apellido.
- Correo electrónico.
- Teléfono.
- Dirección de entrega.
- Ciudad.
- Método de pago informativo.

Al crear un pedido, el backend registra el pedido, sus detalles y un pago con estado `Pendiente`. Después vacía el carrito de la sesión. La integración de una pasarela de pago real queda como una fase posterior.

### Dashboard administrativo

El dashboard ZentraFit está disponible en:

```text
/admin-dashboard
```

Incluye:

- Resumen de productos, variantes y categorías.
- Pedidos pendientes y ventas completadas.
- Pedidos recientes.
- Alertas de inventario bajo.
- Creación de categorías.
- Creación de productos.
- Creación de variantes y SKU.
- Registro de entradas, salidas y ajustes de inventario.
- Cálculo de existencias por variante.

El acceso está restringido a usuarios administrativos de Django.

## Arquitectura de la API

La API utiliza JSON y mantiene la sesión mediante cookies de Django. Las operaciones que modifican datos requieren protección CSRF.

### CSRF

Antes de realizar operaciones `POST`, `PATCH` o `DELETE`, el frontend solicita:

```http
GET /api/csrf/
```

El endpoint establece la cookie CSRF que se envía posteriormente mediante el header `X-CSRFToken`.

### Catálogo

```http
GET /api/catalog/
```

Respuesta simplificada:

```json
{
  "products": [
    {
      "id": "PROD##001",
      "name": "Creatina Monohidratada",
      "description": "Creatina para acompañar fuerza y rendimiento.",
      "brand": "Nutrex",
      "category": "Creatina",
      "imageUrl": null,
      "variants": [
        {
          "id": "VAR##001",
          "sku": "NTR-CREA-300",
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

Solo se muestran productos activos y variantes activas.

### Carrito

Consultar carrito:

```http
GET /api/cart/
```

Añadir una variante:

```http
POST /api/cart/
Content-Type: application/json

{
  "variantId": "VAR##001",
  "quantity": 1
}
```

Actualizar cantidad:

```http
PATCH /api/cart/
Content-Type: application/json

{
  "variantId": "VAR##001",
  "quantity": 3
}
```

Eliminar una variante:

```http
DELETE /api/cart/
Content-Type: application/json

{
  "variantId": "VAR##001"
}
```

Respuesta habitual:

```json
{
  "lines": [],
  "total": 0,
  "count": 0
}
```

### Pedidos

Crear un pedido:

```http
POST /api/orders/
Content-Type: application/json

{
  "name": "Ana",
  "lastName": "Cliente",
  "email": "ana@example.com",
  "phone": "3000000000",
  "address": "Calle 1 # 2-3",
  "city": "Bogotá",
  "paymentMethod": "Transferencia"
}
```

Respuesta:

```json
{
  "orderId": "PD##001",
  "orderNumber": "NMPD##001",
  "total": 108000
}
```

El costo de envío se calcula en el backend y el pago queda inicialmente en estado `Pendiente`.

## API administrativa

Las rutas administrativas requieren una sesión autenticada con permisos `staff` de Django.

| Endpoint | Método | Función |
| --- | --- | --- |
| `/api/admin/overview/` | `GET` | Métricas, pedidos recientes y stock bajo |
| `/api/admin/categories/` | `GET` | Listar categorías |
| `/api/admin/categories/` | `POST` | Crear una categoría |
| `/api/admin/products/` | `GET` | Listar productos y variantes |
| `/api/admin/products/` | `POST` | Crear un producto |
| `/api/admin/variants/` | `POST` | Crear una variante/SKU |
| `/api/admin/inventory/` | `GET` | Consultar existencias calculadas |
| `/api/admin/inventory/` | `POST` | Registrar entrada, salida o ajuste |
| `/api/admin/orders/` | `GET` | Listar pedidos |
| `/api/admin/orders/` | `PATCH` | Actualizar estado de un pedido |

### Crear categoría

```json
{
  "name": "Proteínas",
  "description": "Proteínas para recuperación y crecimiento muscular.",
  "active": true
}
```

### Crear producto

```json
{
  "name": "Proteína Whey",
  "brand": "Marca aliada",
  "description": "Proteína de suero para complementar la alimentación.",
  "categoryId": "CAT##001",
  "active": true
}
```

### Crear variante

```json
{
  "productId": "PROD##001",
  "sku": "WHEY-001",
  "flavor": "Chocolate",
  "size": "2",
  "unit": "kg",
  "price": 180000,
  "active": true
}
```

### Registrar inventario

```json
{
  "variantId": "VAR##001",
  "type": "entrada",
  "quantity": 20,
  "reason": "Compra inicial",
  "notes": "Ingreso de inventario de proveedor aliado"
}
```

Los tipos disponibles son:

- `entrada`: aumenta existencias.
- `salida`: descuenta existencias.
- `ajuste`: corrige positivamente las existencias.

El stock se calcula mediante los movimientos registrados para cada variante.

## Flujo recomendado de uso

1. Crear una categoría.
2. Crear un producto dentro de esa categoría.
3. Añadir una o varias variantes con SKU y precio.
4. Registrar la entrada inicial de inventario.
5. Confirmar existencias en el dashboard.
6. Publicar el producto como activo.
7. Recibir pedidos desde la tienda pública.
8. Revisar pedidos recientes y actualizar su estado desde la gestión administrativa.

## Estados y errores

La API devuelve respuestas JSON con un campo `detail` cuando ocurre un error. Los casos principales son:

- `400`: datos incompletos o inválidos.
- `403`: falta de sesión administrativa.
- `404`: producto, variante, categoría o pedido inexistente.
- `201`: recurso creado correctamente.
- `200`: consulta o actualización correcta.

## Rutas de la aplicación

| Ruta | Descripción |
| --- | --- |
| `/` | Storefront público |
| `/admin-dashboard` | Panel visual de gestión ZentraFit |
| `/admin/` | Administración nativa de Django |
| `/api/catalog/` | Catálogo público en JSON |
| `/api/cart/` | Carrito asociado a la sesión |
| `/api/orders/` | Creación de pedidos |
| `/api/admin/*` | Operaciones protegidas del dashboard |

## Organización del proyecto

```text
zentrafit_project/       Configuración y URLs Django
tienda/                  Modelos, API pública y API administrativa
frontend/client/src/     Aplicación React/Vite
frontend/brand-assets/   Assets de la marca ZentraFit
frontend/INTEGRATION.md  Detalles técnicos de integración
```

## Estado actual

La tienda, el carrito, el checkout, el catálogo, el inventario y el dashboard administrativo están conectados. Los pagos reales mediante Wompi, Mercado Pago, Stripe u otra pasarela todavía no están implementados; por ahora se registra el pedido y el pago queda como `Pendiente`.
