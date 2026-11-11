import subprocess
import time
import json
import urllib.request
import os
import websocket
import base64

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9235
BASE_URL = "http://127.0.0.1:8000"

def send_cdp(ws, method, params=None, msg_id=1):
    req = {"id": msg_id, "method": method}
    if params: req["params"] = params
    ws.send(json.dumps(req))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == msg_id: return resp

def main():
    viewports = [
        (1440, 900, "desktop_1440"),
        (1366, 768, "laptop_1366"),
        (1024, 768, "laptop_1024"),
        (768, 1024, "tablet_768"),
        (390, 844, "mobile_390"),
        (375, 667, "mobile_375"),
        (320, 568, "mobile_320")
    ]

    for width, height, name in viewports:
        print(f"\n--- Testing viewport {width}x{height} ({name}) ---")
        user_dir = f"C:/tmp/chrome_snap_{name}"
        proc = subprocess.Popen([
            CHROME_PATH,
            f"--remote-debugging-port={PORT}",
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            f"--window-size={width},{height}",
            f"--user-data-dir={user_dir}",
            f"{BASE_URL}/"
        ])
        
        try:
            time.sleep(2)
            resp = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list")
            ws = websocket.create_connection(json.loads(resp.read().decode())[0]["webSocketDebuggerUrl"])
            
            # Authenticate and navigate to setup
            auth_res = send_cdp(ws, "Runtime.evaluate", {
                "expression": '''(async () => {
                    const res = await fetch('/auth/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email: 'skgounder50@gmail.com', password: 'password123' })
                    });
                    const data = await res.json();
                    authToken = data.access_token;
                    currentUser = data.user;
                    localStorage.setItem(STORAGE_KEY_TOKEN, authToken);
                    localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(currentUser));
                    updateAuthWidget();
                    navigateToView('interview-setup');
                    initInterviewSetupPage();
                    return { success: true };
                })()''',
                "awaitPromise": True
            }, msg_id=1)
            time.sleep(1)

            # Get layout and scroll metrics
            metrics = send_cdp(ws, "Runtime.evaluate", {
                "expression": '''({
                    scrollHeight: document.documentElement.scrollHeight,
                    clientHeight: document.documentElement.clientHeight,
                    scrollWidth: document.documentElement.scrollWidth,
                    clientWidth: document.documentElement.clientWidth,
                    hasStickyBar: !!document.getElementById('setup-sticky-bottom-bar'),
                    stickyBtnText: document.getElementById('btn-sticky-continue-device-check')?.innerText || '',
                    statusText: document.getElementById('ssb-status-text')?.innerText || ''
                })''',
                "returnByValue": True
            }, msg_id=2)["result"]["result"]["value"]
            
            print(f"  Metrics: scrollHeight={metrics.get('scrollHeight')}, clientHeight={metrics.get('clientHeight')}, scrollWidth={metrics.get('scrollWidth')}, clientWidth={metrics.get('clientWidth')}")
            print(f"  Sticky bar status: {metrics.get('statusText')} | Btn: {metrics.get('stickyBtnText')}")
            
            # Check horizontal overflow
            has_h_overflow = metrics["scrollWidth"] > metrics["clientWidth"]
            print(f"  Horizontal overflow: {has_h_overflow} (scrollWidth={metrics['scrollWidth']} vs clientWidth={metrics['clientWidth']})")
            assert not has_h_overflow, f"Horizontal overflow detected on {name}!"

            # Capture initial screenshot
            shot = send_cdp(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=3)
            with open(f"scripts/screenshots/setup_view_after_{name}.png", "wb") as f:
                f.write(base64.b64decode(shot["result"]["data"]))
            print(f"  Saved scripts/screenshots/setup_view_after_{name}.png")

            # On 1440, also capture scrolled view to test persistent bottom bar in action
            if name == "desktop_1440":
                send_cdp(ws, "Runtime.evaluate", {"expression": "window.scrollTo(0, 400);"}, msg_id=4)
                time.sleep(0.5)
                shot_mid = send_cdp(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=5)
                with open("scripts/screenshots/setup_view_after_desktop_1440_scrolled.png", "wb") as f:
                    f.write(base64.b64decode(shot_mid["result"]["data"]))
                print("  Saved setup_view_after_desktop_1440_scrolled.png")

            ws.close()
        finally:
            proc.terminate()
            proc.wait()

    print("\nAll viewport tests completed successfully!")

if __name__ == "__main__":
    main()
