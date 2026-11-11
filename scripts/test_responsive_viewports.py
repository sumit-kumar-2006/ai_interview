import subprocess
import time
import json
import urllib.request
import base64
import os
import websocket

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9225
BASE_URL = "http://127.0.0.1:8000"
OUTPUT_DIR = "screenshots_audit/responsive"
os.makedirs(OUTPUT_DIR, exist_ok=True)

VIEWPORTS = [
    ("desktop_1920", 1920, 1080),
    ("desktop_1440", 1440, 900),
    ("laptop_1366", 1366, 768),
    ("laptop_1024", 1024, 768),
    ("tablet_768", 768, 1024),
    ("mobile_430", 430, 932),
    ("mobile_390", 390, 844),
    ("mobile_320", 320, 568)
]

VIEWS = [
    ("landing", f"{BASE_URL}/?view=landing"),
    ("dashboard", f"{BASE_URL}/?auto_login=sumit&view=dashboard"),
    ("setup", f"{BASE_URL}/?auto_login=sumit&view=interview-setup"),
    ("device_check", f"{BASE_URL}/?auto_login=sumit&view=device-check"),
    ("practice", f"{BASE_URL}/?auto_login=sumit&view=practice"),
    ("profile", f"{BASE_URL}/?auto_login=sumit&view=profile"),
    ("history", f"{BASE_URL}/?auto_login=sumit&view=history"),
    ("admin", f"{BASE_URL}/?auto_login=sumit&view=admin")
]

def send_cdp(ws, method, params=None, msg_id=1):
    req = {"id": msg_id, "method": method}
    if params:
        req["params"] = params
    ws.send(json.dumps(req))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == msg_id:
            return resp

def evaluate_js(ws, expr, msg_id=100):
    res = send_cdp(ws, "Runtime.evaluate", {
        "expression": expr,
        "returnByValue": True,
        "awaitPromise": True
    }, msg_id=msg_id)
    return res.get("result", {}).get("result", {}).get("value")

def main():
    print("==================================================")
    print("PHASE 2: COMPREHENSIVE RESPONSIVE VIEWPORT AUDIT")
    print("==================================================")

    results = []

    for vp_name, width, height in VIEWPORTS:
        print(f"\n--- Testing Viewport: {vp_name} ({width}x{height}) ---")
        for view_name, url in VIEWS:
            proc = subprocess.Popen([
                CHROME_PATH,
                f"--remote-debugging-port={PORT}",
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                f"--window-size={width},{height}",
                f"--user-data-dir=C:/tmp/chrome_vp_{vp_name}",
                url
            ])

            try:
                time.sleep(1.8)
                resp = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list", timeout=3)
                tabs = json.loads(resp.read().decode())
                ws_url = None
                for tab in tabs:
                    if tab.get("type") == "page":
                        ws_url = tab.get("webSocketDebuggerUrl")
                        break
                if not ws_url and tabs:
                    ws_url = tabs[0].get("webSocketDebuggerUrl")

                if not ws_url:
                    print(f"  [FAIL] Could not connect to Chrome tab for {view_name}")
                    continue

                ws = websocket.create_connection(ws_url, timeout=5)

                # Set Device Metrics Override
                is_mobile = width < 768
                send_cdp(ws, "Emulation.setDeviceMetricsOverride", {
                    "width": width,
                    "height": height,
                    "deviceScaleFactor": 1,
                    "mobile": is_mobile
                }, msg_id=10)

                time.sleep(1.0)

                # Check horizontal scroll overflow
                overflow_info = evaluate_js(ws, """
                    (() => {
                        const docWidth = document.documentElement.scrollWidth;
                        const bodyWidth = document.body.scrollWidth;
                        const winWidth = window.innerWidth;
                        const hasOverflow = docWidth > winWidth + 1 || bodyWidth > winWidth + 1;
                        return {
                            docWidth,
                            bodyWidth,
                            winWidth,
                            hasOverflow
                        };
                    })()
                """, msg_id=20)

                # Capture viewport screenshot
                scr_res = send_cdp(ws, "Page.captureScreenshot", {
                    "format": "png",
                    "captureBeyondViewport": False
                }, msg_id=30)

                if "result" in scr_res and "data" in scr_res["result"]:
                    img_bytes = base64.b64decode(scr_res["result"]["data"])
                    fname = f"{view_name}_{vp_name}.png"
                    fpath = os.path.join(OUTPUT_DIR, fname)
                    with open(fpath, "wb") as f:
                        f.write(img_bytes)

                has_overflow = overflow_info.get("hasOverflow", False) if overflow_info else False
                status = "PASS (No Overflow)" if not has_overflow else f"WARN (Overflow: doc={overflow_info.get('docWidth')} win={width})"
                print(f"  [{status}] View: {view_name:<12} | Width: {width}px | Saved: {fname}")

                results.append({
                    "viewport": vp_name,
                    "width": width,
                    "height": height,
                    "view": view_name,
                    "has_overflow": has_overflow,
                    "details": overflow_info
                })

                ws.close()

            except Exception as e:
                print(f"  [ERROR] {view_name} on {vp_name}: {e}")
            finally:
                proc.terminate()
                proc.wait()
                time.sleep(0.3)

    total_tests = len(results)
    overflow_count = sum(1 for r in results if r["has_overflow"])
    print("\n==================================================")
    print(f"AUDIT SUMMARY: {total_tests} views/viewports tested.")
    print(f"Passed: {total_tests - overflow_count} / {total_tests}")
    print(f"Overflow Warnings: {overflow_count}")
    print("==================================================")

if __name__ == "__main__":
    main()
