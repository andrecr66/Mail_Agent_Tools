from __future__ import annotations
from typing import Any, Dict, List
import argparse
import json

from app.agents.types import DraftRequest, Recipient
from app.mail import workflow


def _parse_context(ctx_arg: str | None) -> Dict[str, Any]:
    # Ensure we always return a Dict[str, Any] (never bare Any)
    if not ctx_arg:
        return {}
    obj = json.loads(ctx_arg)
    if not isinstance(obj, dict):
        raise SystemExit("--context must be a JSON object")
    # Coerce keys to str so the type is Dict[str, Any]
    return {str(k): v for k, v in obj.items()}


def cmd_preview(args: argparse.Namespace) -> Dict[str, Any]:
    req = DraftRequest(
        recipient=Recipient(email=args.to, name=args.name or args.to),
        purpose=args.purpose,
        brand_id=args.brand,
        context=_parse_context(args.context),
    )
    return workflow.preview(req)


def cmd_deliver(args: argparse.Namespace) -> Dict[str, Any]:
    req = DraftRequest(
        recipient=Recipient(email=args.to, name=args.name or args.to),
        purpose=args.purpose,
        brand_id=args.brand,
        context=_parse_context(args.context),
    )
    return workflow.deliver(req)


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
            help='JSON for template vars (e.g. {"cta_text":"Visit","cta_url":"..."})',
        )

    sp_prev = sub.add_parser("preview", help="Render email & show planned action")
    add_common(sp_prev)
    sp_prev.set_defaults(func=cmd_preview)

    sp_send = sub.add_parser("deliver", help="Draft or send email (per settings)")
    add_common(sp_send)
    sp_send.set_defaults(func=cmd_deliver)

    args = p.parse_args(argv)
    result: Dict[str, Any] = args.func(args)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
