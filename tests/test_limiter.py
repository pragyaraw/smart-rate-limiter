import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_rate_limiting():
    print(f" Testing API at {BASE_URL}...")
    
    
    for i in range(5):
        try:
            response = requests.get(BASE_URL)
            if response.status_code == 200:
                print(f" Request {i+1}: Allowed")
            else:
                print(f" Request {i+1}: Failed with {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(" Error: Could not connect. Is 'uvicorn' running in another terminal?")
            return

    
    print("\n Starting Burst Test...")
    blocked = False
    for i in range(10):
        response = requests.get(BASE_URL)
        if response.status_code == 429:
            print(f"🛡️ System Blocked Request {i+6} (Success!)")
            blocked = True
            break
        print(f" Request {i+6}: Still Allowed...")
    
    if not blocked:
        print(" FAILED: Rate limiter did not trigger.")
    else:
        print(" SUCCESS: Rate limiter is working!")

if __name__ == "__main__":
    test_rate_limiting()