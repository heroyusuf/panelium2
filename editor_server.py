import http.server
import socketserver
import json
import os
import cgi
import zipfile
import io
import mimetypes

PORT = 8000

# Files/dirs included in the export zip
EXPORT_FILES  = ['config.json', 'viewer.html', 'pannellum.js', 'pannellum.css',
                 'skin-engine.js', 'skin.css']
EXPORT_DIRS   = ['icon', 'jpeg']
ALLOWED_IMAGE = {'.png', '.jpg', '.jpeg', '.svg', '.gif', '.webp'}

def _json_ok(handler, data):
    body = json.dumps(data, ensure_ascii=False).encode('utf-8')
    handler.send_response(200)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Content-Length', len(body))
    handler.end_headers()
    handler.wfile.write(body)

def _json_err(handler, msg, code=500):
    body = json.dumps({"status": "error", "message": msg}).encode('utf-8')
    handler.send_response(code)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Content-Length', len(body))
    handler.end_headers()
    handler.wfile.write(body)

class EditorHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # ── List icons (legacy) ─────────────────────────────────────────────
        if self.path == '/list_icons':
            try:
                icons = [f for f in os.listdir('icon')
                         if f.lower().endswith(('.png','.jpg','.jpeg','.svg','.gif'))] \
                         if os.path.exists('icon') else []
                _json_ok(self, {"status": "success", "icons": sorted(icons)})
            except Exception as e:
                _json_err(self, str(e))

        # ── List assets (icon/ + jpeg/) ─────────────────────────────────────
        elif self.path == '/list_assets':
            try:
                result = {}
                for d in ('icon', 'jpeg'):
                    if os.path.exists(d):
                        files = []
                        for f in sorted(os.listdir(d)):
                            fp = os.path.join(d, f)
                            if os.path.isfile(fp):
                                ext = os.path.splitext(f)[1].lower()
                                if ext in ALLOWED_IMAGE or d == 'icon':
                                    files.append({
                                        "name": f,
                                        "path": d + '/' + f,
                                        "size": os.path.getsize(fp)
                                    })
                        result[d] = files
                _json_ok(self, {"status": "success", "assets": result})
            except Exception as e:
                _json_err(self, str(e))

        # ── Export tour zip ─────────────────────────────────────────────────
        elif self.path == '/export_tour':
            try:
                buf = io.BytesIO()
                with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for fname in EXPORT_FILES:
                        if os.path.isfile(fname):
                            zf.write(fname)
                    for dname in EXPORT_DIRS:
                        if os.path.isdir(dname):
                            for root, _, files in os.walk(dname):
                                for f in files:
                                    zf.write(os.path.join(root, f))
                body = buf.getvalue()
                self.send_response(200)
                self.send_header('Content-Type', 'application/zip')
                self.send_header('Content-Disposition', 'attachment; filename="panelium_tour.zip"')
                self.send_header('Content-Length', len(body))
                self.end_headers()
                self.wfile.write(body)
                print("Export zip generated and sent.")
            except Exception as e:
                _json_err(self, str(e))

        else:
            super().do_GET()

    def do_POST(self):
        # ── Save config ─────────────────────────────────────────────────────
        if self.path == '/save_config':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                new_config = json.loads(post_data.decode('utf-8'))
                with open('config.json', 'w', encoding='utf-8') as f:
                    json.dump(new_config, f, indent=4, ensure_ascii=False)
                _json_ok(self, {"status": "success"})
                print("config.json successfully updated.")
            except Exception as e:
                _json_err(self, str(e))

        # ── Upload asset ─────────────────────────────────────────────────────
        elif self.path == '/upload_asset':
            try:
                ctype = self.headers.get('Content-Type', '')
                # Parse multipart form data
                environ = {
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': ctype,
                    'CONTENT_LENGTH': self.headers.get('Content-Length', 0),
                }
                form = cgi.FieldStorage(
                    fp=self.rfile, headers=self.headers,
                    environ=environ, keep_blank_values=True
                )
                file_item = form.get('file')
                dest_dir  = form.getvalue('dir', 'icon')   # 'icon' or 'jpeg'

                if not file_item or not file_item.filename:
                    return _json_err(self, "No file received.", 400)

                fname = os.path.basename(file_item.filename)
                ext   = os.path.splitext(fname)[1].lower()
                if ext not in ALLOWED_IMAGE:
                    return _json_err(self, f"File type {ext} not allowed.", 400)
                if dest_dir not in ('icon', 'jpeg'):
                    dest_dir = 'icon'

                os.makedirs(dest_dir, exist_ok=True)
                out_path = os.path.join(dest_dir, fname)
                with open(out_path, 'wb') as f:
                    f.write(file_item.file.read())

                _json_ok(self, {"status": "success", "path": dest_dir + '/' + fname, "name": fname})
                print(f"Uploaded: {out_path}")
            except Exception as e:
                _json_err(self, str(e))

        else:
            self.send_response(404)
            self.end_headers()

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with socketserver.TCPServer(("", PORT), EditorHandler) as httpd:
    print(f"Editör Sunucusu Başlatıldı! Lütfen tarayıcınızdan şu adrese gidin:")
    print(f"http://localhost:{PORT}/editor.html")
    httpd.serve_forever()
