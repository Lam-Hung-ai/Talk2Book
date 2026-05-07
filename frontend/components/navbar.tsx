"use client";

import React, { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BadgeDollarSign,
  Home,
  Menu,
  Sparkles,
  Users,
} from "lucide-react";
import { ModeToggle } from "@/components/mode-toggle";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";

const navLinks = [
  { title: "Trang chủ", href: "/", icon: Home },
  { title: "Tính năng", href: "#features", icon: Sparkles },
  { title: "Bảng giá", href: "#pricing", icon: BadgeDollarSign },
  { title: "Về chúng tôi", href: "#about", icon: Users },
] as const;

function BrandWordmark({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        "select-none font-bold tracking-tight text-lg max-[360px]:text-base sm:text-2xl md:text-3xl",
        className
      )}
      aria-hidden
    >
      <span className="text-slate-800 dark:text-slate-100">Talk</span>
      <span className="bg-linear-to-br from-sky-500 to-cyan-400 bg-clip-text text-transparent">
        2
      </span>
      <span className="text-slate-800 dark:text-slate-100">Book</span>
    </span>
  );
}

const Navbar = () => {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    let raf = 0;
    const onScroll = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        setScrolled(window.scrollY > 4);
      });
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("scroll", onScroll);
    };
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-full h-px bg-linear-to-r from-transparent via-sky-500/25 to-transparent"
      />
      <nav
        className={cn(
          // Trên mobile: bỏ backdrop-blur + transition màu nền (rất tốn GPU, hay gây giật khi cuộn / mở sheet).
          "w-full border-b ease-out transition-[box-shadow,border-color] duration-300 max-md:duration-200",
          scrolled
            ? "border-border/70 bg-background/90 shadow-[0_8px_30px_-12px_rgba(0,0,0,0.12)] backdrop-blur-xl supports-backdrop-filter:bg-background/75 dark:shadow-[0_8px_30px_-12px_rgba(0,0,0,0.45)] max-md:bg-background/98 max-md:shadow-[0_6px_24px_-10px_rgba(0,0,0,0.1)] max-md:backdrop-blur-none"
            : "border-border/40 bg-background/80 backdrop-blur-md supports-backdrop-filter:bg-background/65 max-md:bg-background max-md:backdrop-blur-none"
        )}
      >
        <div className="mx-auto flex min-h-19 max-w-7xl items-center justify-between gap-3 px-4 py-2 sm:min-h-21 sm:px-6 lg:px-8">
          <div className="flex min-w-0 flex-1 items-center gap-3 md:gap-6 lg:gap-10">
            <Link
              href="/"
              className="group flex min-w-0 shrink-0 items-center gap-2.5 rounded-lg outline-none transition-opacity hover:opacity-95 focus-visible:ring-2 focus-visible:ring-sky-500/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background sm:gap-3.5"
              aria-label="Talk2Book – Trang chủ"
            >
              <Image
                src="/logo_remove_background.png"
                alt=""
                width={360}
                height={102}
                className="h-12 w-auto shrink-0 max-[360px]:h-11 sm:h-16 md:h-18"
                priority
                aria-hidden
              />
              <BrandWordmark className="leading-none" />
            </Link>

            <div className="hidden md:flex md:items-center md:gap-0.5 lg:gap-1">
              {navLinks.map((link) => {
                const isActive =
                  link.href === "/"
                    ? pathname === "/"
                    : pathname === link.href;
                return (
                  <Link
                    key={link.title}
                    href={link.href}
                    className={cn(
                      "rounded-full px-3 py-2 text-sm font-medium transition-colors duration-200",
                      isActive
                        ? "bg-sky-500/10 text-sky-700 dark:text-sky-400"
                        : "text-muted-foreground hover:bg-muted/70 hover:text-foreground"
                    )}
                  >
                    {link.title}
                  </Link>
                );
              })}
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-1.5 sm:gap-2">
            <ModeToggle />
            <div className="hidden md:flex md:items-center md:gap-2">
              <Button variant="ghost" size="sm" className="font-medium" asChild>
                <Link href="/login">Đăng nhập</Link>
              </Button>
              <Button
                size="sm"
                className="font-medium shadow-md shadow-sky-500/15 transition-[box-shadow,transform] hover:shadow-lg hover:shadow-sky-500/20"
                asChild
              >
                <Link href="/signup">Đăng ký</Link>
              </Button>
            </div>


            <div className="md:hidden">
              <Sheet open={open} onOpenChange={setOpen}>
                <SheetTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="shrink-0 rounded-xl"
                    aria-label="Mở menu điều hướng"
                  >
                    <Menu className="size-5" />
                  </Button>
                </SheetTrigger>
                <SheetContent
                  side="right"
                  className="flex w-[min(100vw-1rem,22rem)] flex-col border-l border-border/60 bg-background p-0 duration-300 ease-out sm:max-w-sm md:bg-background/98"
                >
                  <SheetHeader className="space-y-2 border-b border-border/50 bg-muted/20 px-5 pb-5 pt-6 text-left">
                    <div className="flex items-center gap-3 pr-10">
                      <Image
                        src="/logo_remove_background.png"
                        alt=""
                        width={320}
                        height={91}
                        className="h-14 w-auto shrink-0 sm:h-16"
                        aria-hidden
                      />
                      <BrandWordmark className="text-xl sm:text-2xl" />
                    </div>
                    <SheetTitle className="sr-only">Talk2Book — Điều hướng</SheetTitle>
                    <SheetDescription className="text-left text-xs text-muted-foreground">
                      Đặt chỗ và kết nối — mọi nơi bạn đến.
                    </SheetDescription>
                  </SheetHeader>

                  <nav
                    className="flex flex-1 flex-col gap-0.5 overflow-y-auto px-3 py-4"
                    aria-label="Menu chính"
                  >
                    {navLinks.map((link) => {
                      const Icon = link.icon;
                      const isActive =
                        link.href === "/"
                          ? pathname === "/"
                          : pathname === link.href;
                      return (
                        <SheetClose asChild key={link.title}>
                          <Link
                            href={link.href}
                            className={cn(
                              "flex items-center gap-3 rounded-xl px-3 py-3 text-base font-medium transition-[color,background-color,transform] duration-200 ease-out active:scale-[0.99] motion-reduce:transition-none motion-reduce:active:scale-100",
                              isActive
                                ? "bg-sky-500/12 text-sky-800 dark:text-sky-300"
                                : "text-foreground/90 hover:bg-muted/80 active:bg-muted"
                            )}
                          >
                            <span
                              className={cn(
                                "flex size-9 shrink-0 items-center justify-center rounded-lg",
                                isActive
                                  ? "bg-sky-500/20 text-sky-700 dark:text-sky-400"
                                  : "bg-muted/80 text-muted-foreground"
                              )}
                            >
                              <Icon className="size-[18px]" aria-hidden />
                            </span>
                            {link.title}
                          </Link>
                        </SheetClose>
                      );
                    })}
                  </nav>

                  <div className="mt-auto border-t border-border/50 bg-muted/10 px-4 py-5 pb-[max(1.25rem,env(safe-area-inset-bottom))]">
                    <div className="flex flex-col gap-2.5">
                      <SheetClose asChild>
                        <Button
                          variant="outline"
                          className="h-11 w-full rounded-xl font-medium"
                          asChild
                        >
                          <Link href="/login">Đăng nhập</Link>
                        </Button>
                      </SheetClose>
                      <SheetClose asChild>
                        <Button
                          className="h-11 w-full rounded-xl border-0 bg-linear-to-r from-sky-600 to-cyan-600 font-medium text-white shadow-md shadow-sky-500/25 hover:from-sky-500 hover:to-cyan-500 hover:text-white"
                          asChild
                        >
                          <Link href="/signup">Tạo tài khoản</Link>
                        </Button>
                      </SheetClose>
                    </div>
                  </div>
                </SheetContent>
              </Sheet>
            </div>
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Navbar;
