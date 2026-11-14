import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/cn";

type CardProps = HTMLAttributes<HTMLDivElement> & { children: ReactNode };

export function Card({ className, children, ...props }: CardProps) {
  return (
    <div className={cn("rounded-xl border bg-surface", className)} {...props}>
      {children}
    </div>
  );
}
