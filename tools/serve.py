#!/usr/bin/env python3
"""Local preview server that tells browsers (Safari especially) never to cache files. Run: python3 tools/serve.py"""
import functools
import http.server
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()


if __name__ == "__main__":
    handler = functools.partial(NoCacheHandler, directory=str(ROOT))
    with http.server.ThreadingHTTPServer(("127.0.0.1", 8765), handler) as srv:
        print("Serving on http://localhost:8765 (no caching)")
        srv.serve_forever()
