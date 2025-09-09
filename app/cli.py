from __future__ import annotations
from typing import Any
import argparse
import json
from typing import Dict, List

from app.agents.types import DraftRequest, Recipient
from app.mail import workflow


def _parse_context(ctx_arg: str | None) -> Dict[str, Any]:
    if not ctx_arg:
        return {}
    try:
        return json.loads(ctx_arg)
    except json.JSONDecodeError as e:
        raise SystemExit(f"--context must be valid JSON: {e}")


def cmd_preview(args: argparse.Namespace) -> int:
    req = DraftRequest(
        recipient=Recipient(email=args.to, name=args.name or args.to),
        purpose=args.purpose,
        brand_id=args.brand,
        context=_parse_context(args.context),
    )
    data: Dict[str, Any] = workflow.preview(req)
    print(json.dumps(data, indent=2))
    return 0


def cmd_deliver(args: argparse.Namespace) -> int:
    req = DraftRequest(
        recipient=Recipient(email=args.to, name=args.name or args.to),
        purpose=args.purpose,
        brand_id=args.brand,
        context=_parse_context(args.context),
    )
    data: Dict[str, Any] = workflow.deliver(req)
    print(json.dumps(data, indent=2))
    return 0


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="mail-agent")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--to", required=True, help="Recipient email")
        sp.add_argument("--name", help="Recipient name")
        sp.add_argument("--purpose", required=True, help="Mail purpose (e.g., welcome)")
        sp.add_argument("--brand", default="default", help="Brand id (default: default)")
        sp.add_argument(
            "--context",
            help='JSON string for template vars (e.g. {"cta_text":"Visit","cta_url":"..."})',
        )

    sp_prev = sub.add_parser("preview", help="Render email & show planned action")
    add_common(sp_prev)
    sp_prev.set_defaults(func=cmd_preview)

    sp_send = sub.add_parser("deliver", help="Draft or send email (per settings)")
    add_common(sp_send)
    sp_send.set_defaults(func=cmd_deliver)

    args = p.parse_args(argv)
    return int(bool(args.func(args)))


if __name__ == "__main__":
    raise SystemExit(main())
