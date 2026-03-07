import requests
import logging
from datetime import datetime

BASE_URL = "http://localhost:5000"

# ======================
# Logging Setup
# ======================
logging.basicConfig(
    filename="test_results.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def log_success(message):
    print(f"✅ {message}")
    logging.info(message)


def log_failure(message):
    print(f"❌ {message}")
    logging.error(message)
    raise AssertionError(message)


def log_response(method, endpoint, response):
    logging.info(
        "%s %s | Status: %s | Response: %s",
        method,
        endpoint,
        response.status_code,
        response.text
    )


# ======================
# Tests
# ======================

def test_health():
    endpoint = "/health"
    r = requests.get(f"{BASE_URL}{endpoint}")
    log_response("GET", endpoint, r)

    if r.status_code == 200:
        log_success("Health check passed")
    else:
        log_failure("Health check failed")


def test_get_features():
    endpoint = "/features"
    r = requests.get(f"{BASE_URL}{endpoint}")
    log_response("GET", endpoint, r)

    if r.status_code == 200 and isinstance(r.json(), list):
        log_success("Features fetched successfully")
    else:
        log_failure("Failed to fetch features")


def test_get_regions():
    endpoint = "/regions"
    r = requests.get(f"{BASE_URL}{endpoint}")
    log_response("GET", endpoint, r)

    if r.status_code == 200 and isinstance(r.json(), list):
        log_success("Regions fetched successfully")
    else:
        log_failure("Failed to fetch regions")


def test_create_snake():
    endpoint = "/snakes"
    payload = {
        "common_name": "Test Cobra",
        "scientific_name": "Naja testus",
        "venom_level": "high",
        "description": "Created during automated testing"
    }

    r = requests.post(f"{BASE_URL}{endpoint}", json=payload)
    log_response("POST", endpoint, r)

    if r.status_code == 201 and "snake_id" in r.json():
        snake_id = r.json()["snake_id"]
        log_success(f"Snake created (ID={snake_id})")
        return snake_id
    else:
        log_failure("Failed to create snake")


def test_get_snake(snake_id):
    endpoint = f"/snakes/{snake_id}"
    r = requests.get(f"{BASE_URL}{endpoint}")
    log_response("GET", endpoint, r)

    if r.status_code == 200:
        log_success("Single snake fetched successfully")
    else:
        log_failure("Failed to fetch snake by ID")


def test_update_snake(snake_id):
    endpoint = f"/snakes/{snake_id}"
    payload = {
        "common_name": "Updated Test Cobra",
        "scientific_name": "Naja updatedus",
        "venom_level": "high",
        "description": "Updated during testing"
    }

    r = requests.put(f"{BASE_URL}{endpoint}", json=payload)
    log_response("PUT", endpoint, r)

    if r.status_code == 200:
        log_success("Snake updated successfully")
    else:
        log_failure("Failed to update snake")


def test_get_snakes():
    endpoint = "/snakes"
    r = requests.get(f"{BASE_URL}{endpoint}")
    log_response("GET", endpoint, r)

    if r.status_code == 200 and isinstance(r.json(), list):
        log_success("All snakes fetched successfully")
    else:
        log_failure("Failed to fetch snakes")


def test_create_user():
    endpoint = "/users"
    payload = {
        "username": "test_user_1",
        "password_hash": "hashed_password_example"
    }

    r = requests.post(f"{BASE_URL}{endpoint}", json=payload)
    log_response("POST", endpoint, r)

    if r.status_code in (200, 201):
        log_success("User creation handled correctly")
    else:
        log_failure("User creation failed")


def test_create_attempt(snake_id):
    endpoint = "/attempts"
    payload = {
        "user_id": 1,
        "snake_id": snake_id,
        "correct": True
    }

    r = requests.post(f"{BASE_URL}{endpoint}", json=payload)
    log_response("POST", endpoint, r)

    if r.status_code in (200, 201):
        log_success("Attempt logged successfully")
    else:
        log_failure("Failed to log attempt")


def test_get_attempts():
    endpoint = "/attempts/1"
    r = requests.get(f"{BASE_URL}{endpoint}")
    log_response("GET", endpoint, r)

    if r.status_code == 200 and isinstance(r.json(), list):
        log_success("Attempts fetched successfully")
    else:
        log_failure("Failed to fetch attempts")


def test_delete_snake(snake_id):
    endpoint = f"/snakes/{snake_id}"
    r = requests.delete(f"{BASE_URL}{endpoint}")
    log_response("DELETE", endpoint, r)

    if r.status_code == 200:
        log_success("Snake deleted successfully")
    else:
        log_failure("Failed to delete snake")


# ======================
# Run Tests
# ======================

if __name__ == "__main__":
    print("🚀 Running integration tests...\n")
    logging.info("==== TEST RUN STARTED ====")

    test_health()
    test_get_features()
    test_get_regions()
    test_get_snakes()

    snake_id = test_create_snake()
    test_get_snake(snake_id)
    test_update_snake(snake_id)

    test_create_user()
    test_create_attempt(snake_id)
    test_get_attempts()

    test_delete_snake(snake_id)

    logging.info("==== TEST RUN COMPLETED SUCCESSFULLY ====")
    print("\n🎉 All tests completed successfully")
