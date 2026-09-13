"""Verify the declared public files using Python's standard library only.

This checks byte integrity, not evidence truth, secret absence or issuer identity.
It ignores local files outside the separately declared public manifest.
"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent

def main():
    manifest = json.loads((ROOT / "PUBLIC_MANIFEST.json").read_text())
    files = manifest["files"]
    errors = []
    for name, record in files.items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts or "\\" in name:
            errors.append({"path": name, "error": "unsafe manifest path"})
            continue
        path = ROOT / name
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(ROOT):
            errors.append({"path": name, "error": "missing file or unsafe link"})
            continue
        data = path.read_bytes()
        if len(data) != record["bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
            errors.append({"path": name, "error": "file differs from public manifest"})
    print(json.dumps({"ok": not errors, "files_checked": len(files), "errors": errors,
                      "issuer_authenticated": False}, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
