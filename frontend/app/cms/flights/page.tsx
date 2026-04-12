"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Pencil, Plus, Search, Trash2, X } from "lucide-react";

import { parseApiError } from "@/lib/api-error";
import { useCategories } from "@/lib/use-categories";
import { CmsSidebar } from "@/components/cms/sidebar";
import { Button } from "@/components/ui/button";
import {
  Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";

type FlightItem = {
  id: string; provider_id: string; route_id: string; flight_number: string;
  dow: string; dep_time: string; arr_time: string; arrival_day_offset: number;
  amenities: string[] | null; price_from: number | null;
};

type FlightListResponse = { items: FlightItem[]; total: number; page: number; page_size: number; total_pages: number };
type ProviderOption = { id: string; display_name: string };
type RouteOption = { id: string; origin: string; destination: string; distance_km: number | null };
type ModalMode = "create" | "edit";

type FlightFormState = {
  provider_id: string; route_id: string; flight_number: string;
  dow: string; dep_time: string; arr_time: string; arrival_day_offset: string;
  amenities: string[]; price_from: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";
const SELECT_CLS = "flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm";
const emptyForm: FlightFormState = {
  provider_id: "", route_id: "", flight_number: "", dow: "1111100",
  dep_time: "", arr_time: "", arrival_day_offset: "0",
  amenities: [], price_from: "",
};

const DOW_LABELS = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"];

function parseDow(dow: string): string {
  return dow.split("").map((c, i) => c === "1" ? DOW_LABELS[i] : null).filter(Boolean).join(", ") || "—";
}

function FlightsPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [items, setItems] = useState<FlightItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(Number(searchParams.get("page") ?? "1") || 1);
  const [pageSize] = useState(10);
  const [totalPages, setTotalPages] = useState(1);
  const [searchInput, setSearchInput] = useState(searchParams.get("q") ?? "");
  const [query, setQuery] = useState(searchParams.get("q") ?? "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [providers, setProviders] = useState<ProviderOption[]>([]);
  const [routes, setRoutes] = useState<RouteOption[]>([]);
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<ModalMode>("create");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<FlightFormState>(emptyForm);
  const [saving, setSaving] = useState(false);

  const { options: amenityOptions } = useCategories("Tiện nghi chuyến bay");

  const syncUrl = useCallback((p: number, q: string) => {
    const ps = new URLSearchParams();
    if (q) ps.set("q", q);
    if (p > 1) ps.set("page", String(p));
    router.replace(`/cms/flights${ps.toString() ? `?${ps.toString()}` : ""}`);
  }, [router]);

  const loadFlights = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const ps = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
      if (query) ps.set("q", query);
      const res = await fetch(`${API_BASE_URL}/flight-schedule?${ps.toString()}`);
      if (!res.ok) throw new Error("Không tải được lịch bay");
      const data = (await res.json()) as FlightListResponse;
      setItems(data.items ?? []); setTotal(data.total ?? 0); setTotalPages(data.total_pages ?? 1);
    } catch (e) { setError(e instanceof Error ? e.message : "Lỗi"); }
    finally { setLoading(false); }
  }, [page, pageSize, query]);

  const loadOptions = useCallback(async () => {
    setOptionsLoading(true);
    try {
      const [pRes, rRes] = await Promise.all([
        // Backend giới hạn page_size: provider <= 100, route <= 200 (FastAPI Query validators)
        fetch(`${API_BASE_URL}/provider?page=1&page_size=100&type_filter=airline`),
        fetch(`${API_BASE_URL}/route?page=1&page_size=200`),
      ]);
      if (pRes.ok) {
        const d = (await pRes.json()) as { items: ProviderOption[] };
        const sorted = (d.items ?? []).sort((a, b) => a.display_name.localeCompare(b.display_name, "vi", { sensitivity: "base" }));
        setProviders(sorted);
      }
      if (rRes.ok) {
        const d = (await rRes.json()) as { items: RouteOption[] };
        const sorted = (d.items ?? []).sort((a, b) => `${a.origin}${a.destination}`.localeCompare(`${b.origin}${b.destination}`, "en", { sensitivity: "base" }));
        setRoutes(sorted);
      }
    } finally {
      setOptionsLoading(false);
    }
  }, []);

  useEffect(() => { void loadFlights(); }, [loadFlights]);
  useEffect(() => { void loadOptions(); }, [loadOptions]);

  function openCreateModal() { setModalMode("create"); setEditingId(null); setForm(emptyForm); setModalOpen(true); }
  function openEditModal(item: FlightItem) {
    setModalMode("edit"); setEditingId(item.id);
    setForm({
      provider_id: item.provider_id, route_id: item.route_id,
      flight_number: item.flight_number, dow: item.dow,
      dep_time: item.dep_time, arr_time: item.arr_time,
      arrival_day_offset: String(item.arrival_day_offset),
      amenities: item.amenities ?? [],
      price_from: item.price_from != null ? String(item.price_from) : "",
    });
    setModalOpen(true);
  }

  async function submitModal() {
    if (!form.flight_number.trim()) { setError("Số hiệu chuyến bay là bắt buộc"); return; }
    if (!form.provider_id) { setError("Vui lòng chọn hãng hàng không"); return; }
    if (!form.route_id) { setError("Vui lòng chọn tuyến bay"); return; }
    if (!form.dep_time || !form.arr_time) { setError("Giờ cất/hạ cánh là bắt buộc"); return; }
    if (form.dow.length !== 7 || !/^[01]{7}$/.test(form.dow)) { setError("DOW phải là 7 ký tự 0/1 (VD: 1111100)"); return; }

    setSaving(true); setError(null);
    const payload: Record<string, unknown> = {
      provider_id: form.provider_id, route_id: form.route_id,
      flight_number: form.flight_number.trim().toUpperCase(),
      dow: form.dow, dep_time: form.dep_time, arr_time: form.arr_time,
      arrival_day_offset: Number(form.arrival_day_offset) || 0,
      amenities: form.amenities.length ? form.amenities : null,
      price_from: form.price_from ? Number(form.price_from) : null,
    };
    const url = modalMode === "create" ? `${API_BASE_URL}/flight-schedule` : `${API_BASE_URL}/flight-schedule/${editingId}`;
    try {
      const res = await fetch(url, { method: modalMode === "create" ? "POST" : "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      if (!res.ok) { setError(await parseApiError(res, "Không thể lưu lịch bay")); return; }
      setModalOpen(false); await loadFlights();
    } catch { setError("Không kết nối được tới máy chủ"); }
    finally { setSaving(false); }
  }

  async function removeSchedule(id: string) {
    if (!window.confirm("Xóa lịch bay này?")) return;
    try {
      const res = await fetch(`${API_BASE_URL}/flight-schedule/${id}`, { method: "DELETE" });
      if (!res.ok) { setError(await parseApiError(res, "Không thể xóa")); return; }
    } catch { setError("Lỗi kết nối"); return; }
    if (items.length === 1 && page > 1) { const n = page - 1; setPage(n); syncUrl(n, query); }
    await loadFlights();
  }

  function toggleAmenity(v: string) {
    setForm((p) => ({ ...p, amenities: p.amenities.includes(v) ? p.amenities.filter((a) => a !== v) : [...p.amenities, v] }));
  }
  function toggleDow(i: number) {
    setForm((p) => {
      const arr = p.dow.split("");
      arr[i] = arr[i] === "1" ? "0" : "1";
      return { ...p, dow: arr.join("") };
    });
  }

  function routeLabel(id: string) {
    const r = routes.find((x) => x.id === id);
    return r ? `${r.origin} → ${r.destination}` : "—";
  }
  function provName(id: string) { const p = providers.find((x) => x.id === id); return p ? p.display_name : "—"; }
  function applySearch() { setPage(1); setQuery(searchInput.trim()); syncUrl(1, searchInput.trim()); }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#f8fdff,_#f8f6ee_40%,_#f5f4ed)]">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-4 p-4 lg:grid-cols-[280px_1fr]">
        <CmsSidebar />
        <main className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Quản lý lịch bay</CardTitle>
              <CardDescription>
                Thêm, sửa, xóa lịch bay — hãng bay, tuyến, tiện ích, giá tham khảo. Hạng ghế và mã máy bay theo từng ngày bay nằm ở flight instance / seat inventory.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-col gap-2 md:flex-row">
                <div className="relative flex-1">
                  <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
                  <Input className="pl-9" value={searchInput} onChange={(e) => setSearchInput(e.target.value)}
                    placeholder="Tìm số hiệu chuyến bay..." onKeyDown={(e) => { if (e.key === "Enter") applySearch(); }} />
                </div>
                <Button variant="outline" onClick={applySearch}>Tìm</Button>
                <Button onClick={openCreateModal}><Plus className="size-4" />Thêm lịch bay</Button>
              </div>
              {error ? <p className="text-sm font-medium text-red-600">{error}</p> : null}
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Số hiệu</TableHead>
                    <TableHead>Hãng bay</TableHead>
                    <TableHead>Tuyến</TableHead>
                    <TableHead>Giờ bay</TableHead>
                    <TableHead>Giá từ</TableHead>
                    <TableHead className="text-right">Hành động</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow><TableCell colSpan={6} className="text-center text-muted-foreground">Đang tải...</TableCell></TableRow>
                  ) : items.length ? items.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>
                        <div className="font-mono font-semibold">{item.flight_number}</div>
                        <div className="text-xs text-muted-foreground">{parseDow(item.dow)}</div>
                      </TableCell>
                      <TableCell>{provName(item.provider_id)}</TableCell>
                      <TableCell>
                        <span className="rounded bg-primary/10 px-1.5 py-0.5 font-mono text-xs text-primary">
                          {routeLabel(item.route_id)}
                        </span>
                      </TableCell>
                      <TableCell className="text-sm">
                        {item.dep_time} → {item.arr_time}
                        {item.arrival_day_offset ? <span className="text-xs text-muted-foreground"> +{item.arrival_day_offset}d</span> : null}
                      </TableCell>
                      <TableCell className="text-sm">
                        {item.price_from ? `${Number(item.price_from).toLocaleString("vi-VN")} đ` : "—"}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="inline-flex gap-1">
                          <Button size="icon" variant="ghost" onClick={() => openEditModal(item)}><Pencil className="size-4" /></Button>
                          <Button size="icon" variant="ghost" onClick={() => void removeSchedule(item.id)}><Trash2 className="size-4" /></Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  )) : (
                    <TableRow><TableCell colSpan={6} className="text-center text-muted-foreground">Chưa có lịch bay nào.</TableCell></TableRow>
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
          <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-xl border border-border bg-card p-5 shadow-xl">
            <div className="mb-4 flex items-start justify-between">
              <h3 className="text-lg font-semibold">{modalMode === "create" ? "Thêm lịch bay" : "Cập nhật lịch bay"}</h3>
              <Button size="icon" variant="ghost" onClick={() => setModalOpen(false)}><X className="size-4" /></Button>
            </div>

            <div className="space-y-3">
              {/* Hãng bay */}
              <div className="space-y-1">
                <label className="text-sm font-medium">Hãng hàng không *</label>
                <select
                  value={form.provider_id}
                  onChange={(e) => setForm((p) => ({ ...p, provider_id: e.target.value }))}
                  className={SELECT_CLS}
                  disabled={optionsLoading || providers.length === 0}
                >
                  <option value="">{optionsLoading ? "Đang tải danh sách..." : "-- Chọn hãng bay --"}</option>
                  {!optionsLoading && providers.length === 0 ? (
                    <option value="" disabled>Chưa có dữ liệu hãng bay</option>
                  ) : null}
                  {providers.map((p) => <option key={p.id} value={p.id}>{p.display_name}</option>)}
                </select>
              </div>

              {/* Tuyến bay */}
              <div className="space-y-1">
                <label className="text-sm font-medium">Tuyến bay *</label>
                <select
                  value={form.route_id}
                  onChange={(e) => setForm((p) => ({ ...p, route_id: e.target.value }))}
                  className={SELECT_CLS}
                  disabled={optionsLoading || routes.length === 0}
                >
                  <option value="">{optionsLoading ? "Đang tải danh sách..." : "-- Chọn tuyến bay --"}</option>
                  {!optionsLoading && routes.length === 0 ? (
                    <option value="" disabled>Chưa có dữ liệu tuyến bay</option>
                  ) : null}
                  {routes.map((r) => <option key={r.id} value={r.id}>{r.origin} → {r.destination}{r.distance_km ? ` (${r.distance_km} km)` : ""}</option>)}
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-sm font-medium">Số hiệu chuyến bay *</label>
                <Input
                  value={form.flight_number}
                  onChange={(e) => setForm((p) => ({ ...p, flight_number: e.target.value.toUpperCase() }))}
                  placeholder="VN201"
                  className="font-mono max-w-md"
                />
              </div>

              {/* Ngày bay trong tuần */}
              <div className="space-y-1">
                <label className="text-sm font-medium">Ngày bay trong tuần</label>
                <div className="flex gap-2">
                  {DOW_LABELS.map((label, i) => (
                    <button key={i} type="button" onClick={() => toggleDow(i)}
                      className={`rounded-md border px-2.5 py-1 text-sm font-medium transition ${form.dow[i] === "1" ? "border-primary bg-primary text-primary-foreground" : "border-border text-muted-foreground hover:bg-accent"}`}>
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Giờ bay */}
              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1">
                  <label className="text-sm font-medium">Giờ khởi hành *</label>
                  <Input value={form.dep_time} onChange={(e) => setForm((p) => ({ ...p, dep_time: e.target.value }))} placeholder="06:00:00" />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium">Giờ hạ cánh *</label>
                  <Input value={form.arr_time} onChange={(e) => setForm((p) => ({ ...p, arr_time: e.target.value }))} placeholder="08:10:00" />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium">Lệch ngày (+)</label>
                  <Input type="number" min="0" value={form.arrival_day_offset} onChange={(e) => setForm((p) => ({ ...p, arrival_day_offset: e.target.value }))} placeholder="0" />
                </div>
              </div>

              {/* Giá tham khảo */}
              <div className="space-y-1">
                <label className="text-sm font-medium">Giá tham khảo (chưa VAT, thuế phí) — VND</label>
                <Input type="number" min="0" value={form.price_from} onChange={(e) => setForm((p) => ({ ...p, price_from: e.target.value }))} placeholder="1500000" />
              </div>

              {/* Tiện ích chuyến bay */}
              {amenityOptions.length > 0 ? (
                <div className="space-y-1">
                  <label className="text-sm font-medium">Tiện ích chuyến bay</label>
                  <div className="flex flex-wrap gap-2">
                    {amenityOptions.map((opt) => (
                      <label key={opt.id} className="flex cursor-pointer items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-sm hover:bg-accent">
                        <input type="checkbox" checked={form.amenities.includes(opt.value)} onChange={() => toggleAmenity(opt.value)} className="accent-primary" />
                        {opt.value}
                      </label>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>

            <div className="mt-5 flex justify-end gap-2">
              <Button variant="outline" onClick={() => setModalOpen(false)}>Hủy</Button>
              <Button onClick={() => void submitModal()} disabled={saving}>
                {saving ? "Đang lưu..." : modalMode === "create" ? "Thêm lịch bay" : "Lưu thay đổi"}
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export default function FlightsPage() {
  return (
    <Suspense fallback={<div className="p-4 text-sm text-muted-foreground">Đang tải...</div>}>
      <FlightsPageContent />
    </Suspense>
  );
}
