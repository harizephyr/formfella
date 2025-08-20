import { NextResponse } from "next/server";

export function middleware(request) {
  const token = request.cookies.get("access_token");
  const { pathname } = request.nextUrl;

  // If user is not logged in and trying to access protected routes
  if (!token && pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  
  // If user is logged in and trying to access auth pages, redirect to dashboard
  if (token && (pathname === '/login' || pathname === '/signup')) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/login',
    '/signup'
  ]
};
