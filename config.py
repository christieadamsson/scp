"""Central configuration. Paths are relative to this project folder."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "instances" / "scp42.txt"
OUTPUT_FILE = BASE_DIR / "solution42.txt"
TIME_LIMIT = 30
K_MAX = 5
SEED = 42
