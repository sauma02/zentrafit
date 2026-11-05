import { useEffect, useMemo, useState } from "react";
import { Link } from "wouter";
import { toast } from "sonner";
import {
  ArrowRight,
  Check,
  ChevronDown,
  CircleHelp,
  Dumbbell,
  Menu,
  Minus,
  Plus,
  Search,
  ShoppingBag,
  Sparkles,
  Truck,
  X,
  Zap,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { djangoApi, type StoreProduct, type ProductVariant } from "@/lib/djangoApi";

const currency = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});

const categories = ["Todos", "Proteínas", "Creatina", "Pre-entreno", "Bienestar"];

type CartLine = {
  product: StoreProduct;
  variant: ProductVariant;
  quantity: number;
};

export default function Home() {
  const [products, setProducts] = useState<StoreProduct[]>([]);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [catalogError, setCatalogError] = useState("");
  const [catalogWarning, setCatalogWarning] = useState("");
  const [query, setQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState("Todos");
  const [cartLines, setCartLines] = useState<CartLine[]>([]);
  const [cartOpen, setCartOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;
    djangoApi
      .getCatalog()
      .then((response) => {
        if (cancelled) return;
        setProducts(response.products);
        setCatalogWarning(response.warning ?? "");
        if (djangoApi.isConfigured && !djangoApi.previewMode) {
          void djangoApi.getCart().then((cart) => {
            if (cancelled) return;
            const restored = cart.lines.flatMap((line) => {
              const product = response.products.find((item) => item.variants.some((variant) => variant.id === line.variantId));
              const variant = product?.variants.find((item) => item.id === line.variantId);
              return product && variant ? [{ product, variant, quantity: line.quantity }] : [];
            });
            setCartLines(restored);
          }).catch(() => undefined);
        }
      })
      .catch((error: Error) => {
        if (cancelled) return;
        setCatalogError(error.message);
      })
      .finally(() => {
        if (!cancelled) setCatalogLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const filteredProducts = useMemo(() => {
    const normalizedQuery = query.toLowerCase().trim();
    return products.filter((product) => {
      const categoryMatch = activeCategory === "Todos" || product.category.toLowerCase() === activeCategory.toLowerCase();
      const queryMatch = !normalizedQuery || [product.name, product.brand, product.category, product.description]
        .join(" ")
        .toLowerCase()
        .includes(normalizedQuery);
      return categoryMatch && queryMatch;
    });
  }, [activeCategory, products, query]);

  const cartCount = cartLines.reduce((total, line) => total + line.quantity, 0);
  const cartTotal = cartLines.reduce((total, line) => total + line.variant.price * line.quantity, 0);

  async function addToCart(product: StoreProduct, variant: ProductVariant) {
    if (!djangoApi.previewMode && djangoApi.isConfigured) {
      try {
        await djangoApi.addCartItem(variant.id);
        setCartLines((current) => {
          const existing = current.find((line) => line.variant.id === variant.id);
          return existing
            ? current.map((line) => line.variant.id === variant.id ? { ...line, quantity: line.quantity + 1 } : line)
            : [...current, { product, variant, quantity: 1 }];
        });
        setCartOpen(true);
        toast.success(`${product.name} añadido al carrito`);
      } catch (error) {
        toast.error(error instanceof Error ? error.message : "No fue posible añadir el producto.");
      }
      return;
    }

    setCartLines((current) => {
      const existing = current.find((line) => line.variant.id === variant.id);
      if (existing) {
        return current.map((line) => line.variant.id === variant.id ? { ...line, quantity: line.quantity + 1 } : line);
      }
      return [...current, { product, variant, quantity: 1 }];
    });
    setCartOpen(true);
    toast.success(`${product.name} añadido al carrito`);
  }

  async function changeQuantity(variantId: string, delta: number) {
    const currentLine = cartLines.find((line) => line.variant.id === variantId);
    if (!currentLine) return;
    const nextQuantity = currentLine.quantity + delta;
    try {
      if (!djangoApi.previewMode && djangoApi.isConfigured) {
        if (nextQuantity > 0) await djangoApi.updateCartItem(variantId, nextQuantity);
        else await djangoApi.removeCartItem(variantId);
      }
      setCartLines((current) => current
        .map((line) => line.variant.id === variantId ? { ...line, quantity: nextQuantity } : line)
        .filter((line) => line.quantity > 0));
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "No fue posible actualizar el carrito.");
    }
  }

  return (
    <div className="min-h-screen overflow-x-hidden bg-[#f7f7f3] text-[#0a0a0a]">
      <AnnouncementBar />
      <header className="sticky top-0 z-30 border-b border-black/10 bg-[#f7f7f3]/90 backdrop-blur-xl">
        <div className="mx-auto flex h-[76px] max-w-[1320px] items-center justify-between px-5 lg:px-10">
          <a href="#inicio" className="group flex items-center gap-3" aria-label="ZentraFit inicio">
            <BrandLogo />
          </a>
          <nav className="hidden items-center gap-8 text-[11px] font-bold uppercase tracking-[0.16em] lg:flex">
            <a className="nav-link" href="#catalogo">Catálogo</a>
            <a className="nav-link" href="#metodo">Nuestro método</a>
            <a className="nav-link" href="#confianza">Confianza</a>
          </nav>
          <div className="flex items-center gap-2">
            <button className="icon-button hidden sm:inline-flex" aria-label="Buscar" onClick={() => document.getElementById("catalogo")?.scrollIntoView({ behavior: "smooth" })}>
              <Search size={18} strokeWidth={2.2} />
            </button>
            <button className="relative inline-flex h-11 items-center gap-2 rounded-full bg-[#0a0a0a] px-4 text-white transition hover:bg-[#252525] active:scale-[.97]" onClick={() => setCartOpen(true)}>
              <ShoppingBag size={17} />
              <span className="hidden text-[11px] font-bold uppercase tracking-[.14em] sm:inline">Tu bolsa</span>
              <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-[#a2ff00] px-1 text-[10px] font-black text-black">{cartCount}</span>
            </button>
            <button className="icon-button lg:hidden" aria-label="Abrir menú" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>
        {mobileMenuOpen && (
          <nav className="border-t border-black/10 bg-[#f7f7f3] px-5 py-5 lg:hidden">
            <div className="flex flex-col gap-5 text-xs font-bold uppercase tracking-[.16em]">
              <a href="#catalogo" onClick={() => setMobileMenuOpen(false)}>Catálogo</a>
              <a href="#metodo" onClick={() => setMobileMenuOpen(false)}>Nuestro método</a>
              <a href="#confianza" onClick={() => setMobileMenuOpen(false)}>Confianza</a>
            </div>
          </nav>
        )}
      </header>

      <main>
        <section id="inicio" className="relative isolate overflow-hidden bg-[#0a0a0a] text-white">
          <div className="absolute inset-0 bg-[url('/manus-storage/zentrafit-hero_f671d4ed.png')] bg-cover bg-center opacity-80" />
          <div className="absolute inset-0 bg-gradient-to-r from-[#0a0a0a] via-[#0a0a0a]/75 to-transparent" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_75%_20%,rgba(162,255,0,.16),transparent_28%)]" />
          <div className="relative mx-auto grid min-h-[620px] max-w-[1320px] items-end gap-16 px-5 pb-16 pt-24 lg:grid-cols-[1.1fr_.9fr] lg:items-center lg:px-10 lg:pb-24">
            <div className="max-w-[680px]">
              <div className="mb-7 flex items-center gap-3 text-[10px] font-bold uppercase tracking-[.24em] text-[#a2ff00]">
                <span className="h-px w-9 bg-[#a2ff00]" />
                Suplementación con propósito
              </div>
              <h1 className="font-display max-w-4xl text-[clamp(4rem,9vw,8.5rem)] font-black uppercase leading-[.82] tracking-[-.075em]">
                Tu mejor<br /><span className="text-[#a2ff00]">versión</span><br />empieza hoy.
              </h1>
              <p className="mt-8 max-w-lg text-base leading-7 text-white/65 sm:text-lg">
                Productos confiables, orientación clara y entrega a domicilio para que avanzar se sienta tan bien como llegar.
              </p>
              <div className="mt-10 flex flex-col gap-3 sm:flex-row">
                <a href="#catalogo" className="cta-primary">Explorar catálogo <ArrowRight size={17} /></a>
                <a href="#metodo" className="cta-secondary">Conoce ZentraFit</a>
              </div>
              <div className="mt-12 flex flex-wrap items-center gap-x-8 gap-y-3 text-xs text-white/55">
                <span className="flex items-center gap-2"><Check size={15} className="text-[#a2ff00]" /> Marcas aliadas</span>
                <span className="flex items-center gap-2"><Check size={15} className="text-[#a2ff00]" /> Entrega nacional</span>
                <span className="flex items-center gap-2"><Check size={15} className="text-[#a2ff00]" /> Compra segura</span>
              </div>
            </div>
            <div className="hidden justify-end lg:flex">
              <div className="hero-orbit">
                <div className="hero-orbit-ring" />
                <div className="hero-orbit-center"><Dumbbell size={72} strokeWidth={1.2} /></div>
                <span className="hero-tag tag-one">Rendimiento</span>
                <span className="hero-tag tag-two">Bienestar</span>
                <span className="hero-tag tag-three">Constancia</span>
              </div>
            </div>
          </div>
        </section>

        <section id="confianza" className="border-b border-black/10 bg-[#a2ff00]">
          <div className="mx-auto grid max-w-[1320px] gap-0 px-5 sm:grid-cols-3 lg:px-10">
            <TrustItem icon={<Truck size={20} />} title="Envíos a Colombia" text="Acompañamos tu pedido hasta la puerta." />
            <TrustItem icon={<Sparkles size={20} />} title="Selección honesta" text="Productos para objetivos reales." />
            <TrustItem icon={<CircleHelp size={20} />} title="Asesoría clara" text="Decisiones informadas, sin promesas vacías." />
          </div>
        </section>

        <section id="catalogo" className="mx-auto max-w-[1320px] px-5 py-24 lg:px-10 lg:py-32">
          <div className="mb-12 flex flex-col justify-between gap-7 lg:flex-row lg:items-end">
            <div>
              <div className="section-kicker">01 / Selección ZentraFit</div>
              <h2 className="font-display mt-4 max-w-xl text-5xl font-black uppercase leading-[.88] tracking-[-.06em] sm:text-7xl">Encuentra lo que <span className="text-[#8cda00]">te mueve.</span></h2>
            </div>
            <div className="relative w-full lg:max-w-xs">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-black/35" size={17} />
              <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar por producto..." className="h-12 rounded-full border-black/15 bg-white pl-11 text-sm shadow-none focus-visible:ring-[#a2ff00]" />
            </div>
          </div>
          <div className="mb-10 flex gap-2 overflow-x-auto pb-2">
            {categories.map((category) => (
              <button key={category} onClick={() => setActiveCategory(category)} className={`whitespace-nowrap rounded-full border px-5 py-3 text-[11px] font-bold uppercase tracking-[.14em] transition ${activeCategory === category ? "border-[#0a0a0a] bg-[#0a0a0a] text-white" : "border-black/15 bg-transparent text-black/60 hover:border-black/45 hover:text-black"}`}>
                {category}
              </button>
            ))}
          </div>

          {catalogWarning && <div className="mb-8 flex items-center gap-3 rounded-2xl border border-[#a2ff00]/70 bg-[#edffd0] px-5 py-4 text-sm text-black/70"><Zap size={17} className="shrink-0 text-[#70a900]" /> {catalogWarning}</div>}
          {catalogError && <div className="mb-8 rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">No pudimos cargar el catálogo: {catalogError}</div>}
          {catalogLoading ? <ProductSkeletons /> : filteredProducts.length ? (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {filteredProducts.map((product, index) => <ProductCard key={product.id} product={product} index={index} onAdd={addToCart} />)}
            </div>
          ) : (
            <div className="rounded-[28px] border border-dashed border-black/20 bg-white px-6 py-20 text-center"><p className="font-display text-3xl font-black uppercase">No encontramos ese producto.</p><p className="mt-3 text-black/55">Prueba con otra búsqueda o categoría.</p></div>
          )}
        </section>

        <section id="metodo" className="bg-[#0a0a0a] px-5 py-24 text-white lg:px-10 lg:py-32">
          <div className="mx-auto grid max-w-[1320px] gap-16 lg:grid-cols-[.8fr_1.2fr] lg:items-end">
            <div>
              <div className="section-kicker text-[#a2ff00]">02 / Nuestra forma de acompañarte</div>
              <h2 className="font-display mt-5 max-w-md text-5xl font-black uppercase leading-[.88] tracking-[-.06em] sm:text-7xl">Menos ruido.<br /><span className="text-[#a2ff00]">Más enfoque.</span></h2>
              <p className="mt-8 max-w-sm leading-7 text-white/55">ZentraFit nace para hacer la suplementación más directa: productos seleccionados, lenguaje humano y una experiencia que te ayuda a sostener el hábito.</p>
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              <MethodCard number="01" title="Elige" text="Explora opciones alineadas con tu objetivo." />
              <MethodCard number="02" title="Decide" text="Compara presentaciones y precios con claridad." />
              <MethodCard number="03" title="Avanza" text="Recibe en casa y vuelve a lo importante." />
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-[1320px] px-5 py-24 lg:px-10 lg:py-32">
          <div className="rounded-[32px] bg-[#dfffb0] p-8 sm:p-12 lg:flex lg:items-end lg:justify-between lg:p-16">
            <div><div className="section-kicker">03 / Tu ritual comienza aquí</div><h2 className="font-display mt-5 max-w-xl text-5xl font-black uppercase leading-[.88] tracking-[-.06em] sm:text-7xl">Construye tu<br /><span className="text-[#608e00]">constancia.</span></h2></div>
            <div className="mt-9 max-w-sm lg:mt-0"><p className="text-sm leading-6 text-black/60">No necesitas hacerlo perfecto. Solo necesitas una opción confiable para seguir avanzando.</p><a className="mt-6 inline-flex items-center gap-2 text-xs font-black uppercase tracking-[.16em] underline decoration-2 underline-offset-8" href="#catalogo">Ver productos <ArrowRight size={15} /></a></div>
          </div>
        </section>
      </main>

      <footer className="border-t border-black/10 bg-[#f7f7f3] px-5 py-10 lg:px-10">
        <div className="mx-auto flex max-w-[1320px] flex-col gap-6 sm:flex-row sm:items-center sm:justify-between"><BrandLogo footer /><p className="text-xs text-black/45">Your ally for wellness and performance.</p><p className="text-xs text-black/45">© 2026 ZentraFit</p></div>
      </footer>

      {cartOpen && <CartDrawer lines={cartLines} total={cartTotal} onClose={() => setCartOpen(false)} onChange={changeQuantity} />}
    </div>
  );
}

function AnnouncementBar() { return <div className="bg-[#0a0a0a] px-5 py-2.5 text-center text-[10px] font-bold uppercase tracking-[.2em] text-white/75">Tu aliado para el bienestar y el rendimiento <span className="mx-2 text-[#a2ff00]">·</span> Envíos a todo Colombia</div>; }
function BrandLogo({ footer = false }: { footer?: boolean }) { return <img className={footer ? "brand-logo brand-logo-footer" : "brand-logo"} src="/manus-storage/zentrafit-000_87db05dc.png" alt="ZentraFit — suplementos deportivos" />; }
function TrustItem({ icon, title, text }: { icon: React.ReactNode; title: string; text: string }) { return <div className="flex items-start gap-4 border-black/15 py-6 sm:border-r sm:px-8 sm:first:pl-0 sm:last:border-0 lg:py-7"><span className="mt-0.5">{icon}</span><div><p className="text-xs font-black uppercase tracking-[.13em]">{title}</p><p className="mt-1 text-xs text-black/55">{text}</p></div></div>; }
function ProductCard({ product, index, onAdd }: { product: StoreProduct; index: number; onAdd: (product: StoreProduct, variant: ProductVariant) => void }) {
  const variant = product.variants.find((item) => item.active) ?? product.variants[0];
  return <article className="product-card group" style={{ animationDelay: `${index * 60}ms` }}>
    <div className="product-art"><div className="product-art-grid" /><span className="product-art-label">{product.category}</span><span className="product-art-symbol">{product.brand.slice(0, 1)}</span><div className="product-art-shine" /></div>
    <div className="p-5 sm:p-6"><div className="flex items-start justify-between gap-4"><div><p className="text-[10px] font-black uppercase tracking-[.16em] text-black/40">{product.brand}</p><h3 className="mt-2 font-display text-2xl font-black uppercase leading-[.94] tracking-[-.04em]">{product.name}</h3></div><Badge className="shrink-0 rounded-full bg-[#edffd0] text-[9px] font-black uppercase tracking-[.12em] text-[#547c00] hover:bg-[#edffd0]">Activo</Badge></div><p className="mt-4 line-clamp-2 min-h-10 text-sm leading-5 text-black/55">{product.description}</p>{variant ? <><div className="mt-5 flex items-center justify-between border-t border-black/10 pt-4"><div><p className="text-[10px] uppercase tracking-[.15em] text-black/40">{variant.size} {variant.unit} · {variant.flavor}</p><p className="mt-1 text-lg font-black tracking-[-.03em]">{currency.format(variant.price)}</p></div><Button onClick={() => onAdd(product, variant)} className="h-11 rounded-full bg-[#0a0a0a] px-5 text-[10px] font-black uppercase tracking-[.13em] text-white hover:bg-[#a2ff00] hover:text-black"><Plus size={15} /> Añadir</Button></div></> : <div className="mt-5 border-t border-black/10 pt-4 text-sm text-black/45">Presentación no disponible.</div>}</div>
  </article>;
}
function ProductSkeletons() { return <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">{[1, 2, 3].map((key) => <div key={key} className="h-[440px] animate-pulse rounded-[24px] bg-black/5" />)}</div>; }
function MethodCard({ number, title, text }: { number: string; title: string; text: string }) { return <div className="rounded-[24px] border border-white/10 bg-white/[.05] p-6 transition hover:-translate-y-1 hover:border-[#a2ff00]/50"><span className="text-xs font-black text-[#a2ff00]">{number}</span><h3 className="font-display mt-14 text-3xl font-black uppercase tracking-[-.04em]">{title}</h3><p className="mt-3 text-sm leading-6 text-white/50">{text}</p></div>; }
function CartDrawer({ lines, total, onClose, onChange }: { lines: CartLine[]; total: number; onClose: () => void; onChange: (variantId: string, delta: number) => void }) {
  const [checkoutOpen, setCheckoutOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({ name: "", lastName: "", email: "", phone: "", address: "", city: "", paymentMethod: "Transferencia" });

  async function submitOrder(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!djangoApi.isConfigured || djangoApi.previewMode) {
      toast.info("Configura VITE_DJANGO_BASE_URL y VITE_PREVIEW_MODE=false para activar pedidos reales.");
      return;
    }
    setSubmitting(true);
    try {
      const order = await djangoApi.createOrder(form);
      toast.success(`Pedido ${order.orderNumber} creado correctamente.`);
      onClose();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "No fue posible crear el pedido.");
    } finally {
      setSubmitting(false);
    }
  }

  const updateField = (field: keyof typeof form) => (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setForm((current) => ({ ...current, [field]: event.target.value }));
  return <div className="fixed inset-0 z-50"><button className="absolute inset-0 bg-black/45 backdrop-blur-sm" aria-label="Cerrar carrito" onClick={onClose} /><aside className="drawer-panel absolute right-0 top-0 flex h-full w-full max-w-md flex-col bg-[#f7f7f3] p-6 shadow-2xl sm:p-8"><div className="flex items-center justify-between border-b border-black/10 pb-6"><div><p className="section-kicker">{checkoutOpen ? "Datos de entrega" : "Tu selección"}</p><h2 className="font-display mt-2 text-3xl font-black uppercase tracking-[-.05em]">{checkoutOpen ? "Finalizar pedido" : <>Bolsa <span className="text-[#77ae00]">({lines.length})</span></>}</h2></div><button className="icon-button" onClick={onClose} aria-label="Cerrar"><X size={20} /></button></div>{lines.length ? checkoutOpen ? <form onSubmit={submitOrder} className="flex flex-1 flex-col overflow-y-auto py-7"><div className="grid gap-3 sm:grid-cols-2"><Input required placeholder="Nombre" value={form.name} onChange={updateField("name")} /><Input required placeholder="Apellido" value={form.lastName} onChange={updateField("lastName")} /></div><Input required type="email" placeholder="Correo electrónico" value={form.email} onChange={updateField("email")} className="mt-3" /><Input required placeholder="Teléfono" value={form.phone} onChange={updateField("phone")} className="mt-3" /><Input required placeholder="Dirección de entrega" value={form.address} onChange={updateField("address")} className="mt-3" /><Input required placeholder="Ciudad" value={form.city} onChange={updateField("city")} className="mt-3" /><select value={form.paymentMethod} onChange={updateField("paymentMethod")} className="mt-3 h-11 rounded-xl border border-black/15 bg-white px-3 text-sm"><option value="Transferencia">Transferencia bancaria</option><option value="Contra entrega">Contra entrega</option></select><div className="mt-auto border-t border-black/10 pt-6"><div className="flex items-center justify-between"><span className="text-sm text-black/50">Total estimado</span><span className="text-xl font-black">{currency.format(total + 18000)}</span></div><button disabled={submitting} className="mt-5 flex h-14 w-full items-center justify-center gap-2 rounded-full bg-[#0a0a0a] text-xs font-black uppercase tracking-[.16em] text-white transition hover:bg-[#a2ff00] hover:text-black disabled:opacity-50">{submitting ? "Enviando..." : "Crear pedido"}</button><button type="button" onClick={() => setCheckoutOpen(false)} className="mt-4 w-full text-xs font-black uppercase tracking-[.15em] text-black/45">Volver a la bolsa</button></div></form> : <><div className="flex-1 space-y-3 overflow-y-auto py-7">{lines.map((line) => <div key={line.variant.id} className="flex gap-4 rounded-2xl border border-black/10 bg-white p-4"><div className="mini-product-art">{line.product.brand.slice(0, 1)}</div><div className="min-w-0 flex-1"><p className="truncate text-sm font-bold">{line.product.name}</p><p className="mt-1 text-xs text-black/45">{line.variant.size} {line.variant.unit}</p><div className="mt-3 flex items-center justify-between"><span className="text-sm font-black">{currency.format(line.variant.price * line.quantity)}</span><div className="flex items-center gap-2 rounded-full bg-black/5 p-1"><button onClick={() => onChange(line.variant.id, -1)} className="flex h-6 w-6 items-center justify-center rounded-full bg-white"><Minus size={12} /></button><span className="w-4 text-center text-xs font-bold">{line.quantity}</span><button onClick={() => onChange(line.variant.id, 1)} className="flex h-6 w-6 items-center justify-center rounded-full bg-white"><Plus size={12} /></button></div></div></div></div>)}</div><div className="border-t border-black/10 pt-6"><div className="flex items-center justify-between"><span className="text-sm text-black/50">Subtotal</span><span className="text-xl font-black">{currency.format(total)}</span></div><button className="mt-5 flex h-14 w-full items-center justify-center gap-2 rounded-full bg-[#0a0a0a] text-xs font-black uppercase tracking-[.16em] text-white transition hover:bg-[#a2ff00] hover:text-black" onClick={() => setCheckoutOpen(true)}><ShoppingBag size={17} /> Continuar compra</button><p className="mt-3 text-center text-[11px] leading-5 text-black/40">Completa tus datos para crear el pedido en Django.</p></div></> : <div className="flex flex-1 flex-col items-center justify-center text-center"><div className="mb-5 flex h-20 w-20 items-center justify-center rounded-full bg-[#dfffb0]"><ShoppingBag size={28} /></div><h3 className="font-display text-3xl font-black uppercase">Tu bolsa está vacía.</h3><p className="mt-3 max-w-xs text-sm leading-6 text-black/50">Añade una opción para empezar a construir tu próximo avance.</p><button onClick={onClose} className="mt-7 text-xs font-black uppercase tracking-[.15em] underline underline-offset-8">Explorar productos</button></div>}</aside></div>;
}
