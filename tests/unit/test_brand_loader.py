from __future__ import annotations
from pathlib import Path
import json
import pytest
from app.tools.brand_loader import load_brand, BrandNotFound


def write_brand(tmp: Path, brand_id: str, data: dict[str, object]) -> Path:
    d = tmp / "brands" / brand_id
    d.mkdir(parents=True, exist_ok=True)
    p = d / "brand.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_load_brand_defaults_injected(tmp_path: Path) -> None:
    data: dict[str, object] = {"name": "CodeRoad", "primary": "#6B21A8", "secondary": "#000000"}
    write_brand(tmp_path, "default", data)
    cfg = load_brand("default", base_dir=tmp_path / "brands")
    assert cfg.name == "CodeRoad"
    assert cfg.primary == "#6B21A8"
    assert cfg.secondary == "#000000"
    assert cfg.content_width_px == 600  # default applied


def test_missing_brand_raises(tmp_path: Path) -> None:
    with pytest.raises(BrandNotFound):
        load_brand("ghost", base_dir=tmp_path / "brands")


def test_invalid_color_rejected(tmp_path: Path) -> None:
    data: dict[str, object] = {"name": "BadCo", "primary": "purple"}  # not hex
    write_brand(tmp_path, "bad", data)
    with pytest.raises(ValueError):
        load_brand("bad", base_dir=tmp_path / "brands")


def test_logo_scheme_allows_common(tmp_path: Path) -> None:
    schemes = ["http://x", "https://x", "cid:logo", "data:image/png;base64,AAA="]
    for idx, s in enumerate(schemes):
        data: dict[str, object] = {
            "name": "OK",
            "primary": "#000",
            "secondary": "#fff",
            "logo_url": s,
        }
        brand_id = f"ok_{idx}"  # unique id to avoid lru_cache collisions
        write_brand(tmp_path, brand_id, data)
        assert load_brand(brand_id, base_dir=tmp_path / "brands").logo_url == s


def test_logo_scheme_rejects_unknown(tmp_path: Path) -> None:
    data: dict[str, object] = {
        "name": "BadURL",
        "primary": "#000",
        "secondary": "#fff",
        "logo_url": "ftp://x",
    }
    write_brand(tmp_path, "badurl", data)
    with pytest.raises(ValueError):
        load_brand("badurl", base_dir=tmp_path / "brands")
