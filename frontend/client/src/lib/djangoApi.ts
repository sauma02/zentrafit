export type ProductVariant = {
  id: string;
  sku: string;
  flavor: string;
  size: string;
  unit: string;
  price: number;
  active: boolean;
};

export type StoreProduct = {
  id: string;
  name: string;
  description: string;
  brand: string;
  category: string;
  imageUrl?: string;
  variants: ProductVariant[];
};

export type CatalogResponse = {
  products: StoreProduct[];
  source: "django-json" | "django-legacy-html" | "preview";
  warning?: string;
};

const baseUrl = (import.meta.env.VITE_DJANGO_BASE_URL ?? "").replace(/\/$/, "");
const catalogEndpoint = import.meta.env.VITE_CATALOG_ENDPOINT?.trim() || "/api/catalog/";

export const djangoApi = {
  isConfigured: Boolean(baseUrl),
  baseUrl,
  previewMode: import.meta.env.VITE_PREVIEW_MODE !== "false",

  async getCatalog(): Promise<CatalogResponse> {
    if (!baseUrl) {
      if (this.previewMode) {
        return { products: previewProducts, source: "preview" };
      }
      throw new Error("VITE_DJANGO_BASE_URL no está configurada.");
    }

    if (catalogEndpoint) {
      const response = await fetch(joinUrl(baseUrl, catalogEndpoint), {
        credentials: "include",
        headers: { Accept: "application/json" },
      });
      if (!response.ok) throw new Error(`El endpoint de catálogo respondió ${response.status}.`);
      const payload = await response.json();
      return { products: normalizeJsonCatalog(payload), source: "django-json" };
    }

    // Compatibility adapter for the current repository, which serves catalogo.html at `/`.
    const response = await fetch(`${baseUrl}/`, { credentials: "include" });
    if (!response.ok) throw new Error(`Django respondió ${response.status} al cargar el catálogo.`);
    const html = await response.text();
    const products = parseLegacyCatalog(html);
    return {
      products,
      source: "django-legacy-html",
      warning: "El backend actual expone HTML, no una API JSON. Conecta VITE_CATALOG_ENDPOINT cuando exista.",
    };
  },

  async getCart() {
    return requestJson<{ lines: Array<{ variantId: string; quantity: number }>; total: number; count: number }>("/api/cart/");
  },

  async addCartItem(variantId: string, quantity = 1) {
    await ensureCsrf();
    return requestJson("/api/cart/", { method: "POST", body: JSON.stringify({ variantId, quantity }) });
  },

  async updateCartItem(variantId: string, quantity: number) {
    await ensureCsrf();
    return requestJson("/api/cart/", { method: "PATCH", body: JSON.stringify({ variantId, quantity }) });
  },

  async removeCartItem(variantId?: string) {
    await ensureCsrf();
    return requestJson("/api/cart/", { method: "DELETE", body: JSON.stringify({ variantId }) });
  },

  async createOrder(payload: Record<string, string>) {
    await ensureCsrf();
    return requestJson<{ orderNumber: string; total: number }>("/api/orders/", { method: "POST", body: JSON.stringify(payload) });
  },
};

function joinUrl(origin: string, path: string) {
  return `${origin}/${path.replace(/^\//, "")}`;
}

async function ensureCsrf() {
  if (!baseUrl) return;
  await fetch(joinUrl(baseUrl, "/api/csrf/"), { credentials: "include" });
}

async function requestJson<T = unknown>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(joinUrl(baseUrl, path), {
    credentials: "include",
    ...init,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
      ...(init.method && init.method !== "GET" ? { "X-CSRFToken": getCookie("csrftoken") } : {}),
    },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || `Django respondió ${response.status}.`);
  return payload as T;
}

function getCookie(name: string) {
  return document.cookie.split("; ").find((part) => part.startsWith(`${name}=`))?.split("=")[1] ?? "";
}

