#!/usr/bin/env python3
import os
import json
import time
import csv
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, ".env"))

from http.server import HTTPServer, SimpleHTTPRequestHandler

SHEET_NINJA_ENDPOINT = os.getenv("SHEET_NINJA_ENDPOINT_URL")
SHEET_NINJA_API_KEY = os.getenv("SHEET_NINJA_API_KEY")

FRONTEND_DIR = os.path.join(project_root, "frontend")
DATA_DIR = os.path.join(project_root, "data")
CACHE_FILE = os.path.join(DATA_DIR, "sales_cache.json")
CSV_FILE = os.path.join(DATA_DIR, "sales.csv")
PENDING_FILE = os.path.join(DATA_DIR, "pending_updates.json")

os.makedirs(DATA_DIR, exist_ok=True)

cache = {"data": [], "timestamp": 0}
pending_updates = []

def load_cache():
    global cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
        except:
            pass

def load_pending():
    global pending_updates
    if os.path.exists(PENDING_FILE):
        try:
            with open(PENDING_FILE, 'r') as f:
                pending_updates = json.load(f)
        except:
            pass

def save_cache(data):
    global cache
    cache = {"data": data, "timestamp": time.time()}
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def save_csv(data):
    if not data:
        return
    keys = list(data[0].keys()) if data else []
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def load_csv():
    data = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    return data

def save_pending():
    with open(PENDING_FILE, 'w') as f:
        json.dump(pending_updates, f)

def fetch_from_api():
    import requests
    headers = {"Authorization": f"Bearer {SHEET_NINJA_API_KEY}"}
    response = requests.get(SHEET_NINJA_ENDPOINT, headers=headers, timeout=10)
    if response.status_code == 200:
        return response.json()
    return None

def push_to_api(data):
    import requests
    headers = {"Authorization": f"Bearer {SHEET_NINJA_API_KEY}", "Content-Type": "application/json"}
    response = requests.post(SHEET_NINJA_ENDPOINT, headers=headers, json=data, timeout=10)
    return response.status_code == 200

def sync_pending():
    global pending_updates
    if not pending_updates:
        return {"success": True, "message": "No pending updates"}
    
    csv_data = load_csv()
    if not csv_data:
        return {"success": False, "message": "No CSV data"}
    
    for update in pending_updates:
        for i, row in enumerate(csv_data):
            if str(row.get('id')) == str(update.get('id')):
                csv_data[i].update(update)
                break
    
    success = push_to_api(csv_data)
    if success:
        pending_updates = []
        save_pending()
        save_csv(csv_data)
        load_cache()
        return {"success": True, "message": f"Synced {len(pending_updates)} updates"}
    
    return {"success": False, "message": "Failed to push updates"}

class APIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/api/sales':
            data = fetch_from_api()
            if data is not None:
                save_cache(data)
                save_csv(data)
                response_data = data
            else:
                csv_data = load_csv()
                if csv_data:
                    response_data = csv_data
                else:
                    response_data = cache.get("data", [])
                response_data = {"fromCache": True, "data": response_data}
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())
        elif self.path == '/api/sync':
            result = sync_pending()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        elif self.path == '/api/pending':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"count": len(pending_updates), "updates": pending_updates}).encode())
        elif self.path == '/' or self.path == '/kanban.html':
            self.path = '/kanban.html'
            super().do_GET()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/sales':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                updates = json.loads(body)
                if isinstance(updates, list):
                    pending_updates.extend(updates)
                else:
                    pending_updates.append(updates)
                save_pending()
                
                csv_data = load_csv()
                for update in (updates if isinstance(updates, list) else [updates]):
                    for i, row in enumerate(csv_data):
                        if str(row.get('id')) == str(update.get('id')):
                            csv_data[i].update(update)
                            break
                save_csv(csv_data)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"saved": True, "pending": len(pending_updates)}).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            super().do_GET()

load_cache()
load_pending()

print(f"Starting server on http://localhost:8001")
print(f"Serving frontend from: {FRONTEND_DIR}")
print(f"Data dir: {DATA_DIR}")
print(f"Pending updates: {len(pending_updates)}")
server = HTTPServer(('0.0.0.0', 8001), APIHandler)
server.serve_forever()