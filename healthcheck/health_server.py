from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

class HealthzHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.info(f"Request received: {self.path}")
        if self.path == "/healthz":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("✅ Health server running on 0.0.0.0:8081")
    server = HTTPServer(("0.0.0.0", 8081), HealthzHandler)
    server.serve_forever()

