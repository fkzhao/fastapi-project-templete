import sys
from pathlib import Path
from dotenv import load_dotenv


project_root = Path(__file__).resolve().parent.parent
print("=============================")
print(f"Project Root: {project_root}")
print("=============================")

# Load .env file before running tests
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✓ Loaded environment variables from {env_file}")
else:
    print(f"⚠ Warning: .env file not found at {env_file}")

# Allow both `import src.` and `import utils...` style imports during tests.
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
