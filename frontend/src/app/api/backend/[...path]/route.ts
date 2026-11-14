import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const COOKIE_NAME = "traceforge_session";
const backendUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function forward(request: Request, context: { params: Promise<{ path: string[] }> }) {
  const token = (await cookies()).get(COOKIE_NAME)?.value;
  if (!token) return NextResponse.json({ detail: "Authentication required." }, { status: 401 });

  const { path } = await context.params;
  const url = new URL(`${backendUrl}/${path.join("/")}`);
  url.search = new URL(request.url).search;
  const headers = new Headers();
  headers.set("Authorization", `Bearer ${token}`);
  const contentType = request.headers.get("content-type");
  if (contentType) headers.set("Content-Type", contentType);

  const backendResponse = await fetch(url, {
    method: request.method,
    headers,
    body: ["GET", "HEAD"].includes(request.method) ? undefined : await request.arrayBuffer(),
    cache: "no-store",
  });

  const response = new NextResponse(backendResponse.body, { status: backendResponse.status, headers: { "Content-Type": backendResponse.headers.get("content-type") ?? "application/json" } });
  if (backendResponse.status === 401) response.cookies.delete(COOKIE_NAME);
  return response;
}

export const GET = forward;
export const POST = forward;
export const PUT = forward;
export const PATCH = forward;
export const DELETE = forward;
