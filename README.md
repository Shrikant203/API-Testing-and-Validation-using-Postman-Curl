# API Testing Report — Digit Classification API

## Scope :

This report documents the testing and validation of the Task 4 Flask REST API (Digit Classification API) using a Postman Collection and equivalent curl commands, covering both positive (functional) tests and negative (error-handling) tests for every endpoint.

## Test Environment :

API under test: app.py (Task 4), served at http://127.0.0.1:5000
Model: cnn_digits_model.pkl (Task 1 from-scratch NumPy CNN, 97.04% test accuracy)
Tools used: Postman (collection provided as postman_collection.json), curl (curl_commands.sh), and an automated Python test runner (test_api_validation.py) that mirrors the same requests and asserts on status codes and response structure

## Test Cases and Results :

### Positive (Functional) Tests

####	Test | Method & Endpoint	| Expected	| Result

1	| API information	| GET /	| 200, JSON with name, endpoints	| PASS

2	| Health check	| GET /health	| 200, model_loaded: true	| PASS

3	| Valid single prediction	POST /predict	| 200, correct digit (0) predicted at 99.98% confidence	| PASS

4	| Valid batch prediction	POST /predict/batch	| 200, all 3 real digits (3, 7, 8) predicted correctly	| PASS

### Negative Tests (Error Handling)

####	Test	| Method & Endpoint	| Expected	| Result

5	| Missing image field	| POST /predict	| 400, structured error JSON	| PASS

6	| Wrong-size image array	| POST /predict	| 400, structured error JSON	| PASS

7	| Invalid JSON body	| POST /predict	| 400, structured error JSON	| PASS

8	| Out-of-range pixel values	| POST /predict	| 400, structured error JSON	| PASS

9	| Empty batch list	| POST /predict/batch	| 400, structured error JSON	| PASS

10	| Mixed valid/invalid batch	| POST /predict/batch	| 200, per-item error isolation	| PASS

11	| Unknown endpoint	| GET /nonexistent	| 404, structured error JSON	| PASS

12	| Wrong HTTP method	| GET /predict	| 405, structured error JSON	| PASS

Total: 20 individual assertions across 12 test cases — 20/20 passed (100%). (Some test cases include more than one assertion, e.g. checking both the status code and the response body structure.)

## Sample Response Validation

Request: POST /predict with a valid 8x8 image of a handwritten "0". Response:


{

  "confidence": 0.9998,

  "predicted_digit": 0,

  "probabilities": {"0": 0.9998, "1": 0.0, "2": 0.0, "3": 0.0, "4": 0.0,
                   "5": 0.0001, "6": 0.0, "7": 0.0, "8": 0.0, "9": 0.0}

}

Validated: status code 200, correct predicted_digit, confidence between 0 and 1, probabilities contains all 10 digit classes summing to approximately 1.0.

Request: POST /predict with an empty JSON body {}. Response:

{"error": "Missing 'image' field in request body."}

Validated: status code 400, response is valid JSON, error field present and human-readable (no raw stack trace leaked to the client).

## Observations :

Every endpoint returns the correct HTTP status code for both valid and invalid input, and every response body is valid JSON in every case tested — including the negative/error cases, which is not guaranteed by default in many APIs (some frameworks return HTML error pages on unhandled errors).
The batch endpoint correctly isolates a single malformed image's error without failing the other, valid images in the same request — verified directly by test case 10 (mixed valid/invalid batch).
No test produced a 500 Internal Server Error, meaning all anticipated failure modes are caught by explicit validation rather than falling through to the generic exception handler.
Response times for single predictions were consistently fast (well under 100ms), since the model is loaded once at API startup rather than per request.

Conclusion :

All 20 assertions across 12 positive and negative test cases passed (100% pass rate). The API correctly handles valid prediction requests, correctly rejects and reports every malformed request tested, and never leaks an unhandled server error to the client.
