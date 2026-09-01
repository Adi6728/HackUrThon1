import os
from pathlib import Path

def load_env():
    """
    Loads key-value pairs from .env into os.environ if not already set.
    """
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'").strip('"')
                if key and key not in os.environ:
                    os.environ[key] = val

# Auto-load on import
load_env()

def get_groq_api_key() -> str:
    load_env()
    return os.getenv("GROQ_API_KEY", "")
