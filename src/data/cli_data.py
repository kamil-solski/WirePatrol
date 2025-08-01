#!/usr/bin/env python3
import time
from datetime import datetime
from utils.paths import get_paths, PROJECT_ROOT
from data import bruteforce, dos_flood
import argparse

PENTESTERS = {
    "bruteforce": bruteforce.run,
    "dos_flood": dos_flood.run,
}

def get_timestamped_label_path():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(PROJECT_ROOT / "Data" / "raw" / f"labels_{timestamp}.json")

def main():
    parser = argparse.ArgumentParser(description="Run automated pentesting attacks.")
    parser.add_argument("--label-output", type=str, default=None,
                        help="Path to save the label file with time_epoch markers.")
    parser.add_argument("--config", type=str, default=str(PROJECT_ROOT / "src" / "config.secret.yaml"),  # change to config.yaml with targeting your own website
                        help="Path to the configuration YAML.")
    args = parser.parse_args()

    config = get_paths(args.config)

    # Use timestamped label path if not manually provided
    label_output = args.label_output or get_timestamped_label_path()

    interval = config["attack"]["interval"]
    iterations = config["attack"]["num_iterations"]

    for i in range(iterations):
        print(f"\n>>> Iteration {i + 1} <<<")

        for name, pentest_fn in PENTESTERS.items():
            print(f"[+] Executing: {name}")
            pentest_fn(config, label_output)
            print(f"[+] Done: {name}")
            time.sleep(interval)

    print(f"\nAll attacks finished. Labels saved to: {args.label_output}")

if __name__ == "__main__":
    main()

# Usage:
# 0) sudo docker compose up 2>&1 | tee -a docker.log  # on server project website folder

# 1) run sudo ./capture_attack.sh ALL </path/to/output/dir/on/server on server

# 2) wait 3 seconds

# 3) cd ./src on server (given that you are in WirePatrol main project folder)

# 4) run PYTHONPATH=. python data/cli_data.py on local computer 

# 5) after end of cli_data.py, 

# 6) wait 3 seconds

# 7) press Ctrl-C for capture_attack.sh

# 8) Ctrl-C on server (if running in foreground) and sudo docker compose down