from pathlib import Path
import sys

try:
    from src.app_factory import create_app
except ModuleNotFoundError:  # pragma: no cover - fallback when executed directly
    current_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(current_dir.parent))
    from src.app_factory import create_app


app = create_app()


if __name__ == "__main__":  # pragma: no cover - convenience for local execution
    print("Starting application on http://")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
