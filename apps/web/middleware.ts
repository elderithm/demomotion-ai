import { NextRequest, NextResponse } from 'next/server';

// Gate the whole dashboard behind HTTP Basic auth. Credentials come from runtime
// env (BASIC_AUTH_USER / BASIC_AUTH_PASS) so they are never baked into the image
// or committed. If they are unset (e.g. local dev), the gate is disabled.
export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)']
};

export function middleware(req: NextRequest) {
  const user = process.env.BASIC_AUTH_USER;
  const pass = process.env.BASIC_AUTH_PASS;
  if (!user || !pass) return NextResponse.next();

  const header = req.headers.get('authorization');
  if (header?.startsWith('Basic ')) {
    const decoded = atob(header.slice(6));
    const sep = decoded.indexOf(':');
    if (sep !== -1 && decoded.slice(0, sep) === user && decoded.slice(sep + 1) === pass) {
      return NextResponse.next();
    }
  }

  return new NextResponse('Authentication required', {
    status: 401,
    headers: { 'WWW-Authenticate': 'Basic realm="DemoMotion AI", charset="UTF-8"' }
  });
}
