export type AuthUser = {
  id: number;
  email: string;
  is_active: boolean;
};

type LoginResponse = { user: AuthUser };

export class AuthError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
    this.name = "AuthError";
  }
}

async function readError(response: Response) {
  const body = await response.json().catch(() => null) as { detail?: string } | null;
  return body?.detail ?? "Unable to complete this request.";
}

export async function login(email: string, password: string): Promise<AuthUser> {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin",
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) throw new AuthError(await readError(response), response.status);
  return (await response.json() as LoginResponse).user;
}

export async function getCurrentUser(): Promise<AuthUser> {
  const response = await fetch("/api/auth/me", { cache: "no-store", credentials: "same-origin" });
  if (!response.ok) throw new AuthError(await readError(response), response.status);
  return response.json() as Promise<AuthUser>;
}

export async function logout(): Promise<void> {
  await fetch("/api/auth/logout", { method: "POST", credentials: "same-origin" });
}
