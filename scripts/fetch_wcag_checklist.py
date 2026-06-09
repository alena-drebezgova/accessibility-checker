#!/usr/bin/env python3
"""Fetch and normalize WCAG checklists from official W3C sources.

The script runs in two explicit stages:
1. Fetch the official WCAG page and store a raw structured extraction.
2. Normalize that raw data into the canonical checklist JSON used by the project.

Default outputs:
- checklists/wcag/raw/wcag_2_1.json
- checklists/wcag/raw/wcag_2_2.json
- checklists/wcag/wcag_2_1.json
- checklists/wcag/wcag_2_2.json
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WCAG21_URL = "https://www.w3.org/TR/WCAG21/"
DEFAULT_WCAG22_URL = "https://www.w3.org/TR/WCAG22/"

DEFAULT_RAW_OUTPUT_21 = ROOT / "checklists/wcag/raw/wcag_2_1.json"
DEFAULT_RAW_OUTPUT_22 = ROOT / "checklists/wcag/raw/wcag_2_2.json"
DEFAULT_NORMALIZED_OUTPUT_21 = ROOT / "checklists/wcag/wcag_2_1.json"
DEFAULT_NORMALIZED_OUTPUT_22 = ROOT / "checklists/wcag/wcag_2_2.json"

PRINCIPLE_BY_PREFIX = {
    "1": "Perceivable",
    "2": "Operable",
    "3": "Understandable",
    "4": "Robust",
}

VERSION_CONFIG = {
    "2.1": {
        "checklist_id": "wcag_2_1",
        "source_url": DEFAULT_WCAG21_URL,
        "published": "2018-06-05",
        "raw_output": DEFAULT_RAW_OUTPUT_21,
        "normalized_output": DEFAULT_NORMALIZED_OUTPUT_21,
    },
    "2.2": {
        "checklist_id": "wcag_2_2",
        "source_url": DEFAULT_WCAG22_URL,
        "published": "2023-10-05",
        "raw_output": DEFAULT_RAW_OUTPUT_22,
        "normalized_output": DEFAULT_NORMALIZED_OUTPUT_22,
    },
}


def fetch_html(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def normalize_text(value: str) -> str:
    return " ".join(unescape(value).split())


class WcagChecklistParser(HTMLParser):
    """Extract success criteria from a WCAG TR page."""

    CRITERION_RE = re.compile(r"Success\s+Criterion\s+(\d+\.\d+\.\d+)\s+(.+)")
    LEVEL_RE = re.compile(r"\bLevel\s+(A{1,3})\b", re.IGNORECASE)

    def __init__(self, source_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.source_url = source_url

        self._in_h4 = False
        self._h4_attrs: dict[str, str] = {}
        self._h4_buffer: list[str] = []

        self._capture_text = False
        self._criterion_text_buffer: list[str] = []

        self._current: dict[str, Any] | None = None
        self.criteria: list[dict[str, Any]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "h4":
            self._finalize_current()
            self._in_h4 = True
            self._h4_buffer = []
            self._h4_attrs = {key: value or "" for key, value in attrs}
            return

        if self._current is not None and tag not in {"script", "style"}:
            self._capture_text = True

    def handle_data(self, data: str) -> None:
        if self._in_h4:
            self._h4_buffer.append(data)
            return

        if self._current is not None and self._capture_text:
            text = normalize_text(data)
            if text:
                self._criterion_text_buffer.append(text)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h4" and self._in_h4:
            self._in_h4 = False
            self._capture_text = False
            heading_text = normalize_text(" ".join(self._h4_buffer))
            self._open_criterion_from_heading(heading_text)
            self._h4_buffer = []
            self._h4_attrs = {}
            return

    def close(self) -> None:
        super().close()
        self._finalize_current()

    def _open_criterion_from_heading(self, heading_text: str) -> None:
        match = self.CRITERION_RE.match(heading_text)
        if not match:
            self._current = None
            self._criterion_text_buffer = []
            return

        criterion_id = match.group(1)
        title = match.group(2).strip()

        self._current = {
            "id": criterion_id,
            "title": title,
            "h4_id": self._h4_attrs.get("id") or "",
            "text": "",
            "level": "",
        }
        self._criterion_text_buffer = []

    def _finalize_current(self) -> None:
        if self._current is None:
            return

        text = " ".join(self._criterion_text_buffer)
        level_match = self.LEVEL_RE.search(text)
        level = level_match.group(1).upper() if level_match else ""

        self._current["text"] = text
        self._current["level"] = level
        self.criteria.append(self._current)

        self._current = None
        self._criterion_text_buffer = []
        self._capture_text = False


def build_raw_payload(version: str, source_url: str) -> dict[str, Any]:
    html = fetch_html(source_url)
    parser = WcagChecklistParser(source_url)
    parser.feed(html)
    parser.close()

    criteria = [
        {
            "id": item["id"],
            "title": item["title"],
            "level": item["level"],
            "description": item["text"],
            "principle": PRINCIPLE_BY_PREFIX.get(item["id"].split(".", maxsplit=1)[0], ""),
            "source_url": f"{source_url}#{item['h4_id']}" if item["h4_id"] else source_url,
        }
        for item in parser.criteria
    ]

    if version == "2.2":
        criteria = [item for item in criteria if item["id"] != "4.1.1"]

    return {
        "schema_version": "1.0",
        "source": {
            "source_url": source_url,
            "version": version,
            "publisher": "W3C",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        },
        "criteria": criteria,
        "total_criteria": len(criteria),
    }


def normalize_payload(
    raw_payload: dict[str, Any],
    checklist_id: str,
    published: str,
    reference_ids_21: set[str] | None = None,
) -> dict[str, Any]:
    version = raw_payload["source"]["version"]
    normalized_criteria = []

    for item in raw_payload["criteria"]:
        normalized_criteria.append(
            {
                "id": item["id"],
                "title": item["title"],
                "level": item["level"],
                "principle": item["principle"],
                "description": item["description"],
                "source_url": item["source_url"],
                "version": version,
                "status": "unmapped",
                "notes": [],
            }
        )

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "checklist_id": checklist_id,
        "version": version,
        "published": published,
        "status": "seed",
        "source_url": raw_payload["source"]["source_url"],
        "total_criteria": len(normalized_criteria),
        "criteria": normalized_criteria,
    }

    if version == "2.2":
        ids_22 = {item["id"] for item in normalized_criteria}
        if reference_ids_21 is None:
            wcag_21 = build_raw_payload("2.1", VERSION_CONFIG["2.1"]["source_url"])
            ids_21 = {item["id"] for item in wcag_21["criteria"]}
        else:
            ids_21 = reference_ids_21
        payload["new_criteria_vs_2_1"] = sorted(ids_22 - ids_21)
        payload["removed_criteria_vs_2_1"] = sorted(ids_21 - ids_22)

    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and normalize WCAG checklists.")
    parser.add_argument(
        "--version",
        choices=["2.1", "2.2", "all"],
        default="all",
        help="WCAG version to fetch.",
    )
    parser.add_argument(
        "--wcag21-url",
        default=DEFAULT_WCAG21_URL,
        help="WCAG 2.1 source URL.",
    )
    parser.add_argument(
        "--wcag22-url",
        default=DEFAULT_WCAG22_URL,
        help="WCAG 2.2 source URL.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    targets = ["2.1", "2.2"] if args.version == "all" else [args.version]
    url_by_version = {"2.1": args.wcag21_url, "2.2": args.wcag22_url}

    raw_cache: dict[str, dict[str, Any]] = {}
    if args.version == "all":
        raw_cache["2.1"] = build_raw_payload("2.1", url_by_version["2.1"])
        raw_cache["2.2"] = build_raw_payload("2.2", url_by_version["2.2"])

    for version in targets:
        config = VERSION_CONFIG[version]
        raw_payload = raw_cache.get(version)
        if raw_payload is None:
            raw_payload = build_raw_payload(version, url_by_version[version])

        reference_ids_21 = None
        if version == "2.2" and "2.1" in raw_cache:
            reference_ids_21 = {item["id"] for item in raw_cache["2.1"]["criteria"]}

        normalized_payload = normalize_payload(
            raw_payload,
            checklist_id=config["checklist_id"],
            published=config["published"],
            reference_ids_21=reference_ids_21,
        )
        write_json(config["raw_output"], raw_payload)
        write_json(config["normalized_output"], normalized_payload)
        print(f"Fetched {raw_payload['total_criteria']} WCAG criteria for version {version}")
        print(f"Raw data written to: {config['raw_output']}")
        print(f"Normalized data written to: {config['normalized_output']}")


if __name__ == "__main__":
    main()