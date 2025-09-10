from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape


def _paragraphize(text: str) -> str:
    """Split on blank lines into <p> blocks; convert single newlines to <br/>."""
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    return "".join(f"<p>{p.replace('\n', '<br/>')}</p>" for p in parts) or ""


def jinja_env(templates_root: str | Path = "templates/jinja") -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(templates_root)),
        autoescape=select_autoescape(enabled_extensions=("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["paragraphize"] = _paragraphize
    return env


def render_template(template_path: str, context: Dict[str, Any]) -> str:
    env = jinja_env()
    tpl = env.get_template(template_path)
    return tpl.render(**context)
"""Jinja2 environment helpers.

Provides a small set of helpers for rendering HTML emails using Jinja2,
including a `paragraphize` filter that turns newline-separated text into
HTML paragraphs and <br/> line breaks.
"""
