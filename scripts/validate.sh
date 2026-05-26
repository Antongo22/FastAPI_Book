#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

export DATABASE_URL="${DATABASE_URL:-sqlite://}"

python -m compileall gateway chapter01 chapter02 chapter03 chapter04 chapter05 chapter06 chapter07 chapter08 chapter09 chapter10 chapter11 chapter12 tests
python - <<'PY'
modules = [
    "gateway.app.main",
    "chapter01.app.main",
    "chapter02.app.main",
    "chapter03.app.main",
    "chapter04.app.main",
    "chapter05.app.main",
    "chapter06.app.main",
    "chapter07.app.main",
    "chapter08.app.main",
    "chapter09.app.main",
    "chapter10.app.main",
    "chapter11.app.main",
    "chapter12.app.main",
]
for module in modules:
    __import__(module)
    print(f"import ok: {module}")
PY
pytest -q
