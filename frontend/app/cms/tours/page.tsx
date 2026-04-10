"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Pencil, Plus, Search, Trash2, X } from "lucide-react";

import { parseApiError } from "@/lib/api-error";
import { useCategories } from "@/lib/use-categories";
import { CmsSidebar } from "@/components/cms/sidebar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";

type ItineraryDay = { day: number; title: string; description: string };
type CostItem = { item: string; amount: string; note: string };

type TourItem = {
  id: string; title: string; type: string; tour_type: string | null;
  city_id: string | null; provider_id: string;
  description: string | null; detail_description: string | null;
  itinerary: ItineraryDay[] | null;
  costs: CostItem[] | null;
  images: string[] | null;
  duration_days: number | null; created_at: string;
};

type TourListResponse = { items: TourItem[]; total: number; page: number; page_size: number; total_pages: number };
type ProviderOption = { id: string; display_name: string };
type CityOption = { id: string; name: string; country_code: string };
type ModalMode = "create" | "edit";

type TourFormState = {
  title: string; type: string; tour_type: string;
  city_id: string; provider_id: string;
  description: string; detail_description: string;
  itinerary: ItineraryDay[]; costs: CostItem[];
  images: string; duration_days: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";
const SELECT_CLS = "flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm";
const TEXTAREA_CLS = "flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm";
const emptyForm: TourFormState = {
  title: "", type: "activity", tour_type: "", city_id: "", provider_id: "",
  description: "", detail_description: "", itinerary: [], costs: [], images: "", duration_days: "",
};

function ToursPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [items, setItems] = useState<TourItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(Number(searchParams.get("page") ?? "1") || 1);
  const [pageSize] = useState(10);
  const [totalPages, setTotalPages] = useState(1);
  const [searchInput, setSearchInput] = useState(searchParams.get("q") ?? "");
  const [query, setQuery] = useState(searchParams.get("q") ?? "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [providers, setProviders] = useState<ProviderOption[]>([]);
  const [cities, setCities] = useState<CityOption[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<ModalMode>("create");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<TourFormState>(emptyForm);
  const [saving, setSaving] = useState(false);

  const { options: tourTypeOptions } = useCategories("Loại tour");

  const syncUrl = useCallback((p: number, q: string) => {
    const ps = new URLSearchParams();
    if (q) ps.set("q", q);
    if (p > 1) ps.set("page", String(p));
    router.replace(`/cms/tours${ps.toString() ? `?${ps.toString()}` : ""}`);
  }, [router]);

  const loadTours = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const ps = new URLSearchParams({ page: String(page), page_size: String(pageSize), type: "activity" });
      if (query) ps.set("q", query);
      const res = await fetch(`${API_BASE_URL}/product?${ps.toString()}`);
      if (!res.ok) throw new Error("Không tải được tour");
      const data = (await res.json()) as TourListResponse;
      setItems(data.items ?? []); setTotal(data.total ?? 0); setTotalPages(data.total_pages ?? 1);
    } catch (e) { setError(e instanceof Error ? e.message : "Lỗi"); }
    finally { setLoading(false); }
  }, [page, pageSize, query]);

  const loadOptions = useCallback(async () => {
    const [pRes, cRes] = await Promise.all([
      fetch(`${API_BASE_URL}/provider?page=1&page_size=200&type_filter=operator`),
      fetch(`${API_BASE_URL}/city?page=1&page_size=500`),
    ]);
    if (pRes.ok) { const d = (await pRes.json()) as { items: ProviderOption[] }; setProviders(d.items ?? []); }
    if (cRes.ok) { const d = (await cRes.json()) as { items: CityOption[] }; setCities(d.items ?? []); }
  }, []);

  useEffect(() => { void loadTours(); }, [loadTours]);
  useEffect(() => { void loadOptions(); }, [loadOptions]);

  function openCreateModal() { setModalMode("create"); setEditingId(null); setForm(emptyForm); setModalOpen(true); }
  function openEditModal(item: TourItem) {
    setModalMode("edit"); setEditingId(item.id);
    setForm({
      title: item.title, type: item.type, tour_type: item.tour_type ?? "",
      city_id: item.city_id ?? "", provider_id: item.provider_id,
      description: item.description ?? "", detail_description: item.detail_description ?? "",
      itinerary: item.itinerary ?? [],
      costs: item.costs ?? [],
      images: (item.images ?? []).join("\n"),
      duration_days: item.duration_days != null ? String(item.duration_days) : "",
    });
    setModalOpen(true);
  }

  async function submitModal() {
    if (!form.title.trim()) { setError("Tên tour là bắt buộc"); return; }
    if (!form.provider_id) { setError("Vui lòng chọn nhà cung cấp"); return; }
    setSaving(true); setError(null);
    const imagesArr = form.images.split("\n").map((s) => s.trim()).filter(Boolean);
    const payload: Record<string, unknown> = {
      title: form.title.trim(), type: form.type,
      tour_type: form.tour_type || null,
      city_id: form.city_id || null, provider_id: form.provider_id,
      description: form.description.trim() || null,
      detail_description: form.detail_description.trim() || null,
      itinerary: form.itinerary.length ? form.itinerary : null,
      costs: form.costs.length ? form.costs : null,
      images: imagesArr.length ? imagesArr : null,
      duration_days: form.duration_days ? Number(form.duration_days) : null,
    };
    const url = modalMode === "create" ? `${API_BASE_URL}/product` : `${API_BASE_URL}/product/${editingId}`;
    try {
      const res = await fetch(url, { method: modalMode === "create" ? "POST" : "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      if (!res.ok) { setError(await parseApiError(res, "Không thể lưu tour")); return; }
      setModalOpen(false); await loadTours();
    } catch { setError("Không kết nối được tới máy chủ"); }
    finally { setSaving(false); }
  }

  async function removeTour(id: string) {
    if (!window.confirm("Xóa tour này?")) return;
    try {
      const res = await fetch(`${API_BASE_URL}/product/${id}`, { method: "DELETE" });
      if (!res.ok) { setError(await parseApiError(res, "Không thể xóa tour")); return; }
    } catch { setError("Lỗi kết nối"); return; }
    if (items.length === 1 && page > 1) { const n = page - 1; setPage(n); syncUrl(n, query); }
    await loadTours();
  }

  // Lộ trình helpers
  function addDay() { setForm((p) => ({ ...p, itinerary: [...p.itinerary, { day: p.itinerary.length + 1, title: "", description: "" }] })); }
  function removeDay(i: number) { setForm((p) => ({ ...p, itinerary: p.itinerary.filter((_, idx) => idx !== i) })); }
  function updateDay(i: number, field: keyof ItineraryDay, val: string) {
    setForm((p) => { const it = [...p.itinerary]; it[i] = { ...it[i], [field]: field === "day" ? Number(val) : val }; return { ...p, itinerary: it }; });
  }

  // Chi phí helpers
  function addCost() { setForm((p) => ({ ...p, costs: [...p.costs, { item: "", amount: "", note: "" }] })); }
  function removeCost(i: number) { setForm((p) => ({ ...p, costs: p.costs.filter((_, idx) => idx !== i) })); }
  function updateCost(i: number, field: keyof CostItem, val: string) {
    setForm((p) => { const cs = [...p.costs]; cs[i] = { ...cs[i], [field]: val }; return { ...p, costs: cs }; });
  }

  function cityName(id: string) { const c = cities.find((x) => x.id === id); return c ? c.name : "—"; }
  function provName(id: string) { const p = providers.find((x) => x.id === id); return p ? p.display_name : "—"; }
  function applySearch() { setPage(1); setQuery(searchInput.trim()); syncUrl(1, searchInput.trim()); }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#f8fdff,_#f8f6ee_40%,_#f5f4ed)]">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-4 p-4 lg:grid-cols-[280px_1fr]">
        <CmsSidebar />
        <main className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Quản lý tour</CardTitle>
              <CardDescription>Thêm, sửa, xóa tour du lịch với lộ trình và chi phí chi tiết.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-col gap-2 md:flex-row">
                <div className="relative flex-1">
                  <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
                  <Input className="pl-9" value={searchInput} onChange={(e) => setSearchInput(e.target.value)}
                    placeholder="Tìm theo tên tour..." onKeyDown={(e) => { if (e.key === "Enter") applySearch(); }} />
                </div>
                <Button variant="outline" onClick={applySearch}>Tìm</Button>
                <Button onClick={openCreateModal}><Plus className="size-4" />Thêm tour</Button>
              </div>
              {error ? <p className="text-sm font-medium text-red-600">{error}</p> : null}
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Tên tour</TableHead>
                    <TableHead>Loại tour</TableHead>
                    <TableHead>Thành phố</TableHead>
                    <TableHead>Nhà cung cấp</TableHead>
                    <TableHead>Số ngày</TableHead>
                    <TableHead className="text-right">Hành động</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow><TableCell colSpan={6} className="text-center text-muted-foreground">Đang tải...</TableCell></TableRow>
                  ) : items.length ? items.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>
                        <div className="font-medium">{item.title}</div>
                        {item.description ? <div className="max-w-xs truncate text-xs text-muted-foreground">{item.description}</div> : null}
                      </TableCell>
                      <TableCell>{item.tour_type ? <Badge variant="secondary">{item.tour_type}</Badge> : "—"}</TableCell>
                      <TableCell>{item.city_id ? cityName(item.city_id) : "—"}</TableCell>
                      <TableCell>{provName(item.provider_id)}</TableCell>
                      <TableCell>{item.duration_days ? `${item.duration_days} ngày` : "—"}</TableCell>
                      <TableCell className="text-right">
                        <div className="inline-flex gap-1">
                          <Button size="icon" variant="ghost" onClick={() => openEditModal(item)}><Pencil className="size-4" /></Button>
                          <Button size="icon" variant="ghost" onClick={() => void removeTour(item.id)}><Trash2 className="size-4" /></Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  )) : (
                    <TableRow><TableCell colSpan={6} className="text-center text-muted-foreground">Chưa có tour nào.</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
            <CardFooter className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">Tổng: {total} | Trang {page}/{totalPages}</p>
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => { const n = page - 1; setPage(n); syncUrl(n, query); }} disabled={page <= 1}>Trang trước</Button>
                <Button variant="outline" onClick={() => { const n = page + 1; setPage(n); syncUrl(n, query); }} disabled={page >= totalPages}>Trang sau</Button>
              </div>
            </CardFooter>
          </Card>
        </main>
      </div>

      {modalOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/35 p-4">
          <div className="w-full max-w-2xl max-h-[92vh] overflow-y-auto rounded-xl border border-border bg-card p-5 shadow-xl">
            <div className="mb-4 flex items-start justify-between">
              <h3 className="text-lg font-semibold">{modalMode === "create" ? "Thêm tour" : "Cập nhật tour"}</h3>
              <Button size="icon" variant="ghost" onClick={() => setModalOpen(false)}><X className="size-4" /></Button>
            </div>

            <div className="space-y-4">
              {/* Thông tin cơ bản */}
              <div className="space-y-1">
                <label className="text-sm font-medium">Tên tour *</label>
                <Input value={form.title} onChange={(e) => setForm((p) => ({ ...p, title: e.target.value }))} placeholder="Tour Đà Nẵng - Hội An 3N2Đ" />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-sm font-medium">Loại tour</label>
                  <select value={form.tour_type} onChange={(e) => setForm((p) => ({ ...p, tour_type: e.target.value }))} className={SELECT_CLS}>
                    <option value="">-- Chọn loại tour --</option>
                    {tourTypeOptions.map((o) => <option key={o.id} value={o.value}>{o.value}</option>)}
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium">Số ngày</label>
                  <Input type="number" min="1" value={form.duration_days} onChange={(e) => setForm((p) => ({ ...p, duration_days: e.target.value }))} placeholder="3" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-sm font-medium">Thành phố</label>
                  <select value={form.city_id} onChange={(e) => setForm((p) => ({ ...p, city_id: e.target.value }))} className={SELECT_CLS}>
                    <option value="">-- Chọn thành phố --</option>
                    {cities.map((c) => <option key={c.id} value={c.id}>{c.name} ({c.country_code})</option>)}
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium">Nhà cung cấp *</label>
                  <select value={form.provider_id} onChange={(e) => setForm((p) => ({ ...p, provider_id: e.target.value }))} className={SELECT_CLS}>
                    <option value="">-- Chọn nhà cung cấp --</option>
                    {providers.map((p) => <option key={p.id} value={p.id}>{p.display_name}</option>)}
                  </select>
                </div>
              </div>

              {/* Giới thiệu chung */}
              <div className="space-y-1">
                <label className="text-sm font-medium">Giới thiệu chung</label>
                <textarea value={form.description} onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
                  className={`${TEXTAREA_CLS} min-h-[72px]`} placeholder="Tour trải nghiệm 3 ngày 2 đêm tại Đà Nẵng..." />
              </div>

              {/* Giới thiệu chi tiết */}
              <div className="space-y-1">
                <label className="text-sm font-medium">Giới thiệu chi tiết</label>
                <textarea value={form.detail_description} onChange={(e) => setForm((p) => ({ ...p, detail_description: e.target.value }))}
                  className={`${TEXTAREA_CLS} min-h-[96px]`} placeholder="Mô tả chi tiết về tour, điểm nổi bật, đặc trưng..." />
              </div>

              {/* Lộ trình */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium">Lộ trình</label>
                  <Button type="button" variant="outline" size="sm" onClick={addDay}><Plus className="size-3" />Thêm ngày</Button>
                </div>
                {form.itinerary.map((day, i) => (
                  <div key={i} className="rounded-md border border-border/70 p-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-primary">Ngày {day.day}</span>
                      <Button type="button" variant="ghost" size="icon" onClick={() => removeDay(i)} className="size-6"><X className="size-3" /></Button>
                    </div>
                    <Input value={day.title} onChange={(e) => updateDay(i, "title", e.target.value)} placeholder="Tiêu đề ngày (VD: Tham quan Hội An cổ phố)" />
                    <textarea value={day.description} onChange={(e) => updateDay(i, "description", e.target.value)}
                      className={`${TEXTAREA_CLS} min-h-[56px]`} placeholder="Chi tiết hoạt động trong ngày..." />
                  </div>
                ))}
              </div>

              {/* Chi phí */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium">Chi phí từng hạng mục</label>
                  <Button type="button" variant="outline" size="sm" onClick={addCost}><Plus className="size-3" />Thêm hạng mục</Button>
                </div>
                {form.costs.map((cost, i) => (
                  <div key={i} className="grid grid-cols-[1fr_1fr_1fr_auto] gap-2 items-start">
                    <Input value={cost.item} onChange={(e) => updateCost(i, "item", e.target.value)} placeholder="Hạng mục (VD: Vé máy bay)" />
                    <Input value={cost.amount} onChange={(e) => updateCost(i, "amount", e.target.value)} placeholder="Số tiền (VD: 2.500.000)" />
                    <Input value={cost.note} onChange={(e) => updateCost(i, "note", e.target.value)} placeholder="Ghi chú" />
                    <Button type="button" variant="ghost" size="icon" onClick={() => removeCost(i)}><X className="size-4" /></Button>
                  </div>
                ))}
              </div>

              {/* Ảnh */}
              <div className="space-y-1">
                <label className="text-sm font-medium">Hình ảnh (mỗi dòng 1 URL)</label>
                <textarea value={form.images} onChange={(e) => setForm((p) => ({ ...p, images: e.target.value }))}
                  className={`${TEXTAREA_CLS} min-h-[64px] font-mono text-xs`}
                  placeholder={"https://example.com/tour1.jpg\nhttps://example.com/tour2.jpg"} />
              </div>
            </div>

            <div className="mt-5 flex justify-end gap-2">
              <Button variant="outline" onClick={() => setModalOpen(false)}>Hủy</Button>
              <Button onClick={() => void submitModal()} disabled={saving}>
                {saving ? "Đang lưu..." : modalMode === "create" ? "Thêm tour" : "Lưu thay đổi"}
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export default function ToursPage() {
  return (
    <Suspense fallback={<div className="p-4 text-sm text-muted-foreground">Đang tải...</div>}>
      <ToursPageContent />
    </Suspense>
  );
}
