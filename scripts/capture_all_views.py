import subprocess
import time
import json
import urllib.request
import base64
import os
import websocket

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9223
OUTPUT_DIR = "screenshots_audit"
os.makedirs(OUTPUT_DIR, exist_ok=True)

VIEWPORTS = [
    ("desktop", 1440, 900),
    ("tablet", 768, 1024),
    ("mobile", 390, 844)
]

VIEWS = [
    ("landing", "http://127.0.0.1:8000/?view=landing"),
    ("dashboard", "http://127.0.0.1:8000/?auto_login=sumit&view=dashboard"),
    ("setup", "http://127.0.0.1:8000/?auto_login=sumit&view=interview-setup"),
    ("device_check", "http://127.0.0.1:8000/?auto_login=sumit&view=device-check"),
    ("profile", "http://127.0.0.1:8000/?auto_login=sumit&view=profile"),
    ("history", "http://127.0.0.1:8000/?auto_login=sumit&view=history"),
    ("practice", "http://127.0.0.1:8000/?auto_login=sumit&view=practice")
]

print("=== STARTING CROSS-VIEWPORT CDP CAPTURE ===")

for vp_name, width, height in VIEWPORTS:
    print(f"\n--- Viewport: {vp_name} ({width}x{height}) ---")
    for view_key, url in VIEWS:
        proc = subprocess.Popen([
            CHROME_PATH,
            f"--remote-debugging-port={PORT}",
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            f"--window-size={width},{height}",
            f"--user-data-dir=C:/tmp/chrome_audit_{vp_name}",
            url
        ])

        try:
            time.sleep(2.0)
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
                # Set device metrics override for proper mobile emulation
                ws.send(json.dumps({
                    "id": 1,
                    "method": "Emulation.setDeviceMetricsOverride",
                    "params": {
                        "width": width,
                        "height": height,
                        "deviceScaleFactor": 1,
                        "mobile": (vp_name == "mobile")
                    }
                }))
                _ = ws.recv()

                time.sleep(1.5)

                ws.send(json.dumps({
                    "id": 2,
                    "method": "Page.captureScreenshot",
                    "params": {
                        "format": "png",
                        "captureBeyondViewport": False
                    }
                }))
                result = json.loads(ws.recv())
                img_data = base64.b64decode(result["result"]["data"])
                out_path = os.path.join(OUTPUT_DIR, f"{view_key}_{vp_name}.png")
                with open(out_path, "wb") as f:
                    f.write(img_data)
                print(f"  [OK] Captured {out_path} ({len(img_data)} bytes)")
                ws.close()
            else:
                print(f"  [ERR] No ws_url for {view_key}")
        except Exception as e:
            print(f"  [ERR] Error on {view_key}_{vp_name}: {e}")
        finally:
            proc.terminate()
            proc.wait()
            time.sleep(0.5)

print("\n=== FINISHED CDP VIEWPORT CAPTURES ===")

