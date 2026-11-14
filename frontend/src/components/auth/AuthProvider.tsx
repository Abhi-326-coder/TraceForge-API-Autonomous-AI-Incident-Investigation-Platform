"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { getCurrentUser, type AuthUser } from "@/lib/auth";

type AuthState = {
  user: AuthUser | null;
  status: "loading" | "authenticated" | "unauthenticated";
  setAuthenticatedUser: (user: AuthUser) => void;
  clearSession: () => void;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [status, setStatus] = useState<AuthState["status"]>("loading");

  const refreshUser = useCallback(async () => {
    setStatus("loading");
    try {
      setUser(await getCurrentUser());
      setStatus("authenticated");
    } catch {
      setUser(null);
      setStatus("unauthenticated");
    }
  }, []);

  useEffect(() => { void refreshUser(); }, [refreshUser]);

  useEffect(() => {
    const handleSessionExpired = () => {
      setUser(null);
      setStatus("unauthenticated");
    };
    window.addEventListener("traceforge:session-expired", handleSessionExpired);
    return () => window.removeEventListener("traceforge:session-expired", handleSessionExpired);
  }, []);

  const value = useMemo<AuthState>(() => ({
    user,
    status,
    setAuthenticatedUser: (nextUser) => { setUser(nextUser); setStatus("authenticated"); },
    clearSession: () => { setUser(null); setStatus("unauthenticated"); },
    refreshUser,
  }), [user, status, refreshUser]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider.");
  return context;
}
