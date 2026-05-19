# Multi-Agent Procesoptimalisatie Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the process optimization app with a three-agent architecture: supervisor (intake for new companies), summary (background extraction to .md), and advisory (existing logic + loaded context).

**Architecture:** Sequential multi-agent flow — supervisor streams response to user, then frontend calls /api/summary which runs the summary agent silently to update the company .md and return missing_fields. When intake_complete is true, frontend switches to advisory mode. Existing companies skip straight to advisory.

**Tech Stack:** Python 3.14, Flask 3.x, Anthropic SDK (claude-sonnet-4-6), pytest, vanilla JS frontend

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `agent/supervisor_prompt.md` | CREATE | System prompt for intake supervisor agent |
| `agent/summary_prompt.md` | CREATE | System prompt for background extraction agent |
| `tests/conftest.py` | CREATE | Flask test client fixture |
| `tests/test_utils.py` | CREATE | Tests for slugify and parse_summary_response |
| `tests/test_endpoints.py` | CREATE | Tests for new endpoints |
| `app.py` | MODIFY | Add slugify, parse_summary_response, call_summary_agent, three endpoints, mode routing in /api/chat |
| `templates/index.html` | MODIFY | New company flow, supervisor mode, intake complete handling |

---

### Task 1: Supervisor system prompt

**Files:**
- Create: `agent/supervisor_prompt.md`

- [ ] **Step 1: Create the supervisor system prompt**

Create `agent/supervisor_prompt.md` with this exact content:

```markdown
# SYSTEM PROMPT — Supervisor Agent (Intake Specialist)

## ROL

Je bent een intake-specialist voor een procesoptimalisatie-adviesbureau. Je taak is om via een natuurlijk gesprek alle benodigde informatie over een bedrijf te verzamelen, zodat een procesoptimalisatie-adviseur daarna gerichte adviezen kan geven.

Je bent vriendelijk, professioneel en nieuwsgierig. Je stelt vragen zoals een consultant dat zou doen in een eerste kennismakingsgesprek — niet als een formulier invullen, maar als een echt gesprek.

---

## DOEL

Verzamel de volgende informatie via het gesprek:

**Verplicht (intake is pas klaar als deze velden beantwoord zijn):**
- Bedrijfsnaam
- Branche / sector
- Bedrijfsgrootte (aantal medewerkers en/of omzet)
- Kernprocessen: minimaal één proces met beschrijving, betrokken rollen, frequentie en bekende problemen
- Bekende knelpunten of uitdagingen

**Optioneel maar waardevol:**
- Locatie
- Rechtsvorm (BV, eenmanszaak, etc.)
- Huidige situatie (wat speelt er op dit moment?)
- Beschikbare data (interviews, rapporten, systemen)
- Waar wil de klant mee geholpen worden?

---

## AANPAK

- Stel maximaal 2 vragen tegelijk — liever 1
- Groepeer logisch samenhangende vragen (bijv. bedrijfsnaam + branche tegelijk is prima)
- Vraag door als een antwoord interessant of onduidelijk is
- Als iemand zegt "weet ik niet" of "wil ik liever niet zeggen" — accepteer dat en ga door
- Stel elke vraag maximaal één keer — als je een lijst krijgt van NOG TE VERZAMELEN VELDEN, focus dan op die velden
- Als alle verplichte velden beantwoord zijn, sluit je de intake af met: "Bedankt, ik heb genoeg informatie verzameld. De adviseur neemt het nu van mij over."

---

## TOON

- Nederlands
- Professioneel maar toegankelijk
- Kort en to the point — geen lange inleidingen
- Geen emoji's of informele symbolen

---

## BELANGRIJK

Aan het einde van je system prompt kan een sectie staan: "NOG TE VERZAMELEN VELDEN". Dit zijn de velden die nog ontbreken op basis van het gesprek tot nu toe. Prioriteer vragen over die velden.
```

- [ ] **Step 2: Verify file exists**

```bash
python3 -c "from pathlib import Path; p = Path('agent/supervisor_prompt.md'); print('OK' if p.exists() else 'MISSING')"
```
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add agent/supervisor_prompt.md
git commit -m "feat: add supervisor agent system prompt"
```

---

### Task 2: Summary system prompt

**Files:**
- Create: `agent/summary_prompt.md`

- [ ] **Step 1: Create the summary system prompt**

Create `agent/summary_prompt.md` with this exact content:

```markdown
# SYSTEM PROMPT — Summary Agent (Extractie Specialist)

