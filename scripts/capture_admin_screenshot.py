import subprocess
import time
import json
import urllib.request
import websocket
import base64
import os

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9226
OUT_DIR = "screenshots_audit"
os.makedirs(OUT_DIR, exist_ok=True)

SHOTS = [
    ("admin_desktop", "http://127.0.0.1:8000/?auto_login=sumit&view=admin", 1440, 900),
    ("admin_mobile", "http://127.0.0.1:8000/?auto_login=sumit&view=admin", 390, 844)
]

for name, url, w, h in SHOTS:
    proc = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={PORT}",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--window-size={w},{h}",
        f"--user-data-dir=C:/tmp/chrome_shot_{name}",
        url
    ])
    try:
        time.sleep(3.0)
        resp = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list", timeout=3)
        tabs = json.loads(resp.read().decode())
        ws_url = None
        for tab in tabs:
            if tab.get("type") == "page":
                ws_url = tab.get("webSocketDebuggerUrl")
                break
        if not ws_url and tabs:
            ws_url = tabs[0].get("webSocketDebuggerUrl")
        
        if ws_url:
            ws = websocket.create_connection(ws_url, timeout=5)
            # Give time for tables to load
            time.sleep(1.0)
            ws.send(json.dumps({
                "id": 1,
                "method": "Page.captureScreenshot",
                "params": {"format": "png"}
            }))
            raw = ws.recv()
            msg = json.loads(raw)
            if "result" in msg and "data" in msg["result"]:
                img_data = base64.b64decode(msg["result"]["data"])
                out_path = os.path.join(OUT_DIR, f"{name}.png")
                with open(out_path, "wb") as f:
                    f.write(img_data)
                print(f"Captured {out_path} ({len(img_data)} bytes)")
            ws.close()
    except Exception as e:
        print(f"Failed {name}: {e}")
    finally:
        proc.terminate()
        proc.wait()
        time.sleep(0.5)

print("Admin screenshots completed!")
