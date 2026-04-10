"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { DoorOpen, Pencil, Plus, Search, Trash2, X } from "lucide-react";

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

type HotelItem = {
  id: string;
  name: string;
  address: string | null;
  star_rating: string | null;
  city_id: string;
  provider_id: string;
  checkin_time: string | null;
  checkout_time: string | null;
  description: string | null;
  images: string | null;
  amenities: string | null;
  usp: string | null;
  room_count: number | null;
  lat: string | null;
  lng: string | null;
};

type HotelListResponse = { items: HotelItem[]; total: number; page: number; page_size: number; total_pages: number };
type ProviderOption = { id: string; display_name: string; type: string };
type CityOption = { id: string; name: string; country_code: string };
type ModalMode = "create" | "edit";

type HotelFormState = {
  name: string; address: string; star_rating: string;
  city_id: string; provider_id: string;
  checkin_time: string; checkout_time: string;
  description: string; images: string; amenities: string[];
  usp: string; room_count: string;
  lat: string; lng: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";
const SELECT_CLS = "flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm disabled:opacity-50";
const emptyForm: HotelFormState = {
  name: "", address: "", star_rating: "", city_id: "", provider_id: "",
  checkin_time: "", checkout_time: "", description: "", images: "",
  amenities: [], usp: "", room_count: "", lat: "", lng: "",
};

function parseJsonArray(s: string | null): string[] {
  if (!s) return [];
  try { return JSON.parse(s) as string[]; } catch { return []; }
}

function HotelsPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [items, setItems] = useState<HotelItem[]>([]);
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
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<ModalMode>("create");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<HotelFormState>(emptyForm);
  const [saving, setSaving] = useState(false);

  const { options: amenityOptions } = useCategories("Tiện nghi khách sạn");

  const syncUrl = useCallback((p: number, q: string) => {
    const ps = new URLSearchParams();
    if (q) ps.set("q", q);
    if (p > 1) ps.set("page", String(p));
    router.replace(`/cms/hotels${ps.toString() ? `?${ps.toString()}` : ""}`);
  }, [router]);

  const loadHotels = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const ps = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
      const url = query
        ? `${API_BASE_URL}/hotel/search/mixin?q=${encodeURIComponent(query)}&page=${page}&page_size=${pageSize}`
        : `${API_BASE_URL}/hotel?${ps.toString()}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error("Không tải được khách sạn");
      const data = (await res.json()) as HotelListResponse;
      setItems(data.items ?? []); setTotal(data.total ?? 0); setTotalPages(data.total_pages ?? 1);
    } catch (e) { setError(e instanceof Error ? e.message : "Lỗi"); }
    finally { setLoading(false); }
  }, [page, pageSize, query]);

  const loadOptions = useCallback(async () => {
    setOptionsLoading(true);
    try {
      const [pRes, cRes] = await Promise.all([
        // Backend giới hạn page_size: provider <= 100, city <= 100 (FastAPI Query validators)
        fetch(`${API_BASE_URL}/provider?page=1&page_size=100&type_filter=hotel`),
        fetch(`${API_BASE_URL}/city?page=1&page_size=100`),
      ]);
      if (pRes.ok) {
        const d = (await pRes.json()) as { items: ProviderOption[] };
        const sorted = (d.items ?? []).sort((a, b) => a.display_name.localeCompare(b.display_name, "vi", { sensitivity: "base" }));
        setProviders(sorted);
        // Tự chọn provider đầu tiên làm mặc định (ẩn combobox)
        setForm((prev) => (prev.provider_id || !sorted[0]?.id ? prev : { ...prev, provider_id: sorted[0].id }));
      }
      if (cRes.ok) {
        const d = (await cRes.json()) as { items: CityOption[] };
        const sorted = (d.items ?? []).sort((a, b) => a.name.localeCompare(b.name, "vi", { sensitivity: "base" }));
        setCities(sorted);
      }
    } finally {
      setOptionsLoading(false);
    }
  }, []);

  useEffect(() => { void loadHotels(); }, [loadHotels]);
  useEffect(() => { void loadOptions(); }, [loadOptions]);

  function openCreateModal() {
    setModalMode("create"); setEditingId(null);
    setForm((prev) => ({
      ...emptyForm,
      // Nếu đã có provider list, tự gán provider đầu tiên làm mặc định
      provider_id: providers[0]?.id ?? "",
    }));
    setModalOpen(true);
  }
  function openEditModal(item: HotelItem) {
    setModalMode("edit"); setEditingId(item.id);
    setForm({
      name: item.name, address: item.address ?? "",
      star_rating: item.star_rating ?? "", city_id: item.city_id,
      provider_id: item.provider_id, checkin_time: item.checkin_time ?? "",
      checkout_time: item.checkout_time ?? "", description: item.description ?? "",
      images: parseJsonArray(item.images).join("\n"),
      amenities: parseJsonArray(item.amenities),
      usp: item.usp ?? "", room_count: item.room_count != null ? String(item.room_count) : "",
      lat: item.lat ?? "", lng: item.lng ?? "",
    });
    setModalOpen(true);
  }

  async function submitModal() {
    if (!form.name.trim()) { setError("Tên khách sạn là bắt buộc"); return; }
    if (!form.city_id) { setError("Vui lòng chọn thành phố"); return; }
    // provider_id được gán mặc định; nếu vẫn trống => thiếu cấu hình
    if (!form.provider_id) { setError("Chưa cấu hình nhà cung cấp mặc định cho khách sạn"); return; }
    setSaving(true); setError(null);
    const imagesArr = form.images.split("\n").map((s) => s.trim()).filter(Boolean);
    const payload: Record<string, unknown> = {
      name: form.name.trim(), city_id: form.city_id, provider_id: form.provider_id,
      address: form.address.trim() || null,
      star_rating: form.star_rating ? Number(form.star_rating) : null,
      checkin_time: form.checkin_time || null, checkout_time: form.checkout_time || null,
      description: form.description.trim() || null,
      images: imagesArr.length ? JSON.stringify(imagesArr) : null,
      amenities: form.amenities.length ? JSON.stringify(form.amenities) : null,
      usp: form.usp.trim() || null,
      room_count: form.room_count ? Number(form.room_count) : null,
      lat: form.lat ? Number(form.lat) : null, lng: form.lng ? Number(form.lng) : null,
    };
    const url = modalMode === "create" ? `${API_BASE_URL}/hotel` : `${API_BASE_URL}/hotel/${editingId}`;
    try {
      const res = await fetch(url, { method: modalMode === "create" ? "POST" : "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      if (!res.ok) { setError(await parseApiError(res, "Không thể lưu")); return; }
      setModalOpen(false); await loadHotels();
    } catch { setError("Không kết nối được tới máy chủ"); }
    finally { setSaving(false); }
  }

  async function removeHotel(id: string) {
    if (!window.confirm("Xóa khách sạn này?")) return;
    try {
      const res = await fetch(`${API_BASE_URL}/hotel/${id}`, { method: "DELETE" });
      if (!res.ok) { setError(await parseApiError(res, "Không thể xóa")); return; }
    } catch { setError("Không kết nối được tới máy chủ"); return; }
    if (items.length === 1 && page > 1) { const n = page - 1; setPage(n); syncUrl(n, query); }
    await loadHotels();
  }

  function toggleAmenity(v: string) {
    setForm((p) => ({
      ...p, amenities: p.amenities.includes(v) ? p.amenities.filter((a) => a !== v) : [...p.amenities, v],
    }));
  }

  function cityName(id: string) { const c = cities.find((x) => x.id === id); return c ? `${c.name}` : "—"; }
  function applySearch() { setPage(1); setQuery(searchInput.trim()); syncUrl(1, searchInput.trim()); }
  function goPrev() { if (page <= 1) return; const n = page - 1; setPage(n); syncUrl(n, query); }
  function goNext() { if (page >= totalPages) return; const n = page + 1; setPage(n); syncUrl(n, query); }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#f8fdff,_#f8f6ee_40%,_#f5f4ed)]">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-4 p-4 lg:grid-cols-[280px_1fr]">
        <CmsSidebar />
        <main className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Quản lý khách sạn</CardTitle>
              <CardDescription>Thêm, sửa, xóa khách sạn. Nhấn nút Phòng để quản lý phòng.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-col gap-2 md:flex-row">
                <div className="relative flex-1">
                  <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
                  <Input className="pl-9" value={searchInput} onChange={(e) => setSearchInput(e.target.value)}
                    placeholder="Tìm theo tên, địa chỉ..." onKeyDown={(e) => { if (e.key === "Enter") applySearch(); }} />
                </div>
                <Button variant="outline" onClick={applySearch}>Tìm</Button>
                <Button onClick={openCreateModal}><Plus className="size-4" />Thêm khách sạn</Button>
              </div>
              {error ? <p className="text-sm font-medium text-red-600">{error}</p> : null}
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Tên khách sạn</TableHead>
                    <TableHead>Thành phố</TableHead>
                    <TableHead>Sao</TableHead>
                    <TableHead>Số phòng</TableHead>
                    <TableHead className="text-right">Hành động</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow><TableCell colSpan={6} className="text-center text-muted-foreground">Đang tải...</TableCell></TableRow>
                  ) : items.length ? items.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>
                        <div className="font-medium">{item.name}</div>
                        {item.usp ? <div className="text-xs text-muted-foreground">{item.usp}</div> : null}
                      </TableCell>
                      <TableCell>{cityName(item.city_id)}</TableCell>
                      <TableCell>{item.star_rating ? <Badge variant="secondary">{item.star_rating}⭐</Badge> : "—"}</TableCell>
                      <TableCell>{item.room_count ?? "—"}</TableCell>
                      <TableCell className="text-right">
                        <div className="inline-flex gap-1">
                          <Button size="icon" variant="ghost" asChild aria-label="Quản lý phòng">
                            <Link href={`/cms/hotels/${item.id}/rooms`}><DoorOpen className="size-4" /></Link>
                          </Button>
                          <Button size="icon" variant="ghost" onClick={() => openEditModal(item)} aria-label="Sửa"><Pencil className="size-4" /></Button>
                          <Button size="icon" variant="ghost" onClick={() => void removeHotel(item.id)} aria-label="Xóa"><Trash2 className="size-4" /></Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  )) : (
                    <TableRow><TableCell colSpan={6} className="text-center text-muted-foreground">Không có dữ liệu.</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
            <CardFooter className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">Tổng: {total} | Trang {page}/{totalPages}</p>
              <div className="flex gap-2">
                <Button variant="outline" onClick={goPrev} disabled={page <= 1}>Trang trước</Button>
                <Button variant="outline" onClick={goNext} disabled={page >= totalPages}>Trang sau</Button>
              </div>
            </CardFooter>
          </Card>
        </main>
      </div>

      {modalOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/35 p-4">
          <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-xl border border-border bg-card p-5 shadow-xl">
            <div className="mb-4 flex items-start justify-between">
              <h3 className="text-lg font-semibold">{modalMode === "create" ? "Thêm khách sạn" : "Cập nhật khách sạn"}</h3>
              <Button size="icon" variant="ghost" onClick={() => setModalOpen(false)}><X className="size-4" /></Button>
            </div>

            <div className="space-y-3">
              {/* Tên */}
              <div className="space-y-1">
                <label className="text-sm font-medium">Tên khách sạn *</label>
                <Input value={form.name} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))} placeholder="Vinpearl Resort Đà Nẵng" />
              </div>

              {/* Thành phố */}
              <div className="space-y-1">
                <label className="text-sm font-medium">Thành phố *</label>
                <select
                  value={form.city_id}
                  onChange={(e) => setForm((p) => ({ ...p, city_id: e.target.value }))}
                  className={SELECT_CLS}
                  disabled={optionsLoading || cities.length === 0}
                >
                  <option value="">{optionsLoading ? "Đang tải danh sách..." : "-- Chọn thành phố --"}</option>
                  {!optionsLoading && cities.length === 0 ? (
                    <option value="" disabled>
                      Chưa có dữ liệu thành phố
                    </option>
                  ) : null}
                  {cities.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} ({c.country_code})
                    </option>
                  ))}
                </select>
              </div>

              {/* Địa chỉ + Sao + Số phòng */}
              <div className="grid grid-cols-3 gap-3">
                <div className="col-span-1 space-y-1">
                  <label className="text-sm font-medium">Số sao</label>
                  <Input type="number" min="0" max="5" step="0.5" value={form.star_rating}
                    onChange={(e) => setForm((p) => ({ ...p, star_rating: e.target.value }))} placeholder="4.5" />
                </div>
                <div className="col-span-1 space-y-1">
                  <label className="text-sm font-medium">Số phòng</label>
                  <Input type="number" min="1" value={form.room_count}
                    onChange={(e) => setForm((p) => ({ ...p, room_count: e.target.value }))} placeholder="120" />
                </div>
                <div className="col-span-1 space-y-1">
                  <label className="text-sm font-medium">Địa chỉ</label>
                  <Input value={form.address} onChange={(e) => setForm((p) => ({ ...p, address: e.target.value }))} placeholder="123 Đường ABC" />
                </div>
              </div>

              {/* Check-in / Check-out */}
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-sm font-medium">Check-in</label>
                  <Input value={form.checkin_time} onChange={(e) => setForm((p) => ({ ...p, checkin_time: e.target.value }))} placeholder="14:00:00" />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium">Check-out</label>
                  <Input value={form.checkout_time} onChange={(e) => setForm((p) => ({ ...p, checkout_time: e.target.value }))} placeholder="12:00:00" />
                </div>
              </div>

              {/* Tọa độ */}
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-sm font-medium">Vị trí - Lat</label>
                  <Input value={form.lat} onChange={(e) => setForm((p) => ({ ...p, lat: e.target.value }))} placeholder="16.047079" />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium">Vị trí - Lng</label>
                  <Input value={form.lng} onChange={(e) => setForm((p) => ({ ...p, lng: e.target.value }))} placeholder="108.206230" />
                </div>
              </div>

              {/* USP */}
              <div className="space-y-1">
                <label className="text-sm font-medium">Điểm đặc trưng (USP)</label>
                <Input value={form.usp} onChange={(e) => setForm((p) => ({ ...p, usp: e.target.value }))} placeholder="Gần biển, view triệu đô, ngay trung tâm..." />
              </div>

              {/* Giới thiệu */}
              <div className="space-y-1">
                <label className="text-sm font-medium">Giới thiệu chung</label>
                <textarea value={form.description} onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
                  className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  placeholder="Mô tả ngắn về khách sạn..." />
              </div>

              {/* Tiện nghi khách sạn - checkbox từ danh mục */}
              <div className="space-y-1">
                <label className="text-sm font-medium">Tiện nghi khách sạn</label>
                {amenityOptions.length === 0 ? (
                  <p className="text-xs text-muted-foreground">Chưa có dữ liệu — thêm vào danh mục "Tiện nghi khách sạn"</p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {amenityOptions.map((opt) => (
                      <label key={opt.id} className="flex cursor-pointer items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-sm hover:bg-accent">
                        <input type="checkbox" checked={form.amenities.includes(opt.value)}
                          onChange={() => toggleAmenity(opt.value)} className="accent-primary" />
                        {opt.value}
                      </label>
                    ))}
                  </div>
                )}
              </div>

              {/* Ảnh - mỗi dòng 1 URL */}
              <div className="space-y-1">
                <label className="text-sm font-medium">Hình ảnh (mỗi dòng 1 URL)</label>
                <textarea value={form.images} onChange={(e) => setForm((p) => ({ ...p, images: e.target.value }))}
                  className="flex min-h-[72px] w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-xs"
                  placeholder={"https://example.com/img1.jpg\nhttps://example.com/img2.jpg"} />
              </div>
            </div>

            <div className="mt-5 flex justify-end gap-2">
              <Button variant="outline" onClick={() => setModalOpen(false)}>Hủy</Button>
              <Button onClick={() => void submitModal()} disabled={saving}>
                {saving ? "Đang lưu..." : modalMode === "create" ? "Thêm mới" : "Lưu thay đổi"}
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export default function HotelsPage() {
  return (
    <Suspense fallback={<div className="p-4 text-sm text-muted-foreground">Đang tải...</div>}>
      <HotelsPageContent />
    </Suspense>
  );
}
