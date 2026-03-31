#!/usr/bin/env python3
import os
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, ".env"))

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

SHEET_NINJA_ENDPOINT = os.getenv("SHEET_NINJA_ENDPOINT_URL")
SHEET_NINJA_API_KEY = os.getenv("SHEET_NINJA_API_KEY")

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()
    
    def do_GET(self):
        if self.path == '/api/sales':
            import requests
            headers = {"Authorization": f"Bearer {SHEET_NINJA_API_KEY}"}
            response = requests.get(SHEET_NINJA_ENDPOINT, headers=headers)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(response.content)
        else:
            super().do_GET()

print("Starting server on http://localhost:8001")
server = HTTPServer(('0.0.0.0', 8001), CORSRequestHandler)
server.serve_forever()
