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

proc = subprocess.Popen([
    CHROME_PATH,
    f"--remote-debugging-port={PORT}",
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--window-size=1440,2400",
    "--user-data-dir=C:/tmp/chrome_setup_profile",
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

    assert ws_url, "Could not find websocket URL"
    ws = websocket.create_connection(ws_url)

    # Wait 2.5 seconds for auto_login and rendering
    time.sleep(2.5)

    ws.send(json.dumps({
        "id": 1,
        "method": "Page.captureScreenshot",
        "params": {
            "format": "png",
            "captureBeyondViewport": True
        }
    }))
    
    result = json.loads(ws.recv())
    img_data = base64.b64decode(result["result"]["data"])
    
    out_path = os.path.join(OUTPUT_DIR, "setup_page_1440.png")
    with open(out_path, "wb") as f:
        f.write(img_data)
    
    print(f"SUCCESS: Screenshot saved to {out_path} ({len(img_data)} bytes)")
    ws.close()

finally:
    proc.terminate()
    proc.wait()
