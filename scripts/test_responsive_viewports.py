import subprocess, time, json, urllib.request, websocket, os

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE_URL = "http://127.0.0.1:8000"

VIEWPORTS = [
    ("desktop", 1440, 900),
    ("tablet", 768, 1024),
    ("mobile", 390, 844)
]

PAGES = [
    ("home", f"{BASE_URL}/"),
    ("dashboard", f"{BASE_URL}/dashboard?auto_login=sumit"),
    ("profile", f"{BASE_URL}/profile?auto_login=sumit"),
    ("analytics", f"{BASE_URL}/analytics?auto_login=sumit"),
    ("setup", f"{BASE_URL}/start-interview?auto_login=sumit"),
    ("device_check", f"{BASE_URL}/device-check?auto_login=sumit"),
    ("reports", f"{BASE_URL}/reports?auto_login=sumit")
]

def send_cdp(ws, method, params=None, msg_id=1):
    req = {"id": msg_id, "method": method}
    if params: req["params"] = params
    ws.send(json.dumps(req))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == msg_id: return resp

def evaluate_js(ws, expr, msg_id=100):
    res = send_cdp(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True}, msg_id=msg_id)
    return res.get("result", {}).get("result", {}).get("value")

results = []

for vp_name, width, height in VIEWPORTS:
    port = 9300 + (width % 100)
    user_data = f"C:/tmp/chrome_vp_{vp_name}_{port}"
    proc = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={port}",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--window-size={width},{height}",
        f"--user-data-dir={user_data}",
        f"{BASE_URL}/?_t={port}"
    ])
    try:
        time.sleep(2.0)
        resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list")
        tabs = json.loads(resp.read().decode())
        ws = websocket.create_connection(tabs[0]["webSocketDebuggerUrl"])
        send_cdp(ws, "Page.enable", {}, msg_id=1)

        for p_name, p_url in PAGES:
            send_cdp(ws, "Page.navigate", {"url": p_url}, msg_id=20)
            time.sleep(1.2)
            eval_res = evaluate_js(ws, """(() => {
                const docEl = document.documentElement;
                const body = document.body;
                const scrollW = Math.max(docEl.scrollWidth, body.scrollWidth);
                const clientW = docEl.clientWidth;
                const hasHOverflow = scrollW > (clientW + 2); // 2px margin for rounding
                const activePanels = Array.from(document.querySelectorAll('.view-panel.active')).map(p => p.id);
                return {
                    scrollW: scrollW,
                    clientW: clientW,
                    hasHOverflow: hasHOverflow,
                    activePanels: activePanels
                };
            })()""", msg_id=30)
            
            status = "PASS" if not eval_res.get("hasHOverflow") and len(eval_res.get("activePanels", [])) == 1 else "FAIL"
            results.append({
                "viewport": vp_name,
                "width": width,
                "page": p_name,
                "status": status,
                "scrollW": eval_res.get("scrollW"),
                "clientW": eval_res.get("clientW"),
                "hasHOverflow": eval_res.get("hasHOverflow"),
                "activePanels": eval_res.get("activePanels")
            })
            print(f"[{vp_name.upper()} {width}px] {p_name:12}: {status} (scrollW={eval_res.get('scrollW')} clientW={eval_res.get('clientW')} active={eval_res.get('activePanels')})")
        ws.close()
    finally:
        proc.terminate()
        proc.wait()

print("\n=== SUMMARY ===")
all_pass = all(r["status"] == "PASS" for r in results)
print(f"Total viewport checks: {len(results)}, All passed: {all_pass}")
