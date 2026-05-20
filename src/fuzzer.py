import requests
import pandas as pd
import time
from bs4 import BeautifulSoup

# DVWA configuration
BASE_URL = "http://192.168.56.101/dvwa"
LOGIN_URL = f"{BASE_URL}/login.php"
SQLI_URL = f"{BASE_URL}/vulnerabilities/sqli/"
XSS_URL = f"{BASE_URL}/vulnerabilities/xss_r/"

CREDENTIALS = {
    "username": "admin",
    "password": "password",
    "Login": "Login"
}

with open("payloads/sqli_payloads.txt", "r", encoding="utf-8", errors="ignore") as f:
    SQLI_PAYLOADS = [line.strip() for line in f.readlines() if line.strip()]


with open("payloads/xss_payloads.txt", "r", encoding="utf-8", errors="ignore") as f:
    XSS_PAYLOADS = [line.strip() for line in f.readlines() if line.strip()]

# A set of benign payloads for control testing. common inputs, and typical search terms
BENIGN_PAYLOADS = [
    # Common names
    "john", "jane", "bob", "alice", "admin",
    # Common words
    "hello", "world", "test", "search", "query",
    # Numbers
    "1", "2", "3", "42", "100",
    # Email-like
    "user@email.com", "test@test.com",
    # Normal search terms
    "laptop", "phone", "shoes", "book", "music",
    # Common inputs
    "password", "username", "login", "home", "help",
    # Dates
    "2024", "01/01/2023", "january",
    # URLs (benign)
    "www.google.com", "http://example.com",
    # Misc
    "hello world", "foo", "bar", "input", "data"
]

def get_session():
    """Log into DVWA and return authenticated session."""
    session = requests.Session()
    
    # Get CSRF token from login page
    response = session.get(LOGIN_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    token = soup.find("input", {"name": "user_token"})
    
    if token:
        CREDENTIALS["user_token"] = token["value"]

    login_data = {**CREDENTIALS, "user_token": token["value"]}
    session.post(LOGIN_URL, data=CREDENTIALS)

    print("[+] Logged into DVWA")
    sec_page = session.get(f"{BASE_URL}/security.php")
    sec_soup = BeautifulSoup(sec_page.text, "html.parser")
    sec_token = sec_soup.find("input", {"name": "user_token"})
    if sec_token:
        sec_data = {
            "security": "low",
            "seclev_submit": "Submit",
            "user_token": sec_token["value"]
        }
        session.post(f"{BASE_URL}/security.php", data=sec_data)
        print("[+] Set security level to low")
    return session


def detect_sqli(response_text):
    """Check if response indicates SQL injection success."""
    indicators = [
        "first name:", "surname:" 
    ]
    response_lower = response_text.lower()
    if response_lower.count("first name:") < 2:
        return False
    else:
        return any(indicator in response_lower for indicator in indicators)

def detect_xss(response_text, payload):
    """Check if payload is reflected in response."""
    if payload in response_text and ("<" in payload):
        return True
    return False

def fuzz_sqli(session, payloads, label_override=None):
    """Fuzz the SQLi endpoint and return results."""
    results = []
    for payload in payloads:
        try:
            # Get fresh CSRF token before each request
            page = session.get(SQLI_URL)
            soup = BeautifulSoup(page.text, "html.parser")
            token = soup.find("input", {"name": "user_token"})
            params = {"id": payload, "Submit": "Submit"}
            if token:
                params["user_token"] = token["value"]
            response = session.get(SQLI_URL, params=params)
            triggered = detect_sqli(response.text)
            label = label_override if label_override is not None else int(triggered)
            results.append({
                "payload": payload,
                "payload_length": len(payload),
                "payload_type": "sqli",
                "response_code": response.status_code,
                "response_length": len(response.text),
                "triggered": label
            })
            print(f"[SQLi] Payload: {payload[:30]:<30} | Triggered: {bool(label)}")
            time.sleep(0.1)
        except Exception as e:
            print(f"[!] Error with payload {payload}: {e}")
    return results

def fuzz_xss(session, payloads, label_override=None):
    """Fuzz the XSS endpoint and return results."""
    results = []
    for payload in payloads:
        try:
            # Get fresh CSRF token before each request
            page = session.get(XSS_URL)
            soup = BeautifulSoup(page.text, "html.parser")
            token = soup.find("input", {"name": "user_token"})
            params = {"name": payload, "Submit": "Submit"}
            if token:
                params["user_token"] = token["value"]
            response = session.get(XSS_URL, params=params)
            triggered = detect_xss(response.text, payload)
            label = label_override if label_override is not None else int(triggered)
            results.append({
                "payload": payload,
                "payload_length": len(payload),
                "payload_type": "xss",
                "response_code": response.status_code,
                "response_length": len(response.text),
                "triggered": label
            })
            print(f"[XSS]  Payload: {payload[:30]:<30} | Triggered: {bool(label)}")
            time.sleep(0.1)
        except Exception as e:
            print(f"[!] Error with payload {payload}: {e}")
    return results

def run_fuzzer():
    session = get_session()
    all_results = []

    print("\n[*] Fuzzing SQL Injection endpoint...")
    all_results += fuzz_sqli(session, SQLI_PAYLOADS)
    all_results += fuzz_sqli(session, BENIGN_PAYLOADS, label_override=0)

    print("\n[*] Fuzzing XSS endpoint...")
    all_results += fuzz_xss(session, XSS_PAYLOADS)
    all_results += fuzz_xss(session, BENIGN_PAYLOADS, label_override=0)

    # Save to CSV
    df = pd.DataFrame(all_results)
    df.to_csv("data/fuzzing_results.csv", index=False)
    print(f"\n[+] Done. {len(df)} results saved to data/fuzzing_results.csv")
    print(df["triggered"].value_counts())

if __name__ == "__main__":
    run_fuzzer()