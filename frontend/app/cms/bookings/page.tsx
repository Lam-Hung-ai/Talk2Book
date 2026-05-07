"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Eye, Search, Trash2, X } from "lucide-react";

import { parseApiError } from "@/lib/api-error";
import { CmsSidebar } from "@/components/cms/sidebar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type BookingItem = {
  id: string;
  user_id: string | null;
  state: string;
  currency_code: string;
  total_amount: string;
  created_at: string;
  updated_at: string | null;
};

type BookingListResponse = {
  items: BookingItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

const BOOKING_STATES = [
  { value: "", label: "Tất cả" },
  { value: "draft", label: "Nháp" },
  { value: "pending_payment", label: "Chờ TT" },
  { value: "confirmed", label: "Đã xác nhận" },
  { value: "cancelled", label: "Đã hủy" },
  { value: "refunded", label: "Đã hoàn" },
];

const STATE_VARIANT: Record<string, "default" | "secondary" | "outline"> = {
  confirmed: "default",
  pending_payment: "secondary",
  draft: "outline",
  cancelled: "outline",
  refunded: "outline",
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

type DetailModal = {
  open: boolean;
  booking: BookingItem | null;
  newState: string;
  saving: boolean;
};

function BookingsPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [items, setItems] = useState<BookingItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(Number(searchParams.get("page") ?? "1") || 1);
  const [pageSize] = useState(10);
  const [totalPages, setTotalPages] = useState(1);

  const [stateFilter, setStateFilter] = useState(searchParams.get("state") ?? "");
  const [searchInput, setSearchInput] = useState(searchParams.get("q") ?? "");
  const [query, setQuery] = useState(searchParams.get("q") ?? "");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [detail, setDetail] = useState<DetailModal>({
    open: false,
    booking: null,
    newState: "",
    saving: false,
  });

  const syncUrl = useCallback(
    (nextPage: number, nextState: string, nextQuery: string) => {
      const params = new URLSearchParams();
      if (nextState) params.set("state", nextState);
      if (nextQuery) params.set("q", nextQuery);
      if (nextPage > 1) params.set("page", String(nextPage));
      router.replace(`/cms/bookings${params.toString() ? `?${params.toString()}` : ""}`);
    },
    [router]
  );

  const loadBookings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
      });
      if (stateFilter) params.set("state", stateFilter);

      const res = await fetch(`${API_BASE_URL}/booking?${params.toString()}`);
      if (!res.ok) throw new Error("Không tải được danh sách đặt chỗ");
      const data = (await res.json()) as BookingListResponse;
      setItems(data.items ?? []);
      setTotal(data.total ?? 0);
      setTotalPages(data.total_pages ?? 1);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Lỗi không xác định");
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, stateFilter]);

  useEffect(() => {
    void loadBookings();
  }, [loadBookings]);

  function openDetail(booking: BookingItem) {
    setDetail({ open: true, booking, newState: booking.state, saving: false });
  }

  async function saveState() {
    if (!detail.booking) return;
    setDetail((d) => ({ ...d, saving: true }));
    try {
      const res = await fetch(`${API_BASE_URL}/booking/${detail.booking.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ state: detail.newState }),
      });
      if (!res.ok) {
        setError(await parseApiError(res, "Không thể cập nhật trạng thái"));
        return;
      }
      setDetail((d) => ({ ...d, open: false }));
      await loadBookings();
    } finally {
      setDetail((d) => ({ ...d, saving: false }));
    }
  }

  async function removeBooking(id: string) {
    if (!window.confirm("Bạn chắc chắn muốn xóa booking này?")) return;
    const res = await fetch(`${API_BASE_URL}/booking/${id}`, { method: "DELETE" });
    if (!res.ok) {
      setError(await parseApiError(res, "Không thể xóa booking"));
      return;
    }
    if (items.length === 1 && page > 1) {
      const next = page - 1;
      setPage(next);
      syncUrl(next, stateFilter, query);
    }
    await loadBookings();
  }

  function onChangeState(value: string) {
    setPage(1);
    setStateFilter(value);
    syncUrl(1, value, query);
  }

  function applySearch() {
    setPage(1);
    setQuery(searchInput.trim());
    syncUrl(1, stateFilter, searchInput.trim());
  }

  function goPrev() {
    if (page <= 1) return;
    const next = page - 1;
    setPage(next);
    syncUrl(next, stateFilter, query);
  }

  function goNext() {
    if (page >= totalPages) return;
    const next = page + 1;
    setPage(next);
    syncUrl(next, stateFilter, query);
  }

  function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString("vi-VN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function formatAmount(amount: string, currency: string) {
    return `${Number(amount).toLocaleString("vi-VN")} ${currency}`;
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#f8fdff,_#f8f6ee_40%,_#f5f4ed)]">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-4 p-4 lg:grid-cols-[280px_1fr]">
        <CmsSidebar />
        <main className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Quản lý Booking</CardTitle>
              <CardDescription>Xem, cập nhật trạng thái và xóa đơn đặt chỗ.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Tab filter trạng thái */}
              <div className="flex flex-wrap gap-1 border-b border-border pb-3">
                {BOOKING_STATES.map(({ value, label }) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => onChangeState(value)}
                    className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
                      stateFilter === value
                        ? "bg-primary text-primary-foreground"
                        : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>

              <div className="flex flex-col gap-2 md:flex-row">
                <div className="relative flex-1">
                  <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    className="pl-9"
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    placeholder="Tìm theo Booking ID..."
                    onKeyDown={(e) => { if (e.key === "Enter") applySearch(); }}
                  />
                </div>
                <Button variant="outline" onClick={applySearch}>Tìm</Button>
              </div>

              {error ? <p className="text-sm font-medium text-red-600">{error}</p> : null}

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Booking ID</TableHead>
                    <TableHead>User ID</TableHead>
                    <TableHead>Trạng thái</TableHead>
                    <TableHead>Tổng tiền</TableHead>
                    <TableHead>Ngày tạo</TableHead>
                    <TableHead className="text-right">Hành động</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center text-muted-foreground">
                        Đang tải dữ liệu...
                      </TableCell>
                    </TableRow>
                  ) : items.length ? (
                    items.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell className="font-mono text-xs">{item.id.slice(0, 8)}...</TableCell>
                        <TableCell className="font-mono text-xs">
                          {item.user_id ? `${item.user_id.slice(0, 8)}...` : "-"}
                        </TableCell>
                        <TableCell>
                          <Badge variant={STATE_VARIANT[item.state] ?? "outline"}>
                            {BOOKING_STATES.find((s) => s.value === item.state)?.label ?? item.state}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-medium">
                          {formatAmount(item.total_amount, item.currency_code)}
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {formatDate(item.created_at)}
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="inline-flex gap-1">
                            <Button size="icon" variant="ghost" onClick={() => openDetail(item)} aria-label="Xem/Sửa">
                              <Eye className="size-4" />
                            </Button>
                            <Button size="icon" variant="ghost" onClick={() => void removeBooking(item.id)} aria-label="Xóa">
                              <Trash2 className="size-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center text-muted-foreground">
                        Không có booking phù hợp.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
            <CardFooter className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Tổng: {total} | Trang {page}/{totalPages}
              </p>
              <div className="flex gap-2">
                <Button variant="outline" onClick={goPrev} disabled={page <= 1}>Trang trước</Button>
                <Button variant="outline" onClick={goNext} disabled={page >= totalPages}>Trang sau</Button>
              </div>
            </CardFooter>
          </Card>
        </main>
      </div>

      {/* Detail / Edit state modal */}
      {detail.open && detail.booking ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/35 p-4">
          <div className="w-full max-w-lg rounded-xl border border-border bg-card p-5 shadow-xl">
            <div className="mb-4 flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold">Chi tiết Booking</h3>
                <p className="font-mono text-xs text-muted-foreground">{detail.booking.id}</p>
              </div>
              <Button size="icon" variant="ghost" onClick={() => setDetail((d) => ({ ...d, open: false }))}>
                <X className="size-4" />
              </Button>
            </div>

            <div className="space-y-2 rounded-md border border-border/70 bg-muted/30 p-3 text-sm">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <p className="text-xs text-muted-foreground">User ID</p>
                  <p className="font-mono text-xs">{detail.booking.user_id ?? "Khách vãng lai"}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Tổng tiền</p>
                  <p className="font-semibold">
                    {formatAmount(detail.booking.total_amount, detail.booking.currency_code)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Ngày tạo</p>
                  <p>{formatDate(detail.booking.created_at)}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Cập nhật</p>
                  <p>{detail.booking.updated_at ? formatDate(detail.booking.updated_at) : "-"}</p>
                </div>
              </div>
            </div>

            <div className="mt-4 space-y-1">
              <label className="text-sm font-medium" htmlFor="b-state">Cập nhật trạng thái</label>
              <select
                id="b-state"
                value={detail.newState}
                onChange={(e) => setDetail((d) => ({ ...d, newState: e.target.value }))}
                className="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
              >
                {BOOKING_STATES.filter((s) => s.value).map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>

            <div className="mt-5 flex justify-end gap-2">
              <Button variant="outline" onClick={() => setDetail((d) => ({ ...d, open: false }))}>
                Đóng
              </Button>
              <Button onClick={() => void saveState()} disabled={detail.saving}>
                {detail.saving ? "Đang lưu..." : "Lưu trạng thái"}
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export default function BookingsPage() {
  return (
    <Suspense fallback={<div className="p-4 text-sm text-muted-foreground">Đang tải trang...</div>}>
      <BookingsPageContent />
    </Suspense>
  );
}
