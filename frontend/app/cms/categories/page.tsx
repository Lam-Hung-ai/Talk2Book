"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Pencil, Plus, Search, Trash2, X } from "lucide-react";

import { parseApiError } from "@/lib/api-error";
import { CmsSidebar } from "@/components/cms/sidebar";
import { CATEGORY_GROUPS } from "@/lib/category-groups";
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
  group_name: string;
  value: string;
  description: string;
  sort_order: number;
  is_active: boolean;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

const emptyForm: CategoryFormState = {
  group_name: "",
  value: "",
  description: "",
  sort_order: 0,
  is_active: true,
};

function CategoriesPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [items, setItems] = useState<CategoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [totalPages, setTotalPages] = useState(1);

  const [searchInput, setSearchInput] = useState(searchParams.get("q") ?? "");
  const [query, setQuery] = useState(searchParams.get("q") ?? "");
  const [groupFilter, setGroupFilter] = useState(searchParams.get("group_name") ?? "");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<ModalMode>("create");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<CategoryFormState>(emptyForm);

  const syncUrl = useCallback(
    (nextPage: number, nextGroup: string, nextQuery: string) => {
      const params = new URLSearchParams();
      if (nextGroup) {
        params.set("group_name", nextGroup);
      }
      if (nextQuery) {
        params.set("q", nextQuery);
      }
      if (nextPage > 1) {
        params.set("page", String(nextPage));
      }
      router.replace(`/cms/categories${params.toString() ? `?${params.toString()}` : ""}`);
    },
    [router]
  );

  const loadCategories = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
      });
      if (groupFilter) {
        params.set("group_name", groupFilter);
      }
      if (query) {
        params.set("q", query);
      }

      const response = await fetch(`${API_BASE_URL}/category?${params.toString()}`);
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
  }, [groupFilter, page, pageSize, query]);


  useEffect(() => {
    const initialPage = Number(searchParams.get("page") ?? "1");
    if (!Number.isNaN(initialPage) && initialPage > 0 && initialPage !== page) {
      setPage(initialPage);
    }

    const qParam = searchParams.get("q") ?? "";
    const groupParam = searchParams.get("group_name") ?? "";
    if (qParam !== query) {
      setQuery(qParam);
      setSearchInput(qParam);
    }
    if (groupParam !== groupFilter) {
      setGroupFilter(groupParam);
    }
  }, [groupFilter, page, query, searchParams]);

  useEffect(() => {
    void loadCategories();
  }, [loadCategories]);

  function openCreateModal() {
    setModalMode("create");
    setEditingId(null);
    setForm({ ...emptyForm, group_name: groupFilter || "" });
    setModalOpen(true);
  }

  function openEditModal(item: CategoryItem) {
    setModalMode("edit");
    setEditingId(item.id);
    setForm({
      group_name: item.group_name,
      value: item.value,
      description: item.description ?? "",
      sort_order: item.sort_order,
      is_active: item.is_active,
    });
    setModalOpen(true);
  }

  async function submitModal() {
    if (!form.group_name.trim() || !form.value.trim()) {
      setError("Nhóm danh mục và giá trị là bắt buộc");
      return;
    }

    const payload = {
      group_name: form.group_name.trim(),
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

    const response = await fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      setError(await parseApiError(response, "Không thể lưu danh mục"));
      return;
    }

    setModalOpen(false);
    await loadCategories();
  }

  async function removeCategory(id: string) {
    const ok = window.confirm("Bạn chắc chắn muốn xóa danh mục này?");
    if (!ok) {
      return;
    }

    const response = await fetch(`${API_BASE_URL}/category/${id}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      setError(await parseApiError(response, "Không thể xóa danh mục"));
      return;
    }

    if (items.length === 1 && page > 1) {
      const nextPage = page - 1;
      setPage(nextPage);
      syncUrl(nextPage, groupFilter, query);
    }
    await loadCategories();
  }

  function applySearch() {
    const nextPage = 1;
    setPage(nextPage);
    setQuery(searchInput.trim());
    syncUrl(nextPage, groupFilter, searchInput.trim());
  }

  function onChangeGroupFilter(value: string) {
    const nextPage = 1;
    setPage(nextPage);
    setGroupFilter(value);
    syncUrl(nextPage, value, query);
  }

  function goPrevPage() {
    if (page <= 1) {
      return;
    }
    const nextPage = page - 1;
    setPage(nextPage);
    syncUrl(nextPage, groupFilter, query);
  }

  function goNextPage() {
    if (page >= totalPages) {
      return;
    }
    const nextPage = page + 1;
    setPage(nextPage);
    syncUrl(nextPage, groupFilter, query);
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#f8fdff,_#f8f6ee_40%,_#f5f4ed)]">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-4 p-4 lg:grid-cols-[280px_1fr]">
        <CmsSidebar selectedCategoryGroup={groupFilter || undefined} />

        <main className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Danh mục hệ thống</CardTitle>
              <CardDescription>
                Quản lý danh mục động bằng API: thêm, sửa, xóa, lọc theo nhóm, tìm kiếm
                và phân trang.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Tabs nhóm danh mục */}
              <div className="flex flex-wrap gap-1 border-b border-border pb-3">
                <button
                  type="button"
                  onClick={() => onChangeGroupFilter("")}
                  className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
                    !groupFilter
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  }`}
                >
                  Tất cả
                </button>
                {CATEGORY_GROUPS.map((name) => (
                  <button
                    key={name}
                    type="button"
                    onClick={() => onChangeGroupFilter(name)}
                    className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
                      groupFilter === name
                        ? "bg-primary text-primary-foreground"
                        : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                    }`}
                  >
                    {name}
                  </button>
                ))}
              </div>

              <div className="flex flex-col gap-2 md:flex-row">
                <div className="relative flex-1">
                  <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    className="pl-9"
                    value={searchInput}
                    onChange={(event) => setSearchInput(event.target.value)}
                    placeholder={groupFilter ? `Tìm trong ${groupFilter}...` : "Tìm theo nhóm, giá trị, mô tả..."}
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
                {groupFilter ? (
                  <Button asChild variant="outline">
                    <Link href={`/cms/categories/${encodeURIComponent(groupFilter)}`}>
                      Mở trang nhóm
                    </Link>
                  </Button>
                ) : null}
                <Button onClick={openCreateModal}>
                  <Plus className="size-4" />
                  {groupFilter ? `Thêm vào ${groupFilter}` : "Thêm danh mục"}
                </Button>
              </div>

              {error ? <p className="text-sm font-medium text-red-600">{error}</p> : null}

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nhóm</TableHead>
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
                      <TableCell colSpan={6} className="text-center text-muted-foreground">
                        Đang tải dữ liệu...
                      </TableCell>
                    </TableRow>
                  ) : items.length ? (
                    items.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell className="font-medium">
                          <Link
                            href={`/cms/categories/${encodeURIComponent(item.group_name)}`}
                            className="text-primary hover:underline"
                          >
                            {item.group_name}
                          </Link>
                        </TableCell>
                        <TableCell>{item.value}</TableCell>
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
                      <TableCell colSpan={6} className="text-center text-muted-foreground">
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
                  {modalMode === "create" ? "Thêm danh mục" : "Cập nhật danh mục"}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {modalMode === "create"
                    ? "Tạo giá trị danh mục mới"
                    : "Chỉnh sửa thông tin danh mục hiện tại"}
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
                <Input
                  id="modal-group-name"
                  value={form.group_name}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, group_name: event.target.value }))
                  }
                  placeholder="Ví dụ: Hãng hàng không"
                />
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
              <Button onClick={() => void submitModal()}>
                {modalMode === "create" ? "Thêm mới" : "Lưu thay đổi"}
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export default function CategoriesPage() {
  return (
    <Suspense
      fallback={<div className="p-4 text-sm text-muted-foreground">Đang tải trang...</div>}
    >
      <CategoriesPageContent />
    </Suspense>
  );
}
