#!/usr/bin/env python3
"""Fetch and normalize the BITV checklist from bitvtest.de.

The script runs in two explicit stages:
1. Fetch the official BITV-Test page and store a raw structured extraction.
2. Normalize that raw data into the canonical checklist JSON used by the project.

Default outputs:
- checklists/bitv/raw/bitv_2_0_web.json
- checklists/bitv/bitv_2_0_web.json
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
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_URL = "https://bitvtest.de/pruefverfahren/bitv-20-web"
DEFAULT_RAW_OUTPUT = ROOT / "checklists/bitv/raw/bitv_2_0_web.json"
DEFAULT_NORMALIZED_OUTPUT = ROOT / "checklists/bitv/bitv_2_0_web.json"
BITV_VERSION = "2.0"
BITV_LOCALE = "de"
BITV_PROFILE = "BIK BITV-Test / EN 301 549 (Web)"
EN_301_549_VERSION = "3.2.1"
WCAG_REFERENCE = "2.1"

SECTION_RE = re.compile(r"^(?P<section_id>\d+(?:\.\d+)*)(?:\s+(?P<section_title>.+))?$")
STEP_RE = re.compile(r"^(?P<step_id>\d+(?:\.\d+)*[a-z]?)\s+(?P<title>.+)$", re.IGNORECASE)


def transliterate_german(value: str) -> str:
    return (
        value.replace("Ä", "Ae")
        .replace("Ö", "Oe")
        .replace("Ü", "Ue")
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )


class BitvChecklistParser(HTMLParser):
    def __init__(self, source_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.source_url = source_url
        self._heading_tag: str | None = None
        self._heading_buffer: list[str] = []
        self._anchor_href: str | None = None
        self._anchor_buffer: list[str] = []
        self._current_section_id: str | None = None
        self._current_section_title: str | None = None
        self.steps: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._heading_tag = tag
            self._heading_buffer = []
            return

        if tag == "a":
            attrs_map = {key: value for key, value in attrs}
            self._anchor_href = attrs_map.get("href")
            self._anchor_buffer = []

    def handle_data(self, data: str) -> None:
        if self._heading_tag is not None:
            self._heading_buffer.append(data)
        if self._anchor_href is not None:
            self._anchor_buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == self._heading_tag:
            heading_text = self._normalize_text("".join(self._heading_buffer))
            self._update_section_from_heading(heading_text)
            self._heading_tag = None
            self._heading_buffer = []
            return

        if tag == "a" and self._anchor_href is not None:
            anchor_text = self._normalize_text("".join(self._anchor_buffer))
            self._capture_step(anchor_text, self._anchor_href)
            self._anchor_href = None
            self._anchor_buffer = []

    @staticmethod
    def _normalize_text(value: str) -> str:
        return transliterate_german(" ".join(unescape(value).split()))

    def _update_section_from_heading(self, heading_text: str) -> None:
        match = SECTION_RE.match(heading_text)
        if not match:
            return

        section_title = match.group("section_title") or ""
        if section_title in {"Additional Links", "Alles zuklappen"}:
            return

        self._current_section_id = match.group("section_id")
        self._current_section_title = section_title or heading_text

    def _capture_step(self, anchor_text: str, href: str) -> None:
        if "/pruefschritt/bitv-20-web/" not in href:
            return

        match = STEP_RE.match(anchor_text)
        if not match:
            return

        if self._current_section_id is None or self._current_section_title is None:
            return

        self.steps.append(
            {
                "section_id": self._current_section_id,
                "section_title": self._current_section_title,
                "id": match.group("step_id"),
                "title": match.group("title"),
                "source_url": urljoin(self.source_url, href),
                "version": BITV_VERSION,
                "locale": BITV_LOCALE,
            }
        )


class BitvStepDetailParser(HTMLParser):
    """Extract selected textual blocks from a single Pruefschritt page."""

    TARGET_BLOCKS = {
        "was wird geprueft?": "description",
        "beschreibung": "description",
        "einordnung des pruefschritts": "classification",
    }

    STOP_MARKERS = {
        "Nach oben springen",
        "Kontakt",
        "Erklaerung zur Barrierefreiheit",
        "Datenschutz",
        "Impressum",
        "Linkedin",
        "Github",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._in_h2 = False
        self._h2_buffer: list[str] = []
        self._current_block_key: str | None = None
        self._capture_depth = 0
        self._in_script = False
        self._in_style = False
        self._blocks: dict[str, list[str]] = {
            "description": [],
            "classification": [],
        }

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script":
            self._in_script = True
            return
        if tag == "style":
            self._in_style = True
            return

        if tag == "h2":
            self._in_h2 = True
            self._h2_buffer = []
            self._current_block_key = None
            self._capture_depth = 0
            return

        if self._current_block_key is not None:
            self._capture_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._in_script = False
            return
        if tag == "style":
            self._in_style = False
            return

        if tag == "h2" and self._in_h2:
            heading_text = self._normalize_label(" ".join(self._h2_buffer))
            self._in_h2 = False
            self._h2_buffer = []
            self._current_block_key = self.TARGET_BLOCKS.get(heading_text)
            self._capture_depth = 0
            return

        if self._current_block_key is not None and self._capture_depth > 0:
            self._capture_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._in_script or self._in_style:
            return

        if self._in_h2:
            self._h2_buffer.append(data)
            return

        if self._current_block_key is None:
            return

        text = self._normalize_text(data)
        if text:
            self._blocks[self._current_block_key].append(text)

    @staticmethod
    def _normalize_text(value: str) -> str:
        return transliterate_german(" ".join(unescape(value).split()))

    @staticmethod
    def _normalize_label(value: str) -> str:
        text = transliterate_german(" ".join(unescape(value).split()))
        return text.lower()

    def as_payload(self) -> dict[str, str]:
        def cleaned(block: list[str]) -> str:
            lines: list[str] = []
            for raw in block:
                line = raw.strip()
                if not line:
                    continue
                normalized = self._normalize_label(line)
                if normalized in {self._normalize_label(marker) for marker in self.STOP_MARKERS}:
                    break
                lines.append(line)
            return "\n".join(lines).strip()

        return {
            "description": cleaned(self._blocks["description"]),
            "classification": cleaned(self._blocks["classification"]),
        }


def fetch_html(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_step_details(step_url: str) -> dict[str, str]:
    try:
        html = fetch_html(step_url)
    except URLError:
        return {"description": "", "classification": ""}

    parser = BitvStepDetailParser()
    parser.feed(html)
    return parser.as_payload()


def build_raw_payload(source_url: str) -> dict[str, Any]:
    html = fetch_html(source_url)
    parser = BitvChecklistParser(source_url)
    parser.feed(html)

    sections: list[dict[str, Any]] = []
    sections_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    seen_step_ids: set[str] = set()

    for step in parser.steps:
        step_id = step["id"]
        if step_id in seen_step_ids:
            continue
        seen_step_ids.add(step_id)

        section_key = (step["section_id"], step["section_title"])
        section = sections_by_key.get(section_key)
        if section is None:
            section = {
                "section_id": step["section_id"],
                "section_title": step["section_title"],
                "source_url": source_url,
                "version": BITV_VERSION,
                "locale": BITV_LOCALE,
                "steps": [],
            }
            sections_by_key[section_key] = section
            sections.append(section)

        details = fetch_step_details(step["source_url"])
        section["steps"].append(
            {
                "id": step["id"],
                "title": step["title"],
                "description": details["description"],
                "classification": details["classification"],
                "source_url": step["source_url"],
                "version": step["version"],
                "locale": step["locale"],
            }
        )

    return {
        "schema_version": "1.0",
        "source": {
            "source_url": source_url,
            "profile": BITV_PROFILE,
            "version": BITV_VERSION,
            "locale": BITV_LOCALE,
            "en_301_549_version": EN_301_549_VERSION,
            "wcag_reference": WCAG_REFERENCE,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        },
        "sections": sections,
        "total_pruefschritte": len(seen_step_ids),
    }


def normalize_payload(raw_payload: dict[str, Any]) -> dict[str, Any]:
    pruefschritte: list[dict[str, Any]] = []

    for section in raw_payload["sections"]:
        for step in section["steps"]:
            pruefschritte.append(
                {
                    "id": step["id"],
                    "title": step["title"],
                    "description": step["description"],
                    "einordnung_des_pruefschritts": step["classification"],
                    "section_id": section["section_id"],
                    "section_title": section["section_title"],
                    "source_url": step["source_url"],
                    "version": step["version"],
                    "locale": step["locale"],
                    "wcag_equivalent": None,
                    "mapping_status": "unmapped",
                    "notes": [],
                }
            )

    return {
        "schema_version": "1.0",
        "checklist_id": "bitv_2_0_web",
        "profile": BITV_PROFILE,
        "version": BITV_VERSION,
        "references": {
            "bitv": "2.0",
            "en_301_549": EN_301_549_VERSION,
            "wcag": WCAG_REFERENCE,
        },
        "source_url": raw_payload["source"]["source_url"],
        "locale": BITV_LOCALE,
        "status": "seed",
        "sections_count": len(raw_payload["sections"]),
        "total_pruefschritte": len(pruefschritte),
        "pruefschritte": pruefschritte,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and normalize the BITV checklist.")
    parser.add_argument(
        "--source-url",
        default=DEFAULT_SOURCE_URL,
        help="Official BITV-Test page to fetch.",
    )
    parser.add_argument(
        "--raw-output",
        default=str(DEFAULT_RAW_OUTPUT),
        help="Path for the raw structured extraction.",
    )
    parser.add_argument(
        "--normalized-output",
        default=str(DEFAULT_NORMALIZED_OUTPUT),
        help="Path for the normalized checklist JSON.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_payload = build_raw_payload(args.source_url)
    normalized_payload = normalize_payload(raw_payload)

    raw_output = Path(args.raw_output)
    normalized_output = Path(args.normalized_output)

    write_json(raw_output, raw_payload)
    write_json(normalized_output, normalized_payload)

    print(f"Fetched {raw_payload['total_pruefschritte']} BITV Pruefschritte")
    print(f"Raw data written to: {raw_output}")
    print(f"Normalized data written to: {normalized_output}")


if __name__ == "__main__":
    main()