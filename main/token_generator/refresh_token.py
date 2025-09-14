# refresh_token.py
import requests
import time
import threading

CLIENT_ID = "ec635afc-faa4-4fb9-ab67-426889896c17"
CLIENT_SECRET = "Je3izWI7LlrHC9wDiZlU2Sqqr1Mnma4YgPliwdfb"

access_token = None
_token_lock = threading.Lock()  # To make access thread-safe

def get_access_token():
    global access_token
    url = "https://api.prokerala.com/token"
    payload = f"grant_type=client_credentials&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                with _token_lock:
                    access_token = token
                print(f"New token generated at {time.strftime('%Y-%m-%d %H:%M:%S')}: {access_token}")
            else:
                print("Error: access_token not found in response")
        else:
            print(f"Failed to get token: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error while fetching token: {e}")

def start_token_refresher():
    # Fetch initial token before starting background refresher
    get_access_token()

    def refresh_loop():
        while True:
            time.sleep(59 * 60)  # wait first, then refresh
            get_access_token()

    thread = threading.Thread(target=refresh_loop, daemon=True)
    thread.start()

def get_current_token():
    """Return the latest token safely"""
    with _token_lock:
        return access_token
