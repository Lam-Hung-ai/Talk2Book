import Link from "next/link";
import { Bell, PenSquare, Plane, Search } from "lucide-react";

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

const posts = [
  {
    id: "BK-2301",
    title: "Tips tiết kiệm khi đặt vé máy bay dịp cao điểm",
    author: "Minh Tran",
    status: "Published",
    views: "12.4k",
    updatedAt: "18/03/2026",
  },
  {
    id: "BK-2302",
    title: "Checklist chuẩn bị cho chuyến đi Đà Nẵng 3N2Đ",
    author: "Linh Nguyen",
    status: "Review",
    views: "8.1k",
    updatedAt: "16/03/2026",
  },
  {
    id: "BK-2303",
    title: "So sánh 5 hạng ghế phổ biến trên chặng nội địa",
    author: "Admin",
    status: "Draft",
    views: "-",
    updatedAt: "14/03/2026",
  },
];

const statusVariant: Record<string, "default" | "secondary" | "outline"> = {
  Published: "default",
  Review: "secondary",
  Draft: "outline",
};

export default function CmsDashboardPage() {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#f8fdff,_#f8f6ee_40%,_#f5f4ed)]">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-4 p-4 lg:grid-cols-[280px_1fr]">
        <CmsSidebar />

        <main className="space-y-4">
          <header className="flex flex-col gap-3 rounded-xl border border-border/70 bg-card/95 p-4 shadow-sm backdrop-blur md:flex-row md:items-center md:justify-between md:p-5">
            <div>
              <h1 className="text-xl font-semibold tracking-tight md:text-2xl">CMS Dashboard</h1>
              <p className="text-sm text-muted-foreground">
                Trang tổng quan quản trị nội dung và vận hành hệ thống du lịch.
              </p>
            </div>
            <div className="flex w-full gap-2 md:w-auto">
              <div className="relative flex-1 md:w-72 md:flex-none">
                <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
                <Input className="pl-9" placeholder="Tìm theo tiêu đề..." />
              </div>
              <Button variant="outline" size="icon" aria-label="Thông báo">
                <Bell className="size-4" />
              </Button>
              <Button>
                <PenSquare className="size-4" />
                Bài viết mới
              </Button>
            </div>
          </header>

          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Tổng bài viết</CardDescription>
                <CardTitle className="text-2xl">148</CardTitle>
              </CardHeader>
              <CardFooter>
                <p className="text-xs text-muted-foreground">+12 trong 30 ngày gần nhất</p>
              </CardFooter>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Đã xuất bản</CardDescription>
                <CardTitle className="text-2xl">96</CardTitle>
              </CardHeader>
              <CardFooter>
                <p className="text-xs text-muted-foreground">Tăng trưởng ổn định tuần này</p>
              </CardFooter>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Danh mục động</CardDescription>
                <CardTitle className="text-2xl">/cms/categories</CardTitle>
              </CardHeader>
              <CardFooter>
                <Link href="/cms/categories" className="text-xs text-primary hover:underline">
                  Đi tới quản lý danh mục
                </Link>
              </CardFooter>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Flight realtime</CardDescription>
                <CardTitle className="text-2xl">API Ready</CardTitle>
              </CardHeader>
              <CardFooter>
                <p className="text-xs text-muted-foreground">Endpoint: /api/v1/flight-realtime/search</p>
              </CardFooter>
            </Card>
          </section>

          <section className="grid gap-4 xl:grid-cols-[1.3fr_1fr]">
            <Card>
              <CardHeader>
                <CardTitle>Danh sách bài viết</CardTitle>
                <CardDescription>
                  Theo dõi trạng thái và cập nhật nhanh nội dung gần đây.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Mã</TableHead>
                      <TableHead>Tiêu đề</TableHead>
                      <TableHead>Tác giả</TableHead>
                      <TableHead>Trạng thái</TableHead>
                      <TableHead>Lượt xem</TableHead>
                      <TableHead className="text-right">Cập nhật</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {posts.map((post) => (
                      <TableRow key={post.id}>
                        <TableCell className="font-medium">{post.id}</TableCell>
                        <TableCell>{post.title}</TableCell>
                        <TableCell>{post.author}</TableCell>
                        <TableCell>
                          <Badge variant={statusVariant[post.status]}>{post.status}</Badge>
                        </TableCell>
                        <TableCell>{post.views}</TableCell>
                        <TableCell className="text-right text-muted-foreground">
                          {post.updatedAt}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Tính năng nổi bật</CardTitle>
                <CardDescription>Những hạng mục đã sẵn sàng cho production.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="rounded-md border border-border/70 p-3">
                  <p className="text-sm font-semibold">Danh mục tách route riêng</p>
                  <p className="text-xs text-muted-foreground">
                    Toàn bộ thêm, sửa, xóa, filter, search, pagination ở /cms/categories.
                  </p>
                </div>
                <div className="rounded-md border border-border/70 p-3">
                  <p className="text-sm font-semibold">Modal form CRUD</p>
                  <p className="text-xs text-muted-foreground">
                    Form tạo/sửa danh mục chạy dạng modal overlay.
                  </p>
                </div>
                <div className="rounded-md border border-border/70 p-3">
                  <p className="text-sm font-semibold">Realtime flight API</p>
                  <p className="text-xs text-muted-foreground">
                    Hỗ trợ AviationStack và fallback OpenSky.
                  </p>
                </div>
              </CardContent>
              <CardFooter>
                <Button asChild>
                  <Link href="/cms/categories">
                    <Plane className="size-4" />
                    Quản lý danh mục ngay
                  </Link>
                </Button>
              </CardFooter>
            </Card>
          </section>
        </main>
      </div>
    </div>
  );
}
