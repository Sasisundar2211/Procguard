
import requests

def test_options(path, headers=None):
    url = f"http://127.0.0.1:8000{path}"
    print(f"Testing OPTIONS {url}")
    try:
        res = requests.options(url, headers=headers)
        print(f"Status: {res.status_code}")
        print(f"Headers: {res.headers}")
        print(f"Body: {res.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with origin
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "X-Correlation-ID"
    }
    test_options("/audit-logs", headers=headers)
    test_options("/audit/filter-events", headers=headers)
    test_options("/system/health", headers=headers)