## ROL

Je bent een extractie-specialist. Je leest een gesprekshistorie tussen een supervisor en een klant, en extraheert uitsluitend de feiten die expliciet zijn bevestigd in het gesprek.

---

## TAAK

Lees de gesprekshistorie en doe het volgende:

1. Extraheer alleen wat letterlijk bevestigd is — verzin nooit iets
2. "Weet ik niet", "wil ik niet zeggen", "geen idee" → sla op als `Onbekend / wil niet delen`
3. Vul het bedrijfsprofiel in als Markdown-document
4. Geef een lijst van velden die nog ontbreken of onbeantwoord zijn
5. Bepaal of de intake klaar is

---

## VERPLICHTE VELDEN (intake klaar als alle vijf beantwoord zijn — ook "onbekend" telt)

- bedrijfsnaam
- branche
- bedrijfsgrootte
- kernprocessen (minimaal 1 proces beschreven)
- bekende_knelpunten

---

## OUTPUT FORMAT

Geef ALLEEN de volgende JSON terug — geen tekst voor of na de JSON:

```json
{
  "missing_fields": ["veld1", "veld2"],
  "intake_complete": false,
  "md_content": "# Bedrijfsprofiel — [NAAM]\n\n..."
}
```

- `missing_fields`: lijst van veldnamen die nog geen antwoord hebben (gebruik de namen uit VERPLICHTE VELDEN)
- `intake_complete`: true als missing_fields leeg is
- `md_content`: het volledige Markdown-bedrijfsprofiel op basis van het gesprek

---

## MD_CONTENT STRUCTUUR

Gebruik altijd deze structuur voor md_content:

```
# Bedrijfsprofiel — [BEDRIJFSNAAM]

## Basisinformatie

- **Bedrijfsnaam:** [waarde of "Onbekend"]
- **Branche:** [waarde of "Onbekend"]
- **Bedrijfsgrootte:** [waarde of "Onbekend / wil niet delen"]
- **Locatie:** [waarde of "Niet gevraagd"]
- **Bedrijfsvorm:** [waarde of "Niet gevraagd"]

## Kernprocessen

### Proces 1: [NAAM]
- **Beschrijving:** [waarde]
- **Betrokken rollen:** [waarde of "Onbekend"]
- **Frequentie:** [waarde of "Onbekend"]
- **Bekende problemen:** [waarde of "Geen genoemd"]

## Huidige Situatie

[waarde of "Niet besproken"]

## Beschikbare Data

[waarde of "Niet besproken"]

## Bekende Knelpunten

[waarde of "Geen specifieke knelpunten besproken"]

## Consultant-Focus

[waarde of "Niet besproken"]
```

---

## STRIKTE REGELS

- Fabriceer NOOIT informatie die niet in het gesprek staat
- Als een veld niet besproken is: schrijf "Niet besproken" of "Onbekend"
- Schrijf nooit aannames als feiten
- Geef ALLEEN de JSON terug — geen uitleg, geen introductie
```

- [ ] **Step 2: Verify file exists**

```bash
python3 -c "from pathlib import Path; p = Path('agent/summary_prompt.md'); print('OK' if p.exists() else 'MISSING')"
```
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add agent/summary_prompt.md
git commit -m "feat: add summary agent system prompt"
```

---

### Task 3: Test setup

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Install pytest**

```bash
pip3 install pytest --break-system-packages -q
```
Expected: no errors

- [ ] **Step 2: Create tests directory and conftest**

```bash
mkdir -p tests && touch tests/__init__.py
```

Create `tests/conftest.py`:

```python
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-key")

from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config["TESTING"] = True
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()
```

- [ ] **Step 3: Verify pytest runs**

```bash
cd "/Users/mats/Downloads/testt kopie" && python3 -m pytest tests/ -v 2>&1 | head -20
```
Expected: `no tests ran` or similar — no import errors

- [ ] **Step 4: Commit**

```bash
git add tests/
git commit -m "feat: add test setup with pytest and Flask test client"
```

