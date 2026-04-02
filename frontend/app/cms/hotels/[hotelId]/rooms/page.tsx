"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Pencil, Plus, Trash2, X } from "lucide-react";

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

type RoomItem = {
  id: string; hotel_id: string; code: string | null; capacity: number;
  bed_config: string | null; room_type: string | null; area_sqm: number | null;
  view_type: string | null; amenities: string | null; service_package: string | null;
  cancellation_policy: string | null; description: string | null; images: string | null;
};

type RoomListResponse = { items: RoomItem[]; total: number; page: number; page_size: number; total_pages: number };
type HotelInfo = { id: string; name: string };
type ModalMode = "create" | "edit";

type RoomFormState = {
  code: string; capacity: string; bed_config: string;
  room_type: string; area_sqm: string; view_type: string;
  amenities: string[]; service_package: string;
  cancellation_policy: string; description: string; images: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";
const SELECT_CLS = "flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm";
const emptyForm: RoomFormState = {
  code: "", capacity: "1", bed_config: "", room_type: "", area_sqm: "",
  view_type: "", amenities: [], service_package: "", cancellation_policy: "", description: "", images: "",
};

function parseJsonArray(s: string | null): string[] {
  if (!s) return [];
  try { return JSON.parse(s) as string[]; } catch { return []; }
}

function RoomsPageContent() {
  const { hotelId } = useParams<{ hotelId: string }>();

  const [hotel, setHotel] = useState<HotelInfo | null>(null);
  const [items, setItems] = useState<RoomItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<ModalMode>("create");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<RoomFormState>(emptyForm);
  const [saving, setSaving] = useState(false);

  const { options: roomTypeOptions } = useCategories("Loại phòng");
  const { options: viewOptions } = useCategories("Tầm nhìn phòng");
  const { options: amenityOptions } = useCategories("Tiện nghi phòng");
  const { options: packageOptions } = useCategories("Gói dịch vụ phòng");

  const loadHotel = useCallback(async () => {
    if (!hotelId) return;
    const res = await fetch(`${API_BASE_URL}/hotel/${hotelId}`);
    if (res.ok) { const d = (await res.json()) as HotelInfo; setHotel(d); }
  }, [hotelId]);

  const loadRooms = useCallback(async () => {
    if (!hotelId) return;
    setLoading(true); setError(null);
    try {
      const ps = new URLSearchParams({ page: String(page), page_size: String(pageSize), hotel_id: hotelId });
      const res = await fetch(`${API_BASE_URL}/hotel-room?${ps.toString()}`);
      if (!res.ok) throw new Error("Không tải được phòng");
      const data = (await res.json()) as RoomListResponse;
      setItems(data.items ?? []); setTotal(data.total ?? 0); setTotalPages(data.total_pages ?? 1);
    } catch (e) { setError(e instanceof Error ? e.message : "Lỗi"); }
    finally { setLoading(false); }
  }, [hotelId, page, pageSize]);

  useEffect(() => { void loadHotel(); void loadRooms(); }, [loadHotel, loadRooms]);

  function openCreateModal() { setModalMode("create"); setEditingId(null); setForm(emptyForm); setModalOpen(true); }
  function openEditModal(item: RoomItem) {
    setModalMode("edit"); setEditingId(item.id);
    setForm({
      code: item.code ?? "", capacity: String(item.capacity), bed_config: item.bed_config ?? "",
      room_type: item.room_type ?? "", area_sqm: item.area_sqm != null ? String(item.area_sqm) : "",
      view_type: item.view_type ?? "", amenities: parseJsonArray(item.amenities),
      service_package: item.service_package ?? "", cancellation_policy: item.cancellation_policy ?? "",
      description: item.description ?? "", images: parseJsonArray(item.images).join("\n"),
    });
    setModalOpen(true);
  }

  async function submitModal() {
    if (!form.capacity || Number(form.capacity) < 1) { setError("Sức chứa phải >= 1"); return; }
    setSaving(true); setError(null);
    const imagesArr = form.images.split("\n").map((s) => s.trim()).filter(Boolean);
    const payload: Record<string, unknown> = {
      hotel_id: hotelId,
      code: form.code.trim() || null, capacity: Number(form.capacity),
      bed_config: form.bed_config.trim() || null,
      room_type: form.room_type || null, area_sqm: form.area_sqm ? Number(form.area_sqm) : null,
      view_type: form.view_type || null,
      amenities: form.amenities.length ? JSON.stringify(form.amenities) : null,
      service_package: form.service_package || null,
      cancellation_policy: form.cancellation_policy.trim() || null,
      description: form.description.trim() || null,
      images: imagesArr.length ? JSON.stringify(imagesArr) : null,
    };
    const url = modalMode === "create" ? `${API_BASE_URL}/hotel-room` : `${API_BASE_URL}/hotel-room/${editingId}`;
    try {
      const res = await fetch(url, { method: modalMode === "create" ? "POST" : "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      if (!res.ok) { setError(await parseApiError(res, "Không thể lưu phòng")); return; }
      setModalOpen(false); await loadRooms();
    } catch { setError("Không kết nối được tới máy chủ"); }
    finally { setSaving(false); }
  }

  async function removeRoom(id: string) {
    if (!window.confirm("Xóa phòng này?")) return;
    try {
      const res = await fetch(`${API_BASE_URL}/hotel-room/${id}`, { method: "DELETE" });
      if (!res.ok) { setError(await parseApiError(res, "Không thể xóa")); return; }
    } catch { setError("Lỗi kết nối"); return; }
    if (items.length === 1 && page > 1) setPage(page - 1);
    await loadRooms();
  }

  function toggleAmenity(v: string) {
    setForm((p) => ({ ...p, amenities: p.amenities.includes(v) ? p.amenities.filter((a) => a !== v) : [...p.amenities, v] }));
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#f8fdff,_#f8f6ee_40%,_#f5f4ed)]">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-4 p-4 lg:grid-cols-[280px_1fr]">
        <CmsSidebar />
        <main className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <Button variant="outline" size="icon" asChild><Link href="/cms/hotels"><ArrowLeft className="size-4" /></Link></Button>
                <div>
                  <CardTitle>Phòng — {hotel?.name ?? hotelId}</CardTitle>
                  <CardDescription>Quản lý phòng khách sạn: loại phòng, tiện nghi, ảnh, giá gói.</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-end">
                <Button onClick={openCreateModal}><Plus className="size-4" />Thêm phòng</Button>
              </div>
              {error ? <p className="text-sm font-medium text-red-600">{error}</p> : null}
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Mã phòng</TableHead>
                    <TableHead>Loại phòng</TableHead>
                    <TableHead>Sức chứa</TableHead>
                    <TableHead>Diện tích</TableHead>
                    <TableHead>Tầm nhìn</TableHead>
                    <TableHead>Gói dịch vụ</TableHead>
                    <TableHead className="text-right">Hành động</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow><TableCell colSpan={7} className="text-center text-muted-foreground">Đang tải...</TableCell></TableRow>
                  ) : items.length ? items.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium">{item.code ?? "—"}</TableCell>
                      <TableCell>{item.room_type ? <Badge variant="secondary">{item.room_type}</Badge> : "—"}</TableCell>
                      <TableCell>{item.capacity} người</TableCell>
                      <TableCell>{item.area_sqm ? `${item.area_sqm} m²` : "—"}</TableCell>
                      <TableCell>{item.view_type ?? "—"}</TableCell>
                      <TableCell>{item.service_package ?? "—"}</TableCell>
                      <TableCell className="text-right">
                        <div className="inline-flex gap-1">
                          <Button size="icon" variant="ghost" onClick={() => openEditModal(item)}><Pencil className="size-4" /></Button>
                          <Button size="icon" variant="ghost" onClick={() => void removeRoom(item.id)}><Trash2 className="size-4" /></Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  )) : (
                    <TableRow><TableCell colSpan={7} className="text-center text-muted-foreground">Chưa có phòng nào.</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
            <CardFooter className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">Tổng: {total} | Trang {page}/{totalPages}</p>
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page <= 1}>Trang trước</Button>
                <Button variant="outline" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page >= totalPages}>Trang sau</Button>
              </div>
            </CardFooter>
          </Card>
        </main>
      </div>

      {modalOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/35 p-4">
          <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-xl border border-border bg-card p-5 shadow-xl">
            <div className="mb-4 flex items-start justify-between">
              <h3 className="text-lg font-semibold">{modalMode === "create" ? "Thêm phòng" : "Cập nhật phòng"}</h3>
              <Button size="icon" variant="ghost" onClick={() => setModalOpen(false)}><X className="size-4" /></Button>
            </div>

            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-sm font-medium">Mã phòng</label>
                  <Input value={form.code} onChange={(e) => setForm((p) => ({ ...p, code: e.target.value }))} placeholder="STD, DLX, STE..." />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium">Sức chứa (người) *</label>
                  <Input type="number" min="1" value={form.capacity} onChange={(e) => setForm((p) => ({ ...p, capacity: e.target.value }))} />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-sm font-medium">Loại phòng</label>
                  <select value={form.room_type} onChange={(e) => setForm((p) => ({ ...p, room_type: e.target.value }))} className={SELECT_CLS}>
                    <option value="">-- Chọn loại phòng --</option>
                    {roomTypeOptions.map((o) => <option key={o.id} value={o.value}>{o.value}</option>)}
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium">Diện tích (m²)</label>
                  <Input type="number" min="1" value={form.area_sqm} onChange={(e) => setForm((p) => ({ ...p, area_sqm: e.target.value }))} placeholder="25" />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-sm font-medium">Cấu hình giường / phòng</label>
                <Input value={form.bed_config} onChange={(e) => setForm((p) => ({ ...p, bed_config: e.target.value }))} placeholder="2 giường đơn, điều hòa, tủ lạnh..." />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-sm font-medium">Tầm nhìn (View)</label>
                  <select value={form.view_type} onChange={(e) => setForm((p) => ({ ...p, view_type: e.target.value }))} className={SELECT_CLS}>
                    <option value="">-- Chọn tầm nhìn --</option>
                    {viewOptions.map((o) => <option key={o.id} value={o.value}>{o.value}</option>)}
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium">Gói dịch vụ</label>
                  <select value={form.service_package} onChange={(e) => setForm((p) => ({ ...p, service_package: e.target.value }))} className={SELECT_CLS}>
                    <option value="">-- Chọn gói --</option>
                    {packageOptions.map((o) => <option key={o.id} value={o.value}>{o.value}</option>)}
                  </select>
                </div>
              </div>

              {/* Tiện nghi phòng - checkbox */}
              <div className="space-y-1">
                <label className="text-sm font-medium">Tiện nghi trong phòng</label>
                {amenityOptions.length === 0 ? (
                  <p className="text-xs text-muted-foreground">Thêm vào danh mục "Tiện nghi phòng" để hiện ở đây</p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {amenityOptions.map((opt) => (
                      <label key={opt.id} className="flex cursor-pointer items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-sm hover:bg-accent">
                        <input type="checkbox" checked={form.amenities.includes(opt.value)} onChange={() => toggleAmenity(opt.value)} className="accent-primary" />
                        {opt.value}
                      </label>
                    ))}
                  </div>
                )}
              </div>

              <div className="space-y-1">
                <label className="text-sm font-medium">Chính sách hoàn hủy</label>
                <textarea value={form.cancellation_policy} onChange={(e) => setForm((p) => ({ ...p, cancellation_policy: e.target.value }))}
                  className="flex min-h-[60px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  placeholder="Miễn phí hủy trước 24h, sau đó tính phí 1 đêm..." />
              </div>

              <div className="space-y-1">
                <label className="text-sm font-medium">Mô tả phòng</label>
                <textarea value={form.description} onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
                  className="flex min-h-[60px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  placeholder="Phòng rộng rãi với nội thất hiện đại..." />
              </div>

              <div className="space-y-1">
                <label className="text-sm font-medium">Hình ảnh (mỗi dòng 1 URL)</label>
                <textarea value={form.images} onChange={(e) => setForm((p) => ({ ...p, images: e.target.value }))}
                  className="flex min-h-[64px] w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-xs"
                  placeholder={"https://example.com/room1.jpg\nhttps://example.com/room2.jpg"} />
              </div>
            </div>

            <div className="mt-5 flex justify-end gap-2">
              <Button variant="outline" onClick={() => setModalOpen(false)}>Hủy</Button>
              <Button onClick={() => void submitModal()} disabled={saving}>
                {saving ? "Đang lưu..." : modalMode === "create" ? "Thêm phòng" : "Lưu thay đổi"}
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export default function RoomsPage() {
  return (
    <Suspense fallback={<div className="p-4 text-sm text-muted-foreground">Đang tải...</div>}>
      <RoomsPageContent />
    </Suspense>
  );
}
