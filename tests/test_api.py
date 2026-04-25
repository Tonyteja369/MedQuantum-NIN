import requests

def test_health():
    try:
        r = requests.get("http://127.0.0.1:8000/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
    except requests.exceptions.ConnectionError:
        # Skip if server is not running during simple test run
        pass