function normalizeJsonCatalog(payload: unknown): StoreProduct[] {
  const rawProducts = Array.isArray(payload)
    ? payload
    : isRecord(payload) && Array.isArray(payload.products)
      ? payload.products
      : [];

  return rawProducts.map((raw, index) => {
    const item = isRecord(raw) ? raw : {};
    const rawVariants = Array.isArray(item.variants) ? item.variants : Array.isArray(item.variantes) ? item.variantes : [];
    return {
      id: stringValue(item.id ?? item.idProducto, `product-${index}`),
      name: stringValue(item.name ?? item.nombre, "Producto ZentraFit"),
      description: stringValue(item.description ?? item.descripcion, "Suplementación para acompañar tus objetivos."),
      brand: stringValue(item.brand ?? item.marca, "ZentraFit"),
      category: stringValue(item.category ?? item.categoria?.nombre ?? item.categoria, "Rendimiento"),
      imageUrl: stringValue(item.imageUrl ?? item.imagen, "") || undefined,
      variants: rawVariants.map((rawVariant, variantIndex) => {
        const variant = isRecord(rawVariant) ? rawVariant : {};
        return {
          id: stringValue(variant.id ?? variant.varianteId, `${index}-${variantIndex}`),
          sku: stringValue(variant.sku, "SKU pendiente"),
          flavor: stringValue(variant.flavor ?? variant.sabor, "Sin sabor"),
          size: stringValue(variant.size ?? variant.tamano, "Presentación estándar"),
          unit: stringValue(variant.unit ?? variant.unidadMedida, "unidad"),
          price: numberValue(variant.price ?? variant.precio),
          active: Boolean(variant.active ?? variant.activo ?? true),
        };
      }),
    };
  });
}

function parseLegacyCatalog(html: string): StoreProduct[] {
  const document = new DOMParser().parseFromString(html, "text/html");
  return Array.from(document.querySelectorAll(".card"))
    .filter((card) => card.querySelector(".marca"))
    .map((card, productIndex) => {
      const name = card.querySelector("h3")?.textContent?.trim() || "Producto ZentraFit";
      const category = card.querySelector("h2")?.textContent?.replace(/^Categoria:\s*/i, "").trim() || "Rendimiento";
      const brand = card.querySelector(".marca")?.textContent?.trim() || "ZentraFit";
      const description = card.querySelector("p")?.textContent?.trim() || "Suplementación para acompañar tus objetivos.";
      const variants = Array.from(card.querySelectorAll(".variante-box")).map((box, variantIndex) => {
        const link = box.querySelector<HTMLAnchorElement>('a[href*="/carrito/add/"]');
        const variantId = link?.href.match(/\/carrito\/add\/([^/]+)\/?$/)?.[1] ?? `${productIndex}-${variantIndex}`;
        const text = box.textContent?.replace(/\s+/g, " ").trim() ?? "";
        return {
          id: decodeURIComponent(variantId),
          sku: extractAfter(text, "SKU:", "SKU pendiente"),
          flavor: extractAfter(text, "Sabor:", "Sin sabor"),
          size: extractAfter(text, "Tamaño:", "Presentación estándar"),
          unit: extractAfter(text, "Medida:", "unidad"),
          price: numberValue(text.match(/\$([\d.,]+)/)?.[1]),
          active: true,
        };
      });
      return { id: `legacy-${productIndex}`, name, description, brand, category, variants };
    });
}

function extractAfter(text: string, label: string, fallback: string) {
  const match = text.match(new RegExp(`${label}\\s*([^|]+)`));
  return match?.[1]?.trim() || fallback;
}

function stringValue(value: unknown, fallback: string) {
  return typeof value === "string" || typeof value === "number" ? String(value) : fallback;
}

function numberValue(value: unknown) {
  if (typeof value === "number") return value;
  const parsed = Number(String(value ?? "0").replace(/[^\d.-]/g, ""));
  return Number.isFinite(parsed) ? parsed : 0;
}

function isRecord(value: unknown): value is Record<string, any> {
  return typeof value === "object" && value !== null;
}

// Preview data is the single product present in the repository's SQLite seed.
const previewProducts: StoreProduct[] = [
  {
    id: "1",
    name: "Creatina Monohidratada Nutrex",
    description: "Creatina monohidratada Nutrex de 300 g para acompañar fuerza, potencia y consistencia.",
    brand: "Nutrex",
    category: "Creatina",
    variants: [
      {
        id: "1",
        sku: "1234567",
        flavor: "Sin sabor",
        size: "300",
        unit: "g",
        price: 90000,
        active: true,
      },
    ],
  },
];
