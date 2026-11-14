"use client";

import { useEffect, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "./AuthProvider";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { LoadingSkeleton } from "@/components/ui/States";

export function AppFrame({ children }: { children: ReactNode }) {
  const { status } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const isLoginPage = pathname === "/login";

  useEffect(() => {
    if (status === "unauthenticated" && !isLoginPage) router.replace("/login");
    if (status === "authenticated" && isLoginPage) router.replace("/dashboard");
  }, [isLoginPage, router, status]);

  if (isLoginPage) return <>{children}</>;

  if (status !== "authenticated") {
    return <main className="flex min-h-screen items-center justify-center bg-background p-6"><div className="w-full max-w-sm space-y-3"><LoadingSkeleton className="h-8 w-32" /><LoadingSkeleton className="h-32 w-full" /></div></main>;
  }

  return <DashboardLayout>{children}</DashboardLayout>;
}
