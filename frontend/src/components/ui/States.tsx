import type { ReactNode } from "react";

import { AlertCircle, Inbox } from "lucide-react";

import { Button } from "./Button";

export function LoadingSkeleton({ className = "" }: { className?: string }) {
  return <div aria-label="Loading" className={`animate-pulse rounded-lg bg-slate-200 ${className}`} />;
}

export function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return (
    <div className="flex min-h-64 flex-col items-center justify-center rounded-xl border border-dashed bg-surface px-6 py-12 text-center">
      <div className="flex size-10 items-center justify-center rounded-lg bg-surface-subtle text-muted"><Inbox size={20} /></div>
      <h2 className="mt-4 text-sm font-semibold text-foreground">{title}</h2>
      <p className="mt-1 max-w-sm text-sm leading-6 text-muted">{description}</p>
      {action ? <div className="mt-5">{action}</div> : null}
    </div>
  );
}

export function ErrorState({ title = "Something went wrong", description, onRetry }: { title?: string; description: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="flex min-h-48 flex-col items-center justify-center rounded-xl border border-red-200 bg-red-50/50 px-6 py-10 text-center">
      <AlertCircle size={22} className="text-red-600" />
      <h2 className="mt-3 text-sm font-semibold text-red-900">{title}</h2>
      <p className="mt-1 max-w-sm text-sm leading-6 text-red-700">{description}</p>
      {onRetry ? <Button className="mt-5" variant="secondary" onClick={onRetry}>Try again</Button> : null}
    </div>
  );
}
