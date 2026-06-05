# 🦾 Robot Framework Accessibility Testing Library — Projektplan

> **Projektziel:** Eine wiederverwendbare Python-Library für Robot Framework, die Web-Accessibility-Tests mit axe-core, Lighthouse und IBM Equal Access Checker durchführt, gegen WCAG- und BIK BITV-Test-Checklisten validiert und via PyPI veröffentlicht wird.

---

## 📋 Inhaltsverzeichnis

1. [Projektstruktur & Setup](#1-projektstruktur--setup)
2. [Core Architecture](#2-core-architecture)
3. [Tool-Integration](#3-tool-integration)
4. [Checklist-Integration (WCAG & BIK BITV)](#4-checklist-integration-wcag--bik-bitv)
5. [Browser Library Integration](#5-browser-library-integration)
6. [Reporting & Ergebnisvergleich](#6-reporting--ergebnisvergleich)
7. [PyPI-Veröffentlichung](#7-pypi-veröffentlichung)
8. [CI/CD Pipeline Integration](#8-cicd-pipeline-integration)
9. [Testing & Qualitätssicherung](#9-testing--qualitätssicherung)
10. [Dokumentation](#10-dokumentation)
11. [Roadmap & Meilensteine](#11-roadmap--meilensteine)

---

## 1. Projektstruktur & Setup

### 1.1 Repository anlegen

```
rf-accessibility-library/
│
├── AccessibilityLibrary/          # Haupt-Library-Package
│   ├── __init__.py
│   ├── keywords/
│   │   ├── __init__.py
│   │   ├── axe_keywords.py
│   │   ├── lighthouse_keywords.py
│   │   ├── ibm_keywords.py
│   │   └── checklist_keywords.py
│   ├── checkers/
│   │   ├── __init__.py
│   │   ├── axe_checker.py
│   │   ├── lighthouse_checker.py
│   │   └── ibm_checker.py
│   ├── checklists/
│   │   ├── __init__.py
│   │   ├── wcag_21.py
│   │   ├── wcag_22.py
│   │   ├── bik_bitv_test.py
│   │   └── checklist_mapper.py
│   ├── reporters/
│   │   ├── __init__.py
│   │   ├── html_reporter.py
│   │   ├── json_reporter.py
│   │   └── comparison_reporter.py
│   └── utils/
│       ├── __init__.py
│       ├── browser_utils.py
│       └── result_aggregator.py
│
├── tests/                         # Unit & Integration Tests
│   ├── unit/
│   ├── integration/
│   └── robot/
│       └── acceptance/
│
├── docs/                          # Dokumentation
│   ├── keywords.md
│   ├── configuration.md
│   └── examples/
│
├── .github/
│   └── workflows/
│       ├── tests.yml
│       ├── publish.yml
│       └── pr_check.yml
│
├── pyproject.toml
├── setup.cfg
├── setup.py
├── MANIFEST.in
├── README.md
├── CHANGELOG.md
└── LICENSE
```

### 1.2 Entwicklungsumgebung einrichten

```bash
# Python 3.9+ empfohlen
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Dev-Dependencies installieren
pip install robotframework
pip install robotframework-browser
pip install playwright
rfbrowser init

# Node.js Tools
npm install -g axe-cli
npm install -g lighthouse
npm install -g @ibm/equal-access-checker
```

### 1.3 pyproject.toml konfigurieren

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "robotframework-accessibility-library"
version = "0.1.0"
description = "Robot Framework library for web accessibility testing"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "Apache-2.0"}
keywords = ["robotframework", "accessibility", "a11y", "wcag", "bitv", "testing"]
classifiers = [
    "Framework :: Robot Framework :: Library",
    "Topic :: Software Development :: Testing",
    "Programming Language :: Python :: 3",
]
dependencies = [
    "robotframework>=6.0",
    "robotframework-browser>=18.0",
    "playwright>=1.40",
    "axe-playwright-python>=0.1.3",
    "requests>=2.31",
    "jinja2>=3.1",
    "jsonschema>=4.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio",
    "black",
    "flake8",
    "mypy",
    "pre-commit",
]
```

---

## 2. Core Architecture

### 2.1 Haupt-Library-Klasse

Die Library erbt von `robot.api.deco` und implementiert das **Keyword**-Pattern von Robot Framework.

```python
# AccessibilityLibrary/__init__.py

from robot.api.deco import library, keyword
from .checkers.axe_checker import AxeChecker
from .checkers.lighthouse_checker import LighthouseChecker
from .checkers.ibm_checker import IBMChecker
from .checklists.checklist_mapper import ChecklistMapper
from .reporters.comparison_reporter import ComparisonReporter

@library(scope='SUITE', version='0.1.0')
class AccessibilityLibrary:
    """
    Robot Framework library for comprehensive web accessibility testing.
    
    Supports axe-core, Google Lighthouse, and IBM Equal Access Checker.
    Results are mapped to WCAG 2.1/2.2 and BIK BITV-Test checklists.
    
    = Table of contents =
    - Keywords
    - Configuration
    - Examples
    """
    
    ROBOT_LIBRARY_SCOPE = 'SUITE'
    ROBOT_LIBRARY_VERSION = '0.1.0'

    def __init__(self, browser_library=None, output_format='html'):
        self._browser = browser_library
        self._axe = AxeChecker()
        self._lighthouse = LighthouseChecker()
        self._ibm = IBMChecker()
        self._mapper = ChecklistMapper()
        self._reporter = ComparisonReporter(output_format)
```

### 2.2 Abstraktes Checker-Interface

```python
# AccessibilityLibrary/checkers/base_checker.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class AccessibilityViolation:
    id: str
    impact: str          # critical, serious, moderate, minor
    description: str
    help_url: str
    elements: List[str]
    wcag_criteria: List[str]   # z.B. ["1.1.1", "4.1.2"]
    tool: str                  # axe, lighthouse, ibm

@dataclass 
class CheckerResult:
    url: str
    tool: str
    violations: List[AccessibilityViolation]
    passes: List[dict]
    incomplete: List[dict]
    timestamp: str
    raw_data: dict

class BaseChecker(ABC):
    @abstractmethod
    def run(self, url: str, page=None) -> CheckerResult:
        pass
    
    @abstractmethod
    def map_to_wcag(self, violation: dict) -> List[str]:
        pass
```

### 2.3 Keyword-Design (Robot Framework DSL)

Keywords sollen lesbar und ausdrucksstark sein:

```robotframework
*** Settings ***
Library    AccessibilityLibrary    browser_library=Browser

*** Test Cases ***
Full Accessibility Audit
    Open Browser    https://example.com
    
    # Einzelne Tools
    ${axe_result}=       Run Axe Check
    ${lh_result}=        Run Lighthouse Check    categories=accessibility
    ${ibm_result}=       Run IBM Accessibility Check
    
    # Kombinierter Check gegen Checkliste
    ${report}=           Run Full Accessibility Audit    checklist=WCAG_22_AA
    Should Have No Critical Violations    ${report}
    
    # BIK BITV spezifisch
    ${bitv}=             Check Against BIK BITV Test
    Generate Comparison Report    ${axe_result}    ${lh_result}    ${ibm_result}
    Fail If Violations Exceed    max_critical=0    max_serious=5
```

---

## 3. Tool-Integration

### 3.1 axe-core Integration

**Ansatz:** `axe-playwright-python` oder direkter JS-Inject über Browser Library.

```python
# AccessibilityLibrary/checkers/axe_checker.py

from axe_playwright_python import Axe
import json

class AxeChecker(BaseChecker):
    
    def __init__(self, rules=None, tags=None):
        self._axe = Axe()
        self._rules = rules or []
        self._tags = tags or ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']
    
    def run(self, page) -> CheckerResult:
        """
        Führt axe-core Analyse auf der aktuellen Seite aus.
        Benötigt Playwright-Page-Objekt von Browser Library.
        """
        results = self._axe.run(
            page,
            options={
                'runOnly': {'type': 'tag', 'values': self._tags},
                'rules': self._rules
            }
        )
        return self._parse_results(results)
    
    def inject_and_run(self, page) -> dict:
        """Fallback: axe-core direkt per JS injizieren"""
        page.add_script_tag(
            url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.2/axe.min.js"
        )
        return page.evaluate("axe.run()")
    
    def map_to_wcag(self, violation: dict) -> List[str]:
        tags = violation.get('tags', [])
        return [t.replace('wcag', '').replace('_', '.') 
                for t in tags if t.startswith('wcag') and not t.endswith('a')]
```

**Keywords für axe:**

```robotframework
Run Axe Check
    [Arguments]    ${tags}=wcag21aa    ${include}=${EMPTY}    ${exclude}=${EMPTY}
    ${page}=    Get Current Playwright Page
    ${result}=    Run Keyword    _run_axe_analysis    ${page}    ${tags}
    [Return]    ${result}

Axe Should Have No Violations
    [Arguments]    ${impact}=critical
    ${violations}=    Get Axe Violations    impact=${impact}
    Should Be Empty    ${violations}    
    ...    msg=axe-core found ${violations.__len__()} ${impact} violations
```

### 3.2 Google Lighthouse Integration

**Ansatz:** Lighthouse CLI via subprocess oder Node.js API.

```python
# AccessibilityLibrary/checkers/lighthouse_checker.py

import subprocess
import json
import tempfile
import os

class LighthouseChecker(BaseChecker):
    
    def __init__(self, chrome_path=None):
        self._chrome_path = chrome_path
    
    def run(self, url: str, categories=None) -> CheckerResult:
        categories = categories or ['accessibility']
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            output_path = f.name
        
        cmd = [
            'lighthouse',
            url,
            '--output=json',
            f'--output-path={output_path}',
            f'--only-categories={",".join(categories)}',
            '--chrome-flags=--headless --no-sandbox',
            '--quiet'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        with open(output_path) as f:
            raw = json.load(f)
        
        os.unlink(output_path)
        return self._parse_lh_results(raw)
    
    def _parse_lh_results(self, raw: dict) -> CheckerResult:
        audits = raw.get('audits', {})
        violations = []
        
        for audit_id, audit in audits.items():
            if audit.get('score', 1) == 0:  # Failed
                violations.append(AccessibilityViolation(
                    id=audit_id,
                    impact=self._map_weight(audit.get('weight', 0)),
                    description=audit.get('description', ''),
                    help_url=f"https://web.dev/{audit_id}/",
                    elements=self._extract_elements(audit),
                    wcag_criteria=self.map_to_wcag(audit),
                    tool='lighthouse'
                ))
        
        return CheckerResult(
            url=raw.get('finalUrl', ''),
            tool='lighthouse',
            violations=violations,
            passes=[],
            incomplete=[],
            timestamp=raw.get('fetchTime', ''),
            raw_data=raw
        )
```

### 3.3 IBM Equal Access Checker Integration

**Ansatz:** `accessibility-checker` npm-Package via Node.js-Bridge.

```python
# AccessibilityLibrary/checkers/ibm_checker.py

import subprocess
import json

IBM_RUNNER_SCRIPT = """
const checker = require('accessibility-checker');

async function runCheck(url) {
    const results = await checker.getCompliance(url, 'scan');
    const summary = await checker.getSummary();
    console.log(JSON.stringify({results, summary}));
    process.exit(0);
}
runCheck(process.argv[2]);
"""

class IBMChecker(BaseChecker):
    
    def run(self, url: str, ruleset='IBM_Accessibility') -> CheckerResult:
        result = subprocess.run(
            ['node', '-e', IBM_RUNNER_SCRIPT, url],
            capture_output=True, text=True, timeout=60
        )
        raw = json.loads(result.stdout)
        return self._parse_ibm_results(raw, url)
    
    def map_to_wcag(self, violation: dict) -> List[str]:
        # IBM gibt WCAG-Referenzen direkt zurück
        return violation.get('wcag', [])
```

---

## 4. Checklist-Integration (WCAG & BIK BITV)

### 4.1 WCAG 2.1 / 2.2 Datenmodell

```python
# AccessibilityLibrary/checklists/wcag_22.py

WCAG_22_CRITERIA = {
    "1.1.1": {
        "title": "Non-text Content",
        "level": "A",
        "principle": "Perceivable",
        "description": "All non-text content has a text alternative.",
        "understanding_url": "https://www.w3.org/WAI/WCAG22/Understanding/non-text-content",
        "axe_rules": ["image-alt", "input-image-alt", "area-alt"],
        "lighthouse_audits": ["image-alt"],
        "ibm_rules": ["img_alt_valid"],
    },
    "1.3.1": {
        "title": "Info and Relationships",
        "level": "A",
        "principle": "Perceivable",
        "axe_rules": ["heading-order", "list", "listitem", "label"],
        "lighthouse_audits": ["heading-order", "list"],
        "ibm_rules": ["heading_markup_misuse"],
    },
    # ... alle 78 Kriterien WCAG 2.2
    "2.5.8": {  # Neu in WCAG 2.2
        "title": "Target Size (Minimum)",
        "level": "AA",
        "principle": "Operable",
        "axe_rules": ["target-size"],
        "ibm_rules": ["target_spacing_sufficient"],
    }
}

WCAG_LEVELS = {
    'A': [c for c, v in WCAG_22_CRITERIA.items() if v['level'] == 'A'],
    'AA': [c for c, v in WCAG_22_CRITERIA.items() if v['level'] in ('A', 'AA')],
    'AAA': list(WCAG_22_CRITERIA.keys()),
}
```

### 4.2 BIK BITV-Test Mapping

Der **BIK BITV-Test** (Bundesfachstelle Barrierefreiheit) ist der deutsche Standard für die BITV 2.0-Prüfung.

```python
# AccessibilityLibrary/checklists/bik_bitv_test.py

BIK_BITV_PRUEFSCHRITTE = {
    "9.1.1.1a": {
        "title": "Alternativtexte für Bedienelemente",
        "bitv_paragraph": "§ 3 Abs. 1",
        "wcag_criterion": "1.1.1",
        "prüfschritt_url": "https://www.bitvtest.de/pruefschritte/bitv-20-web/9-1-1-1a",
        "tools_coverage": ["axe", "ibm"],
        "manual_check_required": True,
        "manual_instructions": "Prüfe ob alle Bedienelemente aussagekräftige Alternativtexte haben",
    },
    "9.1.1.1b": {
        "title": "Alternativtexte für Grafiken und Objekte",
        "wcag_criterion": "1.1.1",
        "tools_coverage": ["axe", "lighthouse", "ibm"],
        "manual_check_required": True,
    },
    "9.1.3.1a": {
        "title": "HTML-Strukturelemente für Überschriften",
        "wcag_criterion": "1.3.1",
        "tools_coverage": ["axe", "ibm"],
        "manual_check_required": False,
    },
    # ... alle 98 BIK BITV-Test Prüfschritte
}

# Konformitätsstufen nach BITV 2.0
BITV_COMPLIANCE_LEVELS = {
    'BITV_20_A': [...],   # Entspricht WCAG 2.1 Level A
    'BITV_20_AA': [...],  # Entspricht WCAG 2.1 Level AA
    'EN_301_549': [...],  # EU-Norm für öffentliche Stellen
}
```

### 4.3 Checklist-Mapper

```python
# AccessibilityLibrary/checklists/checklist_mapper.py

class ChecklistMapper:
    """
    Mappt Tool-Violations auf WCAG- und BIK BITV-Kriterien
    und berechnet den Erfüllungsgrad je Prüfschritt.
    """
    
    SUPPORTED_CHECKLISTS = ['WCAG_21_A', 'WCAG_21_AA', 'WCAG_22_AA', 'BIK_BITV_20', 'EN_301_549']
    
    def map_results_to_checklist(
        self, 
        results: List[CheckerResult],
        checklist: str = 'WCAG_22_AA'
    ) -> ChecklistReport:
        
        criteria = self._load_checklist(checklist)
        mapped = {}
        
        for criterion_id, criterion in criteria.items():
            violations_for_criterion = []
            
            for result in results:
                for v in result.violations:
                    if criterion_id in v.wcag_criteria:
                        violations_for_criterion.append(v)
            
            mapped[criterion_id] = {
                'criterion': criterion,
                'status': 'FAIL' if violations_for_criterion else 'PASS',
                'violations': violations_for_criterion,
                'covered_by_tools': self._get_coverage(criterion_id, results),
                'manual_check_needed': criterion.get('manual_check_required', False),
            }
        
        return ChecklistReport(checklist=checklist, criteria=mapped)
```

---

## 5. Browser Library Integration

### 5.1 Playwright Browser Library Anbindung

```python
# AccessibilityLibrary/utils/browser_utils.py

from robot.libraries.BuiltIn import BuiltIn

class BrowserUtils:
    """
    Utility-Klasse zur Integration mit robotframework-browser (Playwright).
    Ermöglicht Zugriff auf aktive Browser-Session für Tool-Checks.
    """
    
    def get_current_page(self):
        """Gibt das aktive Playwright Page-Objekt zurück."""
        browser_lib = BuiltIn().get_library_instance('Browser')
        return browser_lib.get_page()
    
    def get_current_url(self) -> str:
        browser_lib = BuiltIn().get_library_instance('Browser')
        return browser_lib.get_url()
    
    def inject_axe_script(self, page):
        """Injiziert axe-core in die aktuelle Seite."""
        page.add_script_tag(
            url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.1/axe.min.js"
        )
    
    def capture_screenshot_on_violation(self, page, violation_id: str):
        """Screenshot für Violation-Dokumentation."""
        page.screenshot(path=f"a11y_violation_{violation_id}.png")
```

### 5.2 Nutzungsbeispiel in Robot Framework

```robotframework
*** Settings ***
Library    Browser
Library    AccessibilityLibrary    WITH NAME    A11y

*** Test Cases ***
Accessibility Test für Homepage
    New Browser    chromium    headless=True
    New Page       https://meine-webseite.de
    
    # Alle Tools in einem Schritt
    A11y.Run Full Accessibility Audit
    ...    checklist=BIK_BITV_20
    ...    output=accessibility_report.html
    
    # Oder einzeln
    ${axe}=       A11y.Run Axe Check    tags=wcag22aa
    ${lh}=        A11y.Run Lighthouse Check
    ${ibm}=       A11y.Run IBM Check
    
    # Vergleichsreport
    A11y.Generate Comparison Report
    ...    results=${axe}    ${lh}    ${ibm}
    ...    checklist=WCAG_22_AA
    ...    format=html
    
    A11y.Should Conform To    BIK_BITV_20
    
    Close Browser
```

---

## 6. Reporting & Ergebnisvergleich

### 6.1 Vergleichsreporter

```python
# AccessibilityLibrary/reporters/comparison_reporter.py

class ComparisonReporter:
    """
    Erstellt vergleichende Reports über alle drei Tools.
    Zeigt Überschneidungen, unique Findings und Gesamtkonformität.
    """
    
    def generate_comparison(
        self,
        results: List[CheckerResult],
        checklist_report: ChecklistReport
    ) -> ComparisonReport:
        
        # Finde Violations die von mehreren Tools gefunden wurden
        overlaps = self._find_overlapping_violations(results)
        
        # Einzigartige Findings je Tool
        unique = {
            'axe': self._get_unique(results, 'axe', results),
            'lighthouse': self._get_unique(results, 'lighthouse', results),
            'ibm': self._get_unique(results, 'ibm', results),
        }
        
        # Konformitätsscore
        total = len(checklist_report.criteria)
        passed = sum(1 for c in checklist_report.criteria.values() if c['status'] == 'PASS')
        
        return ComparisonReport(
            overall_score=passed/total * 100,
            tool_results=results,
            overlapping_violations=overlaps,
            unique_findings=unique,
            checklist_report=checklist_report,
            summary=self._generate_summary(results, checklist_report)
        )
```

### 6.2 HTML Report Template (Jinja2)

Der Report zeigt:
- Gesamtübersicht (Pass/Fail Score)
- Side-by-Side Vergleich der drei Tools
- Checklisten-Matrix (WCAG/BIK BITV)
- Detailansicht je Violation mit betroffenen Elementen
- Manuelle Prüfschritte die noch notwendig sind

```
Report-Struktur:
┌─────────────────────────────────────────┐
│  Accessibility Audit Report             │
│  URL: https://example.com               │
│  Score: 87% (WCAG 2.2 AA)              │
├─────────┬──────────────┬────────────────┤
│  axe    │  Lighthouse  │  IBM Checker   │
│  47/52  │  89/100      │  23 Violations │
├─────────┴──────────────┴────────────────┤
│  BIK BITV-Test Prüfschritte            │
│  ✅ 9.1.1.1a  ❌ 9.1.3.1a  ⚠️ manual  │
├─────────────────────────────────────────┤
│  Violations Detail                      │
│  [CRITICAL] image-alt (axe + ibm)      │
│  [SERIOUS]  color-contrast (axe)        │
└─────────────────────────────────────────┘
```

---

## 7. PyPI-Veröffentlichung

### 7.1 Package-Konfiguration

```toml
# pyproject.toml (vollständig)

[project.urls]
Homepage = "https://github.com/dein-user/rf-accessibility-library"
Documentation = "https://rf-accessibility-library.readthedocs.io"
Repository = "https://github.com/dein-user/rf-accessibility-library"
Changelog = "https://github.com/dein-user/rf-accessibility-library/CHANGELOG.md"
"Bug Tracker" = "https://github.com/dein-user/rf-accessibility-library/issues"

[tool.setuptools.packages.find]
where = ["."]
include = ["AccessibilityLibrary*"]

[tool.setuptools.package-data]
AccessibilityLibrary = [
    "checklists/data/*.json",
    "reporters/templates/*.html",
    "reporters/templates/*.css",
]
```

### 7.2 Versioning (Semantic Versioning)

```
MAJOR.MINOR.PATCH
│     │     └── Bugfixes
│     └──────── Neue Keywords, neue Checklist-Versionen  
└────────────── Breaking Changes in der API
```

- `0.1.0` — MVP: axe-core + WCAG 2.1 Mapping
- `0.2.0` — Lighthouse Integration
- `0.3.0` — IBM Checker + BIK BITV Mapping
- `1.0.0` — Stable API, alle drei Tools, PyPI-Release

### 7.3 Build & Publish Workflow

```bash
# Lokal testen
pip install build twine
python -m build

# Test-Upload auf TestPyPI zuerst!
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ robotframework-accessibility-library

# Produktions-Upload
twine upload dist/*

# Dann installierbar via:
pip install robotframework-accessibility-library
```

### 7.4 Automatisches Release via GitHub Actions

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write  # OIDC für PyPI Trusted Publishing
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install build
      - run: python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
        # Kein API-Key nötig dank OIDC Trusted Publishing
```

---

## 8. CI/CD Pipeline Integration

### 8.1 GitHub Actions — Test-Pipeline

```yaml
# .github/workflows/tests.yml
name: Tests & Accessibility Checks

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          npm install -g axe-cli lighthouse @ibm/equal-access-checker
          rfbrowser init
      - name: Run unit tests
        run: pytest tests/unit -v
      - name: Run Robot Framework tests
        run: robot --outputdir results tests/robot/
      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: robot-results-${{ matrix.python-version }}
          path: results/

  accessibility-self-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check our own documentation page
        run: |
          pip install -e .
          rfbrowser init
          robot tests/robot/check_docs_accessibility.robot
```

### 8.2 Nutzung in Projekt-CI/CD

So können andere Teams die Library in ihrer eigenen Pipeline nutzen:

```yaml
# Beispiel für Nutzer der Library
name: Accessibility Gate

on:
  pull_request:
    branches: [main]

jobs:
  a11y-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - uses: actions/setup-node@v4
      - name: Install accessibility tools
        run: |
          pip install robotframework-accessibility-library
          npm install -g axe-cli lighthouse
          rfbrowser init
      - name: Run accessibility tests
        run: |
          robot \
            --variable URL:https://staging.meine-seite.de \
            --variable CHECKLIST:WCAG_22_AA \
            --outputdir a11y-results \
            tests/accessibility/
      - name: Publish Report
        uses: actions/upload-artifact@v4
        with:
          name: accessibility-report
          path: a11y-results/
      - name: Fail on critical violations
        run: |
          python -c "
          import json
          with open('a11y-results/summary.json') as f:
              data = json.load(f)
          if data['critical_violations'] > 0:
              exit(1)
          "
```

### 8.3 GitLab CI / Azure DevOps

```yaml
# GitLab CI
accessibility-test:
  image: python:3.11
  before_script:
    - apt-get update && apt-get install -y nodejs npm
    - pip install robotframework-accessibility-library
    - npm install -g axe-cli lighthouse
    - rfbrowser init
  script:
    - robot --outputdir results tests/accessibility/
  artifacts:
    paths:
      - results/
    reports:
      junit: results/output.xml
  allow_failure: false  # Pipeline blockieren bei Violations
```

---

## 9. Testing & Qualitätssicherung

### 9.1 Unit Tests (pytest)

```python
# tests/unit/test_axe_checker.py
import pytest
from unittest.mock import MagicMock, patch
from AccessibilityLibrary.checkers.axe_checker import AxeChecker

def test_axe_checker_parses_violations():
    checker = AxeChecker()
    mock_result = {
        "violations": [
            {
                "id": "image-alt",
                "impact": "critical",
                "tags": ["wcag2a", "wcag111"],
                "nodes": [{"html": "<img src='test.png'>"}]
            }
        ]
    }
    result = checker._parse_results(mock_result)
    assert len(result.violations) == 1
    assert result.violations[0].impact == "critical"

def test_wcag_mapping():
    checker = AxeChecker()
    violation = {"tags": ["wcag2a", "wcag111", "cat.text-alternatives"]}
    criteria = checker.map_to_wcag(violation)
    assert "1.1.1" in criteria
```

### 9.2 Integration Tests mit echter Seite

```python
# tests/integration/test_full_audit.py
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture
def browser_page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        yield page
        browser.close()

def test_full_audit_on_test_page(browser_page):
    """Testet gegen eine bewusst fehlerhafte Test-HTML-Seite."""
    browser_page.goto("file://tests/fixtures/bad_accessibility.html")
    # ... weitere Tests
```

### 9.3 Test-Fixture HTML

Erstelle `tests/fixtures/bad_accessibility.html` mit bekannten Violations für reproduzierbare Tests:

```html
<!-- Tests/fixtures/bad_accessibility.html -->
<!-- Enthält absichtliche Accessibility-Fehler für Tests -->
<img src="logo.png">  <!-- kein alt-Text: verletzt 1.1.1 -->
<div onclick="foo()">Klick mich</div>  <!-- kein role: verletzt 4.1.2 -->
<p style="color: #aaa">Geringer Kontrast</p>  <!-- verletzt 1.4.3 -->
```

---

## 10. Dokumentation

### 10.1 README.md Struktur

```markdown
# Robot Framework Accessibility Library

🔍 Comprehensive web accessibility testing for Robot Framework

## Quick Start
pip install robotframework-accessibility-library

## Features
- axe-core, Lighthouse, IBM Equal Access Checker
- WCAG 2.1 / 2.2 and BIK BITV-Test support
- HTML comparison reports
- CI/CD ready

## Keywords Documentation
[Link to full keyword docs]
```

### 10.2 Keyword-Dokumentation (libdoc)

Robot Framework kann automatisch Dokumentation aus Docstrings generieren:

```bash
# HTML-Dokumentation generieren
python -m robot.libdoc AccessibilityLibrary docs/AccessibilityLibrary.html

# Auf ReadTheDocs hosten oder als GitHub Pages
```

### 10.3 Beispiel-Projekte

Erstelle unter `docs/examples/` vollständige Beispiele:

- `basic_audit.robot` — Einfacher Schnelltest
- `full_bitv_audit.robot` — Vollständiger BIK BITV-Test
- `ci_integration.robot` — Für CI/CD optimiert
- `spa_testing.robot` — Single Page Applications (mit Warten auf JS)

---

## 11. Roadmap & Meilensteine

### Phase 1 — MVP (Wochen 1–3)
- [ ] Projektstruktur anlegen, pyproject.toml konfigurieren
- [ ] axe-core Integration (Playwright-basiert)
- [ ] WCAG 2.1 AA Checklist-Daten erstellen
- [ ] Basis-Keywords implementieren
- [ ] Unit Tests für Checker
- [ ] Einfacher HTML-Report

### Phase 2 — Multi-Tool (Wochen 4–6)
- [ ] Lighthouse Integration via CLI
- [ ] IBM Equal Access Checker Integration
- [ ] Vergleichs-Reporter (Side-by-Side)
- [ ] WCAG 2.2 Checklist ergänzen
- [ ] Integration Tests mit Playwright

### Phase 3 — BIK BITV & Reporting (Wochen 7–9)
- [ ] BIK BITV-Test Prüfschritte vollständig mappen
- [ ] Manuelle Prüfschritte dokumentieren und flaggen
- [ ] Erweiterte HTML-Reports mit Jinja2-Templates
- [ ] JSON-Export für weitere Verarbeitung
- [ ] Robot Framework Log-Integration

### Phase 4 — PyPI & CI/CD (Wochen 10–11)
- [ ] PyPI Trusted Publishing einrichten (TestPyPI zuerst)
- [ ] GitHub Actions Workflows (Tests + Publish)
- [ ] README & vollständige Keyword-Docs
- [ ] Erste Release 0.1.0 auf PyPI

### Phase 5 — Stabilisierung (Woche 12+)
- [ ] Community-Feedback einarbeiten
- [ ] Performance-Optimierung (parallele Tool-Ausführung)
- [ ] Azure DevOps / GitLab CI Beispiele
- [ ] ReadTheDocs Dokumentation
- [ ] Release 1.0.0

---

## 🔗 Wichtige Ressourcen

| Ressource | URL |
|-----------|-----|
| BIK BITV-Test | https://www.bitvtest.de |
| WCAG 2.2 | https://www.w3.org/TR/WCAG22/ |
| axe-core Regeln | https://dequeuniversity.com/rules/axe/ |
| IBM Checker Docs | https://www.ibm.com/able/toolkit/tools/ |
| RF Browser Library | https://robotframework-browser.org |
| PyPI Trusted Publishing | https://docs.pypi.org/trusted-publishers/ |
| libdoc Docs | https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#libdoc |

---

*Erstellt: 2025 | Lizenz: Apache 2.0*
