import { useEffect, useState } from "react";
import { Link, useRoute } from "wouter";
import { ArrowLeft, ChevronLeft, ChevronRight, ShoppingBag } from "lucide-react";
import { toast } from "sonner";
import { djangoApi, type ProductVariant, type StoreProduct } from "@/lib/djangoApi";

const currency = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});

export default function ProductDetail() {
  const [, params] = useRoute("/producto/:id");
  const [product, setProduct] = useState<StoreProduct | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [imageIndex, setImageIndex] = useState(0);
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null);

  useEffect(() => {
    let cancelled = false;
    djangoApi.getCatalog()
      .then((catalog) => {
        if (cancelled) return;
        const found = catalog.products.find((item) => item.id === decodeURIComponent(params?.id ?? ""));
        if (!found) {
          setError("No encontramos este producto.");
          return;
        }
        setProduct(found);
        setSelectedVariant(found.variants.find((variant) => variant.active) ?? found.variants[0] ?? null);
      })
      .catch((reason: Error) => {
        if (!cancelled) setError(reason.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [params?.id]);

  if (loading) return <div className="flex min-h-screen items-center justify-center bg-[#f7f7f3] text-sm text-black/50">Cargando producto...</div>;
  if (error || !product) return <div className="flex min-h-screen flex-col items-center justify-center bg-[#f7f7f3] px-6 text-center"><p className="section-kicker">Catálogo ZentraFit</p><h1 className="font-display mt-4 text-4xl font-black uppercase">{error || "Producto no disponible"}</h1><Link href="/" className="mt-8 inline-flex items-center gap-2 rounded-full bg-[#0a0a0a] px-6 py-4 text-xs font-black uppercase tracking-[.14em] text-white"><ArrowLeft size={16} /> Volver al catálogo</Link></div>;

  const images = product.images.length ? product.images : product.imageUrl ? [product.imageUrl] : [];
  const goPrevious = () => setImageIndex((current) => (current - 1 + images.length) % images.length);
  const goNext = () => setImageIndex((current) => (current + 1) % images.length);
  const addToCart = async () => {
    if (!selectedVariant) return;
    if (djangoApi.previewMode || !djangoApi.isConfigured) {
      toast.info("Configura la conexión con Django para activar pedidos reales.");
      return;
    }
    try {
      await djangoApi.addCartItem(selectedVariant.id);
      toast.success(`${product.name} añadido al carrito.`);
    } catch (reason) {
      toast.error(reason instanceof Error ? reason.message : "No fue posible añadir el producto.");
    }
  };

  return <main className="min-h-screen bg-[#f7f7f3] text-[#0a0a0a]">
    <header className="border-b border-black/10 bg-[#f7f7f3]/90 px-5 py-5 backdrop-blur-xl lg:px-10"><div className="mx-auto flex max-w-[1320px] items-center justify-between"><Link href="/" className="inline-flex items-center gap-2 text-xs font-black uppercase tracking-[.14em] text-black/60 hover:text-black"><ArrowLeft size={16} /> Volver al catálogo</Link><Link href="/" className="font-display text-lg font-black tracking-[-.05em]">Zentra<span className="text-[#70a900]">Fit</span></Link></div></header>
    <section className="mx-auto grid max-w-[1320px] gap-10 px-5 py-12 lg:grid-cols-[1.05fr_.95fr] lg:gap-20 lg:px-10 lg:py-20">
      <div>
        <div className="product-art h-[min(72vw,540px)] rounded-[28px] shadow-[0_22px_55px_rgba(10,10,10,.12)]">
          <div className="product-art-grid" /><span className="product-art-label">{product.category}</span><span className="product-art-symbol">{product.brand.slice(0, 1)}</span><div className="product-art-shine" />
          {images.length ? <img src={images[imageIndex]} alt={`${product.name} — imagen ${imageIndex + 1}`} className="relative z-10 h-full w-full object-contain p-8 sm:p-14 drop-shadow-[0_18px_25px_rgba(0,0,0,.38)]" /> : <p className="relative z-10 m-auto font-display text-8xl font-black italic text-[#a2ff00]/70">{product.brand.slice(0, 1)}</p>}
          {images.length > 1 && <><button type="button" aria-label="Imagen anterior" onClick={goPrevious} className="absolute left-4 top-1/2 z-20 flex h-11 w-11 -translate-y-1/2 items-center justify-center rounded-full bg-black/55 text-white hover:bg-[#a2ff00] hover:text-black"><ChevronLeft /></button><button type="button" aria-label="Siguiente imagen" onClick={goNext} className="absolute right-4 top-1/2 z-20 flex h-11 w-11 -translate-y-1/2 items-center justify-center rounded-full bg-black/55 text-white hover:bg-[#a2ff00] hover:text-black"><ChevronRight /></button></>}
        </div>
        {images.length > 1 && <div className="mt-4 flex gap-3 overflow-x-auto">{images.map((image, index) => <button key={image} type="button" onClick={() => setImageIndex(index)} className={`h-20 w-20 shrink-0 overflow-hidden rounded-2xl border-2 bg-[#161616] p-1 ${index === imageIndex ? "border-[#a2ff00]" : "border-transparent"}`}><img src={image} alt={`${product.name} miniatura ${index + 1}`} className="h-full w-full object-contain" /></button>)}</div>}
      </div>
      <div className="flex flex-col justify-center"><p className="section-kicker">{product.brand} · {product.category}</p><h1 className="font-display mt-5 text-5xl font-black uppercase leading-[.88] tracking-[-.06em] sm:text-7xl">{product.name}</h1><p className="mt-7 max-w-xl text-base leading-7 text-black/60">{product.description}</p>{product.variants.length > 1 && <div className="mt-8"><p className="text-[10px] font-black uppercase tracking-[.16em] text-black/45">Presentación</p><div className="mt-3 flex flex-wrap gap-2">{product.variants.map((variant) => <button key={variant.id} type="button" onClick={() => setSelectedVariant(variant)} className={`rounded-full border px-4 py-3 text-xs font-bold ${selectedVariant?.id === variant.id ? "border-black bg-black text-white" : "border-black/15 bg-white hover:border-black/40"}`}>{variant.size} {variant.unit} · {variant.flavor}</button>)}</div></div>}{selectedVariant && <div className="mt-10 border-t border-black/10 pt-6"><p className="text-sm text-black/50">{selectedVariant.size} {selectedVariant.unit} · {selectedVariant.flavor}</p><p className="mt-2 text-3xl font-black">{currency.format(selectedVariant.price)}</p><button type="button" onClick={addToCart} className="mt-6 inline-flex h-14 w-full items-center justify-center gap-3 rounded-full bg-[#0a0a0a] text-xs font-black uppercase tracking-[.14em] text-white transition hover:bg-[#a2ff00] hover:text-black sm:w-auto sm:px-8"><ShoppingBag size={17} /> Añadir al carrito</button></div>}</div>
    </section>
  </main>;
}