---

### Task 4: Utility functions — slugify and parse_summary_response

**Files:**
- Create: `tests/test_utils.py`
- Modify: `app.py` (add `slugify` and `parse_summary_response` functions)

- [ ] **Step 1: Write failing tests**

Create `tests/test_utils.py`:

```python
from app import slugify, parse_summary_response


def test_slugify_basic():
    assert slugify("Bouwbedrijf Van der Berg") == "bouwbedrijf_van_der_berg"


def test_slugify_special_chars():
    assert slugify("Bedrijf & Zonen B.V.") == "bedrijf_zonen_bv"


def test_slugify_strips_whitespace():
    assert slugify("  Test Bedrijf  ") == "test_bedrijf"


def test_slugify_multiple_spaces():
    assert slugify("Test  Bedrijf") == "test_bedrijf"


def test_parse_summary_valid_json():
    raw = '{"missing_fields": ["branche"], "intake_complete": false, "md_content": "# Test"}'
    result = parse_summary_response(raw)
    assert result["missing_fields"] == ["branche"]
    assert result["intake_complete"] is False
    assert result["md_content"] == "# Test"


def test_parse_summary_json_with_preamble():
    raw = 'Here is the result:\n{"missing_fields": [], "intake_complete": true, "md_content": "# Done"}'
    result = parse_summary_response(raw)
    assert result["intake_complete"] is True
    assert result["missing_fields"] == []


def test_parse_summary_invalid_json_returns_defaults():
    result = parse_summary_response("this is not json at all")
    assert "missing_fields" in result
    assert result["intake_complete"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd "/Users/mats/Downloads/testt kopie" && python3 -m pytest tests/test_utils.py -v 2>&1 | head -30
```
Expected: `ImportError` or `AttributeError` — functions don't exist yet

- [ ] **Step 3: Add slugify and parse_summary_response to app.py**

Open `app.py`. After the existing imports, add `import re`. Then after the line `AGENT_DIR = Path("agent")`, add these two functions:

```python
REQUIRED_FIELDS = ["bedrijfsnaam", "branche", "bedrijfsgrootte", "kernprocessen", "bekende_knelpunten"]


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    s = re.sub(r'\s+', '_', s.strip())
    return s


def parse_summary_response(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return {"missing_fields": REQUIRED_FIELDS, "intake_complete": False, "md_content": ""}
```

Also add `import re` at the top of `app.py` if not already present.

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd "/Users/mats/Downloads/testt kopie" && python3 -m pytest tests/test_utils.py -v
```
Expected:
```
PASSED tests/test_utils.py::test_slugify_basic
PASSED tests/test_utils.py::test_slugify_special_chars
PASSED tests/test_utils.py::test_slugify_strips_whitespace
PASSED tests/test_utils.py::test_slugify_multiple_spaces
PASSED tests/test_utils.py::test_parse_summary_valid_json
PASSED tests/test_utils.py::test_parse_summary_json_with_preamble
PASSED tests/test_utils.py::test_parse_summary_invalid_json_returns_defaults
```

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_utils.py
git commit -m "feat: add slugify and parse_summary_response utilities"
```

---

### Task 5: New endpoints — /api/companies and /api/new-company

**Files:**
- Create: `tests/test_endpoints.py`
- Modify: `app.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_endpoints.py`:

```python
import json
import os
from pathlib import Path
import pytest


def test_companies_returns_list(client):
    resp = client.get("/api/companies")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "companies" in data
    assert isinstance(data["companies"], list)


def test_companies_excludes_template(client):
    resp = client.get("/api/companies")
    data = resp.get_json()
    slugs = [c["value"] for c in data["companies"]]
    assert "template" not in slugs


def test_new_company_creates_file(client, tmp_path, monkeypatch):
    import app as app_module
    monkeypatch.setattr(app_module, "BEDRIJVEN_DIR", tmp_path)
    (tmp_path / "template.md").write_text("# Template")

    resp = client.post(
        "/api/new-company",
        data=json.dumps({"name": "Test Bedrijf BV"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["slug"] == "test_bedrijf_bv"
    assert (tmp_path / "test_bedrijf_bv.md").exists()


def test_new_company_empty_name_returns_400(client):
    resp = client.post(
        "/api/new-company",
        data=json.dumps({"name": ""}),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_new_company_idempotent(client, tmp_path, monkeypatch):
    import app as app_module
    monkeypatch.setattr(app_module, "BEDRIJVEN_DIR", tmp_path)
    (tmp_path / "template.md").write_text("# Template")
    (tmp_path / "bestaand_bedrijf.md").write_text("# Existing")

    resp = client.post(
        "/api/new-company",
        data=json.dumps({"name": "Bestaand Bedrijf"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert (tmp_path / "bestaand_bedrijf.md").read_text() == "# Existing"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd "/Users/mats/Downloads/testt kopie" && python3 -m pytest tests/test_endpoints.py -v 2>&1 | head -30
```
Expected: failures because endpoints don't exist yet

