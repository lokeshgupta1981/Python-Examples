import base64
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

class Handler(BaseHTTPRequestHandler):
    def send_text(self, body, status=200, extra=None):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "max-age=60")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            self.send_text("<html><head><title>Something.</title></head><body>Something.</body></html>")
        elif url.path == "/greet":
            name = parse_qs(url.query).get("name", ["stranger"])[0]
            self.send_text(f"Hello {name}")
        elif url.path == "/agent":
            self.send_text(self.headers.get("User-Agent", ""))
        elif url.path == "/secure/":
            expected = "Basic " + base64.b64encode(b"user7:7user").decode()
            if self.headers.get("Authorization") == expected:
                self.send_text("This is a secure page.")
            else:
                self.send_text("Unauthorized", 401, {"WWW-Authenticate": 'Basic realm="Restricted Area"'})
        else:
            self.send_text("Not Found", 404)

    do_HEAD = do_GET

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode("utf-8"))
        self.send_text("Hello " + form.get("name", ["stranger"])[0])

    def log_message(self, *args):
        pass

if __name__ == "__main__":
    ThreadingHTTPServer(("localhost", 8000), Handler).serve_forever()
