import json

from django.test import Client, TestCase

from tienda.entidades import Categoria, Producto, VarianteProducto


class StoreApiTests(TestCase):
    def setUp(self):
        category = Categoria.objects.create(categoriaId="cat-api", nombre="Creatina", descripcion="Rendimiento")
        product = Producto.objects.create(
            idProducto="prod-api",
            categoriaId=category,
            nombre="Creatina API",
            descripcion="Producto de prueba",
            marca="ZentraFit",
        )
        self.variant = VarianteProducto.objects.create(
            varianteId="var-api",
            idProducto=product,
            sku="API-001",
            sabor="Sin sabor",
            tamano="300",
            unidadMedida="g",
            precio="90000.00",
        )
        self.client = Client(enforce_csrf_checks=True)
        self.client.get("/api/csrf/")
        self.csrf = self.client.cookies["csrftoken"].value

    def headers(self):
        return {"HTTP_X_CSRFTOKEN": self.csrf}

    def test_catalog_cart_and_order_flow(self):
        catalog = self.client.get("/api/catalog/")
        self.assertEqual(catalog.status_code, 200)
        self.assertEqual(catalog.json()["products"][0]["variants"][0]["id"], "var-api")

        added = self.client.post(
            "/api/cart/",
            data=json.dumps({"variantId": "var-api", "quantity": 2}),
            content_type="application/json",
            **self.headers(),
        )
        self.assertEqual(added.status_code, 201)
        self.assertEqual(added.json()["count"], 2)

        updated = self.client.patch(
            "/api/cart/",
            data=json.dumps({"variantId": "var-api", "quantity": 1}),
            content_type="application/json",
            **self.headers(),
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["count"], 1)

        order = self.client.post(
            "/api/orders/",
            data=json.dumps(
                {
                    "name": "Ana",
                    "lastName": "Cliente",
                    "email": "ana@example.com",
                    "phone": "3000000000",
                    "address": "Calle 1 # 2-3",
                    "city": "Bogotá",
                    "paymentMethod": "Transferencia",
                }
            ),
            content_type="application/json",
            **self.headers(),
        )
        self.assertEqual(order.status_code, 201)
        self.assertTrue(order.json()["orderNumber"])
        self.assertEqual(self.client.get("/api/cart/").json()["count"], 0)
