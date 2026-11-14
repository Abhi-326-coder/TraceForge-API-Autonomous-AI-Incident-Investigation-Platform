import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/cn";

type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  children: ReactNode;
  tone?: "neutral" | "info" | "success" | "warning" | "danger";
};

const tones = {
  neutral: "border-slate-200 bg-slate-50 text-slate-700",
  info: "border-blue-200 bg-blue-50 text-blue-700",
  success: "border-emerald-200 bg-emerald-50 text-emerald-700",
  warning: "border-amber-200 bg-amber-50 text-amber-700",
  danger: "border-red-200 bg-red-50 text-red-700",
};

export function Badge({ className, children, tone = "neutral", ...props }: BadgeProps) {
  return (
    <span
      className={cn("inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium", tones[tone], className)}
      {...props}
    >
      {children}
    </span>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const normalized = status.toLowerCase();
  const tone = normalized.includes("complete") || normalized.includes("approved") || normalized.includes("pass")
    ? "success"
    : normalized.includes("fail") || normalized.includes("reject") || normalized.includes("critical")
      ? "danger"
      : normalized.includes("pending") || normalized.includes("queue") || normalized.includes("review")
        ? "warning"
        : "info";

  return <Badge tone={tone}>{status.replaceAll("_", " ")}</Badge>;
}
