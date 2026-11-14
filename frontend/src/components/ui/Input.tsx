import { forwardRef, type InputHTMLAttributes } from "react";

import { cn } from "@/lib/cn";

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "h-10 w-full rounded-lg border bg-surface px-3 text-sm text-foreground outline-none transition placeholder:text-slate-400 focus:border-accent focus:ring-3 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-surface-subtle",
        className,
      )}
      {...props}
    />
  ),
);

Input.displayName = "Input";
