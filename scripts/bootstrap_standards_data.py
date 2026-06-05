#!/usr/bin/env python3
"""Generate versioned standards/checklist artifacts for local use and CI.

This script creates structured artifact folders for scale:
- checklists/wcag/
- checklists/bitv/
- config/bitv/
- coverage/tools/
- coverage/standards/

It also writes compatibility mirror files in legacy flat paths to avoid
breaking existing references while the repository transitions.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


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


def bitv_30_payload() -> dict:
    return {
        "schema_version": "1.0",
        "checklist_id": "bitv_3_0",
        "version": "3.0",
        "base_standard": "WCAG 2.1 AA",
        "status": "seed",
        "pruefschritte": [
            {
                "id": "1.1.1a",
                "title": "Nicht-Text-Inhalte",
                "wcag_equivalent": "1.1.1",
                "manual_only": False,
            },
            {
                "id": "9.1.3.1a",
                "title": "HTML-Strukturelemente fuer Ueberschriften",
                "wcag_equivalent": "1.3.1",
                "manual_only": False,
            },
            {
                "id": "3.2.5c",
                "title": "Change on Request",
                "wcag_equivalent": "3.2.5",
                "manual_only": True,
            },
        ],
    }


def bitv_mapping_payload() -> dict:
    return {
        "schema_version": "1.0",
        "mapping_id": "bitv_axe_mapping",
        "bitv_version": "3.0",
        "status": "seed",
        "mappings": {
            "1.1.1a": {
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
            "3.2.5c": {
                "mapped_to": {"axe_rules": [], "lighthouse_audits": [], "ibm_rules": []},
                "wcag_equivalent": "3.2.5",
                "status": "MANUAL_ONLY",
            },
        },
    }


def bitv_candidates_payload() -> dict:
    return {
        "schema_version": "1.0",
        "mapping_id": "bitv_axe_mapping_candidates",
        "bitv_version": "3.0",
        "status": "seed",
        "generated_by": "scripts/bootstrap_standards_data.py",
        "candidates": {
            "1.1.1a": [
                {"rule": "image-alt", "similarity_score": 0.92},
                {"rule": "input-image-alt", "similarity_score": 0.88},
                {"rule": "area-alt", "similarity_score": 0.83},
            ],
            "9.1.3.1a": [
                {"rule": "heading-order", "similarity_score": 0.84},
                {"rule": "list", "similarity_score": 0.73},
                {"rule": "listitem", "similarity_score": 0.71},
            ],
            "3.2.5c": [
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
        "standard": "bitv_3_0",
        "status": "seed",
        "pruefschritte": {
            "1.1.1a": {
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
            "3.2.5c": {
                "axe_rules": [],
                "lighthouse_audits": [],
                "ibm_rules": [],
                "wcag_equivalent": "3.2.5",
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
            "bitv_3_0": {
                "1.1.1a": {"covered_by": ["axe", "lighthouse", "ibm"]},
                "9.1.3.1a": {"covered_by": ["axe", "lighthouse", "ibm"]},
                "3.2.5c": {"covered_by": [], "status": "MANUAL_ONLY"},
            },
        },
    }


def checklists_manifest_payload() -> dict:
    return {
        "schema_version": "1.0",
        "latest": {
            "wcag": "2.2",
            "bitv": "3.0",
        },
        "paths": {
            "wcag_2_1": "checklists/wcag/wcag_2_1.json",
            "wcag_2_2": "checklists/wcag/wcag_2_2.json",
            "bitv_3_0": "checklists/bitv/bitv_3_0.json",
        },
    }


def main() -> None:
    wcag21 = wcag_21_payload()
    wcag22 = wcag_22_payload()
    bitv30 = bitv_30_payload()
    bitv_mapping = bitv_mapping_payload()
    bitv_candidates = bitv_candidates_payload()
    axe_cov = axe_coverage_payload()
    lh_cov = lighthouse_coverage_payload()
    ibm_cov = ibm_coverage_payload()
    bitv_cov = bitv_coverage_payload()
    cov_map = coverage_map_payload()

    # Structured paths (preferred)
    write_json(ROOT / "checklists/wcag/wcag_2_1.json", wcag21)
    write_json(ROOT / "checklists/wcag/wcag_2_2.json", wcag22)
    write_json(ROOT / "checklists/bitv/bitv_3_0.json", bitv30)
    write_json(ROOT / "checklists/manifest.json", checklists_manifest_payload())

    write_json(ROOT / "config/bitv/bitv_axe_mapping.json", bitv_mapping)
    write_json(ROOT / "config/bitv/bitv_axe_mapping_candidates.json", bitv_candidates)

    write_json(ROOT / "coverage/tools/axe_core_coverage.json", axe_cov)
    write_json(ROOT / "coverage/tools/lighthouse_coverage.json", lh_cov)
    write_json(ROOT / "coverage/tools/ibm_coverage.json", ibm_cov)
    write_json(ROOT / "coverage/standards/bitv_coverage.json", bitv_cov)
    write_json(ROOT / "coverage/coverage_map.json", cov_map)

    print("Bootstrap completed: standards, mapping, and coverage artifacts generated.")


if __name__ == "__main__":
    main()
