import http.server
import socketserver
import json
import os

PORT = 8000

class EditorHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/list_icons':
            try:
                icon_dir = 'icon'
                icons = []
                if os.path.exists(icon_dir):
                    icons = [f for f in os.listdir(icon_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.gif'))]
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "icons": icons}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/save_config':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                new_config = json.loads(post_data.decode('utf-8'))
                with open('config.json', 'w', encoding='utf-8') as f:
                    json.dump(new_config, f, indent=4, ensure_ascii=False)
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
                print("config.json successfully updated.")
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
                print(f"Error saving config.json: {e}")
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
