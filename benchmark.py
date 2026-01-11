import requests
import time
import concurrent.futures

URL = "http://127.0.0.1:8000"
TOTAL_REQUESTS = 50

def send_request(i):
    try:
        start = time.time()
        resp = requests.get(URL)
        end = time.time()
        return resp.status_code, end - start
    except:
        return 0, 0

print(f"Benchmarking Rate Limiter with {TOTAL_REQUESTS} concurrent requests...")

status_codes = []
latencies = []

# Send 50 requests at the exact same time
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(send_request, range(TOTAL_REQUESTS)))

for code, latency in results:
    status_codes.append(code)
    latencies.append(latency)

# Generate Report
print("\n--- REPORT ---")
print(f"Total Requests: {TOTAL_REQUESTS}")
print(f"Allowed (200 OK): {status_codes.count(200)}")
print(f"Blocked (429 Too Many Requests): {status_codes.count(429)}")
print(f"Avg Latency: {sum(latencies)/len(latencies):.4f}s")