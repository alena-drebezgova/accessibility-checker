#!/usr/bin/env python3
"""Fetch static tool capabilities from GitHub and write local capability files.

Outputs:
- tools_capabilities/axe_core_capabilities.json
- tools_capabilities/lighthouse_capabilities.json
- tools_capabilities/ibm_capabilities.json
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
BITV_MAPPING_FILE = ROOT / "coverage/mappings/bitv_axe_mapping.json"
CAPABILITIES_DIR = ROOT / "tools_capabilities"


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_json(url: str) -> Any:
    return json.loads(fetch_text(url))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def wcag_from_tags(tags: list[str]) -> list[str]:
    wcag: set[str] = set()
    for tag in tags:
        match = re.fullmatch(r"wcag(\d)(\d)(\d+)", tag)
        if not match:
            continue
        wcag.add(f"{match.group(1)}.{match.group(2)}.{match.group(3)}")
    return sorted(wcag)


def load_bitv_index() -> tuple[dict[str, set[str]], dict[str, set[str]], dict[str, set[str]]]:
    payload = json.loads(BITV_MAPPING_FILE.read_text(encoding="utf-8"))
    mappings = payload.get("mappings", {})

    by_axe: dict[str, set[str]] = defaultdict(set)
    by_lh: dict[str, set[str]] = defaultdict(set)
    by_ibm: dict[str, set[str]] = defaultdict(set)

    for bitv_id, entry in mappings.items():
        mapped = entry.get("mapped_to", {})
        for axe_rule in mapped.get("axe_rules", []):
            if axe_rule:
                by_axe[axe_rule].add(bitv_id)
        for audit in mapped.get("lighthouse_audits", []):
            if audit:
                by_lh[audit].add(bitv_id)
        for rule in mapped.get("ibm_rules", []):
            if rule:
                by_ibm[rule].add(bitv_id)

    return by_axe, by_lh, by_ibm


def fetch_axe_capabilities(by_axe: dict[str, set[str]]) -> dict[str, Any]:
    rules_dir_url = "https://api.github.com/repos/dequelabs/axe-core/contents/lib/rules"
    package_url = "https://raw.githubusercontent.com/dequelabs/axe-core/develop/package.json"

    items = fetch_json(rules_dir_url)
    package = fetch_json(package_url)

    rules: dict[str, Any] = {}
    for item in items:
        name = item.get("name", "")
        if not name.endswith(".json"):
            continue

        rule_json = fetch_json(item["download_url"])
        rule_id = rule_json.get("id")
        if not rule_id:
            continue

        tags = [tag for tag in rule_json.get("tags", []) if isinstance(tag, str)]
        wcag = wcag_from_tags(tags)
        bitv = sorted(by_axe.get(rule_id, set()))

        if not wcag and not bitv:
            continue

        rules[rule_id] = {
            "wcag": wcag,
            "bitv": bitv,
            "tags": tags,
            "notes": [],
        }

    return {
        "schema_version": "1.0",
        "tool": "axe-core",
        "tool_version": package.get("version", "unknown"),
        "status": "generated",
        "source": {
            "type": "static_capabilities",
            "collected_from": "github",
            "repository": "dequelabs/axe-core",
            "branch": "develop",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
        "capabilities": {
            "rules": dict(sorted(rules.items())),
        },
    }


def fetch_lighthouse_capabilities(
    by_lh: dict[str, set[str]],
    axe_rules: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    audits_dir_url = (
        "https://api.github.com/repos/GoogleChrome/lighthouse/contents/core/audits/accessibility"
    )
    package_url = "https://raw.githubusercontent.com/GoogleChrome/lighthouse/main/package.json"

    items = fetch_json(audits_dir_url)
    package = fetch_json(package_url)

    audits: dict[str, Any] = {}
    for item in items:
        name = item.get("name", "")
        if not name.endswith(".js") or name == "axe-audit.js":
            continue

        source = fetch_text(item["download_url"])
        if "extends AxeAudit" not in source:
            continue

        id_match = re.search(r"id:\s*'([^']+)'", source)
        if not id_match:
            continue
        audit_id = id_match.group(1)

        axe_entry = axe_rules.get(audit_id, {})
        wcag = list(axe_entry.get("wcag", []))
        bitv = sorted(by_lh.get(audit_id, set()))

        audits[audit_id] = {
            "axe_rule": audit_id,
            "wcag": wcag,
            "bitv": bitv,
            "notes": [],
        }

    return {
        "schema_version": "1.0",
        "tool": "lighthouse",
        "tool_version": package.get("version", "unknown"),
        "status": "generated",
        "source": {
            "type": "static_capabilities",
            "collected_from": "github",
            "repository": "GoogleChrome/lighthouse",
            "branch": "main",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
        "capabilities": {
            "audits": dict(sorted(audits.items())),
        },
    }


def fetch_ibm_capabilities(by_ibm: dict[str, set[str]]) -> dict[str, Any]:
    rules_dir_url = (
        "https://api.github.com/repos/IBMa/equal-access/contents/"
        "accessibility-checker-engine/src/v4/rules"
    )
    package_meta_url = (
        "https://api.github.com/repos/IBMa/equal-access/contents/"
        "accessibility-checker-engine/package.json"
    )

    items = fetch_json(rules_dir_url)
    package_meta = fetch_json(package_meta_url)
    package = fetch_json(package_meta["download_url"])

    rules: dict[str, Any] = {}
    for item in items:
        name = item.get("name", "")
        if not name.endswith(".ts"):
            continue

        source = fetch_text(item["download_url"])
        id_match = re.search(r"\bid\s*:\s*\"([^\"]+)\"", source)
        if not id_match:
            continue
        rule_id = id_match.group(1)

        if "WCAG_2_0" not in source and "WCAG_2_1" not in source and "WCAG_2_2" not in source:
            continue

        nums: set[str] = set(re.findall(r"\b\d+\.\d+\.\d+\b", source))
        wcag = sorted(nums)
        bitv = sorted(by_ibm.get(rule_id, set()))

        if not wcag and not bitv:
            continue

        rules[rule_id] = {
            "wcag": wcag,
            "bitv": bitv,
            "policy": "IBM_Accessibility",
            "notes": [],
        }

    return {
        "schema_version": "1.0",
        "tool": "ibm_equal_access_checker",
        "tool_version": package.get("version", "unknown"),
        "status": "generated",
        "source": {
            "type": "static_capabilities",
            "collected_from": "github",
            "repository": "IBMa/equal-access",
            "branch": "main",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
        "capabilities": {
            "rules": dict(sorted(rules.items())),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch static tool capabilities from GitHub and write local files."
    )
    parser.add_argument(
        "--tool",
        choices=["axe", "lighthouse", "ibm", "all"],
        default="all",
        help="Choose which tool capability set to refresh.",
    )
    return parser.parse_args()


def run_for_tool(tool: str) -> None:
    by_axe, by_lh, by_ibm = load_bitv_index()

    if tool in {"axe", "all"}:
        axe_payload = fetch_axe_capabilities(by_axe)
        write_json(CAPABILITIES_DIR / "axe_core_capabilities.json", axe_payload)
        print(f"Axe rules saved: {len(axe_payload['capabilities']['rules'])}")

    if tool in {"lighthouse", "all"}:
        # Lighthouse accessibility audits are axe-backed; derive WCAG from current axe map.
        axe_payload_for_lh = fetch_axe_capabilities(by_axe)
        axe_rules = axe_payload_for_lh["capabilities"]["rules"]
        lh_payload = fetch_lighthouse_capabilities(by_lh, axe_rules)
        write_json(CAPABILITIES_DIR / "lighthouse_capabilities.json", lh_payload)
        print(f"Lighthouse audits saved: {len(lh_payload['capabilities']['audits'])}")

    if tool in {"ibm", "all"}:
        ibm_payload = fetch_ibm_capabilities(by_ibm)
        write_json(CAPABILITIES_DIR / "ibm_capabilities.json", ibm_payload)
        print(f"IBM rules saved: {len(ibm_payload['capabilities']['rules'])}")


def main() -> None:
    args = parse_args()
    run_for_tool(args.tool)


if __name__ == "__main__":
    main()
