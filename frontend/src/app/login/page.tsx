"use client";

import { Eye, EyeOff, ShieldCheck } from "lucide-react";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/auth/AuthProvider";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { login } from "@/lib/auth";
import { validateLogin, type LoginValidationErrors } from "@/lib/auth-validation";

export default function LoginPage() {
  const router = useRouter();
  const { setAuthenticatedUser } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<LoginValidationErrors>({});
  const [formError, setFormError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isComplete, setIsComplete] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const validationErrors = validateLogin(email, password);
    setErrors(validationErrors);
    setFormError("");
    if (Object.keys(validationErrors).length) return;

    setIsSubmitting(true);
    try {
      const user = await login(email, password);
      setAuthenticatedUser(user);
      setIsComplete(true);
      router.replace("/dashboard");
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Unable to sign in. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="grid min-h-screen bg-background lg:grid-cols-[1.1fr_0.9fr]">
      <section className="hidden border-r bg-surface p-10 lg:flex lg:flex-col lg:justify-between">
        <div className="flex items-center gap-3"><span className="flex size-9 items-center justify-center rounded-lg bg-slate-900 text-sm font-semibold text-white">T</span><span className="font-semibold tracking-tight">TraceForge</span></div>
        <div className="max-w-md"><p className="text-sm font-semibold tracking-[0.14em] text-accent uppercase">Incident intelligence</p><h1 className="mt-4 text-4xl font-semibold tracking-tight text-foreground">Clearer answers when systems fail.</h1><p className="mt-5 text-base leading-7 text-muted">TraceForge brings evidence, investigation progress, and human-approved remediation into one focused workspace.</p></div>
        <p className="text-xs text-muted">Built for deliberate, accountable incident response.</p>
      </section>

      <section className="flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-sm">
          <div className="mb-8 lg:hidden"><div className="flex items-center gap-3"><span className="flex size-9 items-center justify-center rounded-lg bg-slate-900 text-sm font-semibold text-white">T</span><span className="font-semibold tracking-tight">TraceForge</span></div></div>
          <div className="rounded-2xl border bg-surface p-6 shadow-sm sm:p-8">
            <div className="flex size-10 items-center justify-center rounded-lg bg-accent-subtle text-accent"><ShieldCheck size={21} /></div>
            <h2 className="mt-5 text-2xl font-semibold tracking-tight">Welcome back</h2>
            <p className="mt-2 text-sm leading-6 text-muted">Sign in to your incident response workspace.</p>
            <form className="mt-7 space-y-5" onSubmit={handleSubmit} noValidate>
              <label className="block"><span className="mb-2 block text-sm font-medium text-foreground">Email</span><Input autoComplete="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} aria-invalid={Boolean(errors.email)} aria-describedby={errors.email ? "email-error" : undefined} placeholder="you@company.com" />{errors.email ? <span id="email-error" className="mt-1.5 block text-xs text-red-600">{errors.email}</span> : null}</label>
              <label className="block"><span className="mb-2 block text-sm font-medium text-foreground">Password</span><div className="relative"><Input autoComplete="current-password" type={showPassword ? "text" : "password"} value={password} onChange={(event) => setPassword(event.target.value)} aria-invalid={Boolean(errors.password)} aria-describedby={errors.password ? "password-error" : undefined} className="pr-11" /> <button type="button" className="absolute inset-y-0 right-0 px-3 text-muted hover:text-foreground" onClick={() => setShowPassword((value) => !value)} aria-label={showPassword ? "Hide password" : "Show password"}>{showPassword ? <EyeOff size={18} /> : <Eye size={18} />}</button></div>{errors.password ? <span id="password-error" className="mt-1.5 block text-xs text-red-600">{errors.password}</span> : null}</label>
              {formError ? <p role="alert" className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{formError}</p> : null}
              {isComplete ? <p className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">Signed in successfully. Redirecting…</p> : null}
              <Button className="w-full" type="submit" disabled={isSubmitting || isComplete}>{isSubmitting ? "Signing in…" : "Sign in"}</Button>
            </form>
          </div>
          <p className="mt-5 text-center text-xs leading-5 text-muted">Secure session handling is managed by TraceForge.</p>
        </div>
      </section>
    </main>
  );
}
