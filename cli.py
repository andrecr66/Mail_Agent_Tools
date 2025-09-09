from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path
import sys

from app.tools.brand_loader import load_brand, BrandNotFound

BRANDS_DIR = Path("brands")
DEFAULT_BRAND = {
    "name": "YourCo",
    "logo_url": "https://cdn.example.com/yourco/logo.png",
    "primary": "#2563EB",
    "secondary": "#111827",
    "links": {"website": "https://yourco.com", "support": "https://yourco.com/support"},
    "footer_html": '<p>© YourCo • <a href="https://yourco.com">yourco.com</a></p>',
    "signature_html": "<p>— Team YourCo</p>",
    "legal_address": "123 Example St, City, Country",
}


def cmd_brand_validate(brand_id: str) -> int:
    try:
        cfg = load_brand(brand_id)
        print(json.dumps(cfg.model_dump(), indent=2))
        return 0
    except BrandNotFound as e:
        print(str(e), file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Invalid brand: {e}", file=sys.stderr)
        return 1


def cmd_brand_init(brand_id: str, force: bool) -> int:
    dest = BRANDS_DIR / brand_id
    dest.mkdir(parents=True, exist_ok=True)
    brand_file = dest / "brand.json"
    if brand_file.exists() and not force:
        print(f"{brand_file} exists. Use --force to overwrite.", file=sys.stderr)
        return 3
    brand_file.write_text(json.dumps(DEFAULT_BRAND, indent=2), encoding="utf-8")
    print(f"Created {brand_file}")
    return 0


def run(cmd: list[str]) -> int:
    print("$ " + " ".join(cmd))
    return subprocess.call(cmd)


def cmd_check(run_all: bool, do_tests: bool, do_lint: bool, do_types: bool) -> int:
    if not any([run_all, do_tests, do_lint, do_types]):
        run_all = True
    rc = 0
    if run_all or do_lint:
        rc = run(["ruff", "check", "--fix", "."]) or rc
        rc = run(["ruff", "format", "."]) or rc
    if run_all or do_types:
        rc = run(["mypy", "--strict", "."]) or rc
    if run_all or do_tests:
        rc = run(["pytest", "-q", "--cov=app", "--cov-report=term-missing"]) or rc
    return rc


def main() -> int:
    p = argparse.ArgumentParser(prog="mail-agent")
    sub = p.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("brand-validate", help="Validate a brand and print normalized JSON")
    pv.add_argument("brand_id")

    pi = sub.add_parser("brand-init", help="Create a new brand folder with a starter brand.json")
    pi.add_argument("brand_id")
    pi.add_argument("--force", action="store_true")

    pc = sub.add_parser("check", help="Run developer checks (lint/types/tests)")
    pc.add_argument("--all", action="store_true", help="Run all checks (default)")
    pc.add_argument("--tests", action="store_true", help="Run pytest only")
    pc.add_argument("--lint", action="store_true", help="Run ruff only")
    pc.add_argument("--types", action="store_true", help="Run mypy only")

    args = p.parse_args()
    if args.cmd == "brand-validate":
        return cmd_brand_validate(args.brand_id)
    if args.cmd == "brand-init":
        return cmd_brand_init(args.brand_id, args.force)
    if args.cmd == "check":
        return cmd_check(args.all, args.tests, args.lint, args.types)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
