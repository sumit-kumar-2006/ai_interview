import subprocess
import time
import json
import urllib.request
import base64
import os
import websocket

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9222
URL = "http://127.0.0.1:8000/?auto_login=sumit&view=interview-setup"
OUTPUT_DIR = "scripts/screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

viewports = [
    (1024, 2600, "setup_page_1024.png"),
    (768, 3000, "setup_page_768.png"),
    (390, 3600, "setup_page_390.png")
]

for w, h, fname in viewports:
    proc = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={PORT}",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--window-size={w},{h}",
        "--user-data-dir=C:/tmp/chrome_setup_profile_multi",
        URL
    ])
    try:
        time.sleep(3)
        resp = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list")
        tabs = json.loads(resp.read().decode())
        ws_url = None
        for tab in tabs:
            if tab.get("type") == "page":
                ws_url = tab.get("webSocketDebuggerUrl")
                break
        if not ws_url and tabs:
            ws_url = tabs[0].get("webSocketDebuggerUrl")
        
        ws = websocket.create_connection(ws_url)
        time.sleep(2)
        
        ws.send(json.dumps({
            "id": 1,
            "method": "Page.captureScreenshot",
            "params": {
                "format": "png",
                "captureBeyondViewport": True
            }
        }))
        res = json.loads(ws.recv())
        img_data = base64.b64decode(res["result"]["data"])
        out_path = os.path.join(OUTPUT_DIR, fname)
        with open(out_path, "wb") as f:
            f.write(img_data)
        print(f"Captured {fname} at {w}x{h}: {len(img_data)} bytes")
        ws.close()
    finally:
        proc.terminate()
        proc.wait()
        time.sleep(1)

print("All responsive viewports captured successfully!")

