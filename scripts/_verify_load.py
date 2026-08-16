"""One-off script: verify the FastAPI app loads and GitHub routes are mounted."""
import sys

sys.path.insert(0, ".")

from main import app  # noqa: E402


def paths_of(router, prefix=""):
    result = []
    for route in router.routes:
        if hasattr(route, "path"):
            result.append(prefix + route.path)
        elif hasattr(route, "routes"):
            result.extend(paths_of(route, prefix + getattr(route, "prefix", "")))
    return result


all_paths = paths_of(app)
gh = sorted(p for p in all_paths if "github" in p)
print("App loads OK; GitHub routes mounted:")
for p in gh:
    print(" ", p)
