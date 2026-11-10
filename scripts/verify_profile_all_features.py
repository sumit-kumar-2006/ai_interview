import subprocess
import time
import json
import urllib.request
import base64
import os
import websocket

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9224
BASE_URL = "http://127.0.0.1:8000/?auto_login=sumit&view=profile"
OUTPUT_DIR = "scripts/screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def send_cdp(ws, method, params=None, msg_id=1):
    req = {"id": msg_id, "method": method}
    if params:
        req["params"] = params
    ws.send(json.dumps(req))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == msg_id:
            return resp

def evaluate_js(ws, script, msg_id=100):
    res = send_cdp(ws, "Runtime.evaluate", {
        "expression": script,
        "returnByValue": True,
        "awaitPromise": True
    }, msg_id=msg_id)
    return res.get("result", {}).get("result", {}).get("value")

def run_tests():
    print("=== STARTING FULL PROFILE & ANALYTICS VERIFICATION ===")
    
    # 1. Start Chrome
    proc = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={PORT}",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1440,2400",
        "--user-data-dir=C:/tmp/chrome_profile_verify",
        BASE_URL
    ])

    ws = None
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
        print("Connected to Chrome CDP.")
        time.sleep(4) # Let analytics load and chart render

        # Test 1: Check Auth and Profile DOM Elements
        check_dom_script = """
        (() => {
            const userName = document.getElementById('profile-user-name')?.textContent?.trim();
            const userSub = document.getElementById('profile-user-subtitle')?.textContent?.trim();
            const totalInterviews = document.getElementById('card-total-interviews')?.textContent?.trim();
            const practiceTime = document.getElementById('card-total-time')?.textContent?.trim();
            const avgScore = document.getElementById('card-avg-score')?.textContent?.trim();
            const overallScore = document.getElementById('card-overall-score')?.textContent?.trim();
            const apiStatus = document.getElementById('api-status-text')?.textContent?.trim();
            const reportsCount = document.querySelectorAll('#profile-recent-reports-list .recent-report-row').length;
            const radarCanvas = !!document.getElementById('perf-radar-canvas');
            const trendCanvas = !!document.getElementById('score-trend-canvas');
            
            return {
                userName,
                userSub,
                totalInterviews,
                practiceTime,
                avgScore,
                overallScore,
                apiStatus,
                reportsCount,
                radarCanvas,
                trendCanvas
            };
        })()
        """
        dom_status = evaluate_js(ws, check_dom_script, 101)
        print("DOM Status Check:", json.dumps(dom_status, indent=2))
        assert dom_status["userName"] == "Sumit Gounder", f"Expected Sumit Gounder, got {dom_status['userName']}"
        assert dom_status["totalInterviews"] == "8", f"Expected 8 interviews, got {dom_status['totalInterviews']}"
        assert dom_status["overallScore"] == "85.0%", f"Expected 85.0%, got {dom_status['overallScore']}"
        assert dom_status["avgScore"] == "78.3%", f"Expected 78.3%, got {dom_status['avgScore']}"
        assert dom_status["practiceTime"] == "3h 24m", f"Expected 3h 24m, got {dom_status['practiceTime']}"
        assert dom_status["reportsCount"] >= 3, f"Expected at least 3 recent reports, got {dom_status['reportsCount']}"
        assert dom_status["radarCanvas"], "Radar canvas not found"
        assert dom_status["trendCanvas"], "Score trend canvas not found"
        print("-> Test 1 (DOM & User Data Verification) PASSED!")

        # Test 2: Test User Dropdown Menu toggle
        toggle_dropdown_script = """
        (() => {
            const trigger = document.getElementById('nav-user-chip');
            if (trigger) trigger.click();
            const menu = document.getElementById('nav-profile-menu-dropdown');
            const isVisible = menu ? (!menu.classList.contains('hidden')) : false;
            return { dropdownExists: !!menu, isVisible };
        })()
        """
        dropdown_status = evaluate_js(ws, toggle_dropdown_script, 102)
        print("Dropdown Menu Toggle Check:", dropdown_status)
        assert dropdown_status["dropdownExists"], "Profile dropdown menu missing"
        assert dropdown_status["isVisible"], "Profile dropdown should be visible after click"
        print("-> Test 2 (Profile Dropdown Menu) PASSED!")

        # Test 3: Test Date Filter Interaction
        filter_test_script = """
        (() => {
            const filterSelect = document.getElementById('profile-date-filter');
            if (!filterSelect) return { success: false, reason: 'Select not found' };
            
            // Change to 7 days
            filterSelect.value = '7';
            filterSelect.dispatchEvent(new Event('change'));
            
            // Also test pill buttons in trend chart header
            const btn7d = document.getElementById('pill-7d');
            if (btn7d) btn7d.click();
            
            return {
                success: true,
                currentFilter: filterSelect.value,
                pillActive: btn7d?.classList.contains('active')
            };
        })()
        """
        filter_status = evaluate_js(ws, filter_test_script, 103)
        print("Date Filter Toggle Check:", filter_status)
        assert filter_status["success"], "Date filter toggle failed"
        assert filter_status["pillActive"], "7D pill should be active after click"
        print("-> Test 3 (Date Filter & Chart Period Pill) PASSED!")

        # Test 4: PDF Generation Direct Check via Backend API
        token_script = "localStorage.getItem('ai_interview_token') || ''"
        auth_token = evaluate_js(ws, token_script, 104)
        print(f"Auth token retrieved: {auth_token[:20]}...")

        # Test /profile/pdf
        req_pdf = urllib.request.Request("http://127.0.0.1:8000/profile/pdf")
        req_pdf.add_header("Authorization", f"Bearer {auth_token}")
        pdf_res = urllib.request.urlopen(req_pdf)
        pdf_bytes = pdf_res.read()
        print(f"Profile PDF Endpoint Status: {pdf_res.status}, Size: {len(pdf_bytes)} bytes, Header: {pdf_bytes[:5]}")
        assert pdf_res.status == 200, f"Expected 200, got {pdf_res.status}"
        assert pdf_bytes.startswith(b"%PDF"), "Response is not a valid PDF file"
        print("-> Test 4 (/profile/pdf generation) PASSED!")

        # Test /interviews/{id}/pdf (using User 2's latest interview: ID 79)
        req_interview_pdf = urllib.request.Request("http://127.0.0.1:8000/interviews/79/pdf")
        req_interview_pdf.add_header("Authorization", f"Bearer {auth_token}")
        interview_pdf_res = urllib.request.urlopen(req_interview_pdf)
        interview_pdf_bytes = interview_pdf_res.read()
        print(f"Interview 1 PDF Endpoint Status: {interview_pdf_res.status}, Size: {len(interview_pdf_bytes)} bytes, Header: {interview_pdf_bytes[:5]}")
        assert interview_pdf_res.status == 200
        assert interview_pdf_bytes.startswith(b"%PDF")
        print("-> Test 5 (/interviews/1/pdf generation) PASSED!")

        # Reset filter to 30 for pristine captures
        evaluate_js(ws, """
        (() => {
            const filterSelect = document.getElementById('profile-date-filter');
            if (filterSelect) {
                filterSelect.value = '30';
                filterSelect.dispatchEvent(new Event('change'));
            }
            const btn30d = document.getElementById('pill-30d');
            if (btn30d) btn30d.click();
            const menu = document.getElementById('nav-profile-menu-dropdown');
            if (menu) menu.classList.add('hidden');
        })()
        """, 105)
        time.sleep(1)

        # Multi-Resolution Screenshot captures
        resolutions = [
            ("profile_1440_desktop.png", 1440, 900),
            ("profile_1024_laptop.png", 1024, 768),
            ("profile_768_tablet.png", 768, 1024),
            ("profile_390_mobile.png", 390, 844)
        ]

        for filename, width, height in resolutions:
            send_cdp(ws, "Emulation.setDeviceMetricsOverride", {
                "width": width,
                "height": height,
                "deviceScaleFactor": 1,
                "mobile": (width <= 768)
            }, msg_id=200)
            time.sleep(1)
            
            # Re-render charts for the new canvas dimensions
            evaluate_js(ws, """
            (() => {
                if (window.renderRadarChart && window.lastProfileAnalytics) {
                    window.renderRadarChart(window.lastProfileAnalytics.skills_radar);
                }
                if (window.renderScoreTrendChart && window.lastProfileAnalytics) {
                    window.renderScoreTrendChart(window.lastProfileAnalytics.score_trend);
                }
            })()
            """, 201)
            time.sleep(0.5)

            shot = send_cdp(ws, "Page.captureScreenshot", {
                "format": "png",
                "captureBeyondViewport": True
            }, msg_id=202)
            
            img_bytes = base64.b64decode(shot["result"]["data"])
            save_path = os.path.join(OUTPUT_DIR, filename)
            with open(save_path, "wb") as f:
                f.write(img_bytes)
            print(f"Captured {filename}: {len(img_bytes)} bytes ({width}px width)")

        # Test Dark Theme Toggle
        evaluate_js(ws, """
        (() => {
            document.documentElement.setAttribute('data-theme', 'dark');
            document.body.classList.add('dark-theme');
        })()
        """, 301)
        time.sleep(1)

        dark_shot = send_cdp(ws, "Page.captureScreenshot", {
            "format": "png",
            "captureBeyondViewport": True
        }, msg_id=302)
        dark_bytes = base64.b64decode(dark_shot["result"]["data"])
        with open(os.path.join(OUTPUT_DIR, "profile_1440_dark.png"), "wb") as f:
            f.write(dark_bytes)
        print(f"Captured profile_1440_dark.png: {len(dark_bytes)} bytes")

        print("=== ALL PROFILE & ANALYTICS VERIFICATIONS SUCCEEDED ===")

    finally:
        if ws:
            try:
                ws.close()
            except Exception:
                pass
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    run_tests()
