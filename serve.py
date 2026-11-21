#!/usr/bin/env python3
"""启洵看板 · 局域网静态服务（带 no-cache，便于 iPad 安装 PWA）。"""
import http.server
import os
import socketserver

DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8123


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Service-Worker-Allowed", "/")
        super().end_headers()

    def log_message(self, format, *args):  # noqa: A002
        pass


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    with Server(("0.0.0.0", PORT), Handler) as httpd:
        print(f"serving {DIR} on 0.0.0.0:{PORT}")
        httpd.serve_forever()
