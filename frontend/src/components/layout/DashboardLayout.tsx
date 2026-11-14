"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, type ReactNode } from "react";
import {
  BarChart3,
  FolderKanban,
  Gauge,
  Menu,
  Search,
  Settings,
  ShieldAlert,
  X,
} from "lucide-react";

import { cn } from "@/lib/cn";
import { logout } from "@/lib/auth";
import { useAuth } from "@/components/auth/AuthProvider";
import { useRouter } from "next/navigation";

type DashboardLayoutProps = { children: ReactNode };

const navigation = [
  { href: "/dashboard", label: "Overview", icon: Gauge },
  { href: "/projects", label: "Projects", icon: FolderKanban },
  { href: "/incidents", label: "Incidents", icon: ShieldAlert },
  { href: "/investigations", label: "Investigations", icon: Search },
  { href: "/evaluations", label: "Evaluations", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings },
];

function Brand() {
  return (
    <Link href="/dashboard" className="flex items-center gap-3 px-2" aria-label="TraceForge dashboard">
      <span className="flex size-8 items-center justify-center rounded-lg bg-slate-900 text-sm font-semibold text-white">T</span>
      <span className="text-sm font-semibold tracking-tight text-slate-950">TraceForge</span>
    </Link>
  );
}

function Navigation({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();

  return (
    <nav className="space-y-1" aria-label="Primary navigation">
      {navigation.map(({ href, label, icon: Icon }) => {
        const isActive = pathname === href || (href === "/incidents" && pathname.startsWith("/incidents/"));
        return (
          <Link
            key={href}
            href={href}
            onClick={onNavigate}
            className={cn(
              "flex h-10 items-center gap-3 rounded-lg px-3 text-sm font-medium transition-colors",
              isActive ? "bg-accent-subtle text-accent" : "text-muted hover:bg-surface-subtle hover:text-foreground",
            )}
          >
            <Icon size={17} strokeWidth={isActive ? 2.25 : 1.8} />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}

function Sidebar({ mobile = false, onNavigate }: { mobile?: boolean; onNavigate?: () => void }) {
  const { user, clearSession } = useAuth();
  const router = useRouter();

  async function handleLogout() {
    await logout();
    clearSession();
    router.replace("/login");
  }

  return (
    <div className={cn("flex h-full flex-col", mobile ? "p-4" : "p-4") }>
      <div className="flex items-center justify-between">
        <Brand />
        {mobile ? (
          <button onClick={onNavigate} className="rounded-md p-2 text-muted hover:bg-surface-subtle" aria-label="Close navigation">
            <X size={18} />
          </button>
        ) : null}
      </div>
      <div className="mt-8"><Navigation onNavigate={onNavigate} /></div>
      <div className="mt-auto border-t pt-4">
        <div className="flex items-center gap-3 rounded-lg px-2 py-2">
          <span className="flex size-8 items-center justify-center rounded-full bg-slate-200 text-xs font-semibold text-slate-700">{user?.email.slice(0, 1).toUpperCase() ?? "T"}</span>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-foreground">{user?.email ?? "TraceForge user"}</p>
            <p className="truncate text-xs text-muted">Workspace member</p>
          </div>
        </div>
        <button onClick={() => void handleLogout()} className="mt-1 w-full rounded-lg px-3 py-2 text-left text-xs font-medium text-muted transition-colors hover:bg-surface-subtle hover:text-foreground">
          Log out
        </button>
      </div>
    </div>
  );
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-60 border-r bg-surface lg:block">
        <Sidebar />
      </aside>

      {isMobileMenuOpen ? (
        <div className="fixed inset-0 z-50 lg:hidden" role="dialog" aria-modal="true" aria-label="Navigation menu">
          <button className="absolute inset-0 bg-slate-950/20" onClick={() => setIsMobileMenuOpen(false)} aria-label="Close navigation overlay" />
          <aside className="relative h-full w-72 border-r bg-surface shadow-xl">
            <Sidebar mobile onNavigate={() => setIsMobileMenuOpen(false)} />
          </aside>
        </div>
      ) : null}

      <div className="lg:pl-60">
        <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b bg-surface/95 px-4 backdrop-blur sm:px-6 lg:px-8">
          <button className="rounded-lg p-2 text-muted hover:bg-surface-subtle lg:hidden" onClick={() => setIsMobileMenuOpen(true)} aria-label="Open navigation">
            <Menu size={20} />
          </button>
          <div className="hidden text-sm text-muted lg:block">Incident investigation workspace</div>
          <div className="flex items-center gap-3">
            <span className="hidden text-xs text-muted sm:inline">Autonomous response, human approved</span>
            <span className="size-2 rounded-full bg-emerald-500" aria-label="System operational" />
          </div>
        </header>
        <main className="mx-auto w-full max-w-[1600px] p-5 sm:p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
