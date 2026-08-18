from __future__ import annotations

import ast
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

with (ROOT / 'config' / 'capabilities.yaml').open(encoding='utf-8') as handle:
    data = yaml.safe_load(handle) or {}
capabilities = data.get('capabilities', [])
ids = [item.get('id') for item in capabilities if isinstance(item, dict)]
assert len(ids) == len(set(ids)), 'duplicate capability IDs'
assert len(ids) >= 20, f'capability registry unexpectedly small: {len(ids)}'

for required in [
    ROOT / 'vendor' / 'source-sets' / 'first',
    ROOT / 'vendor' / 'source-sets' / 'second',
    ROOT / 'docs' / 'intelligence-fabric' / 'FULL-CAPABILITY-DIRECTIVE.txt',
    ROOT / 'docs' / 'intelligence-fabric' / 'UPLOAD-PRESERVATION-MANIFEST.md',
    ROOT / 'david_fabric' / 'services' / 'execution.py',
    ROOT / 'david_fabric' / 'services' / 'verification.py',
]:
    assert required.exists(), f'missing required integration path: {required}'

for py_file in [
    ROOT / 'david_fabric' / 'api' / 'router.py',
    ROOT / 'david_fabric' / 'core' / 'models.py',
    ROOT / 'david_fabric' / 'services' / 'execution.py',
    ROOT / 'david_fabric' / 'services' / 'verification.py',
    ROOT / 'david_fabric' / 'services' / 'registry.py',
]:
    ast.parse(py_file.read_text(encoding='utf-8'), filename=str(py_file))

for path in ROOT.rglob('*'):
    if any(part in {'__pycache__', '.pytest_cache'} for part in path.parts):
        raise AssertionError(f'generated cache is present: {path}')

print(f'capabilities={len(ids)}')
print(f'first_vendor_bytes={sum(p.stat().st_size for p in (ROOT / "vendor" / "source-sets" / "first").rglob("*") if p.is_file())}')
print(f'second_vendor_bytes={sum(p.stat().st_size for p in (ROOT / "vendor" / "source-sets" / "second").rglob("*") if p.is_file())}')
print('verification=passed')
