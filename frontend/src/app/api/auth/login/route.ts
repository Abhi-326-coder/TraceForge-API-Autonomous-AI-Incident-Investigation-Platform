import { NextResponse } from "next/server";

const COOKIE_NAME = "traceforge_session";
const backendUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function POST(request: Request) {
  const payload = await request.json().catch(() => null);
  if (!payload || typeof payload.email !== "string" || typeof payload.password !== "string") {
    return NextResponse.json({ detail: "Email and password are required." }, { status: 400 });
  }

  const loginResponse = await fetch(`${backendUrl}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: payload.email, password: payload.password }),
    cache: "no-store",
  });

  if (!loginResponse.ok) {
    const error = await loginResponse.json().catch(() => null) as { detail?: string } | null;
    return NextResponse.json({ detail: error?.detail ?? "Unable to sign in." }, { status: loginResponse.status });
  }

  const token = await loginResponse.json() as { access_token: string; expires_in: number };
  const userResponse = await fetch(`${backendUrl}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token.access_token}` },
    cache: "no-store",
  });

  if (!userResponse.ok) return NextResponse.json({ detail: "Unable to verify this session." }, { status: 502 });

  const response = NextResponse.json({ user: await userResponse.json() });
  response.cookies.set(COOKIE_NAME, token.access_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: token.expires_in,
  });
  return response;
}
