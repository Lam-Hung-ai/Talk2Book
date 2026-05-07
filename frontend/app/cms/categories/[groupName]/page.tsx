"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { ArrowLeft, Pencil, Plus, Search, Trash2, X } from "lucide-react";

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

type CategoryItem = {
  id: string;
  group_name: string;
  value: string;
  description: string | null;
  sort_order: number;
  is_active: boolean;
};

type CategoryListResponse = {
  items: CategoryItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

type ModalMode = "create" | "edit";

type CategoryFormState = {
  value: string;
  description: string;
  sort_order: number;
  is_active: boolean;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

const emptyForm: CategoryFormState = {
  value: "",
  description: "",
  sort_order: 0,
  is_active: true,
};

function CategoryGroupPageContent() {
  const params = useParams<{ groupName: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();

  const groupName = decodeURIComponent(params.groupName);

  const [items, setItems] = useState<CategoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [totalPages, setTotalPages] = useState(1);

  const [searchInput, setSearchInput] = useState(searchParams.get("q") ?? "");
  const [query, setQuery] = useState(searchParams.get("q") ?? "");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<ModalMode>("create");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<CategoryFormState>(emptyForm);

  const syncUrl = useCallback(
    (nextPage: number, nextQuery: string) => {
      const paramsUrl = new URLSearchParams();
      if (nextQuery) {
        paramsUrl.set("q", nextQuery);
      }
      if (nextPage > 1) {
        paramsUrl.set("page", String(nextPage));
      }
      router.replace(
        `/cms/categories/${encodeURIComponent(groupName)}${
          paramsUrl.toString() ? `?${paramsUrl.toString()}` : ""
        }`
      );
    },
    [groupName, router]
  );

  const loadCategories = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const paramsUrl = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
        group_name: groupName,
      });
      if (query) {
        paramsUrl.set("q", query);
      }

      const response = await fetch(`${API_BASE_URL}/category?${paramsUrl.toString()}`);
      if (!response.ok) {
        throw new Error("Không tải được danh mục");
      }

      const payload = (await response.json()) as CategoryListResponse;
      setItems(payload.items ?? []);
      setTotal(payload.total ?? 0);
      setTotalPages(payload.total_pages ?? 1);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Lỗi không xác định");
    } finally {
      setLoading(false);
    }
  }, [groupName, page, pageSize, query]);

  useEffect(() => {
    const initialPage = Number(searchParams.get("page") ?? "1");
    if (!Number.isNaN(initialPage) && initialPage > 0 && initialPage !== page) {
      setPage(initialPage);
    }

    const qParam = searchParams.get("q") ?? "";
    if (qParam !== query) {
      setQuery(qParam);
      setSearchInput(qParam);
    }
  }, [page, query, searchParams]);

  useEffect(() => {
    void loadCategories();
  }, [loadCategories]);

  function openCreateModal() {
    setModalMode("create");
    setEditingId(null);
    setForm(emptyForm);
    setModalOpen(true);
  }

  function openEditModal(item: CategoryItem) {
    setModalMode("edit");
    setEditingId(item.id);
    setForm({
      value: item.value,
      description: item.description ?? "",
      sort_order: item.sort_order,
      is_active: item.is_active,
    });
    setModalOpen(true);
  }

  const [saving, setSaving] = useState(false);

  async function submitModal() {
    if (!form.value.trim()) {
      setError("Giá trị danh mục là bắt buộc");
      return;
    }

    setSaving(true);
    setError(null);

    const payload = {
      group_name: groupName,
      value: form.value.trim(),
      description: form.description.trim() || null,
      sort_order: Number(form.sort_order) || 0,
      is_active: form.is_active,
    };

    const url =
      modalMode === "create"
        ? `${API_BASE_URL}/category`
        : `${API_BASE_URL}/category/${editingId}`;
    const method = modalMode === "create" ? "POST" : "PUT";

    try {
      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        setError(await parseApiError(response, "Không thể lưu danh mục"));
        return;
      }

      setModalOpen(false);
      await loadCategories();
    } catch {
      setError("Không kết nối được tới máy chủ");
    } finally {
      setSaving(false);
    }
  }

  async function removeCategory(id: string) {
    const ok = window.confirm("Bạn chắc chắn muốn xóa danh mục này?");
    if (!ok) return;

    try {
      const response = await fetch(`${API_BASE_URL}/category/${id}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        setError(await parseApiError(response, "Không thể xóa danh mục"));
        return;
      }
    } catch {
      setError("Không kết nối được tới máy chủ");
      return;
    }

    if (items.length === 1 && page > 1) {
      const nextPage = page - 1;
      setPage(nextPage);
      syncUrl(nextPage, query);
    }
    await loadCategories();
  }

  function applySearch() {
    const nextPage = 1;
    setPage(nextPage);
    setQuery(searchInput.trim());
    syncUrl(nextPage, searchInput.trim());
  }

  function goPrevPage() {
    if (page <= 1) {
      return;
    }
    const nextPage = page - 1;
    setPage(nextPage);
    syncUrl(nextPage, query);
  }

  function goNextPage() {
    if (page >= totalPages) {
      return;
    }
    const nextPage = page + 1;
    setPage(nextPage);
    syncUrl(nextPage, query);
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#f8fdff,_#f8f6ee_40%,_#f5f4ed)]">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-4 p-4 lg:grid-cols-[280px_1fr]">
        <CmsSidebar selectedCategoryGroup={groupName} />

        <main className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Danh mục: {groupName}</CardTitle>
              <CardDescription>
                Trang riêng cho nhóm danh mục này, hỗ trợ thêm, sửa, xóa, tìm kiếm và phân
                trang.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-col gap-2 md:flex-row">
                <Button asChild variant="outline">
                  <Link href="/cms/categories">
                    <ArrowLeft className="size-4" />
                    Về danh mục tổng hợp
                  </Link>
                </Button>
                <div className="relative flex-1">
                  <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    className="pl-9"
                    value={searchInput}
                    onChange={(event) => setSearchInput(event.target.value)}
                    placeholder={`Tìm trong ${groupName}...`}
                    onKeyDown={(event) => {
                      if (event.key === "Enter") {
                        applySearch();
                      }
                    }}
                  />
                </div>
                <Button variant="outline" onClick={applySearch}>
                  Tìm
                </Button>
                <Button onClick={openCreateModal}>
                  <Plus className="size-4" />
                  Thêm mục mới
                </Button>
              </div>

              {error ? <p className="text-sm font-medium text-red-600">{error}</p> : null}

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Giá trị</TableHead>
                    <TableHead>Mô tả</TableHead>
                    <TableHead>Thứ tự</TableHead>
                    <TableHead>Trạng thái</TableHead>
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
                        <TableCell className="font-medium">{item.value}</TableCell>
                        <TableCell>{item.description ?? "-"}</TableCell>
                        <TableCell>{item.sort_order}</TableCell>
                        <TableCell>
                          <Badge variant={item.is_active ? "default" : "outline"}>
                            {item.is_active ? "Active" : "Inactive"}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="inline-flex gap-1">
                            <Button
                              size="icon"
                              variant="ghost"
                              onClick={() => openEditModal(item)}
                              aria-label="Sửa"
                            >
                              <Pencil className="size-4" />
                            </Button>
                            <Button
                              size="icon"
                              variant="ghost"
                              onClick={() => void removeCategory(item.id)}
                              aria-label="Xóa"
                            >
                              <Trash2 className="size-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center text-muted-foreground">
                        Không có dữ liệu phù hợp.
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
                <Button variant="outline" onClick={goPrevPage} disabled={page <= 1}>
                  Trang trước
                </Button>
                <Button variant="outline" onClick={goNextPage} disabled={page >= totalPages}>
                  Trang sau
                </Button>
              </div>
            </CardFooter>
          </Card>
        </main>
      </div>

      {modalOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/35 p-4">
          <div className="w-full max-w-lg rounded-xl border border-border bg-card p-5 shadow-xl">
            <div className="mb-4 flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold">
                  {modalMode === "create" ? `Thêm mục cho ${groupName}` : "Cập nhật mục"}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {modalMode === "create"
                    ? "Tạo giá trị danh mục mới"
                    : "Chỉnh sửa thông tin danh mục"}
                </p>
              </div>
              <Button size="icon" variant="ghost" onClick={() => setModalOpen(false)}>
                <X className="size-4" />
              </Button>
            </div>

            <div className="space-y-3">
              <div className="space-y-1">
                <label className="text-sm font-medium" htmlFor="modal-group-name">
                  Nhóm danh mục
                </label>
                <Input id="modal-group-name" value={groupName} disabled />
              </div>

              <div className="space-y-1">
                <label className="text-sm font-medium" htmlFor="modal-value">
                  Giá trị
                </label>
                <Input
                  id="modal-value"
                  value={form.value}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, value: event.target.value }))
                  }
                  placeholder="Ví dụ: Vietnam Airlines"
                />
              </div>

              <div className="space-y-1">
                <label className="text-sm font-medium" htmlFor="modal-description">
                  Mô tả
                </label>
                <Input
                  id="modal-description"
                  value={form.description}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, description: event.target.value }))
                  }
                  placeholder="Mô tả ngắn"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-sm font-medium" htmlFor="modal-sort-order">
                    Thứ tự
                  </label>
                  <Input
                    id="modal-sort-order"
                    type="number"
                    value={form.sort_order}
                    onChange={(event) =>
                      setForm((prev) => ({
                        ...prev,
                        sort_order: Number(event.target.value) || 0,
                      }))
                    }
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-sm font-medium" htmlFor="modal-active">
                    Trạng thái
                  </label>
                  <select
                    id="modal-active"
                    value={form.is_active ? "active" : "inactive"}
                    onChange={(event) =>
                      setForm((prev) => ({
                        ...prev,
                        is_active: event.target.value === "active",
                      }))
                    }
                    className="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="mt-5 flex justify-end gap-2">
              <Button variant="outline" onClick={() => setModalOpen(false)}>
                Hủy
              </Button>
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

export default function CategoryGroupPage() {
  return (
    <Suspense
      fallback={<div className="p-4 text-sm text-muted-foreground">Đang tải trang...</div>}
    >
      <CategoryGroupPageContent />
    </Suspense>
  );
}
