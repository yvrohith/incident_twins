"""Build a metadata-free source ZIP from the reviewed public manifest.

No Git operation, scientific execution or network request is performed.
"""
import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo, is_zipfile

ROOT = Path(__file__).resolve().parent


def safe_name(name):
    path = PurePosixPath(name)
    return (not path.is_absolute() and ".." not in path.parts and "\\" not in name
            and not any(part in {".git", ".DS_Store", "__MACOSX", "author_records"}
                        or part.startswith("._") for part in path.parts))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path("dist/Incident_Twins_Source.zip"))
    args = parser.parse_args()
    manifest_data = (ROOT / "PUBLIC_MANIFEST.json").read_bytes()
    records = json.loads(manifest_data)["files"]
    payloads = {}
    for name, record in records.items():
        path = ROOT / name
        if not safe_name(name) or path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise ValueError(f"Unsafe public path: {name}")
        data = path.read_bytes()
        if len(data) != record["bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
            raise ValueError(f"Public file changed since manifest: {name}")
        if is_zipfile(BytesIO(data)):
            with ZipFile(BytesIO(data)) as nested:
                if nested.testzip() is not None or any(not safe_name(n) for n in nested.namelist()):
                    raise ValueError(f"Nested archive contains invalid or private metadata: {name}")
        payloads[name] = data
    payloads["PUBLIC_MANIFEST.json"] = manifest_data
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation preserves any earlier archive. Fixed archive metadata
    # avoids serializing local paths, Finder state, permissions or timestamps.
    with ZipFile(args.output, "x", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(payloads.items()):
            entry = ZipInfo("Incident_Twins/" + name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)
    print(json.dumps({"archive": str(args.output), "files": len(payloads),
                      "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
                      "metadata_excluded": [".git", ".DS_Store", "__MACOSX", "._*"],
                      "scientific_execution": False}, indent=2))


if __name__ == "__main__":
    main()
