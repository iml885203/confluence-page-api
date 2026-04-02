from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"""<!DOCTYPE html>
<html>
<head><title>OAuth Success</title></head>
<body>
<h1>Authorization Successful</h1>
<p>You can close this window.</p>
<pre id="tokens"></pre>
<script>
  const hash = window.location.hash.substring(1);
  if (hash) {
    const params = new URLSearchParams(hash);
    const data = Object.fromEntries(params.entries());
    document.getElementById('tokens').textContent = JSON.stringify(data, null, 2);
  }
</script>
</body>
</html>""")
