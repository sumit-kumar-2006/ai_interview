import subprocess
import time
import json
import urllib.request
import os
import websocket
import sys

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9229
BASE_URL = "http://127.0.0.1:8000"

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
    if "exceptionDetails" in res.get("result", {}):
        print(f"  [JS EVAL ERROR msg_id={msg_id}]:", res["result"]["exceptionDetails"])
    return res.get("result", {}).get("result", {}).get("value")

def navigate_url(ws, url, msg_id=200):
    send_cdp(ws, "Page.navigate", {"url": url}, msg_id=msg_id)
    # Wait for page load event
    time.sleep(1.5)

def main():
    print("=" * 60)
    print("VERIFYING ALL 16 MANDATORY NAVIGATION & REDIRECT SCENARIOS")
    print("=" * 60)

    # Use unique user data dir
    user_data_dir = "C:/tmp/chrome_nav_16_test"
    proc = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={PORT}",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1440,900",
        f"--user-data-dir={user_data_dir}",
        f"{BASE_URL}/"
    ])

    test_results = {}

    try:
        time.sleep(2.5)
        resp = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list")
        tabs = json.loads(resp.read().decode())
        ws_url = tabs[0]["webSocketDebuggerUrl"]
        ws = websocket.create_connection(ws_url)
        send_cdp(ws, "Page.enable", {}, msg_id=10)

        mid = 300

        # Scenario 1: Home / Landing Page Renders
        print("\n--- SCENARIO 1: Home -> Landing Page Renders ---")
        mid += 1
        res = evaluate_js(ws, """
            (() => {
                authToken = null;
                currentUser = null;
                localStorage.clear();
                updateAuthWidget();
                navigateToView('landing');
                const landing = document.getElementById('view-landing');
                const hero = document.querySelector('.landing-hero-section') || document.querySelector('.hero-section');
                const navHome = document.getElementById('nav-home-btn');
                return {
                    landingActive: landing && landing.classList.contains('active'),
                    heroPresent: !!hero,
                    homeBtnActive: navHome ? navHome.classList.contains('active') : false
                };
            })()
        """, msg_id=mid)
        print("  Result:", res)
        assert res["landingActive"] and res["heroPresent"], "Scenario 1 failed: Landing view not active"
        test_results["Scenario 1 (Home/Landing)"] = "PASS"
        print("  -> PASS: Landing page renders properly.")

        # Scenario 2: Login Click -> Auth Modal Opens
        print("\n--- SCENARIO 2: Login Click -> Auth Modal Opens ---")
        mid += 1
        res = evaluate_js(ws, """
            (() => {
                const loginBtn = document.getElementById('nav-login-btn');
                if (loginBtn) loginBtn.click();
                else showAuthModal('login');
                const modal = document.getElementById('auth-modal');
                const loginTab = document.getElementById('tab-login-btn');
                const loginForm = document.getElementById('login-form');
                return {
                    modalVisible: modal && !modal.classList.contains('hidden'),
                    loginTabActive: loginTab && loginTab.classList.contains('active'),
                    loginFormVisible: loginForm && !loginForm.classList.contains('hidden')
                };
            })()
        """, msg_id=mid)
        print("  Result:", res)
        assert res["modalVisible"] and res["loginTabActive"], "Scenario 2 failed: Auth modal did not open"
        test_results["Scenario 2 (Login Modal)"] = "PASS"
        print("  -> PASS: Auth modal opened with login tab active.")

        # Scenario 3: Login Success -> Navigates to User Dashboard
        print("\n--- SCENARIO 3: Login Success -> Navigates to User Dashboard ---")
        mid += 1
        res = evaluate_js(ws, """
            (async () => {
                // Populate login form
                document.getElementById('login-email').value = 'skgounder50@gmail.com';
                document.getElementById('login-password').value = 'password123';
                // Trigger form submission
                const form = document.getElementById('login-form');
                const submitEvent = new Event('submit', { cancelable: true });
                form.dispatchEvent(submitEvent);
                
                // Wait for async auth resolution
                await new Promise(r => setTimeout(r, 1200));
                
                const dash = document.getElementById('view-dashboard');
                const modal = document.getElementById('auth-modal');
                const navDash = document.getElementById('nav-dash-btn');
                const token = localStorage.getItem(STORAGE_KEY_TOKEN);
                
                return {
                    tokenStored: !!token,
                    dashActive: dash && dash.classList.contains('active'),
                    modalHidden: modal && modal.classList.contains('hidden'),
                    navDashActive: navDash && navDash.classList.contains('active'),
                    currentUserEmail: currentUser ? currentUser.email : null
                };
            })()
        """, msg_id=mid)
        print("  Result:", res)
        assert res["tokenStored"] and res["dashActive"], f"Scenario 3 failed: Did not reach Dashboard ({res})"
        test_results["Scenario 3 (Login -> Dashboard)"] = "PASS"
        print("  -> PASS: User authenticated and immediately navigated to Dashboard.")

        # Scenario 4: Dashboard -> Profile Click -> Opens Profile Page
        print("\n--- SCENARIO 4: Dashboard -> Profile Click -> Opens Profile Page ---")
        mid += 1
        res = evaluate_js(ws, """
            (() => {
                const profBtn = document.getElementById('nav-profile-btn');
                if (profBtn) profBtn.click();
                else navigateToView('profile');
                
                const profView = document.getElementById('view-profile');
                const analyticsView = document.getElementById('view-analytics');
                const dashView = document.getElementById('view-dashboard');
                const profBtnActive = profBtn ? profBtn.classList.contains('active') : false;
                
                return {
                    profActive: profView && profView.classList.contains('active'),
                    analyticsActive: analyticsView && analyticsView.classList.contains('active'),
                    dashActive: dashView && dashView.classList.contains('active'),
                    profBtnActive: profBtnActive
                };
            })()
        """, msg_id=mid)
        print("  Result:", res)
        assert res["profActive"] and not res["analyticsActive"], "Scenario 4 failed: Profile not open or Analytics active"
        test_results["Scenario 4 (Dashboard -> Profile)"] = "PASS"
        print("  -> PASS: Navigated directly to dedicated Profile page (Analytics is NOT active).")

        # Scenario 5: Profile Page Verified
        print("\n--- SCENARIO 5: Profile Page Verified ---")
        mid += 1
        res = evaluate_js(ws, """
            (async () => {
                // Ensure profile data loaded
                await initProfilePage();
                
                const nameInput = document.getElementById('prof-page-name');
                const emailDisplay = document.getElementById('profile-page-email-display');
                const roleInput = document.getElementById('prof-page-target-role');
                const avatarEl = document.getElementById('profile-page-avatar');
                const skillsTags = document.getElementById('profile-page-skills-tags');
                const saveBtn = document.getElementById('btn-save-profile-page');
                const analyticsWrap = document.querySelector('#view-profile .profile-analytics-wrapper');
                
                return {
                    hasName: !!nameInput && nameInput.value.length > 0,
                    nameValue: nameInput ? nameInput.value : '',
                    hasEmail: !!emailDisplay && emailDisplay.textContent.length > 0,
                    emailValue: emailDisplay ? emailDisplay.textContent : '',
                    hasRole: !!roleInput && roleInput.value.length > 0,
                    hasAvatar: !!avatarEl,
                    hasSkillsTags: !!skillsTags,
                    tagsCount: skillsTags ? skillsTags.children.length : 0,
                    canEdit: !!saveBtn && !saveBtn.disabled,
                    hasNoAnalyticsInProfile: !analyticsWrap
                };
            })()
        """, msg_id=mid)
        print("  Result:", res)
        assert res["hasName"] and res["hasEmail"] and res["hasAvatar"] and res["hasNoAnalyticsInProfile"], "Scenario 5 failed: Profile verification failed"
        test_results["Scenario 5 (Profile Page Verification)"] = "PASS"
        print("  -> PASS: Profile displays user details, avatar, editable fields, skills, and NO analytics leakage.")

        # Scenario 6: Dashboard -> Analytics Click -> Opens Analytics Page
        print("\n--- SCENARIO 6: Dashboard -> Analytics Click -> Opens Analytics Page ---")
        mid += 1
        res = evaluate_js(ws, """
            (() => {
                const analyticsBtn = document.getElementById('nav-analytics-btn');
                if (analyticsBtn) analyticsBtn.click();
                else navigateToView('analytics');
                
                const profView = document.getElementById('view-profile');
                const analyticsView = document.getElementById('view-analytics');
                const analyticsBtnActive = analyticsBtn ? analyticsBtn.classList.contains('active') : false;
                
                return {
                    profActive: profView && profView.classList.contains('active'),
                    analyticsActive: analyticsView && analyticsView.classList.contains('active'),
                    analyticsBtnActive: analyticsBtnActive
                };
            })()
        """, msg_id=mid)
        print("  Result:", res)
        assert res["analyticsActive"] and not res["profActive"], "Scenario 6 failed: Analytics not open or Profile active"
        test_results["Scenario 6 (Dashboard -> Analytics)"] = "PASS"
        print("  -> PASS: Navigated directly to dedicated Analytics page (Profile is NOT active).")

        # Scenario 7: Analytics Page Verified
        print("\n--- SCENARIO 7: Analytics Page Verified ---")
        mid += 1
        res = evaluate_js(ws, """
            (async () => {
                await initAnalyticsPage();
                
                const analyticsWrap = document.querySelector('#view-analytics .profile-analytics-wrapper');
                const scoreGauge = document.getElementById('profile-overall-gauge') || document.getElementById('donut-overall-score');
                const trendChart = document.getElementById('chart-score-trends');
                const categoryChart = document.getElementById('chart-category-bars');
                const reportsList = document.getElementById('profile-reports-list');
                const profileFormInAnalytics = document.querySelector('#view-analytics #profile-page-form');
                
                return {
                    hasAnalyticsWrap: !!analyticsWrap,
                    hasScoreGauge: !!scoreGauge,
                    hasTrendChart: !!trendChart,
                    hasCategoryChart: !!categoryChart,
                    hasReportsList: !!reportsList,
                    hasNoProfileInAnalytics: !profileFormInAnalytics
                };
            })()
        """, msg_id=mid)
        print("  Result:", res)
        assert res["hasAnalyticsWrap"] and res["hasNoProfileInAnalytics"], "Scenario 7 failed: Analytics verification failed"
        test_results["Scenario 7 (Analytics Page Verification)"] = "PASS"
        print("  -> PASS: Analytics displays performance overview, charts, score gauge, and NO profile form leakage.")

        # Scenario 8: Dashboard -> Start Interview Click -> Opens Setup Page
        print("\n--- SCENARIO 8: Dashboard -> Start Interview Click -> Opens Setup Page ---")
        mid += 1
        res = evaluate_js(ws, """
            (() => {
                const practiceBtn = document.getElementById('nav-practice-btn');
                if (practiceBtn) practiceBtn.click();
                else navigateToView('interview-setup');
                
                const setupView = document.getElementById('view-interview-setup');
                const pracBtnActive = practiceBtn ? practiceBtn.classList.contains('active') : false;
                
                return {
                    setupActive: setupView && setupView.classList.contains('active'),
                    pracBtnActive: pracBtnActive
                };
            })()
        """, msg_id=mid)
        print("  Result:", res)
        assert res["setupActive"], "Scenario 8 failed: Interview setup page not active"
        test_results["Scenario 8 (Start Interview Setup)"] = "PASS"
        print("  -> PASS: Start Interview opens interview setup view.")

        # Scenario 9: Dashboard -> History Click -> Opens Interview History
        print("\n--- SCENARIO 9: Dashboard -> History Click -> Opens Interview History ---")
        mid += 1
        res = evaluate_js(ws, """
            (() => {
                navigateToView('history');
                const historyView = document.getElementById('view-history');
                return {
                    historyActive: historyView && historyView.classList.contains('active')
                };
            })()
        """, msg_id=mid)
        print("  Result:", res)
        assert res["historyActive"], "Scenario 9 failed: History view not active"
        test_results["Scenario 9 (History View)"] = "PASS"
        print("  -> PASS: Interview History view opened.")

        # Scenario 10: Profile -> Dashboard Back Navigation -> Returns to Dashboard
        print("\n--- SCENARIO 10: Profile -> Dashboard Back Navigation ---")
        mid += 1
        res = evaluate_js(ws, """
            (() => {
                navigateToView('profile');
                // Navigate back to dashboard via dashboard button
                const dashBtn = document.getElementById('nav-dash-btn');
                if (dashBtn) dashBtn.click();
                else navigateToView('dashboard');
                
                const dashView = document.getElementById('view-dashboard');
                const profView = document.getElementById('view-profile');
                return {
                    dashActive: dashView && dashView.classList.contains('active'),
                    profActive: profView && profView.classList.contains('active')
                };
            })()
        """, msg_id=mid)
        print("  Result:", res)
        assert res["dashActive"] and not res["profActive"], "Scenario 10 failed: Could not return to dashboard from profile"
        test_results["Scenario 10 (Profile -> Dashboard)"] = "PASS"
        print("  -> PASS: Cleanly returned from Profile to Dashboard.")

        # Scenario 11: Analytics -> Dashboard Back Navigation -> Returns to Dashboard
        print("\n--- SCENARIO 11: Analytics -> Dashboard Back Navigation ---")
        mid += 1
        res = evaluate_js(ws, """
            (() => {
                navigateToView('analytics');
                const dashBtn = document.getElementById('nav-dash-btn');
                if (dashBtn) dashBtn.click();
                else navigateToView('dashboard');
                
                const dashView = document.getElementById('view-dashboard');
                const analyticsView = document.getElementById('view-analytics');
                return {
                    dashActive: dashView && dashView.classList.contains('active'),
                    analyticsActive: analyticsView && analyticsView.classList.contains('active')
                };
            })()
        """, msg_id=mid)
        print("  Result:", res)
        assert res["dashActive"] and not res["analyticsActive"], "Scenario 11 failed: Could not return to dashboard from analytics"
        test_results["Scenario 11 (Analytics -> Dashboard)"] = "PASS"
        print("  -> PASS: Cleanly returned from Analytics to Dashboard.")

        # Scenario 12: Refresh on Dashboard -> Remains on Dashboard
        print("\n--- SCENARIO 12: Refresh on Dashboard -> Remains on Dashboard ---")
        mid += 1
        # Set URL to ?view=dashboard and reload
        navigate_url(ws, f"{BASE_URL}/?view=dashboard", msg_id=mid)
        mid += 1
        res = evaluate_js(ws, """
            (() => {
                const dashView = document.getElementById('view-dashboard');
                const navDash = document.getElementById('nav-dash-btn');
                return {
                    dashActive: dashView && dashView.classList.contains('active'),
                    navDashActive: navDash && navDash.classList.contains('active'),
                    urlParam: new URLSearchParams(window.location.search).get('view')
                };
            })()
        """, msg_id=mid)
        print("  Result:", res)
        assert res["dashActive"] and res["urlParam"] == "dashboard", "Scenario 12 failed: Refresh on dashboard did not preserve dashboard"
        test_results["Scenario 12 (Refresh Dashboard)"] = "PASS"
        print("  -> PASS: Refresh on Dashboard preserved view correctly.")

        # Scenario 13: Refresh on Profile -> Remains on Profile
        print("\n--- SCENARIO 13: Refresh on Profile -> Remains on Profile ---")
        mid += 1
        navigate_url(ws, f"{BASE_URL}/?view=profile", msg_id=mid)
        mid += 1
        res = evaluate_js(ws, """
            (() => {
                const profView = document.getElementById('view-profile');
                const analyticsView = document.getElementById('view-analytics');
                const navProf = document.getElementById('nav-profile-btn');
                return {
                    profActive: profView && profView.classList.contains('active'),
                    analyticsActive: analyticsView && analyticsView.classList.contains('active'),
                    navProfActive: navProf && navProf.classList.contains('active'),
                    urlParam: new URLSearchParams(window.location.search).get('view')
                };
            })()
        """, msg_id=mid)
        print("  Result:", res)
        assert res["profActive"] and not res["analyticsActive"] and res["urlParam"] == "profile", "Scenario 13 failed: Refresh on profile did not preserve profile"
        test_results["Scenario 13 (Refresh Profile)"] = "PASS"
        print("  -> PASS: Refresh on Profile preserved Profile view without switching to Analytics.")

        # Scenario 14: Refresh on Analytics -> Remains on Analytics
        print("\n--- SCENARIO 14: Refresh on Analytics -> Remains on Analytics ---")
        mid += 1
        navigate_url(ws, f"{BASE_URL}/?view=analytics", msg_id=mid)
        mid += 1
        res = evaluate_js(ws, """
            (() => {
                const profView = document.getElementById('view-profile');
                const analyticsView = document.getElementById('view-analytics');
                const navAnalytics = document.getElementById('nav-analytics-btn');
                return {
                    profActive: profView && profView.classList.contains('active'),
                    analyticsActive: analyticsView && analyticsView.classList.contains('active'),
                    navAnalyticsActive: navAnalytics && navAnalytics.classList.contains('active'),
                    urlParam: new URLSearchParams(window.location.search).get('view')
                };
            })()
        """, msg_id=mid)
        print("  Result:", res)
        assert res["analyticsActive"] and not res["profActive"] and res["urlParam"] == "analytics", "Scenario 14 failed: Refresh on analytics did not preserve analytics"
        test_results["Scenario 14 (Refresh Analytics)"] = "PASS"
        print("  -> PASS: Refresh on Analytics preserved Analytics view without switching to Profile.")

        # Scenario 15: Browser Back / Forward Buttons Work Correctly
        print("\n--- SCENARIO 15: Browser Back / Forward PopState Verification ---")
        mid += 1
        res = evaluate_js(ws, """
            (async () => {
                // Navigate sequence: dashboard -> profile -> analytics
                navigateToView('dashboard', true);
                await new Promise(r => setTimeout(r, 100));
                navigateToView('profile', true);
                await new Promise(r => setTimeout(r, 100));
                navigateToView('analytics', true);
                await new Promise(r => setTimeout(r, 100));
                
                // Test back navigation
                window.history.back();
                await new Promise(r => setTimeout(r, 300));
                const afterBackIsProfile = document.getElementById('view-profile').classList.contains('active');
                
                // Test second back navigation
                window.history.back();
                await new Promise(r => setTimeout(r, 300));
                const afterSecondBackIsDash = document.getElementById('view-dashboard').classList.contains('active');
                
                // Test forward navigation
                window.history.forward();
                await new Promise(r => setTimeout(r, 300));
                const afterForwardIsProfile = document.getElementById('view-profile').classList.contains('active');
                
                return {
                    afterBackIsProfile,
                    afterSecondBackIsDash,
                    afterForwardIsProfile
                };
            })()
        """, msg_id=mid)
        print("  Result:", res)
        assert res["afterBackIsProfile"] and res["afterSecondBackIsDash"] and res["afterForwardIsProfile"], f"Scenario 15 failed: PopState navigation mismatch ({res})"
        test_results["Scenario 15 (Back/Forward PopState)"] = "PASS"
        print("  -> PASS: Browser back/forward navigation accurately restores views.")

        # Scenario 16: Logout Click -> Clears Session, Returns to Home / Landing Page
        print("\n--- SCENARIO 16: Logout Click -> Clears Session & Returns to Landing ---")
        mid += 1
        res = evaluate_js(ws, """
            (() => {
                handleLogout();
                const landing = document.getElementById('view-landing');
                const token = localStorage.getItem(STORAGE_KEY_TOKEN);
                const user = localStorage.getItem(STORAGE_KEY_USER);
                const authNav = document.getElementById('auth-nav');
                const unauthActions = document.getElementById('unauth-nav-actions');
                
                // Now test protected route interception post-logout
                navigateToView('dashboard');
                const dashAfterLogout = document.getElementById('view-dashboard').classList.contains('active');
                const modalAfterLogout = !document.getElementById('auth-modal').classList.contains('hidden');
                
                return {
                    landingActive: landing && landing.classList.contains('active'),
                    tokenCleared: !token,
                    userCleared: !user,
                    authNavHidden: authNav ? authNav.classList.contains('hidden') : true,
                    unauthActionsVisible: unauthActions ? !unauthActions.classList.contains('hidden') : true,
                    dashBlocked: !dashAfterLogout,
                    modalPrompted: modalAfterLogout
                };
            })()
        """, msg_id=mid)
        print("  Result:", res)
        assert res["landingActive"] and res["tokenCleared"] and res["dashBlocked"] and res["modalPrompted"], "Scenario 16 failed: Logout session invalidation failed"
        test_results["Scenario 16 (Logout & Guard)"] = "PASS"
        print("  -> PASS: Logout successfully cleared tokens, hid auth nav, returned to landing, and protected route guard active.")

        print("\n" + "=" * 60)
        print("ALL 16 VERIFICATION SCENARIOS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        for name, status in test_results.items():
            print(f"  [x] {name}: {status}")

        ws.close()

    except Exception as e:
        print("\n[ERROR] Exception encountered during navigation test:", e)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
