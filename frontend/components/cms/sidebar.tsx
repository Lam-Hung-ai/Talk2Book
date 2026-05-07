"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookText,
  Calendar,
  ChevronRight,
  Globe,
  Hotel,
  LayoutGrid,
  ListTree,
  Map,
  Plane,
  Settings2,
  Users,
  type LucideIcon,
} from "lucide-react";

import { Separator } from "@/components/ui/separator";
import { CATEGORY_GROUPS } from "@/lib/category-groups";

type SidebarItem = {
  key: string;
  icon: LucideIcon;
  name: string;
  href: string;
};

type CmsSidebarProps = {
  selectedCategoryGroup?: string;
};

const navItems: SidebarItem[] = [
  // { key: "dashboard", icon: LayoutGrid, name: "Dashboard", href: "/cms" },
  { key: "booking", icon: Calendar, name: "Quản lý Booking", href: "/cms/bookings" },
  { key: "tour", icon: Map, name: "Quản lý tour", href: "/cms/tours" },
  { key: "hotel", icon: Hotel, name: "Quản lý khách sạn", href: "/cms/hotels" },
  { key: "flight", icon: Plane, name: "Quản lý chuyến bay", href: "/cms/flights" },
  // { key: "web", icon: Globe, name: "Nội dung website", href: "/cms/categories" },
  // { key: "user", icon: Users, name: "Người dùng", href: "/cms/users" },
  { key: "system", icon: Settings2, name: "Hệ thống", href: "/cms" },
];

export function CmsSidebar({ selectedCategoryGroup }: CmsSidebarProps) {
  const pathname = usePathname();
  const isCategoryRoute = pathname.startsWith("/cms/categories");
  const pathGroupName = decodeURIComponent(pathname.replace("/cms/categories/", ""));
  const activeGroupName = selectedCategoryGroup ?? (pathGroupName !== pathname ? pathGroupName : undefined);

  return (
    <aside className="rounded-xl border border-border/70 bg-card/95 p-4 shadow-sm backdrop-blur md:p-5">
      <div className="flex items-center gap-3">
        <div className="flex size-9 items-center justify-center rounded-lg bg-primary/15 text-primary">
          <BookText className="size-4" />
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Talk2Book</p>
          <h2 className="text-base font-semibold">Content CMS</h2>
        </div>
      </div>

      <Separator className="my-4" />

      <nav className="space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active =
            item.href === "/cms"
              ? pathname === "/cms" && !isCategoryRoute
              : pathname.startsWith(item.href);

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm transition ${
                active
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              }`}
            >
              <Icon className="size-4" />
              {item.name}
            </Link>
          );
        })}

        <details className="group rounded-md" open={isCategoryRoute}>
          <summary className="flex list-none cursor-pointer items-center justify-between rounded-md px-3 py-2 text-sm transition text-muted-foreground hover:bg-accent hover:text-accent-foreground [&::-webkit-details-marker]:hidden">
            <span className="flex items-center gap-3">
              <ListTree className="size-4" />
              Danh mục
            </span>
            <ChevronRight className="size-4 transition-transform group-open:rotate-90" />
          </summary>
          <div className="mt-1 ml-9 space-y-1 border-l border-border/70 pl-3">
            <Link
              href="/cms/categories"
              className={`block w-full rounded-md px-2 py-1.5 text-left text-sm transition ${
                isCategoryRoute && !activeGroupName
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              }`}
            >
              Tất cả danh mục
            </Link>
            {CATEGORY_GROUPS.map((groupName) => (
              <Link
                key={groupName}
                href={`/cms/categories/${encodeURIComponent(groupName)}`}
                className={`block w-full rounded-md px-2 py-1.5 text-left text-sm transition ${
                  activeGroupName === groupName
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                }`}
              >
                {groupName}
              </Link>
            ))}
          </div>
        </details>
      </nav>

      <div className="mt-8 rounded-lg border border-dashed border-border bg-muted/40 p-3 text-sm">
        <p className="font-medium">Storage</p>
        <p className="mt-1 text-muted-foreground">4.2 GB / 10 GB đã sử dụng</p>
        <div className="mt-3 h-2 rounded-full bg-background">
          <div className="h-2 w-[42%] rounded-full bg-primary" />
        </div>
      </div>
    </aside>
  );
}
