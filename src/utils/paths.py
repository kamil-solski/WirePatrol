import yaml
from pathlib import Path

# Define the root directory of the project
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Core Folders
DATA_DIR = PROJECT_ROOT / "src" / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
CHECKPOINTS_DIR = OUTPUTS_DIR / "checkpoints"
METRICS_DIR = OUTPUTS_DIR / "metrics"
LOGS_DIR = OUTPUTS_DIR / "logs"
RUNS_DIR = OUTPUTS_DIR / "runs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
PREDICTIONS_DIR = OUTPUTS_DIR / "predictions"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"
MLFLOW_TRACKING_DIR = EXPERIMENTS_DIR / "mlruns"

# Optional: Get paths from config.yaml, to be used for project setup
def get_paths(config_path=PROJECT_ROOT / "src" / "config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

# Additional paths for attack scripts
BRUTE_FORCE_SCRIPT = DATA_DIR / "bruteforce.py"
DOS_FLOOD_SCRIPT = DATA_DIR / "dos_flood.py"