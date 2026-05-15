"""Normalization logic for raw company records."""

from __future__ import annotations

from typing import Any


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_company_record(raw: dict, source_url: str, retrieved_at: str) -> dict:
    """Map raw government open data fields into normalized schema."""

    return {
        "tax_id": _clean_text(raw.get("統一編號")),
        "name": _clean_text(raw.get("公司名稱")),
        "status": _clean_text(raw.get("公司狀況")),
        "owner": _clean_text(raw.get("代表人姓名")),
        "capital": _clean_text(raw.get("資本總額(元)")),
        "setup_date": _clean_text(raw.get("核准設立日期")),
        "address": _clean_text(raw.get("公司所在地")),
        "business_scope": _clean_text(raw.get("所營事業資料")),
        "source": "gov_open_data",
        "source_url": source_url,
        "retrieved_at": retrieved_at,
    }
