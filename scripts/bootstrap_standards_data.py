#!/usr/bin/env python3
"""Generate versioned standards/checklist artifacts for local use and CI.

This script creates structured artifact folders for scale:
- checklists/wcag/
- checklists/bitv/
- coverage/mappings/
- coverage/standards/

For BITV data, this script uses the official-source fetch+normalize pipeline
from scripts/fetch_bitv_checklist.py.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fetch_bitv_checklist import DEFAULT_SOURCE_URL, build_raw_payload, normalize_payload
from fetch_wcag_checklist import (
    VERSION_CONFIG as WCAG_VERSION_CONFIG,
    build_raw_payload as build_wcag_raw_payload,
    normalize_payload as normalize_wcag_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def wcag_21_payload() -> dict:
    return {
        "schema_version": "1.0",
        "checklist_id": "wcag_2_1",
        "version": "2.1",
        "published": "2018-06-05",
        "status": "seed",
        "criteria": [
            {
                "id": "1.1.1",
                "title": "Non-text Content",
                "level": "A",
                "principle": "Perceivable",
            },
            {
                "id": "1.3.1",
                "title": "Info and Relationships",
                "level": "A",
                "principle": "Perceivable",
            },
            {
                "id": "1.4.3",
                "title": "Contrast (Minimum)",
                "level": "AA",
                "principle": "Perceivable",
            },
        ],
    }


def wcag_22_payload() -> dict:
    return {
        "schema_version": "1.0",
        "checklist_id": "wcag_2_2",
        "version": "2.2",
        "published": "2023-10-05",
        "status": "seed",
        "new_criteria_vs_2_1": [
            "2.4.11",
            "2.4.12",
            "2.4.13",
            "2.5.7",
            "2.5.8",
            "3.2.6",
            "3.3.7",
            "3.3.8",
            "3.3.9",
        ],
        "removed_criteria_vs_2_1": ["4.1.1"],
        "criteria": [
            {
                "id": "1.1.1",
                "title": "Non-text Content",
                "level": "A",
                "principle": "Perceivable",
            },
            {
                "id": "1.3.1",
                "title": "Info and Relationships",
                "level": "A",
                "principle": "Perceivable",
            },
            {
                "id": "1.4.3",
                "title": "Contrast (Minimum)",
                "level": "AA",
                "principle": "Perceivable",
            },
            {
                "id": "2.5.8",
                "title": "Target Size (Minimum)",
                "level": "AA",
                "principle": "Operable",
            },
        ],
    }


def bitv_mapping_payload() -> dict:
    return {
        "schema_version": "1.0",
        "mapping_id": "bitv_axe_mapping",
        "bitv_version": "2.0",
        "bitv_profile": "bitv_2_0_web",
        "status": "seed",
        "mappings": {
            "9.1.1.1a": {
                "mapped_to": {
                    "axe_rules": ["image-alt", "input-image-alt", "area-alt"],
                    "lighthouse_audits": ["image-alt"],
                    "ibm_rules": ["RPT_Img_UsemapAlt"],
                },
                "wcag_equivalent": "1.1.1",
            },
            "9.1.3.1a": {
                "mapped_to": {
                    "axe_rules": ["heading-order"],
                    "lighthouse_audits": ["heading-order"],
                    "ibm_rules": ["heading_markup_misuse"],
                },
                "wcag_equivalent": "1.3.1",
            },
            "9.2.4.7": {
                "mapped_to": {"axe_rules": [], "lighthouse_audits": [], "ibm_rules": []},
                "wcag_equivalent": "2.4.7",
                "status": "MANUAL_ONLY",
            },
        },
    }


def bitv_candidates_payload() -> dict:
    return {
        "schema_version": "1.0",
        "mapping_id": "bitv_axe_mapping_candidates",
        "bitv_version": "2.0",
        "bitv_profile": "bitv_2_0_web",
        "status": "seed",
        "generated_by": "scripts/bootstrap_standards_data.py",
        "candidates": {
            "9.1.1.1a": [
                {"rule": "image-alt", "similarity_score": 0.92},
                {"rule": "input-image-alt", "similarity_score": 0.88},
                {"rule": "area-alt", "similarity_score": 0.83},
            ],
            "9.1.3.1a": [
                {"rule": "heading-order", "similarity_score": 0.84},
                {"rule": "list", "similarity_score": 0.73},
                {"rule": "listitem", "similarity_score": 0.71},
            ],
            "9.2.4.7": [
                {"rule": None, "similarity_score": 0.0, "note": "Likely MANUAL_ONLY"}
            ],
        },
    }


def axe_coverage_payload() -> dict:
    return {
        "schema_version": "1.0",
        "tool": "axe-core",
        "tool_version": "4.11.4",
        "status": "seed",
        "rules": {
            "image-alt": {"wcag": ["1.1.1"], "tags": ["wcag2a", "wcag111", "wcag22a"]},
            "heading-order": {"wcag": ["1.3.1"], "tags": ["wcag2a", "wcag131"]},
            "target-size": {"wcag": ["2.5.8"], "tags": ["wcag22aa", "wcag258"]},
        },
    }


def lighthouse_coverage_payload() -> dict:
    return {
        "schema_version": "1.0",
        "tool": "lighthouse",
        "tool_version": "13.3.0",
        "status": "seed",
        "audits": {
            "image-alt": {"axe_rule": "image-alt", "wcag": ["1.1.1"]},
            "heading-order": {"axe_rule": "heading-order", "wcag": ["1.3.1"]},
        },
    }


def ibm_coverage_payload() -> dict:
    return {
        "schema_version": "1.0",
        "tool": "ibm_equal_access_checker",
        "tool_version": "3.0.0",
        "status": "seed",
        "rules": {
            "RPT_Img_UsemapAlt": {"wcag": ["1.1.1"], "policy": "IBM_Accessibility"},
            "heading_markup_misuse": {"wcag": ["1.3.1"], "policy": "IBM_Accessibility"},
        },
    }


def bitv_coverage_payload() -> dict:
    return {
        "schema_version": "1.0",
        "standard": "bitv_2_0_web",
        "version": "2.0",
        "status": "seed",
        "pruefschritte": {
            "9.1.1.1a": {
                "axe_rules": ["image-alt", "input-image-alt", "area-alt"],
                "lighthouse_audits": ["image-alt"],
                "ibm_rules": ["RPT_Img_UsemapAlt"],
                "wcag_equivalent": "1.1.1",
            },
            "9.1.3.1a": {
                "axe_rules": ["heading-order"],
                "lighthouse_audits": ["heading-order"],
                "ibm_rules": ["heading_markup_misuse"],
                "wcag_equivalent": "1.3.1",
            },
            "9.2.4.7": {
                "axe_rules": [],
                "lighthouse_audits": [],
                "ibm_rules": [],
                "wcag_equivalent": "2.4.7",
                "status": "MANUAL_ONLY",
            },
        },
    }


def coverage_map_payload() -> dict:
    return {
        "schema_version": "1.0",
        "status": "seed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool_versions": {
            "axe_core": "4.11.4",
            "lighthouse": "13.3.0",
            "ibm_checker": "3.0.0",
        },
        "standards": {
            "wcag_2_2": {
                "1.1.1": {
                    "covered_by": ["axe", "lighthouse", "ibm"],
                    "axe_rules": ["image-alt"],
                    "lighthouse_audits": ["image-alt"],
                    "ibm_rules": ["RPT_Img_UsemapAlt"],
                },
                "1.3.1": {
                    "covered_by": ["axe", "lighthouse", "ibm"],
                    "axe_rules": ["heading-order"],
                    "lighthouse_audits": ["heading-order"],
                    "ibm_rules": ["heading_markup_misuse"],
                },
                "2.5.8": {
                    "covered_by": ["axe"],
                    "axe_rules": ["target-size"],
                    "lighthouse_audits": [],
                    "ibm_rules": [],
                    "status": "PARTIAL",
                },
            },
            "bitv_2_0_web": {
                "9.1.1.1a": {"covered_by": ["axe", "lighthouse", "ibm"]},
                "9.1.3.1a": {"covered_by": ["axe", "lighthouse", "ibm"]},
                "9.2.4.7": {"covered_by": [], "status": "MANUAL_ONLY"},
            },
        },
    }


def checklists_manifest_payload() -> dict:
    return {
        "schema_version": "1.0",
        "latest": {
            "wcag": "2.2",
            "bitv": "2_0",
        },
        "paths": {
            "wcag_2_1": "checklists/wcag/wcag_2_1.json",
            "wcag_2_2": "checklists/wcag/wcag_2_2.json",
            "bitv_2_0_web": "checklists/bitv/bitv_2_0_web.json",
        },
    }


def main() -> None:
    wcag21_raw = build_wcag_raw_payload("2.1", WCAG_VERSION_CONFIG["2.1"]["source_url"])
    wcag22_raw = build_wcag_raw_payload("2.2", WCAG_VERSION_CONFIG["2.2"]["source_url"])
    wcag21 = normalize_wcag_payload(
        wcag21_raw,
        checklist_id=WCAG_VERSION_CONFIG["2.1"]["checklist_id"],
        published=WCAG_VERSION_CONFIG["2.1"]["published"],
    )
    wcag21_ids = {item["id"] for item in wcag21_raw["criteria"]}
    wcag22 = normalize_wcag_payload(
        wcag22_raw,
        checklist_id=WCAG_VERSION_CONFIG["2.2"]["checklist_id"],
        published=WCAG_VERSION_CONFIG["2.2"]["published"],
        reference_ids_21=wcag21_ids,
    )
    bitv_raw = build_raw_payload(DEFAULT_SOURCE_URL)
    bitv20 = normalize_payload(bitv_raw)
    bitv_mapping = bitv_mapping_payload()
    bitv_candidates = bitv_candidates_payload()
    bitv_cov = bitv_coverage_payload()
    cov_map = coverage_map_payload()

    # Structured paths (preferred)
    write_json(ROOT / "checklists/wcag/raw/wcag_2_1.json", wcag21_raw)
    write_json(ROOT / "checklists/wcag/raw/wcag_2_2.json", wcag22_raw)
    write_json(ROOT / "checklists/wcag/wcag_2_1.json", wcag21)
    write_json(ROOT / "checklists/wcag/wcag_2_2.json", wcag22)
    write_json(ROOT / "checklists/bitv/raw/bitv_2_0_web.json", bitv_raw)
    write_json(ROOT / "checklists/bitv/bitv_2_0_web.json", bitv20)
    write_json(ROOT / "checklists/manifest.json", checklists_manifest_payload())

    write_json(ROOT / "coverage/mappings/bitv_axe_mapping.json", bitv_mapping)
    write_json(ROOT / "coverage/mappings/bitv_axe_mapping_candidates.json", bitv_candidates)

    write_json(ROOT / "coverage/standards/bitv_coverage.json", bitv_cov)
    write_json(ROOT / "coverage/coverage_map.json", cov_map)

    print("Bootstrap completed: standards, mapping, and coverage artifacts generated.")


if __name__ == "__main__":
    main()
