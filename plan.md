# План разработки: Accessibility Checker Library для Robot Framework

## Обзор проекта

**Цель**: Создать полнофункциональную open-source библиотеку для Robot Framework, которая проверяет доступность веб-сайтов, интегрирует несколько инструментов аксессибилити (axe-core, Lighthouse, IBM Accessibility Checker) и сравнивает результаты с чек-листами (WCAG 2.1, BIK BITV-Test).

**Технический стек**:
- Python 3.11+
- Robot Framework 7.x
- robotframework-browser
- axe-core, lighthouse, ibm-aix
- Packaging: pyproject.toml (modern setuptools)
- CI/CD: GitHub Actions
- PyPI distribution

**Требования**:
- Целостный пакет: library + примеры тестов + полная документация
- Поддержка всех стандартов WCAG и BIK BITV-Test
- Параллельный и последовательный режимы для инструментов (параметризуемо)

---

## ⚠️ КРИТИЧЕСКАЯ ФАЗА 0: Анализ версий и совместимости (Version Compatibility Matrix)

**ДОЛЖНА БЫТЬ ПЕРВОЙ** — это определяет всю архитектуру.

### 0.1 Анализ версионных зависимостей

**Проблема**: Каждый инструмент (Lighthouse, axe-core, IBM Checker) имеет собственные версии, и они НЕ совместимы произвольно:
- Версия инструмента != версия встроенного движка правил
- Версия инструмента != совместимая версия runtime (Node/Python)
- Версия инструмента != версия web surface (report UI, extension UI, engine archive)
- Один и тот же результат проверки может отличаться из-за версии браузера/движка, даже при одинаковом tool version

**Базовые подтвержденные факты (на 2026-05-29)**:
- Lighthouse 13.3.0, Node >=22.19, dependency: axe-core ^4.11.4
- axe-core 4.11.4 (пакетная runtime совместимость Node >=4, но build-tooling может требовать выше)
- IBM accessibility-checker 3.0.0, Node >=16, rule engine поставляется через date-based archives

**Что нужно сделать**:

### Текущий статус 0.1 (на 2026-06-05)

- [x] 1. Матрица совместимости создана и используется как source of truth:
  - docs/reports/matrices/version_matrix.json
  - docs/reports/matrices/compatibility_matrix.csv
  - docs/VERSION_COMPATIBILITY.md
