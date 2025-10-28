import sys
from pathlib import Path


project_root = Path(__file__).resolve().parent.parent

# Allow both `import ..` and `import utils...` style imports during tests.
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
