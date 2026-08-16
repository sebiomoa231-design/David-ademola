from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    'fastapi-backend-template': 85,
    'fastapi-boilerplate': 262,
    'pgvector': 158,
    'supabase-postgres': 884,
}


def source_files(path: Path) -> list[Path]:
    return [candidate for candidate in path.rglob('*') if candidate.is_file() and '.git' not in candidate.parts]


actual_total = 0
for name, expected_count in EXPECTED.items():
    tree = ROOT / name
    if not tree.is_dir():
        raise SystemExit(f'Missing database source tree: {tree}')
    if (tree / '.git').exists():
        raise SystemExit(f'Nested Git metadata must not be copied: {tree / ".git"}')
    files = source_files(tree)
    actual_total += len(files)
    if len(files) != expected_count:
        raise SystemExit(f'{name}: expected {expected_count} files, found {len(files)}')
    print(f'{name}: {len(files)} files verified')

print(f'All {len(EXPECTED)} database source trees verified: {actual_total} source files')