- [ ] **Step 3: Add endpoints to app.py**

In `app.py`, add these two routes after the existing `index()` route:

```python
@app.route("/api/companies")
def companies_list():
    return {"companies": list_companies()}


@app.route("/api/new-company", methods=["POST"])
def new_company():
    data = request.get_json()
    name = (data.get("name") or "").strip()
    if not name:
        return {"error": "Naam is verplicht"}, 400

    slug = slugify(name)
    path = BEDRIJVEN_DIR / f"{slug}.md"

    if not path.exists():
        path.write_text(
            f"# Bedrijfsprofiel — {name}\n\n*Profiel wordt aangemaakt via intake gesprek.*\n",
            encoding="utf-8",
        )

    return {"slug": slug, "name": name}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd "/Users/mats/Downloads/testt kopie" && python3 -m pytest tests/test_endpoints.py -v
```
Expected: all 5 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_endpoints.py
git commit -m "feat: add /api/companies and /api/new-company endpoints"
```

---

### Task 6: Summary endpoint — /api/summary and call_summary_agent

**Files:**
- Modify: `tests/test_endpoints.py` (add summary tests)
- Modify: `app.py` (add call_summary_agent and /api/summary)

- [ ] **Step 1: Add failing tests for /api/summary**

Append to `tests/test_endpoints.py`:

```python
def test_summary_missing_fields_returns_400(client):
    resp = client.post(
        "/api/summary",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_summary_calls_agent_and_writes_file(client, tmp_path, monkeypatch):
    import app as app_module

    monkeypatch.setattr(app_module, "BEDRIJVEN_DIR", tmp_path)

    fake_result = {
        "missing_fields": [],
        "intake_complete": True,
        "md_content": "# Bedrijfsprofiel — Testbedrijf\n\n## Basisinformatie\n- **Bedrijfsnaam:** Testbedrijf\n",
    }

    def fake_call_summary_agent(history, slug):
        return fake_result

    monkeypatch.setattr(app_module, "call_summary_agent", fake_call_summary_agent)

    resp = client.post(
        "/api/summary",
        data=json.dumps({"company_slug": "testbedrijf", "history": [{"role": "user", "content": "hoi"}]}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["intake_complete"] is True
    assert data["missing_fields"] == []
    assert (tmp_path / "testbedrijf.md").exists()
```

- [ ] **Step 2: Run to verify test fails**

```bash
cd "/Users/mats/Downloads/testt kopie" && python3 -m pytest tests/test_endpoints.py::test_summary_missing_fields_returns_400 tests/test_endpoints.py::test_summary_calls_agent_and_writes_file -v 2>&1 | head -20
```
Expected: failures — endpoint doesn't exist yet

- [ ] **Step 3: Add call_summary_agent and /api/summary to app.py**

Add `load_summary_prompt` and `call_summary_agent` functions in `app.py` after the existing `load_company` function:

```python
def load_supervisor_prompt() -> str:
    return (AGENT_DIR / "supervisor_prompt.md").read_text(encoding="utf-8")


def load_summary_prompt() -> str:
    return (AGENT_DIR / "summary_prompt.md").read_text(encoding="utf-8")


def call_summary_agent(history: list, company_slug: str) -> dict:
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    summary_prompt = load_summary_prompt()

    history_text = "\n".join([
        f"{'KLANT' if m['role'] == 'user' else 'SUPERVISOR'}: {m['content']}"
        for m in history
    ])

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=summary_prompt,
        messages=[{"role": "user", "content": f"GESPREKSHISTORIE:\n{history_text}"}],
    )

    result = parse_summary_response(message.content[0].text)

    md_content = result.get("md_content", "")
    if md_content:
        (BEDRIJVEN_DIR / f"{company_slug}.md").write_text(md_content, encoding="utf-8")

    return {
        "missing_fields": result.get("missing_fields", REQUIRED_FIELDS),
        "intake_complete": result.get("intake_complete", False),
    }
```

Then add the `/api/summary` route after `/api/new-company`:

```python
@app.route("/api/summary", methods=["POST"])
def summary():
    data = request.get_json()
    company_slug = data.get("company_slug", "")
    history = data.get("history", [])

    if not company_slug or not history:
        return {"error": "company_slug en history zijn verplicht"}, 400

    result = call_summary_agent(history, company_slug)
    return result
```

- [ ] **Step 4: Run all tests**

```bash
cd "/Users/mats/Downloads/testt kopie" && python3 -m pytest tests/ -v
```
Expected: all tests PASSED

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_endpoints.py
git commit -m "feat: add call_summary_agent and /api/summary endpoint"
```

---

### Task 7: Modify /api/chat for supervisor mode

**Files:**
- Modify: `app.py` (update `/api/chat` to handle `mode` and `missing_fields`)

- [ ] **Step 1: Replace the /api/chat route in app.py**

Find the existing `chat()` function and replace it entirely with:

```python
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    company_stem = data.get("company", "")
    user_message = data.get("message", "").strip()
    history = data.get("history", [])
    mode = data.get("mode", "advisory")
    missing_fields = data.get("missing_fields", [])

    if not user_message:
        return {"error": "Geen bericht ontvangen"}, 400

    if mode == "supervisor":
        system_prompt = load_supervisor_prompt()
        if missing_fields:
            fields_text = "\n".join(f"- {f}" for f in missing_fields)
            system_prompt += f"\n\n## NOG TE VERZAMELEN VELDEN\n{fields_text}"
    else:
        system_prompt = load_system_prompt()

    company_context = load_company(company_stem)

    messages = []
    for turn in history:
        messages.append({"role": turn["role"], "content": turn["content"]})

    if mode == "advisory" and not history and company_context:
        full_user_content = f"BEDRIJFSCONTEXT:\n{company_context}\n\nVRAAG VAN DE CONSULTANT:\n{user_message}"
    else:
        full_user_content = user_message

    messages.append({"role": "user", "content": full_user_content})

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    def generate():
        try:
            with client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=2000,
                system=system_prompt,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    yield f"data: {json.dumps(text)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps(f'[FOUT: {str(e)}]')}\n\n"
            yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

- [ ] **Step 2: Run all tests to confirm nothing is broken**

```bash
cd "/Users/mats/Downloads/testt kopie" && python3 -m pytest tests/ -v
```
Expected: all tests PASSED

- [ ] **Step 3: Restart server and smoke test**

```bash
pkill -f "python3 app.py"; sleep 1
cd "/Users/mats/Downloads/testt kopie" && python3 app.py &
sleep 2
curl -s -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"company":"bouwbedrijf_vanderberg","message":"hoi","history":[],"mode":"advisory"}' \
  | head -3
```
Expected: `data: "` — streaming works

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: add mode routing to /api/chat for supervisor and advisory modes"
```

---

### Task 8: Frontend — new company flow and supervisor UI

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Add new company option to dropdown and name input bar**

In `index.html`, find the `<select id="company-select">` block and replace it with:

```html
<select id="company-select">
  {% for c in companies %}
  <option value="{{ c.value }}">{{ c.label }}</option>
  {% endfor %}
  <option value="__new__">— Nieuw bedrijf toevoegen...</option>
</select>
```

After the `<select>` closing tag and before `<button class="btn-new"`, add:

```html
<div id="new-company-bar" style="display:none; align-items:center; gap:8px;">
  <input
    id="new-company-name"
    type="text"
    placeholder="Bedrijfsnaam..."
    style="background:#1a2d47;color:#fff;border:1px solid #2a4060;border-radius:6px;padding:6px 12px;font-size:13px;outline:none;min-width:200px;"
  />
  <button onclick="confirmNewCompany()" style="background:#1abc9c;color:#fff;border:none;border-radius:6px;padding:6px 12px;font-size:13px;cursor:pointer;">Starten</button>
  <button onclick="cancelNewCompany()" style="background:transparent;color:#8899aa;border:1px solid #2a4060;border-radius:6px;padding:6px 12px;font-size:13px;cursor:pointer;">Annuleren</button>
</div>
```

- [ ] **Step 2: Add frontend state variables and update script**

In the `<script>` section, find the existing state variables (`let history = [];` etc.) and add below them:

```javascript
let mode = 'advisory';
let companySlug = selectEl.value;
let missingFields = [];
```

- [ ] **Step 3: Replace selectEl change handler**

Find `selectEl.addEventListener('change', newChat);` and replace with:

```javascript
selectEl.addEventListener('change', () => {
  if (selectEl.value === '__new__') {
    document.getElementById('new-company-bar').style.display = 'flex';
    document.getElementById('new-company-name').focus();
  } else {
    companySlug = selectEl.value;
    mode = 'advisory';
    missingFields = [];
    newChat();
  }
});
```

- [ ] **Step 4: Add new company functions to script**

Add these functions inside the `<script>` block, after the `newChat()` function:

```javascript
function cancelNewCompany() {
  document.getElementById('new-company-bar').style.display = 'none';
  selectEl.value = companySlug || selectEl.options[0].value;
}

async function confirmNewCompany() {
  const input = document.getElementById('new-company-name');
  const name = input.value.trim();
  if (!name) return;

  const resp = await fetch('/api/new-company', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  });
  const data = await resp.json();

  // Add to dropdown before __new__ option
  const newOpt = document.createElement('option');
  newOpt.value = data.slug;
  newOpt.textContent = name + ' (intake bezig...)';
  newOpt.dataset.pending = 'true';
  const newOption = selectEl.querySelector('option[value="__new__"]');
  selectEl.insertBefore(newOpt, newOption);
  selectEl.value = data.slug;

  // Reset input and hide bar
  input.value = '';
  document.getElementById('new-company-bar').style.display = 'none';

  // Switch to supervisor mode
  companySlug = data.slug;
  mode = 'supervisor';
  missingFields = [];
  history = [];
  newChat();

  // Trigger supervisor's first message automatically
  await kickoffSupervisor(name);
}

