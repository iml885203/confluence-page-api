from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"""<!DOCTYPE html>
<html>
<head><title>OAuth</title></head>
<body>
<h1 id="title">Authorization Successful</h1>
<p id="message">You can close this window.</p>
<pre id="data"></pre>
<script>
  const params = new URLSearchParams(window.location.hash.substring(1) || window.location.search);
  const error = params.get('error');
  if (error) {
    document.getElementById('title').textContent = 'Authorization Failed';
    document.getElementById('message').textContent = error;
    document.getElementById('title').style.color = '#dc2626';
  } else {
    const data = Object.fromEntries(params.entries());
    document.getElementById('data').textContent = JSON.stringify(data, null, 2);
  }
</script>
</body>
</html>""")
