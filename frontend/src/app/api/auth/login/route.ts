import { NextResponse } from "next/server";

const COOKIE_NAME = "traceforge_session";
const backendUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function GET() {
  if (process.env.NEXT_PUBLIC_DEMO_MODE !== "true") return NextResponse.json({ detail: "Demo mode is disabled." }, { status: 404 });
  try {
    const response = await fetch(`${backendUrl}/api/auth/demo-account`, { method: "POST", cache: "no-store" });
    const body = await response.json().catch(() => ({ detail: "Unable to prepare a demo account." }));
    return NextResponse.json(body, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "Unable to reach the TraceForge API. Start the backend and check its database connection." }, { status: 503 });
  }
}

export async function POST(request: Request) {
  const payload = await request.json().catch(() => null);
  if (!payload || typeof payload.email !== "string" || typeof payload.password !== "string") {
    return NextResponse.json({ detail: "Email and password are required." }, { status: 400 });
  }

  let loginResponse: Response;
  try {
    loginResponse = await fetch(`${backendUrl}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: payload.email, password: payload.password }),
      cache: "no-store",
    });
  } catch {
    return NextResponse.json({ detail: "Unable to reach the TraceForge API. Start the backend and check its database connection." }, { status: 503 });
  }

  if (!loginResponse.ok) {
    const error = await loginResponse.json().catch(() => null) as { detail?: string } | null;
    return NextResponse.json({ detail: error?.detail ?? "Unable to sign in." }, { status: loginResponse.status });
  }

  const token = await loginResponse.json() as { access_token: string; expires_in: number };
  let userResponse: Response;
  try {
    userResponse = await fetch(`${backendUrl}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token.access_token}` },
      cache: "no-store",
    });
  } catch {
    return NextResponse.json({ detail: "Unable to verify the login session because the TraceForge API is unavailable." }, { status: 503 });
  }

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
