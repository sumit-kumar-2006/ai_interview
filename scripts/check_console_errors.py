import subprocess
import time
import json
import urllib.request
import websocket
import os

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9224

VIEWS = [
    ("landing", "http://127.0.0.1:8000/?view=landing"),
    ("dashboard", "http://127.0.0.1:8000/?auto_login=sumit&view=dashboard"),
    ("setup", "http://127.0.0.1:8000/?auto_login=sumit&view=interview-setup"),
    ("device_check", "http://127.0.0.1:8000/?auto_login=sumit&view=device-check"),
    ("profile", "http://127.0.0.1:8000/?auto_login=sumit&view=profile"),
    ("history", "http://127.0.0.1:8000/?auto_login=sumit&view=history"),
    ("practice", "http://127.0.0.1:8000/?auto_login=sumit&view=practice"),
    ("admin", "http://127.0.0.1:8000/?auto_login=sumit&view=admin")
]

print("=== CHECKING RUNTIME BROWSER CONSOLE ERRORS & EXCEPTIONS ===")

for view_key, url in VIEWS:
    proc = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={PORT}",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1440,900",
        "--user-data-dir=C:/tmp/chrome_err_check",
        url
    ])

    errors = []
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
            # Enable Runtime and Log domains
            ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
            ws.send(json.dumps({"id": 2, "method": "Log.enable"}))
            
            # Wait 2.5 seconds to collect logs
            t_end = time.time() + 2.5
            while time.time() < t_end:
                try:
                    ws.settimeout(0.5)
                    raw = ws.recv()
                    msg = json.loads(raw)
                    method = msg.get("method", "")
                    if method == "Runtime.exceptionThrown":
                        details = msg.get("params", {}).get("exceptionDetails", {})
                        errors.append(f"EXCEPTION: {details.get('text')} {details.get('exception', {}).get('description', '')[:100]}")
                    elif method == "Log.entryAdded":
                        entry = msg.get("params", {}).get("entry", {})
                        if entry.get("level") in ["error", "fatal"]:
                            errors.append(f"LOG_ERROR: {entry.get('text')}")
                except Exception:
                    pass
            ws.close()
        
        if errors:
            print(f"[{view_key}] Found {len(errors)} runtime error(s):")
            for e in errors:
                print(f"   {e}")
        else:
            print(f"[{view_key}] 0 errors detected. CLEAN!")
    except Exception as ex:
        print(f"[{view_key}] CDP check failed: {ex}")
    finally:
        proc.terminate()
        proc.wait()
        time.sleep(0.5)

print("\n=== RUNTIME CONSOLE ERROR CHECK COMPLETE ===")
