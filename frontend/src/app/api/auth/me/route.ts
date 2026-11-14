import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const COOKIE_NAME = "traceforge_session";
const backendUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function GET() {
  const token = (await cookies()).get(COOKIE_NAME)?.value;
  if (!token) return NextResponse.json({ detail: "Authentication required." }, { status: 401 });

  const backendResponse = await fetch(`${backendUrl}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  if (!backendResponse.ok) {
    const response = NextResponse.json({ detail: "Your session has expired. Please sign in again." }, { status: 401 });
    response.cookies.delete(COOKIE_NAME);
    return response;
  }

  return NextResponse.json(await backendResponse.json());
}
