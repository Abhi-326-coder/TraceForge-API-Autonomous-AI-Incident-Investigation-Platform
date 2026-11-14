import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const COOKIE_NAME = "traceforge_session";

export function proxy(request: NextRequest) {
  const hasSession = Boolean(request.cookies.get(COOKIE_NAME)?.value);
  const isLogin = request.nextUrl.pathname === "/login";

  if (!hasSession && !isLogin) return NextResponse.redirect(new URL("/login", request.url));
  if (hasSession && isLogin) return NextResponse.redirect(new URL("/dashboard", request.url));
  return NextResponse.next();
}

export const config = { matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"] };
