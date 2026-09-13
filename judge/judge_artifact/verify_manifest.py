"""Verify packaged bytes against the local manifest; this does not authenticate its issuer."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'file_manifest.json').read_bytes())
errors = []
actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
expected = {r['path'] for r in manifest['files']} | {'file_manifest.json'}
if actual != expected:
    errors.append({'file_set_mismatch': {'extra': sorted(actual-expected), 'missing': sorted(expected-actual)}})
for row in manifest['files']:
    p = root / row['path']
    if p.is_symlink() or not p.is_file():
        errors.append({'path': row['path'], 'error': 'missing or symlink'})
    elif hashlib.sha256(p.read_bytes()).hexdigest() != row['sha256'] or p.stat().st_size != row['bytes']:
        errors.append({'path': row['path'], 'error': 'bytes differ'})
print(json.dumps({'files_checked': len(manifest['files']), 'errors': errors,
                  'issuer_authenticated': False}, sort_keys=True))
raise SystemExit(1 if errors else 0)
