import os
import sys
from pathlib import Path

# Ensure `import app` works when running pytest from the backend folder.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Ensure FastAPI startup doesn't try to connect to external services during unit tests.
os.environ.setdefault("ENV", "test")
os.environ.setdefault("RSS_SKIP_STARTUP", "1")
