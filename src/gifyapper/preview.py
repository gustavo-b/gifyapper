import base64
import io
import json
import threading
import webbrowser
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from PIL import Image


def _img_to_base64(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


class _PreviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, api_data=None, result_event=None, result_store=None, **kwargs):
        self.api_data = api_data
        self.result_event = result_event
        self.result_store = result_store
        super().__init__(*args, **kwargs)

    def _no_cache(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            html_path = Path(self.api_data["static_dir"]) / "preview.html"
            content = html_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(content))
            self._no_cache()
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/api/data":
            payload = {
                "frame": self.api_data["frame_b64"],
                "gif_width": self.api_data["gif_width"],
                "gif_height": self.api_data["gif_height"],
                "bubble_width": self.api_data["bubble_width"],
                "bubble_height": self.api_data["bubble_height"],
                "bg_color": self.api_data["bg_color"],
            }
            body = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(body))
            self._no_cache()
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/generate":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            self.result_store["data"] = body
            resp = json.dumps({"status": "ok"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(resp))
            self.end_headers()
            self.wfile.write(resp)
            self.result_event.set()
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass  # Suppress request logs


def run_preview(frame_img, bubble_width, bubble_height, bg_color, static_dir):
    """Start a local preview server, open browser, wait for user to position bubble.

    Returns dict with keys: x, y, width, height, tail_direction, pad_top, shape, etc.
    """
    result_event = threading.Event()
    result_store = {}

    api_data = {
        "frame_b64": _img_to_base64(frame_img),
        "gif_width": frame_img.width,
        "gif_height": frame_img.height,
        "bubble_width": bubble_width,
        "bubble_height": bubble_height,
        "bg_color": bg_color,
        "static_dir": str(static_dir),
    }

    handler = partial(
        _PreviewHandler,
        api_data=api_data,
        result_event=result_event,
        result_store=result_store,
    )

    server = HTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    url = f"http://localhost:{port}/"
    print(f"Preview server at {url}")
    webbrowser.open(url)

    result_event.wait()
    server.shutdown()

    return result_store["data"]
