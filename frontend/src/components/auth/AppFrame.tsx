"use client";

import { Suspense, useEffect, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "./AuthProvider";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { LoadingSkeleton } from "@/components/ui/States";

export function AppFrame({ children }: { children: ReactNode }) {
  return (
    <Suspense fallback={<FrameLoading />}>
      <RouteAwareFrame>{children}</RouteAwareFrame>
    </Suspense>
  );
}

function RouteAwareFrame({ children }: { children: ReactNode }) {
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

  return <DashboardLayout>{process.env.NEXT_PUBLIC_DEMO_MODE === "true" ? <div className="mx-auto max-w-screen-2xl px-4 pt-3 sm:px-6 lg:px-8"><p className="rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900">Demo mode: deterministic investigation and illustrative patch data. GitHub operations are simulated and will not create real resources.</p></div> : null}{children}</DashboardLayout>;
}

function FrameLoading() {
  return <main className="flex min-h-screen items-center justify-center bg-background p-6"><div className="w-full max-w-sm space-y-3"><LoadingSkeleton className="h-8 w-32" /><LoadingSkeleton className="h-32 w-full" /></div></main>;
}
