"""
Task 5: API Testing and Validation using Postman/Curl
=========================================================
Automated test suite for the Task 4 Flask Digit Classification API,
mirroring every request in postman_collection.json (positive/functional
tests and negative/error-handling tests). Each test sends a real HTTP
request to the running API, validates the status code and JSON response
structure, and prints a clear PASS/FAIL line - producing the same kind of
pass/fail report a Postman Collection Runner (or `newman run`) would.

Run the API first (`python app.py`), then run this script:
    python test_api_validation.py
"""

import json
import sys
import requests
from sklearn.datasets import load_digits

BASE_URL = "http://127.0.0.1:5000"

results = []


def record(name, passed, detail=""):
    results.append({"name": name, "passed": passed, "detail": detail})
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}" + (f"  -  {detail}" if detail else ""))


def check(name, condition, detail=""):
    record(name, bool(condition), detail)


SAMPLE_ZERO = [
    0, 0, 5, 13, 9, 1, 0, 0,
    0, 0, 13, 15, 10, 15, 5, 0,
    0, 3, 15, 2, 0, 11, 8, 0,
    0, 4, 12, 0, 0, 8, 8, 0,
    0, 5, 8, 0, 0, 9, 8, 0,
    0, 4, 11, 0, 1, 12, 7, 0,
    0, 2, 14, 5, 10, 12, 0, 0,
    0, 0, 6, 13, 10, 0, 0, 0,
]


def get_real_digit(digit):
    d = load_digits()
    idx = list(d.target).index(digit)
    return d.images[idx].flatten().tolist()


print("=" * 70)
print("SECTION 1: Positive (Functional) Tests")
print("=" * 70)

# --- GET / ---
r = requests.get(f"{BASE_URL}/")
check("GET / returns 200", r.status_code == 200, f"status={r.status_code}")
body = r.json()
check("GET / response has 'name' and 'endpoints'",
      "name" in body and "endpoints" in body, json.dumps(body)[:80] + "...")

# --- GET /health ---
r = requests.get(f"{BASE_URL}/health")
check("GET /health returns 200", r.status_code == 200, f"status={r.status_code}")
check("GET /health reports model_loaded=true",
      r.json().get("model_loaded") is True, json.dumps(r.json()))

# --- POST /predict (valid) ---
r = requests.post(f"{BASE_URL}/predict", json={"image": SAMPLE_ZERO})
check("POST /predict (valid image) returns 200", r.status_code == 200, f"status={r.status_code}")
body = r.json()
check("POST /predict response has predicted_digit/confidence/probabilities",
      all(k in body for k in ("predicted_digit", "confidence", "probabilities")))
check("POST /predict correctly predicts digit 0",
      body.get("predicted_digit") == 0, f"predicted={body.get('predicted_digit')}, confidence={body.get('confidence')}")

# --- POST /predict/batch (valid, real digits 3, 7, 8) ---
images = [get_real_digit(3), get_real_digit(7), get_real_digit(8)]
r = requests.post(f"{BASE_URL}/predict/batch", json={"images": images})
check("POST /predict/batch (valid) returns 200", r.status_code == 200, f"status={r.status_code}")
body = r.json()
check("POST /predict/batch returns count == 3", body.get("count") == 3, json.dumps(body.get("count")))
preds = [item["predicted_digit"] for item in body.get("results", [])]
check("POST /predict/batch correctly predicts [3, 7, 8]", preds == [3, 7, 8], f"got {preds}")

print()
print("=" * 70)
print("SECTION 2: Negative Tests (Error Handling)")
print("=" * 70)

# --- Missing 'image' field ---
r = requests.post(f"{BASE_URL}/predict", json={})
check("POST /predict (missing image) returns 400", r.status_code == 400, f"status={r.status_code}")
check("POST /predict (missing image) response has 'error'", "error" in r.json(), json.dumps(r.json()))

# --- Wrong-size image array ---
r = requests.post(f"{BASE_URL}/predict", json={"image": [1, 2, 3]})
check("POST /predict (wrong size) returns 400", r.status_code == 400, f"status={r.status_code}")

# --- Invalid JSON body ---
r = requests.post(f"{BASE_URL}/predict", data="not-json", headers={"Content-Type": "application/json"})
check("POST /predict (invalid JSON) returns 400", r.status_code == 400, f"status={r.status_code}")

# --- Out-of-range pixel values ---
bad_pixels = [999] * 64
r = requests.post(f"{BASE_URL}/predict", json={"image": bad_pixels})
check("POST /predict (out-of-range pixels) returns 400", r.status_code == 400, f"status={r.status_code}")

# --- Empty batch list ---
r = requests.post(f"{BASE_URL}/predict/batch", json={"images": []})
check("POST /predict/batch (empty list) returns 400", r.status_code == 400, f"status={r.status_code}")

# --- Batch with one bad image among good ones (per-item isolation) ---
r = requests.post(f"{BASE_URL}/predict/batch", json={"images": [SAMPLE_ZERO, [1, 2, 3]]})
body = r.json()
check("POST /predict/batch (mixed valid/invalid) still returns 200", r.status_code == 200, f"status={r.status_code}")
check("POST /predict/batch isolates the bad image's error",
      "error" in body["results"][1] and "predicted_digit" in body["results"][0],
      json.dumps(body))

# --- Unknown endpoint ---
r = requests.get(f"{BASE_URL}/nonexistent")
check("GET /nonexistent returns 404", r.status_code == 404, f"status={r.status_code}")

# --- Wrong HTTP method ---
r = requests.get(f"{BASE_URL}/predict")
check("GET /predict (wrong method) returns 405", r.status_code == 405, f"status={r.status_code}")

# ------------------------------------------------------------------
print()
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)
total = len(results)
passed = sum(1 for r in results if r["passed"])
failed = total - passed
print(f"Total tests : {total}")
print(f"Passed      : {passed}")
print(f"Failed      : {failed}")
print(f"Pass rate   : {passed/total*100:.1f}%")

with open("test_results.json", "w") as f:
    json.dump({"total": total, "passed": passed, "failed": failed, "results": results}, f, indent=2)

if failed > 0:
    sys.exit(1)