- [~] 2. Поддерживаемые версии по каждому tool зафиксированы в отдельных tool-файлах.
  - Требование min/target/max formalized: выполнено в docs/tools/*.md
  - Дальше: поддерживать эти диапазоны синхронно с matrix updates.
- [~] 3. Mapping WCAG и BIK BITV-Test описан документально.
  - Дальше: поддерживать operational JSON artifacts в checklists/, config/, coverage/.
- [x] 4. Таблица совместимости создана:
  - docs/reports/matrices/compatibility_matrix.csv

1. **Создать матрицу совместимости** (source of truth):
  - `docs/reports/matrices/version_matrix.json`
  - `docs/reports/matrices/compatibility_matrix.csv`
   - `docs/VERSION_COMPATIBILITY.md`
   - Обязательные измерения для каждой строки матрицы:
     - `tool_package_version`
     - `embedded_engine_version`
     - `runtime_version` (Node/Python)
     - `web_ui_or_report_surface_version`
     - `python_wrapper_version`

2. **Определить поддерживаемые версии** каждого инструмента (версия минимум и максимум):
   - Lighthouse: v13.x baseline (Node >=22.19)
   - axe-core npm: v4.11.x baseline
   - IBM Checker: v3.x baseline (Node >=16)
   - Дополнительные constraint-ы от WCAG/BIK версий
   - Отдельные constraint-ы для Browser/Chrome channel и web report UI

3. **Mapping WCAG и BIK BITV-Test версии**:
   - BIK BITV-Test v3.0 → основан на WCAG 2.1 AA
   - Какие версии чек-листов поддерживает каждый инструмент?
   - Есть ли различия в интерпретации критериев?

   ⚠️ **Ключевая проблема**: инструменты покрывают только ЧАСТЬ критериев WCAG/BITV.
   Например:
   - axe-core покрывает ~57 из 78 WCAG 2.2 AA критериев
   - Lighthouse покрывает ~50 (пересечение с axe, но не полное)
   - IBM покрывает свой набор — частично пересекается с axe

   Это значит: нужен отдельный слой — **Standards Comparator** — который знает
   полный список WCAG/BITV-правил и отвечает на вопрос:
   - Критерий 1.4.3: axe→FAIL, IBM→FAIL, LH→не покрывает
   - Критерий 2.5.8 (новый в WCAG 2.2): только axe покрывает, остальные — нет
   - Критерий 3.2.5: ни один инструмент не покрывает → требует ручной проверки

4. **Версионирование самих стандартов (WCAG/BITV)**:
   - WCAG 2.0 → 2.1 → 2.2 → будущие версии
   - BIK BITV-Test v3.0 → возможны обновления
   - Наша библиотека должна хранить чек-листы как **версионированные данные**:
     - `checklists/wcag/wcag_2_1.json`, `checklists/wcag/wcag_2_2.json`
     - `checklists/bitv/bitv_3_0.json`
   - При появлении новой версии стандарта → добавляем новый файл, старый не удаляем
   - Comparator умеет работать с любой версией и показывать **diff между версиями**

5. **Создать таблицу совместимости** (docs/reports/matrices/compatibility_matrix.csv):
   ```
   Tool | Tool_Version | Embedded_Engine | Node_Requirement | Python_Requirement | Web_UI_Surface | WCAG_Baseline | BITV_Support | Python_Wrapper_Version
   Lighthouse | 13.3.0 | axe-core ^4.11.4 | >=22.19 | N/A | LH report renderer | 2.1 AA baseline | mapped by checklist | 0.1.0a
   axe-core | 4.11.4 | self | >=4 | N/A | consumer-defined | 2.x tags | mapped by checklist | 0.1.0a
   IBM checker | 3.0.0 | ACE archive | >=16 | N/A | IBM extension/report | vendor mapping | mapped by checklist | 0.1.0a
   ```

### 0.1.1 Архитектура потока данных (как всё работает вместе)

```
┌─────────────────────────────────────────────────────┐
│  СТАНДАРТЫ (версионированные, source of truth)      │
│  wcag_2_1.json / wcag_2_2.json / bitv_3_0.json      │
│  78 критериев / 98 прюфшрит — полный список         │
└──────────────────────┬──────────────────────────────┘
                       │ (эталон для сравнения)
                       ▼
┌─────────────────────────────────────────────────────┐
│  ИНСТРУМЕНТЫ (каждый покрывает свой subset)         │
│  axe 4.11.4 → покрывает ~57 критериев               │
│  Lighthouse 13.3.0 → покрывает ~50 критериев        │
│  IBM checker 3.0.0 → покрывает ~60 критериев        │
└──────────────────────┬──────────────────────────────┘
                       │ (результаты сканирования)
                       ▼
┌─────────────────────────────────────────────────────┐
│  COMPARATOR (ядро нашей библиотеки)                 │
│  1. Нормализует результаты всех инструментов        │
│  2. Маппит правила инструментов → WCAG/BITV ID      │
│  3. Для каждого критерия: status + кто нашёл        │
│  4. Помечает критерии без покрытия (gap analysis)   │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│  REPORTS (два вида)                                 │
│                                                     │
│  Per-tool reports:                                  │
│  ├── axe_report.html / .json                        │
│  ├── lighthouse_report.html / .json                 │
│  └── ibm_report.html / .json                        │
│                                                     │
│  Standards compliance report (главный):             │
│  ├── wcag_2_2_compliance.html / .json               │
│  │   ┌─────────┬──────┬──────┬──────┬───────────┐  │
│  │   │ Критер. │ axe  │ LH   │ IBM  │ Итог      │  │
│  │   ├─────────┼──────┼──────┼──────┼───────────┤  │
│  │   │ 1.1.1   │ FAIL │ FAIL │ FAIL │ ❌ FAIL   │  │
│  │   │ 1.3.1   │ PASS │ N/A  │ PASS │ ✅ PASS   │  │
│  │   │ 2.5.8   │ PASS │ N/A  │ N/A  │ ⚠️ PARTIAL│  │
│  │   │ 3.2.5   │ N/A  │ N/A  │ N/A  │ 👁 MANUAL │  │
│  │   └─────────┴──────┴──────┴──────┴───────────┘  │
│  └── bitv_3_0_compliance.html / .json               │
└─────────────────────────────────────────────────────┘
```

**Легенда статусов в standards report**:
- `❌ FAIL` — хотя бы один инструмент нашёл нарушение
- `✅ PASS` — все покрывающие инструменты прошли
- `⚠️ PARTIAL` — только часть инструментов покрывает этот критерий (остальные N/A)
- `👁 MANUAL` — ни один инструмент не покрывает → нужна ручная проверка
- `N/A` — инструмент не поддерживает этот критерий

**Версионирование стандартов в отчёте**:
Каждый запущенный отчёт фиксирует:
- Какую версию WCAG/BITV использовали как эталон
- Что изменилось по сравнению с предыдущим запуском (если есть базовый отчёт)

### 0.2 Архитектурное решение: Pure Python vs. Node.js Wrapper

**Вы спросили**: Стоит ли копировать Browser Library (JS → Node → Python wrapper)?

**Ответ: НЕТ** — вот почему:

**Browser Library архитектура**:
```
Robot Keywords (Python)
    ↓ (gRPC)
Python Wrapper
    ↓ (gRPC)  
Node.js Server (TypeScript)
    ↓
Playwright (Chromium engines)
```
✅ Нужна для Browser Library, потому что:
- Playwright-core требует прямого контроля браузера на Node.js уровне
- Нужны асинхронные операции и гонки между процессами
- Сложный код лучше на TS

❌ **Не нужна для Accessibility Checker**, потому что:
- Все инструменты (axe, lighthouse, ibm) уже имеют Python API или REST endpoints
- Нет нужды в низкоуровневом контроле браузера отдельно
- Pure Python simpler = easier debugging, contributions, installation
- Node.js не обязателен для базового режима (axe+IBM), но обязателен для Lighthouse-адаптера

**Рекомендуемая архитектура**:
```
Robot Keywords (Python)
    ↓
Python Library (session_orchestrator + state_bridge + tools + comparator + reporter)
  ↓
State Bridge (единый доступ к Browser Library context/page/storage)
  ↓
Инструменты-адаптеры (axe/lighthouse/ibm), все читают один и тот же runtime state
```

**Ключевой runtime-сценарий (обязательный): проверка ВНУТРИ теста, а не только по статичному URL**

Библиотека должна уметь делать accessibility checkpoints в любом месте Robot-сценария:

```robot
*** Test Cases ***
Checkout Flow
  Login
  Go To    ${url1}
  Make Accessibility Report    checkpoint=after_login
  Click    ${selector}
  Wait For Elements State    ${dialog}    visible
  Fill Text    ${input}    ${text}
  Make Accessibility Report    checkpoint=after_dialog
```

То есть продукт проектируется как stateful scanner:
- использует текущий Browser Library context/page
- не сбрасывает cookies/localStorage/sessionStorage между checkpoint-сканами
- умеет сравнивать снимки между checkpoint-ами (regression in flow)
2
Ключевое правило: связь с Browser Library обязательна для ВСЕХ checker-ов, не только для Lighthouse.
- axe adapter работает на текущем page DOM из Browser Library
- IBM adapter работает на том же page/context
- Lighthouse adapter использует тот же state через attached/isolated стратегию

Для Lighthouse это отдельная сложность: по умолчанию Lighthouse часто стартует изолированно и теряет login state.
Поэтому в архитектуре фиксируем 2 режима Lighthouse:
- `lighthouse_mode=session_attached` (предпочтительный): подключение к уже запущенному Chromium/CDP в рамках текущей сессии
- `lighthouse_mode=isolated` (fallback): отдельный запуск с явным импортом auth state (cookies/storage) и пометкой о меньшей надёжности для сложных SPA-flow

Чтобы исключить расхождения между tool-ами, вводим обязательный промежуточный слой:
- `Session Orchestrator` — жизненный цикл accessibility session в рамках Robot-теста
- `State Bridge` — сериализация/восстановление runtime state (url, cookies, localStorage/sessionStorage, active context/page)
- `Tool Adapters` — единый контракт `run(snapshot)` для axe/lighthouse/ibm

### 0.3 Стратегия обновлений и миграции версий

**Проблема**: "Как не сломать всю систему при обновлении?"

**Решение: Версионная политика с backward compatibility**:

1. **Pinned dependencies в pyproject.toml** (для стабильности):
   ```toml
   # Критические зависимости - точно зафиксированы
   lighthouse == 12.0.0
   axe-core == 4.8.3
   
   # Гибкие зависимости - minor версии допускаются
   robotframework >= 7.0, < 8.0
   robotframework-browser >= 17.0, < 18.0
   ```

2. **Миграционные версии для новых инструментов**:
   - v0.1.0: baseline (lighthouse v12, axe v4.8)
   - v0.2.0: добавляем IBM Checker, дополнительные mappings
   - v0.3.0: поддержка Lighthouse v13 (если выходит)
   - v1.0.0: стабильная версия с доказанной совместимостью

3. **Breaking changes policy**:
   - MAJOR: меняется поддержка стандартов или архитектура
   - MINOR: новые инструменты или стандарты
   - PATCH: баг-фиксы, улучшения comparator-а

4. **Документация обновлений** (UPGRADE.md):
   - Какие версии инструментов используются в каждой версии
   - Как обновиться между версиями
   - What breaks, what doesn't

### 0.4 Вывод Фазы 0: Архитектурные решения

**Принято**:
- ✅ Pure Python-only библиотека (без Node.js wrapper)
- ✅ Pinned versions для критических инструментов
- ✅ Version compatibility matrix как source of truth
- ✅ Backward compatibility policy (MAJOR.MINOR.PATCH)
- ✅ Фаза 2 будет использовать эту матрицу для wrapper-ов
- ✅ Чеклисты WCAG/BITV и карты покрытия генерируются скриптами → коммитятся в репо как статические JSON
- ✅ Comparator работает с локальными JSON (нет runtime-запросов к W3C / bitvtest.de)

---

### 0.5 Скрипты генерации данных (Data Bootstrap Scripts)

**Проблема**: Чеклисты WCAG/BITV и карты покрытия инструментов нельзя писать вручную —
слишком много данных, они меняются при обновлении стандартов и инструментов.
Нужны автоматические скрипты-загрузчики.

#### 0.5.1 Откуда берутся данные

**WCAG 2.1 / 2.2:**
- W3C ведёт официальный GitHub: https://github.com/w3c/wcag
- Там есть machine-readable XML/JSON исходники с ID критериев, уровнями, описаниями
- Альтернатива: парсинг JSON-LD из https://www.w3.org/TR/WCAG21/ / WCAG22/

**BIK BITV-Test v3.0:**
- bitvtest.de — HTML-страницы Prüfschritte; нет готового machine-readable формата
- Скрипт делает scraping: список Prüfschritte с маппингом на WCAG ID
- Источник: https://www.bitvtest.de/pruefverfahren/bitv-2-0-nach-eu-standard

**Покрытие axe-core:**
- Каждое правило axe имеет массив тегов: `wcag111`, `wcag143`, `wcag22aa` и т.д.
- Источник 1 (без Node.js): GitHub API — raw JSON файлы правил
  `https://raw.githubusercontent.com/dequelabs/axe-core/develop/doc/rule-descriptions.md`
- Источник 2 (с Node.js): `node -e "const a=require('axe-core'); console.log(JSON.stringify(a.getRules()))"`
- Тег `wcag111` = критерий 1.1.1, `wcag143` = 1.4.3, `wcag22aa` = признак WCAG 2.2 AA

**Покрытие Lighthouse:**
- Каждый accessibility audit — отдельный файл в `core/audits/accessibility/`
  `https://github.com/GoogleChrome/lighthouse/tree/main/core/audits/accessibility/`
- Каждый файл содержит ссылку на axe rule ID → маппим axe rule → WCAG критерий
- Скрипт: GitHub API list directory → скачать каждый JS/TS файл → извлечь meta.id и axe rule ref

**Покрытие IBM Equal Access:**
- Правила в `accessibility-checker-engine/src/v4/rules/`
  `https://github.com/IBMa/equal-access/tree/main/accessibility-checker-engine/src/v4/rules`
- Каждое правило содержит маппинг на `WCAG_X_X_X` или политику IBM_Accessibility
- Дополнительно: `ibm-accessibility-checker --list-rules` (если установлен)

#### 0.5.2 Структура скриптов

```
scripts/                              # утилиты разработчика, не часть пакета
├── fetch_wcag_checklist.py           # Скачивает WCAG 2.1 и 2.2 с W3C GitHub
├── fetch_bitv_checklist.py           # Scraping bitvtest.de → BITV Prüfschritte JSON
├── fetch_axe_coverage.py             # axe-core rules → WCAG mapping (через теги)
├── fetch_lighthouse_coverage.py      # LH audits → axe rule → WCAG mapping
├── fetch_ibm_coverage.py             # IBM rules → WCAG mapping
├── generate_bitv_axe_embeddings.py   # ⭐ Embedding-based BITV candidates (multilingual semantic matching)
├── generate_coverage_map.py          # Объединяет WCAG + BITV coverage в итоговый coverage_map.json
├── config/
│   └── bitv_axe_mapping.json         # Curated mapping Prüfschritte → axe/IBM/LH rules (вручную после embeddings)
└── README.md                         # Как запустить, когда обновлять
```

Выходные файлы (в репозитории, закоммичены как source of truth):
```
checklists/
├── wcag_2_1.json          # 78 критериев, сгенерировано fetch_wcag_checklist.py
├── wcag_2_2.json          # 87 критериев
└── bitv_3_0.json          # 98 Prüfschritte (описания + метаданные)

config/
└── bitv_axe_mapping.json  # Curated mapping: {bitv_id → {axe_rules, ibm_rules, lh_audits}}

coverage/
├── axe_core_coverage.json            # {rule_id: {wcag: ["1.1.1", "1.3.1"], level: "AA"}}
├── lighthouse_coverage.json          # {audit_id: {axe_rule: "...", wcag: ["1.1.1"]}}
├── ibm_coverage.json                 # {rule_id: {wcag: ["1.1.1"], policy: "IBM_Accessibility"}}
├── bitv_coverage.json                # {bitv_id: {axe_rules: [...], wcag_equivalent: "1.1.1"}}
└── coverage_map.json                 # Итог: {wcag + bitv} с полным mapping
```

#### 0.5.3 Формат coverage_map.json

```json
{
  "generated_at": "2026-05-29T10:00:00Z",
  "tool_versions": {
    "axe_core": "4.11.4",
    "lighthouse": "13.3.0",
    "ibm_checker": "3.0.0"
  },
  "wcag_version": "2.2",
  "criteria": {
    "1.1.1": {
      "level": "A",
      "covered_by": ["axe", "lighthouse", "ibm"],
      "axe_rules": ["image-alt", "input-image-alt", "area-alt"],
      "lighthouse_audits": ["image-alt"],
      "ibm_rules": ["RPT_Img_UsemapAlt", "WCAG20_Input_ExplicitLabel"]
    },
    "2.5.8": {
      "level": "AA",
      "wcag_version_introduced": "2.2",
      "covered_by": ["axe"],
      "axe_rules": ["target-size"],
      "lighthouse_audits": [],
      "ibm_rules": []
    },
    "3.3.7": {
      "level": "A",
      "wcag_version_introduced": "2.2",
      "covered_by": [],
      "axe_rules": [],
      "lighthouse_audits": [],
      "ibm_rules": [],
      "status": "MANUAL_ONLY"
    }
  }
}
```

#### 0.5.4 Специфика BITV mapping (semantic matching через описания)

⚠️ **Отличие от WCAG mapping**: BITV — это отдельный стандарт, не просто перемаппинг WCAG критериев.

BITV 3.0 содержит 98 Prüfschritte, организованные в модули (Модуль A, B, C, D, E, F).
Каждый Prüfschritt имеет:
- Описание (на немецком)
- Методологию проверки (как проверить)
- Связь с WCAG 2.1 AA (но разная структура)

**Проблема**: Невозможно маппить BITV → axe-core через простые теги, как с WCAG.
Нужно **семантическое сопоставление через описания**.

**Пример**:
```
BITV Prüfschritt 1.1.1a "Nicht-Text-Inhalte"
  Beschreibung: Bilder, Icons, Diagramme müssen alt-Text haben
  
axe-core rule: "image-alt"
  tags: ["wcag111", "wcag21a", "images"]
  
Mapping: BITV 1.1.1a ← semantically matches → axe "image-alt"
```

**Как это реализовать**:

Вариант 1 (Embedding-based semantic matching — полуавтоматизировано):
- Скачиваем описания всех Prüfschritte (scraping bitvtest.de)
- Скачиваем описания всех axe-core правил
- Генерируем embeddings (например, с помощью `sentence-transformers` и multilingual модели типа `distiluse-base-multilingual-cased-v2`)
- Считаем семантическое сходство (cosine similarity) между каждым Prüfschritt и каждым axe-rule
- Автоматически рекомендуем top-3 matching правила с score для каждого Prüfschritt
- **Результат:** `config/bitv/bitv_axe_mapping_candidates.json` с оценками уверенности
- Куратор **вручную проверяет** и подтверждает → финальный `config/bitv/bitv_axe_mapping.json`
- Преимущество: быстро находит кандидатов, но финальное решение остаётся в руках человека
- Недостаток: требует установки `sentence-transformers`, зависит от качества embeddings модели

**Реализация варианта 1:**
```python
# scripts/generate_bitv_axe_embeddings.py

from sentence_transformers import SentenceTransformer, util
import json

# Загружаем мультиязычную модель (понимает немецкий + английский)
model = SentenceTransformer('distiluse-base-multilingual-cased-v2')

# Загружаем Prüfschritte descriptions (уже скрепленные fetch_bitv_checklist.py)
# Источник: https://www.bitvtest.de/pruefverfahren/bitv-2-0-nach-eu-standard
with open('checklists/bitv/bitv_3_0.json', 'r', encoding='utf-8') as f:
    bitv_data = json.load(f)

# Загружаем axe-core descriptions  
# Источник 1 (без Node): https://raw.githubusercontent.com/dequelabs/axe-core/develop/doc/rule-descriptions.md
# Источник 2 (с Node): node -e "const a=require('axe-core'); console.log(JSON.stringify(a.getRules()))"
with open('coverage/tools/axe_core_coverage.json', 'r') as f:
    axe_data = json.load(f)

# Генерируем embeddings для всех Prüfschritte
# Вектор каждого описания в 384-мерном пространстве (семантическое представление смысла)
bitv_embeddings = {}
for bitv_id, bitv_info in bitv_data['pruefschritte'].items():
    # Комбинируем title + description для более полного контекста
    text = f"{bitv_id}: {bitv_info['title']}. {bitv_info['description']}"
    bitv_embeddings[bitv_id] = model.encode(text, convert_to_tensor=True)

# Генерируем embeddings для всех axe-rule descriptions
axe_embeddings = {}
for rule_id, rule_info in axe_data.items():
    text = f"{rule_id}: {rule_info.get('description', rule_info.get('help', ''))}"
    axe_embeddings[rule_id] = model.encode(text, convert_to_tensor=True)

# Считаем сходство (cosine similarity: число от 0.0 до 1.0)
# и находим top-3 matching правила для каждого Prüfschritt
candidates = {}
for bitv_id, bitv_emb in bitv_embeddings.items():
    similarities = {}
    for rule_id, rule_emb in axe_embeddings.items():
        # cosine_similarity: сколько похожи два вектора
        # 1.0 = идентичны, 0.5 = среднее сходство, 0.0 = совсем разные
        sim = util.pytorch_cos_sim(bitv_emb, rule_emb)[0][0].item()
        similarities[rule_id] = sim
    
    # Top-3 с наибольшим сходством
    top_3 = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:3]
    candidates[bitv_id] = [
        {"rule": rule_id, "similarity_score": score}
        for rule_id, score in top_3
    ]

# Сохраняем как candidates.json для review человеком
with open('config/bitv/bitv_axe_mapping_candidates.json', 'w', encoding='utf-8') as f:
    json.dump(candidates, f, indent=2, ensure_ascii=False)

print(f"Generated {len(candidates)} candidate mappings")
print("Review config/bitv/bitv_axe_mapping_candidates.json and confirm in bitv_axe_mapping.json")
print("\nEdge cases to focus on:")
for bitv_id, cands in candidates.items():
    # Edge cases: score < 0.70 (куратор сосредоточивается здесь)
    if cands and cands[0][1] < 0.70:
        print(f"  {bitv_id}: top score {cands[0][1]:.2f} (needs manual review or MANUAL_ONLY)")
```

**Интерпретация scores:**

```
Score > 0.85  → ✅ Обычно правильное (embedding нашёл хорошее совпадение)
Score 0.70-0.85 → ⚠️ Нужна проверка (есть сходство, но не идеальное)
Score < 0.70  → 🔍 Edge case (не очень похожи, требует внимания куратора)
Score 0.0     → 👁 Ничего не нашлось (скорее всего MANUAL_ONLY)
```

**Использование**:
```bash
python scripts/generate_bitv_axe_embeddings.py
# Генерирует config/bitv/bitv_axe_mapping_candidates.json с рекомендациями

# Куратор открывает файл, смотрит на similarity_score:
# - score > 0.85 — часто правильное, быстрая проверка
# - score 0.7-0.85 — нужно проверить, прочитать описания обоих
# - score < 0.7 — edge cases, вероятно MANUAL_ONLY или требует исследования
# - score 0.0 — no candidates, точно MANUAL_ONLY

# Затем вручную создаёт config/bitv/bitv_axe_mapping.json с подтверждениями
```

---

Вариант 2 (Curated mapping config — полностью надёжный):
- Вручную составляем `config/bitv/bitv_axe_mapping.json` — явный mapping каждого Prüfschritt → правила (axe + IBM + LH)
- Один раз при создании, затем обновляем при новых версиях стандартов
- Структура:
  ```json
  {
    "bitv_3_0": {
      "mappings": {
        "1.1.1a": {
          "title": "Nicht-Text-Inhalte",
          "description": "Alle Nicht-Text-Inhalte müssen alt-Text haben",
          "mapped_to": {
            "axe_rules": ["image-alt", "input-image-alt", "area-alt"],
            "ibm_rules": ["RPT_Img_UsemapAlt"],
            "lighthouse_audits": ["image-alt"]
          },
          "wcag_equivalent": "1.1.1"
        },
        "2.4.11b": {
          "title": "Fokusreihenfolge",
          "description": "Fokusreihenfolge muss logisch sein",
          "mapped_to": {
            "axe_rules": ["focusorder"],
            "ibm_rules": ["RPT_Focusorder"],
            "lighthouse_audits": []
          },
          "wcag_equivalent": "2.4.3",
          "notes": "BITV требует больше строгости, чем WCAG 2.4.3"
        },
        "3.2.5c": {
          "title": "Change on Request (ручная проверка)",
          "description": "Контекст должен меняться только по явному запросу",
          "mapped_to": {
            "axe_rules": [],
            "ibm_rules": [],
            "lighthouse_audits": []
          },
          "wcag_equivalent": "3.2.5",
          "status": "MANUAL_ONLY"
        }
      }
    }
  }
  ```

**Скрипты для BITV mapping**:
```
scripts/
├── fetch_bitv_checklist.py       # Scraping bitvtest.de → bitv_3_0.json
├── create_bitv_axe_mapping.py    # Вручную создаём config/bitv/bitv_axe_mapping.json
└── generate_bitv_coverage_map.py # Преобразует mapping → bitv_coverage.json
```

**Выходные файлы**:
```
config/
└── bitv_axe_mapping.json          # Curated mapping (вручную + версионировано)

coverage/
├── bitv_coverage.json             # {bitv_id: {axe_rules: [...], ibm_rules: [...], wcag_equivalent: "X.X.X"}}
└── coverage_map.json              # Объединённая матрица: WCAG + BITV
```

**Обновление политики для BITV**:
| Событие | Действие | Примечание |
|---------|----------|-----------|
| Новая версия BITV | `fetch_bitv_checklist.py` + ручной review `bitv_axe_mapping.json` | Могут появиться новые Prüfschritte |
| Новая версия axe-core | Обновляем `bitv_axe_mapping.json` + `generate_bitv_coverage_map.py` | Могут появиться новые rules, старые могут изменить поведение |
| Обнаружена неточность в mapping | Корректируем `bitv_axe_mapping.json` + коммит с note | Кураторское обслуживание |

#### 0.5.5 Итоговый формат coverage_map.json (WCAG + BITV)

```json
{
  "generated_at": "2026-05-29T10:00:00Z",
  "tool_versions": {
    "axe_core": "4.11.4",
    "lighthouse": "13.3.0",
    "ibm_checker": "3.0.0"
  },
  "standards": {
    "wcag_2_2": {
      "version": "2.2",
      "total_criteria": 87,
      "criteria": {
        "1.1.1": {
          "level": "A",
          "covered_by": ["axe", "lighthouse", "ibm"],
          "axe_rules": ["image-alt"],
          "bitv_equivalent": "1.1.1a"
        },
        "2.5.8": {
          "level": "AA",
          "wcag_version_introduced": "2.2",
          "covered_by": ["axe"],
          "axe_rules": ["target-size"],
          "bitv_equivalent": null,
          "note": "Критерий новый в WCAG 2.2, в BITV 3.0 нет эквивалента"
        }
      }
    },
    "bitv_3_0": {
      "version": "3.0",
      "total_pruefschritte": 98,
      "base_standard": "WCAG 2.1 AA",
      "pruefschritte": {
        "1.1.1a": {
          "title": "Nicht-Text-Inhalte",
          "wcag_equivalent": "1.1.1",
          "covered_by": ["axe", "ibm"],
          "axe_rules": ["image-alt", "input-image-alt"],
          "ibm_rules": ["RPT_Img_UsemapAlt"],
          "lighthouse_audits": []
        },
        "3.2.5c": {
          "title": "Change on Request",
          "wcag_equivalent": "3.2.5",
          "covered_by": [],
          "status": "MANUAL_ONLY",
          "note": "Требует человеческого суждения, автоматическая проверка невозможна"
        }
      }
    }
  }
}
```

#### 0.5.6 Политика обновления скриптов

| Триггер | Действие | Кто запускает |
|---------|----------|---------------|
| Новая версия axe-core | `python scripts/fetch_axe_coverage.py` | CI или разработчик |
| Новая версия Lighthouse | `python scripts/fetch_lighthouse_coverage.py` | CI или разработчик |
| Новая версия IBM checker | `python scripts/fetch_ibm_coverage.py` | CI или разработчик |
| Новая версия WCAG | `python scripts/fetch_wcag_checklist.py --version 2.3` | Разработчик вручную |
| Обновление BITV (Prüfschritte) | `python scripts/fetch_bitv_checklist.py` | Разработчик вручную |
| **BITV маппинг (embedding)** | **`python scripts/generate_bitv_axe_embeddings.py`** | **Разработчик → генерирует candidates** |
| **BITV маппинг (review)** | **Куратор проверяет `config/bitv/bitv_axe_mapping_candidates.json` → создаёт `config/bitv/bitv_axe_mapping.json`** | **Куратор (человек, обязательно!)** |
| После любого из выше | `python scripts/generate_coverage_map.py` | Всегда в конце |

После генерации → файлы в `checklists/`, `coverage/`, `config/` коммитятся в репозиторий.
Comparator работает с этими статическими JSON → никаких runtime-запросов к внешним сайтам.

**Dependencies для `scripts/generate_bitv_axe_embeddings.py`:**
```toml
[project.optional-dependencies]
bootstrap = [
    "sentence-transformers>=2.2.2",
    "torch>=2.0.0",
    "requests>=2.31.0",
    "beautifulsoup4>=4.12.0"  # для scraping bitvtest.de
]
```

**Установка для разработчика:**
```bash
pip install -e ".[bootstrap]"
python scripts/generate_bitv_axe_embeddings.py
```

---

## Фаза 1: Подготовка проекта (Foundation)

### 1.1 Инициализация структуры проекта
- Создать `pyproject.toml` с конфигурацией для современного упаковки (setuptools + wheel)
- Создать `src/robotframework_accessibility_checker/` — главный пакет библиотеки
- Создать `tests/` директорию с примерами Robot тестов
- Создать `docs/` для документации (README, API docs, примеры)
- Добавить `LICENSE` (рекомендуется MIT или Apache 2.0)
- Создать `.gitignore` и `.editorconfig`
- Инициализировать `MANIFEST.in` для включения в распределение

### 1.2 Зависимости в pyproject.toml
- robotframework >= 7.0
- robotframework-browser >= 17.0
- selenium или драйверы для axe-core
- axe-python-selenium (или собственная обертка для axe-core)
- lighthouse (Node.js requirement — будет задокументировано)
- pip install ibm-aix или аналог IBM Accessibility Checker API
- requests (для REST API calls)
- json для обработки результатов

**Критические зависимости** (pinned версии из version_matrix):
```toml
# Версии из phase 0 version matrix
lighthouse == 12.0.0     # фиксированная версия для стабильности
axe-core == 4.8.3        # фиксированная версия
```

### 1.3 Версионирование и метаданные
- Установить версию 0.1.0a (alpha) — соответствует базовым версиям инструментов
- Использовать version matrix для отслеживания совместимости
- UPGRADE.md документировать как переходить между версиями
- Автоматизировать обновление версии через CI (bumpversion или аналог)

---

## Фаза 2: Разработка основной библиотеки (Core Library)

### 2.1 Структура пакета
```
src/robotframework_accessibility_checker/
├── __init__.py
├── keywords.py          # Main keyword library для Robot Framework
├── session_orchestrator.py  # Управление stateful accessibility session и checkpoint timeline
├── state_bridge.py      # Интеграция с Browser Library (context/page/storage state)
├── tools/
│   ├── __init__.py
│   ├── axe_core.py      # Wrapper для axe-core
│   ├── lighthouse.py    # Wrapper для Lighthouse
│   └── ibm_checker.py   # Wrapper для IBM Accessibility Checker
├── checklists/
│   ├── __init__.py
│   ├── wcag_checklist.py   # WCAG 2.1 Level A/AA/AAA references
│   └── bitv_test_checklist.py  # BIK BITV-Test rules
├── comparator.py        # Сравнение результатов инструментов с чек-листами
├── reporter.py          # Генерирование отчетов (JSON, HTML, console)
└── utils.py            # Helper функции
```

### 2.2 Основной keyword library (keywords.py)
Должен предоставлять следующие keywords (Robot Framework style):
- `Open Browser For Accessibility Testing` — инициализирует браузер с Browser Library
- `Run Accessibility Check [URL] | Run On Current Page` — запускает проверку(и)
- `Start Accessibility Session` — начинает stateful-сессию сбора accessibility-результатов в рамках текущего теста
- `Make Accessibility Report` / `Capture Accessibility Checkpoint` — снимает checkpoint на ТЕКУЩЕЙ странице без потери login/session state
- `Run Accessibility Check With Axe` / `Run With Lighthouse` / `Run With IBM Checker` — инструмент-специфичные keywords
- `Compare Results With WCAG Checklist`
- `Compare Results With BIK BITV Test`
- `Get Accessibility Report` — возвращает структурированный отчет
- `Assert No Accessibility Violations` — для assert-ов в тестах
- `Export Report To JSON` / `Export Report To HTML`

### 2.3 Инструменты (tools/)
Каждый tool должен быть задокументирован с примерами:

**axe_core.py**:
- Инициализация с конфигурацией (tags для фильтрации результатов)
- Запуск axe-core на странице через JavaScript injection
- Обязательно использует активный Browser Library page/context из `state_bridge.py`
- Парсинг результатов в стандартный формат

**lighthouse.py**:
- Запуск Lighthouse CLI (требует Node.js)
- Поддержка `session_attached` режима для работы в уже открытой браузерной сессии (после Login)
- Fallback `isolated` режим с явным переносом auth state
- Получает state через `state_bridge.py` по тому же контракту, что и другие checker-ы
- Обработка accessibility category
- Извлечение rules и scores

**ibm_checker.py**:
- Интеграция с IBM Accessibility Checker API или npm пакетом
- Использует тот же Browser Library context/page (без отдельного логина/открытия новой страницы)
- Параметризация уровня проверки (WCAG 2.1 Level, Early Release rules)

Единый контракт адаптеров (обязательный):
```python
class ToolAdapter(Protocol):
  def run(self, snapshot: BrowserSnapshot) -> ToolResult:
    ...
```

### 2.4 Чек-листы (checklists/)
- `wcag_checklist.py`: Структура для WCAG 2.1 правил (принципы, гайдлайны, критерии успеха)
  - Уровни: A, AA, AAA
  - Доступ к метаданным (описание, примеры, техники)
- `bitv_test_checklist.py`: BIK BITV-Test спецификация
  - Модули (структура, контент, диалоги и т.д.)
  - Mapping между WCAG и BITV

### 2.5 Comparator (comparator.py)
Алгоритм сравнения:
- Нормализация результатов от разных инструментов в единый формат
- Маппинг между issue-ами инструментов и WCAG/BITV правилами
- Обнаружение консенсуса между инструментами
- Детекция false positives/negatives
- Генерирование матрицы согласия (какие инструменты нашли какие проблемы)

### 2.6 Reporter (reporter.py)
- JSON export (для CI/CD потребления)
- HTML report (красивый view с графиками)
- Console output (для локального запуска)
- Summary metrics (общее количество issues, по инструментам, по стандартам)

### 2.7 Конфигурация и параметризация
- Environment variables: `ACCESSIBILITY_CHECKER_MODE` (parallel / sequential)
- Robot Framework global variables: `TOOLS`, `CHECKLIST_STANDARD`, `REPORT_FORMAT`
- Lighthouse execution mode: `LIGHTHOUSE_MODE=session_attached|isolated`
- Stateful checkpoints: `ACCESSIBILITY_CHECKPOINT_MODE=per_step|manual`
- Логирование с разными уровнями debug/info

### 2.8 Stateful Flow и сохранение login/session state (критично)

Проблема из предыдущего JS-модуля: Lighthouse открывал новую страницу/контекст и терял storage state после Login.

Архитектурное требование для этой библиотеки:
- `Make Accessibility Report` всегда читает текущее состояние Browser Library (активная страница)
- axe/IBM запускаются прямо на текущем DOM после действий теста
- Lighthouse запускается в режиме `session_attached`, где возможно
- Любой checker получает snapshot из одного источника (`state_bridge.py`), чтобы исключить рассинхрон

Порядок выполнения checkpoint (единый pipeline):
1. Session Orchestrator запрашивает `BrowserSnapshot` у State Bridge
2. Snapshot передаётся всем выбранным checker-ам (axe/lighthouse/ibm)
3. Каждый checker возвращает результат в общем формате
4. Comparator собирает единый статус по WCAG/BITV
5. Reporter добавляет checkpoint в timeline текущего теста

Минимальный контракт для результата checkpoint:

```json
{
  "test_name": "Checkout Flow",
  "checkpoint": "after_dialog",
  "url": "https://example/app/checkout",
  "stateful": true,
  "tools": {
    "axe": {"status": "ok", "violations": 3},
    "lighthouse": {"status": "ok", "mode": "session_attached", "score": 0.86},
    "ibm": {"status": "ok", "violations": 1}
  }
}
```

Итоговый отчёт должен поддерживать timeline checkpoint-ов внутри одного теста:
- `after_login`
- `after_dialog`
- `after_submit`

Это позволяет ловить регрессии доступности на динамических шагах (диалоги, формы, lazy-loaded блоки), а не только на стартовом URL.

---

## Фаза 3: Примеры и документация (Examples & Docs)

### 3.1 Примеры тестов (tests/robot/examples/)
- `01_simple_check.robot` — базовый пример проверки одного URL
- `02_multiple_urls.robot` — проверка нескольких страниц
- `03_wcag_compliance.robot` — проверка на WCAG AA compliance
- `04_bitv_test.robot` — BIK BITV-Test проверка
- `05_custom_configuration.robot` — параллельный/последовательный режим, фильтры
- `06_reporting.robot` — кастомные отчеты

Каждый пример должен быть полностью рабочим и запускаемым.

### 3.2 Документация
- **README.md**: Quick start, примеры, требования (Node.js для Lighthouse)
- **docs/INSTALLATION.md**: Пошаговые инструкции установки
- **docs/API.md**: Каждый keyword с параметрами, возвращаемых значениями, примерами
- **docs/CONFIGURATION.md**: Конфигурация инструментов, режимы, переменные
- **docs/STANDARDS.md**: Объяснение WCAG и BIK BITV-Test поддержки
- **docs/EXAMPLES.md**: Сценарии использования кейсы
- **docs/TROUBLESHOOTING.md**: Common issues и решения

### 3.3 Автодокументация
- Docstrings в Python коде в формате для robotdoc
- Генерирование `libdoc` для Robot Framework интеграции в IDE

---

## Фаза 4: Packaging и PyPI публикация

### 4.1 Packaging конфигурация
- Финализировать `pyproject.toml`:
  - metadata (name, version, description, author, license, urls)
  - dependencies и optional extras (docs, dev, test)
  - build-system (setuptools + wheel)
  - tool.setuptools.packages-find
  - project urls (GitHub, documentation, issues)
- Создать `MANIFEST.in` для non-Python файлов
- Создать `setup.cfg` (если нужно legacy compatibility)

### 4.2 Testing package локально
- `pip install -e .` (editable install)
- Запуск примеров тестов из installed package
- Проверка, что все keywords готовы для Robot Framework

### 4.3 PyPI публикация
- Регистрация на PyPI (тестовый и продакшен)
- Создание `.pypirc` конфиг (документированиия для CI)
- Build distribution: `python -m build`
- Загрузка на TestPyPI для проверки
- Загрузка на PyPI в GA (v1.0.0+)

### 4.4 Версионирование и релизы
- Semantic versioning: major.minor.patch
- Git tags для каждого релиза
- Changelog (CHANGELOG.md) с каждым рилизом

---

## Фаза 5: CI/CD интеграция (GitHub Actions)

### 5.1 Workflows файлы
- `.github/workflows/test.yml` — на каждый push:
  - Запуск Unit тестов (если они есть)
  - Запуск примеров Robot тестов на демо-сайте
  - Проверка кода (linting, type-checking)
- `.github/workflows/publish.yml` — на каждый релиз (tag):
  - Build package
  - Публикация на PyPI
- `.github/workflows/docs.yml` (опционально):
  - Генерирование и публикование документации на GitHub Pages

### 5.2 Тестирование в CI
- Тестирование на Python 3.11+ (параллельные версии)
- Загрузка необходимых зависимостей (Node.js для Lighthouse)
- Использование headless browsers для Robot тестов
- Проверка что package может быть установлен

### 5.3 Качество кода
- Linting: flake8 или ruff
- Type checking: mypy (опционально)
- Code coverage: coverage.py (опционально для unit тестов)

---

## Фаза 6: Финальная подготовка и публикация

### 6.1 Pre-release подготовка
- Последний раунд документации review
- Финальное тестирование на всех примерах
- Обновить CHANGELOG.md
- Обновить версию в pyproject.toml на v0.1.0 (или v1.0.0 если достаточно функционала)

### 6.2 GitHub релиз
- Создать Release с тегом
- Добавить summary и links в Release notes
- CI автоматически публикует на PyPI

### 6.3 Post-release
- Документация для пользователей как установить: `pip install robotframework-accessibility-checker`
- Создать примеры использования в README для быстрого старта новых пользователей

---

## Структура инструментов (параллельный/последовательный режим)

**Параллельный режим** (faster, better for comparing tools):
```
Run accessibility check (parallel):
├─ axe-core check (async)
├─ Lighthouse check (async)  
└─ IBM Checker (async)
→ Aggregated results with comparator
```

**Последовательный режим** (slower, detailed per-tool reports):
```
Run accessibility check (sequential):
├─ Run axe-core → report
├─ Run Lighthouse → report
└─ Run IBM Checker → report
→ Individual reports and comparison matrix
```

**Параметризация** (Robot Framework variable):
```robot
*** Test Cases ***
My Test
    Run Accessibility Checks    url=https://example.com
    ...    mode=parallel
    ...    tools=axe,lighthouse,ibm
    ...    standard=wcag
```

---

## Критические файлы для изменения/создания

- `pyproject.toml` — новый файл, конфиг
- `src/robotframework_accessibility_checker/` — новая директория с Python пакетом
- `tests/robot/examples/` — примеры Robot тестов
- `docs/` — документация
- `.github/workflows/` — CI/CD конфигурация
- `CHANGELOG.md` — версионирование изменений
- `LICENSE` — новый файл
- `.github/` — финал структура для релизов

---

## Порядок реализации (зависимости между фазами)

1. ⚠️ **Фаза 0**: Анализ версий и совместимости (VERSION FIRST!) 
  - Создать docs/reports/matrices/version_matrix.json
  - Создать docs/reports/matrices/compatibility_matrix.csv
   - Определить pinned versions в pyproject.toml
   - Документировать upgrade path

2. ✅ Фаза 1: Подготовка проекта (зависит от Фазы 0)

3. ✅ Фаза 2: Разработка основной библиотеки (зависит от Фаз 0+1)
   - 2.1-2.3: Разработка инструментов (используя version matrix) (параллельно)
   - 2.4-2.5: Чек-листы и компаратор (параллельно)
   - 2.6-2.7: Reporter и конфигурация (параллельно)

4. ✅ Фаза 3: Примеры и документация (зависит от Фазы 2)

5. ✅ Фаза 4: Packaging (зависит от Фазы 3)

6. ✅ Фаза 5: CI/CD (параллель с Фазой 4-6)

7. ✅ Фаза 6: Финальная подготовка и публикация (зависит от Фаз 3-5)

---

## Проверка и валидация

### Для каждой фазы:
1. **Фаза 1**: Проверить структура проекта, pyproject.toml валиден, .gitignore добавлен
2. **Фаза 2**: Запустить unit тесты для каждого tool и comparator
3. **Фаза 3**: Запустить все примеры Robot тестов локально
4. **Фаза 4**: `pip install .` успешно, импорт library работает в Robot Framework
5. **Фаза 5**: GitHub Actions workflows зеленые для каждого пуша и релиза
6. **Фаза 6**: `pip install robotframework-accessibility-checker` из PyPI работает, примеры из доков запускаются

---

## 📌 Дополнительные замечания

1. **Лицензирование зависимостей**: 
   - axe-core (есть npm лицензия) — проверить совместимость
   - Lighthouse (Apache 2.0)
   - IBM Accessibility Checker (проверить лицензию и API доступ)

2. **Node.js и Lighthouse**:
   - Lighthouse требует Node.js но как ОПЦИОНАЛЬНАЯ зависимость (для расширенных checks)
   - В CI/CD использовать setup-node@4 GitHub Action для тестирования
   - Документировать в INSTALLATION.md что Lighthouse requires Node.js

3. **Тестирование на реальных сайтах**:
   - Использовать demo-сайты для примеров (может быть localhost ил axe-demo)
   - Документировать как запустить собственный тест-сайт

4. **Расширяемость**:
   - Структура позволяет добавить новые инструменты в tools/
   - Структура позволяет добавить новые стандарты в checklists/
   - Version matrix будет путеводителем при добавлении новых инструментов

---

# Архитектурная справка: robotframework-browser (Browser Library)

## Обзор архитектуры Browser Library

**Browser Library** (v19.14.2) — это многоуровневая архитектура, которая может служить эталоном для проектирования accessibility-checker.

### Основные слои архитектуры:

```
Robot Framework Layer (Keywords)
    ↓
Python API Layer (robotframework-pythonlibcore)
    ↓
gRPC Client (Python)
    ↕ [Network IPC: localhost:port]
    ↑
gRPC Server (Node.js)
    ↓
Playwright Core (TypeScript/JavaScript)
    ↓
Browser APIs (Chromium, Firefox, WebKit)
```

### Ключевые компоненты:

1. **Слой пакета Python (pyproject.toml)**
   - Версия: 19.14.2 (synchronized с Node.js package.json)
   - Python требование: >= 3.10
   - Инструменты сборки: setuptools >= 61.0
   - Основные зависимости:
     * `robotframework >= 6.1.1, < 9.0.0`
     * `robotframework-pythonlibcore >= 4.4.1, < 5.0.0` (для Robot Framework интеграции)
     * `grpcio == 1.80.0` + `grpcio-tools == 1.80.0` (для gRPC коммуникации)
     * `protobuf == 6.33.6` (версия pinned, критично!)
   - Точное версионирование: используются == для критических зависимостей
   - Включение: скрипт `rfbrowser` как entry point в `[project.scripts]`

2. **Слой Node.js (package.json)**
   - Версия: 19.14.2 (synchronized с pyproject.toml)
   - Node.js requirement: LTS версии 20, 22, 24
   - DevDependencies: TypeScript 5.9.3, ESLint, Jest, esbuild
   - Runtime Dependencies:
     * `@grpc/grpc-js ^1.14.3` (gRPC server)
     * `playwright ^1.59.1` (браузер automation)
     * `@bufbuild/protobuf ^2.11.0` (протобуф клиент)
     * `pino ^10.3.1` (логирование)
     * `uuid ^13.0.0` (уникальные ID)

3. **Механизм коммуникации: gRPC + Protocol Buffers**
   - **Почему gRPC?** Высокопроизводительный RPC для Python-Node.js коммуникации
   - **Протобуф files**: в /protobuf папке (определяют API контракт)
   - **Синхронизация версий**: критично! protobuf версия == между Python и Node.js
   - **Спецификация сервиса**: PlaywrightService определена в protobuf
   - **Server инициализация**: Node.js запускается как отдельный процесс на localhost:[port]

4. **Build процесс (node/build.wrapper.js)**
   - **Bundler**: ESBuild (быстрый TypeScript bundler)
   - **Точка входа**: `node/playwright-wrapper/index.ts`
   - **Выход**: `Browser/wrapper/index.js` (bundled JavaScript)
   - **Плагины**: `esbuild-node-externals` для исключения большие зависимостей (playwright-core)
   - **Bundling strategy**: Playwright core остается external, чтобы избежать дублирования
   - **Coverage support**: опциональный sourcemap для code coverage

5. **Структура проекта**
   ```
   robotframework-browser/
   ├── Browser/                 # Python package
   │   ├── __init__.py
   │   ├── entry/               # CLI commands (rfbrowser command)
   │   ├── wrapper/             # Generated Node.js wrapper (bundled)
   │   │   ├── index.js         # Main entry point (bundled с esbuild)
   │   │   └── package.json
   │   └── ...                  # Python library code
   ├── node/                    # TypeScript/Node.js source
   │   ├── playwright-wrapper/  # gRPC server implementation
   │   │   ├── index.ts
   │   │   ├── grpc-service.ts
   │   │   └── ...
   │   ├── build.wrapper.js     # esbuild configuration
   │   ├── jest.config.cjs      # Testing configuration
   │   └── eslint.config.mjs    # Linting configuration
   ├── protobuf/                # Protocol Buffer definitions
   │   └── *.proto              # Service contracts
   ├── pyproject.toml           # Python packaging config
   ├── package.json             # Node.js dependencies
   └── ...
   ```

### Разделение ответственности:

| Слой | Язык | Ответственность |
|------|------|-----------------|
| Robot Framework Keywords | Python | Пользовательский интерфейс, тестирование |
| Python gRPC Client | Python | Сериализация аргументов, вызов сервиса |
| Protocol Buffers | Protobuf | API контракт между Python и Node.js |
| Node.js gRPC Server | TypeScript | Десериализация, маршрутизация к Playwright |
| Playwright | TypeScript | Фактическое управление браузером |

### Управление версиями и совместимостью:

1. **Версионирование**:
   - Единая версия: pyproject.toml и package.json синхронизированы
   - Major.Minor.Patch semantic versioning
   - Каждый релиз — общий тег в Git

2. **Dependency pinning стратегия**:
   - **Critical dependencies** (grpcio, protobuf, playwright): `== точная версия`
   - **Support libraries** (robotframework, robotframework-pythonlibcore): `>= min, < max`
   - **Package-lock.json**: для гарантированного воспроизведения Node.js окружения
   - **No pre-releases**: production dependencies должны быть stable

3. **Тестирование совместимости**:
   - CI/CD проверяет на нескольких версиях Python (3.10+)
   - CI/CD проверяет на нескольких версиях Node.js (20, 22, 24 LTS)
   - Test coverage для оба слоев (Node.js jest, Python unittest)

### Инсталяция и инициализация:

**Две модели поставки**:

1. **С Node.js установленным пользователем**:
   ```
   pip install robotframework-browser
   rfbrowser init  # Устанавливает Node deps, Playwright binaries
   ```

2. **Без Node.js (с robotframework-browser-batteries)**:
   ```
   pip install robotframework-browser[bb]
   rfbrowser install  # Только Playwright binaries
   ```

**Батарейки** (browser-batteries) предкомпилированный Node.js + dependencies для скорости.

### Применимые паттерны для Accessibility Checker:

1. **Не нужно использовать gRPC**:
   - Accessibility Checker может быть **pure Python** (все инструменты имеют Python API или CLI)
   - Нет нужды в отдельном Node.js процессе для основной функциональности
   - **Упрощение**: прямая интеграция, меньше точек отказа

2. **Используй синхронизированное версионирование**:
   - Одна версия in pyproject.toml
   - Update once, deploy everywhere

3. **Pinned dependencies для критических**:
   ```toml
   grpcio == 1.80.0  # Exact version if using gRPC
   robotframework >= 6.1.1, < 9.0.0  # Range for flexibility
   ```

4. **Разделение на слои** (даже без gRPC):
   ```
   Keywords (Robot Framework layer)
       ↓
   Library class (robotframework-pythonlibcore)
       ↓
   Tools (axe, lighthouse, ibm) as separate modules
       ↓
   Comparator & Reporter (utility layer)
   ```

5. **CLI entry point**:
   ```toml
   [project.scripts]
   accessibility-checker = "robotframework_accessibility_checker.entry:cli"
   ```

6. **Installation modes**:
   - Basic: `pip install robotframework-accessibility-checker`
   - With dev tools: `pip install robotframework-accessibility-checker[dev]`
   - Full with docs: `pip install robotframework-accessibility-checker[all]`

7. **Build & packaging**:
   - Используй setuptools с pyproject.toml (modern approach)
   - wheel для binary distribution
   - Не нужен nesting (accessibility checker — pure Python)

8. **Threading/Parallelization**:
   - Browser Library использует один Node.js процесс на браузер сессию
   - Для accessibility checker: use `concurrent.futures.ThreadPoolExecutor` или `asyncio` для параллельных проверок tools
   - Или используй `multiprocessing` для процесс-уровня изоляции

---

## Рекомендации для Accessibility Checker

**✅ Применить из Browser Library**:
- Synchronized versioning между файлами
- Pinned dependencies для stability
- Clear separation of concerns (keywords → library → tools)
- Optional extras in pyproject.toml
- Good documentation structure (README, API docs, examples)
- CI/CD on every commit and release

**❌ Избежать (сложность)**:
- gRPC (не нужен для чисто Python пакета)
- Multi-language build pipeline (TypeScript bundling)
- Отдельные процессы (Node.js wrapper)

**✨ Уникальные преимущества для Accessibility Checker**:
- Pure Python → simpler installation
- No external process management
- Easier to debug and contribute
- Works on any OS without Node.js requirement
- Faster startup time
