#!/bin/bash
# Task 5: API Testing and Validation using curl
# ==================================================
# Raw curl commands corresponding to every request in postman_collection.json.
# Run the API first (`python app.py`), then run this script:
#     bash curl_commands.sh

BASE_URL="http://127.0.0.1:5000"

echo "=== SECTION 1: Positive Tests ==="

echo -e "\n--- GET / ---"
curl -s -w "\nHTTP Status: %{http_code}\n" "$BASE_URL/"

echo -e "\n--- GET /health ---"
curl -s -w "\nHTTP Status: %{http_code}\n" "$BASE_URL/health"

echo -e "\n--- POST /predict (valid image, digit 0) ---"
curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$BASE_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{"image": [0,0,5,13,9,1,0,0, 0,0,13,15,10,15,5,0, 0,3,15,2,0,11,8,0, 0,4,12,0,0,8,8,0, 0,5,8,0,0,9,8,0, 0,4,11,0,1,12,7,0, 0,2,14,5,10,12,0,0, 0,0,6,13,10,0,0,0]}'

echo -e "\n--- POST /predict/batch (valid batch) ---"
curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$BASE_URL/predict/batch" \
  -H "Content-Type: application/json" \
  -d '{"images": [[0,0,5,13,9,1,0,0,0,0,13,15,10,15,5,0,0,3,15,2,0,11,8,0,0,4,12,0,0,8,8,0,0,5,8,0,0,9,8,0,0,4,11,0,1,12,7,0,0,2,14,5,10,12,0,0,0,0,6,13,10,0,0,0]]}'

echo -e "\n\n=== SECTION 2: Negative Tests (Error Handling) ==="

echo -e "\n--- POST /predict (missing 'image' field -> expect 400) ---"
curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$BASE_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{}'

echo -e "\n--- POST /predict (wrong-size array -> expect 400) ---"
curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$BASE_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{"image": [1, 2, 3]}'

echo -e "\n--- POST /predict (invalid JSON body -> expect 400) ---"
curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$BASE_URL/predict" \
  -H "Content-Type: application/json" \
  -d 'not-json'

echo -e "\n--- POST /predict/batch (empty list -> expect 400) ---"
curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$BASE_URL/predict/batch" \
  -H "Content-Type: application/json" \
  -d '{"images": []}'

echo -e "\n--- GET /nonexistent (unknown endpoint -> expect 404) ---"
curl -s -w "\nHTTP Status: %{http_code}\n" "$BASE_URL/nonexistent"

echo -e "\n--- GET /predict (wrong HTTP method -> expect 405) ---"
curl -s -w "\nHTTP Status: %{http_code}\n" "$BASE_URL/predict"

echo -e "\n"
