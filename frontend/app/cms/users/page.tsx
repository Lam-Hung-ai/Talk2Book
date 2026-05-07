"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Pencil, Plus, Search, Trash2, X } from "lucide-react";

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

type UserItem = {
  id: string;
  email: string;
  phone: string;
  status: string;
  created_at: string;
};

type UserListResponse = {
  items: UserItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

type ModalMode = "create" | "edit";

type UserFormState = {
  email: string;
  phone: string;
  password: string;
  status: string;
};

const STATUS_OPTIONS = [
  { value: "", label: "Tất cả" },
  { value: "active", label: "Hoạt động" },
  { value: "suspended", label: "Tạm khóa" },
  { value: "deleted", label: "Đã xóa" },
];

const STATUS_VARIANT: Record<string, "default" | "secondary" | "outline"> = {
  active: "default",
  suspended: "secondary",
  deleted: "outline",
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

const emptyForm: UserFormState = {
  email: "",
  phone: "",
  password: "",
  status: "active",
};

function UsersPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [items, setItems] = useState<UserItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(Number(searchParams.get("page") ?? "1") || 1);
  const [pageSize] = useState(10);
  const [totalPages, setTotalPages] = useState(1);

  const [statusFilter, setStatusFilter] = useState(searchParams.get("status") ?? "");
  const [searchInput, setSearchInput] = useState(searchParams.get("q") ?? "");
  const [query, setQuery] = useState(searchParams.get("q") ?? "");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<ModalMode>("create");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<UserFormState>(emptyForm);
  const [saving, setSaving] = useState(false);

  const syncUrl = useCallback(
    (nextPage: number, nextStatus: string, nextQuery: string) => {
      const params = new URLSearchParams();
      if (nextStatus) params.set("status", nextStatus);
      if (nextQuery) params.set("q", nextQuery);
      if (nextPage > 1) params.set("page", String(nextPage));
      router.replace(`/cms/users${params.toString() ? `?${params.toString()}` : ""}`);
    },
    [router]
  );

  const loadUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      if (query) {
        const res = await fetch(
          `${API_BASE_URL}/user/search/mixin?q=${encodeURIComponent(query)}&page=${page}&page_size=${pageSize}`
        );
        if (!res.ok) throw new Error("Không tải được người dùng");
        const data = (await res.json()) as UserListResponse;
        setItems(data.items ?? []);
        setTotal(data.total ?? 0);
        setTotalPages(data.total_pages ?? 1);
      } else {
        const params = new URLSearchParams({
          page: String(page),
          page_size: String(pageSize),
        });
        const res = await fetch(`${API_BASE_URL}/user?${params.toString()}`);
        if (!res.ok) throw new Error("Không tải được người dùng");
        const data = (await res.json()) as UserListResponse;
        setItems(data.items ?? []);
        setTotal(data.total ?? 0);
        setTotalPages(data.total_pages ?? 1);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Lỗi không xác định");
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, query]);

  useEffect(() => {
    void loadUsers();
  }, [loadUsers]);

  function openCreateModal() {
    setModalMode("create");
    setEditingId(null);
    setForm(emptyForm);
    setModalOpen(true);
  }

  function openEditModal(item: UserItem) {
    setModalMode("edit");
    setEditingId(item.id);
    setForm({
      email: item.email,
      phone: item.phone,
      password: "",
      status: item.status,
    });
    setModalOpen(true);
  }

  async function submitModal() {
    if (!form.email.trim() || !form.phone.trim()) {
      setError("Email và số điện thoại là bắt buộc");
      return;
    }
    if (modalMode === "create" && !form.password.trim()) {
      setError("Mật khẩu là bắt buộc khi tạo mới");
      return;
    }

    setSaving(true);
    setError(null);

    const url =
      modalMode === "create"
        ? `${API_BASE_URL}/user`
        : `${API_BASE_URL}/user/${editingId}`;
    const method = modalMode === "create" ? "POST" : "PUT";

    const payload: Record<string, unknown> = {
      email: form.email.trim(),
      phone: form.phone.trim(),
      status: form.status,
    };
    if (modalMode === "create") {
      payload.password = form.password;
    } else if (form.password.trim()) {
      payload.password = form.password.trim();
    }

    try {
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        setError(await parseApiError(res, "Không thể lưu người dùng"));
        return;
      }
      setModalOpen(false);
      await loadUsers();
    } finally {
      setSaving(false);
    }
  }

  async function removeUser(id: string) {
    if (!window.confirm("Bạn chắc chắn muốn xóa người dùng này?")) return;
    const res = await fetch(`${API_BASE_URL}/user/${id}`, { method: "DELETE" });
    if (!res.ok) {
      setError(await parseApiError(res, "Không thể xóa người dùng"));
      return;
    }
    if (items.length === 1 && page > 1) {
      const next = page - 1;
      setPage(next);
      syncUrl(next, statusFilter, query);
    }
    await loadUsers();
  }

  function onChangeStatus(value: string) {
    setPage(1);
    setStatusFilter(value);
    syncUrl(1, value, query);
  }

  function applySearch() {
    setPage(1);
    setQuery(searchInput.trim());
    syncUrl(1, statusFilter, searchInput.trim());
  }

  function goPrev() {
    if (page <= 1) return;
    const next = page - 1;
    setPage(next);
    syncUrl(next, statusFilter, query);
  }

  function goNext() {
    if (page >= totalPages) return;
    const next = page + 1;
    setPage(next);
    syncUrl(next, statusFilter, query);
  }

  function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString("vi-VN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#f8fdff,_#f8f6ee_40%,_#f5f4ed)]">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-4 p-4 lg:grid-cols-[280px_1fr]">
        <CmsSidebar />
        <main className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Quản lý người dùng</CardTitle>
              <CardDescription>Thêm, sửa, xóa tài khoản người dùng trong hệ thống.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Tab filter trạng thái */}
              <div className="flex flex-wrap gap-1 border-b border-border pb-3">
                {STATUS_OPTIONS.map(({ value, label }) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => onChangeStatus(value)}
                    className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
                      statusFilter === value
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
                    placeholder="Tìm theo email, tên..."
                    onKeyDown={(e) => { if (e.key === "Enter") applySearch(); }}
                  />
                </div>
                <Button variant="outline" onClick={applySearch}>Tìm</Button>
                <Button onClick={openCreateModal}>
                  <Plus className="size-4" />
                  Thêm người dùng
                </Button>
              </div>

              {error ? <p className="text-sm font-medium text-red-600">{error}</p> : null}

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Email</TableHead>
                    <TableHead>Số điện thoại</TableHead>
                    <TableHead>Trạng thái</TableHead>
                    <TableHead>Ngày tạo</TableHead>
                    <TableHead className="text-right">Hành động</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center text-muted-foreground">
                        Đang tải dữ liệu...
                      </TableCell>
                    </TableRow>
                  ) : items.length ? (
                    items.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell className="font-medium">{item.email}</TableCell>
                        <TableCell>{item.phone}</TableCell>
                        <TableCell>
                          <Badge variant={STATUS_VARIANT[item.status] ?? "outline"}>
                            {STATUS_OPTIONS.find((s) => s.value === item.status)?.label ?? item.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {formatDate(item.created_at)}
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="inline-flex gap-1">
                            <Button size="icon" variant="ghost" onClick={() => openEditModal(item)} aria-label="Sửa">
                              <Pencil className="size-4" />
                            </Button>
                            <Button size="icon" variant="ghost" onClick={() => void removeUser(item.id)} aria-label="Xóa">
                              <Trash2 className="size-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center text-muted-foreground">
                        Không có người dùng phù hợp.
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

      {modalOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/35 p-4">
          <div className="w-full max-w-md rounded-xl border border-border bg-card p-5 shadow-xl">
            <div className="mb-4 flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold">
                  {modalMode === "create" ? "Thêm người dùng" : "Cập nhật người dùng"}
                </h3>
              </div>
              <Button size="icon" variant="ghost" onClick={() => setModalOpen(false)}>
                <X className="size-4" />
              </Button>
            </div>

            <div className="space-y-3">
              <div className="space-y-1">
                <label className="text-sm font-medium" htmlFor="u-email">Email *</label>
                <Input id="u-email" type="email" value={form.email}
                  onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
                  placeholder="user@example.com" />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium" htmlFor="u-phone">Số điện thoại *</label>
                <Input id="u-phone" value={form.phone}
                  onChange={(e) => setForm((p) => ({ ...p, phone: e.target.value }))}
                  placeholder="+84912345678" />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium" htmlFor="u-password">
                  {modalMode === "create" ? "Mật khẩu *" : "Mật khẩu mới (để trống để giữ nguyên)"}
                </label>
                <Input id="u-password" type="password" value={form.password}
                  onChange={(e) => setForm((p) => ({ ...p, password: e.target.value }))}
                  placeholder="Ít nhất 6 ký tự" />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium" htmlFor="u-status">Trạng thái</label>
                <select
                  id="u-status"
                  value={form.status}
                  onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))}
                  className="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
                >
                  <option value="active">Hoạt động</option>
                  <option value="suspended">Tạm khóa</option>
                  <option value="deleted">Đã xóa</option>
                </select>
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

export default function UsersPage() {
  return (
    <Suspense fallback={<div className="p-4 text-sm text-muted-foreground">Đang tải trang...</div>}>
      <UsersPageContent />
    </Suspense>
  );
}
