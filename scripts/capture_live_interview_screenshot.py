import subprocess
import time
import json
import urllib.request
import base64
import os
import websocket

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9222
URL = "http://127.0.0.1:8000/?auto_login=sumit&view=practice"
OUTPUT_DIR = "scripts/screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

proc = subprocess.Popen([
    CHROME_PATH,
    f"--remote-debugging-port={PORT}",
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--use-fake-ui-for-media-stream",
    "--use-fake-device-for-media-stream",
    "--window-size=1648,927",
    "--user-data-dir=C:/tmp/chrome_practice_profile",
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

    # Let auto_login and page settle
    time.sleep(3.5)

    # Ensure overlay is hidden if needed and question is loaded
    ws.send(json.dumps({
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {
            "expression": """
            (() => {
                const overlay = document.getElementById('interview-init-overlay');
                if (overlay) overlay.classList.add('hidden');
                const mainStage = document.getElementById('interview-main-stage');
                if (mainStage) mainStage.style.display = 'grid';
                const bottomBar = document.getElementById('interview-bottombar');
                if (bottomBar) bottomBar.style.display = 'flex';
                if (typeof loadQuestion === 'function') loadQuestion(0);
                // Set attention and pose indicators
                const faceAlert = document.getElementById('face-alert-banner');
                if (faceAlert) faceAlert.classList.remove('hidden');
                const videoFace = document.getElementById('video-face-text');
                if (videoFace) videoFace.textContent = 'Face Detected • Eyes: Away';
                const videoPose = document.getElementById('video-pose-text');
                if (videoPose) videoPose.textContent = 'Head: RIGHT';
                const sessionTimer = document.getElementById('topbar-session-timer');
                if (sessionTimer) sessionTimer.textContent = '00:37';
            })()
            """
        }
    }))
    time.sleep(1)

    ws.send(json.dumps({
        "id": 2,
        "method": "Page.captureScreenshot",
        "params": {
            "format": "png",
            "captureBeyondViewport": False
        }
    }))
    
    result = json.loads(ws.recv())
    while "result" not in result or "data" not in result["result"]:
        result = json.loads(ws.recv())

    img_data = base64.b64decode(result["result"]["data"])
    out_path = os.path.join(OUTPUT_DIR, "live_interview_1648.png")
    with open(out_path, "wb") as f:
        f.write(img_data)
    
    print(f"SUCCESS: Screenshot saved to {out_path} ({len(img_data)} bytes)")
    ws.close()

finally:
    proc.terminate()
    proc.wait()