async function kickoffSupervisor(companyName) {
  const starterMessage = `Ik wil graag informatie invullen voor een nieuw bedrijf: ${companyName}`;
  addMessage('user', starterMessage);

  const typingRow = addTyping();
  let fullResponse = '';

  try {
    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company: companySlug,
        message: starterMessage,
        history: [],
        mode: 'supervisor',
        missing_fields: [],
      }),
    });

    removeTyping();
    const bubble = addMessage('assistant', '');
    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const chunk = line.slice(6);
        if (chunk === '[DONE]') break;
        try {
          const text = JSON.parse(chunk);
          fullResponse += text;
          bubble.innerHTML = marked.parse(fullResponse);
          chatEl.scrollTop = chatEl.scrollHeight;
        } catch {}
      }
    }

    history.push({ role: 'user', content: starterMessage });
    history.push({ role: 'assistant', content: fullResponse });

    await runSummary();
  } catch (err) {
    removeTyping();
    addMessage('assistant', `**Fout:** ${err.message}`);
  }
}
```

- [ ] **Step 5: Add runSummary and addSystemMessage functions**

Add these functions in the `<script>` block:

```javascript
function addSystemMessage(text) {
  const div = document.createElement('div');
  div.style.cssText = 'text-align:center;color:#8899aa;font-size:12px;padding:8px 0;border-top:1px solid #e4e9f0;border-bottom:1px solid #e4e9f0;margin:4px 0;';
  div.textContent = text;
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

async function runSummary() {
  if (mode !== 'supervisor') return;
  try {
    const resp = await fetch('/api/summary', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company_slug: companySlug, history }),
    });
    const data = await resp.json();
    missingFields = data.missing_fields || [];

    if (data.intake_complete) {
      mode = 'advisory';
      // Update dropdown label
      const opt = selectEl.querySelector(`option[value="${companySlug}"]`);
      if (opt) {
        opt.textContent = opt.textContent.replace(' (intake bezig...)', '');
        delete opt.dataset.pending;
      }
      addSystemMessage('Intake afgerond — de adviseur is nu actief. Stel je procesoptimalisatievraag.');
      history = [];
    }
  } catch (err) {
    console.error('Summary agent fout:', err);
  }
}
```

- [ ] **Step 6: Update sendMessage to pass mode and missing_fields, and call runSummary after**

Find the `body: JSON.stringify({ company, message: text, history }),` line in `sendMessage` and replace it with:

```javascript
body: JSON.stringify({ company: selectEl.value, message: text, history, mode, missing_fields: missingFields }),
```

Find `history.push({ role: 'assistant', content: fullResponse });` at the bottom of the try block in `sendMessage`, and add after it:

```javascript
if (mode === 'supervisor') {
  await runSummary();
}
```

- [ ] **Step 7: Restart server and test in browser**

```bash
pkill -f "python3 app.py"; sleep 1
cd "/Users/mats/Downloads/testt kopie" && python3 app.py &
```

Open http://localhost:8080 and verify:
1. Dropdown shows "— Nieuw bedrijf toevoegen..." at the bottom
2. Clicking it shows the name input bar
3. Typing a name and clicking "Starten" creates the company and starts supervisor conversation
4. Existing companies (Bouwbedrijf Vanderberg etc.) still work normally

- [ ] **Step 8: Commit**

```bash
git add templates/index.html
git commit -m "feat: add new company flow, supervisor mode and intake complete UI"
```

---

### Task 9: Push to GitHub and final verification

**Files:** none

- [ ] **Step 1: Run full test suite**

```bash
cd "/Users/mats/Downloads/testt kopie" && python3 -m pytest tests/ -v
```
Expected: all tests PASSED

- [ ] **Step 2: Full end-to-end smoke test**

With server running on http://localhost:8080:
1. Select an existing company → send a message → verify advisory response streams correctly
2. Select "Nieuw bedrijf toevoegen..." → enter "Test Logistiek BV" → click Starten
3. Verify supervisor greets and asks first question
4. Answer a few questions → verify summary agent runs silently in background
5. Continue conversation until intake complete message appears
6. Verify advisory mode activates and new company appears in dropdown without "(intake bezig...)"

- [ ] **Step 3: Push to GitHub**

```bash
cd "/Users/mats/Downloads/testt kopie" && git push origin main
```

---

## Self-Review

**Spec coverage check:**
- [x] Supervisor agent — Task 1 (prompt) + Task 7 (chat routing) + Task 8 (frontend)
- [x] Summary agent — Task 2 (prompt) + Task 6 (endpoint + call_summary_agent)
- [x] Advisory agent — Task 7 (existing logic preserved, mode routing added)
- [x] /api/new-company — Task 5
- [x] /api/companies — Task 5
- [x] /api/summary — Task 6
- [x] missing_fields injection into supervisor — Task 7 (system prompt injection)
- [x] intake_complete signal — Task 6 (backend) + Task 8 (frontend runSummary)
- [x] "weet ik niet" handling — Task 2 (summary prompt explicit instruction)
- [x] Dropdown "Nieuw bedrijf toevoegen..." — Task 8
- [x] Pending label in dropdown — Task 8 (kickoffSupervisor adds "(intake bezig...)")
- [x] System message on intake complete — Task 8 (addSystemMessage)
- [x] History reset after intake — Task 8 (history = [] in runSummary)
- [x] Existing companies unaffected — Task 7 (advisory mode unchanged)

**Type consistency check:**
- `slugify` defined Task 4, used in Task 5 (/api/new-company) ✓
- `parse_summary_response` defined Task 4, used in Task 6 (call_summary_agent) ✓
- `call_summary_agent` defined Task 6, monkeypatched in test Task 6 ✓
- `load_supervisor_prompt` defined Task 6, used in Task 7 (/api/chat) ✓
- `REQUIRED_FIELDS` defined Task 4, used in Task 6 (parse_summary_response fallback) ✓
- `companySlug` frontend variable defined Task 8 Step 2, used in kickoffSupervisor and runSummary ✓
- `missingFields` defined Task 8 Step 2, passed in sendMessage and runSummary ✓
