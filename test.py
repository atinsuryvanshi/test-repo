from http.server import BaseHTTPRequestHandler, HTTPServer

class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>Bina PIP ke AWS chal gaya! Account verified hai.</h1>")

HTTPServer(('0.0.0.0', 8080), SimpleServer).serve_forever()
