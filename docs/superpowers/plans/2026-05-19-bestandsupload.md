# Bestandsupload Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a file upload button (PDF/DOCX/TXT) to the chat UI that extracts text and injects it into the conversation as context for the active agent.

**Architecture:** New `POST /api/upload` endpoint extracts text from uploaded files using pypdf and python-docx, returns the text to the frontend, which then adds it to the chat history as a user message so both supervisor and advisory agents see it as context.

**Tech Stack:** Python 3.14, Flask 3.x, pypdf>=4.0.0, python-docx>=1.0.0, vanilla JS

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `requirements.txt` | MODIFY | Add pypdf and python-docx |
| `tests/test_upload.py` | CREATE | Tests for extract_text and /api/upload |
| `app.py` | MODIFY | Add extract_text() and /api/upload route |
| `templates/index.html` | MODIFY | Paperclip button, hidden file input, upload JS |

---

### Task 1: Install dependencies

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Add dependencies to requirements.txt**

Replace the contents of `requirements.txt` with:

```
anthropic>=0.40.0
python-dotenv>=1.0.0
flask>=3.0.0
pypdf>=4.0.0
python-docx>=1.0.0
```

- [ ] **Step 2: Install them**

```bash
pip3 install pypdf python-docx --break-system-packages -q
```
Expected: no errors

- [ ] **Step 3: Verify both import correctly**

```bash
python3 -c "import pypdf; import docx; print('OK')"
```
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
cd "/Users/mats/Downloads/testt kopie" && git add requirements.txt && git commit -m "feat: add pypdf and python-docx dependencies"
```

---

### Task 2: extract_text function with tests

**Files:**
- Create: `tests/test_upload.py`
- Modify: `app.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_upload.py`:

```python
import io
import pytest


def test_extract_txt():
    from app import extract_text
    content = b"Dit is een testdocument.\nMet twee regels."
    result = extract_text(content, "test.txt")
    assert "testdocument" in result
    assert "twee regels" in result


def test_extract_txt_encoding():
    from app import extract_text
    content = "Bedrijf: Café & Zonen".encode("utf-8")
    result = extract_text(content, "test.txt")
    assert "Café" in result


def test_extract_pdf():
    from app import extract_text
    import pypdf
    writer = pypdf.PdfWriter()
    page = writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)
    # Blank PDF returns empty string — just verify no exception
    result = extract_text(buf.getvalue(), "test.pdf")
    assert isinstance(result, str)


def test_extract_docx():
    from app import extract_text
    import docx
    doc = docx.Document()
    doc.add_paragraph("Procesoptimalisatie test")
    doc.add_paragraph("Tweede alinea")
    buf = io.BytesIO()
    doc.save(buf)
    result = extract_text(buf.getvalue(), "test.docx")
    assert "Procesoptimalisatie test" in result
    assert "Tweede alinea" in result


def test_extract_unsupported_type():
    from app import extract_text
    with pytest.raises(ValueError, match="Niet ondersteund"):
        extract_text(b"data", "test.xlsx")
```

- [ ] **Step 2: Run to verify they fail**

```bash
cd "/Users/mats/Downloads/testt kopie" && python3 -m pytest tests/test_upload.py -v 2>&1 | head -20
```
Expected: ImportError — `extract_text` not defined yet

- [ ] **Step 3: Add extract_text to app.py**

In `app.py`, add `import io` to the imports at the top (after `import re`).

Then add the `extract_text` function after the `parse_summary_response` function (around line 44):

```python
def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore")
    if ext == "pdf":
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if ext == "docx":
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(para.text for para in doc.paragraphs)
    raise ValueError(f"Niet ondersteund bestandstype: .{ext}")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd "/Users/mats/Downloads/testt kopie" && python3 -m pytest tests/test_upload.py -v
```
Expected:
```
PASSED tests/test_upload.py::test_extract_txt
PASSED tests/test_upload.py::test_extract_txt_encoding
PASSED tests/test_upload.py::test_extract_pdf
PASSED tests/test_upload.py::test_extract_docx
PASSED tests/test_upload.py::test_extract_unsupported_type
```

- [ ] **Step 5: Commit**

```bash
cd "/Users/mats/Downloads/testt kopie" && git add app.py tests/test_upload.py && git commit -m "feat: add extract_text function for PDF, DOCX and TXT"
```

---

### Task 3: /api/upload endpoint with tests

**Files:**
- Modify: `tests/test_upload.py` (append endpoint tests)
- Modify: `app.py` (add /api/upload route)

- [ ] **Step 1: Append endpoint tests to tests/test_upload.py**

Add these tests at the END of `tests/test_upload.py`:

```python
def test_upload_txt_returns_text(client):
    data = {"file": (io.BytesIO(b"Testinhoud voor upload"), "test.txt")}
    resp = client.post("/api/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    result = resp.get_json()
    assert result["filename"] == "test.txt"
    assert "Testinhoud" in result["text"]
    assert result["chars"] > 0


def test_upload_no_file_returns_400(client):
    resp = client.post("/api/upload", data={}, content_type="multipart/form-data")
    assert resp.status_code == 400


def test_upload_unsupported_type_returns_400(client):
    data = {"file": (io.BytesIO(b"data"), "test.xlsx")}
    resp = client.post("/api/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 400


def test_upload_empty_file_returns_400(client):
    data = {"file": (io.BytesIO(b"   "), "leeg.txt")}
    resp = client.post("/api/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 400


def test_upload_docx_returns_text(client):
    import docx
    doc = docx.Document()
    doc.add_paragraph("Testbedrijf intake document")
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    data = {"file": (buf, "rapport.docx")}
    resp = client.post("/api/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    result = resp.get_json()
    assert "Testbedrijf" in result["text"]
```

- [ ] **Step 2: Run to verify new tests fail**

```bash
cd "/Users/mats/Downloads/testt kopie" && python3 -m pytest tests/test_upload.py::test_upload_txt_returns_text -v 2>&1 | head -15
```
Expected: failure — endpoint doesn't exist yet

- [ ] **Step 3: Add /api/upload route to app.py**

Add this route to `app.py` after the `/api/summary` route (around line 145):

```python
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return {"error": "Geen bestand ontvangen"}, 400

    file = request.files["file"]
    if not file.filename:
        return {"error": "Geen bestandsnaam"}, 400

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return {"error": f"Bestandstype .{ext} wordt niet ondersteund. Gebruik PDF, DOCX of TXT."}, 400

    file_bytes = file.read()
    try:
        text = extract_text(file_bytes, file.filename)
    except Exception as e:
        return {"error": f"Fout bij verwerken bestand: {str(e)}"}, 500

    if not text.strip():
        return {"error": "Geen leesbare tekst gevonden in het bestand"}, 400

    return {"filename": file.filename, "text": text, "chars": len(text)}
```

- [ ] **Step 4: Run all tests**

```bash
cd "/Users/mats/Downloads/testt kopie" && python3 -m pytest tests/ -v
```
Expected: all 24 tests PASSED (14 existing + 10 upload)

- [ ] **Step 5: Commit**

```bash
cd "/Users/mats/Downloads/testt kopie" && git add app.py tests/test_upload.py && git commit -m "feat: add /api/upload endpoint"
```

---

### Task 4: Frontend upload UI

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Add paperclip button and hidden file input to the input bar**

Find this block in `templates/index.html`:

```html
<div id="input-bar">
  <textarea
    id="user-input"
    rows="1"
    placeholder="Stel een vraag over de processen van het geselecteerde bedrijf..."
  ></textarea>
  <button id="send-btn" onclick="sendMessage()">Stuur</button>
</div>
```

Replace with:

```html
<div id="input-bar">
  <input type="file" id="file-input" accept=".pdf,.docx,.txt" style="display:none;" onchange="handleFileUpload(event)" />
  <button id="upload-btn" onclick="document.getElementById('file-input').click()" title="Bijlage toevoegen (PDF, DOCX, TXT)" style="background:transparent;border:1px solid #dde3ec;border-radius:10px;padding:10px 12px;font-size:16px;cursor:pointer;color:#8899aa;transition:all 0.15s;height:42px;flex-shrink:0;" onmouseover="this.style.borderColor='#1abc9c';this.style.color='#1abc9c'" onmouseout="this.style.borderColor='#dde3ec';this.style.color='#8899aa'">📎</button>
  <textarea
    id="user-input"
    rows="1"
    placeholder="Stel een vraag over de processen van het geselecteerde bedrijf..."
  ></textarea>
  <button id="send-btn" onclick="sendMessage()">Stuur</button>
</div>
```

- [ ] **Step 2: Add handleFileUpload function to the script**

In the `<script>` block, add this function just before the closing `</script>` tag:

```javascript
  async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const uploadBtn = document.getElementById('upload-btn');
    uploadBtn.disabled = true;
    uploadBtn.textContent = '⏳';

    const formData = new FormData();
    formData.append('file', file);

    try {
      const resp = await fetch('/api/upload', { method: 'POST', body: formData });
      const data = await resp.json();

      if (!resp.ok) {
        addMessage('assistant', `**Fout bij uploaden:** ${data.error}`);
      } else {
        const contextMessage = `[Bijlage: ${data.filename}]\n\n${data.text}`;
        addMessage('user', `📎 ${data.filename} (${data.chars} tekens geüpload)`);
        history.push({ role: 'user', content: contextMessage });

        if (mode === 'supervisor') {
          await runSummary();
        }
      }
    } catch (err) {
      addMessage('assistant', `**Fout bij uploaden:** ${err.message}`);
    }

    uploadBtn.disabled = false;
    uploadBtn.textContent = '📎';
    event.target.value = '';
  }
```

- [ ] **Step 3: Restart server and verify**

```bash
pkill -f "python3 app.py" 2>/dev/null; sleep 1
cd "/Users/mats/Downloads/testt kopie" && python3 app.py &
sleep 2
curl -s -X POST http://localhost:8080/api/upload \
  -F "file=@/Users/mats/Downloads/testt kopie/README.md" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if d.get('chars',0)>0 else 'FAIL')"
```
Expected: `OK`

- [ ] **Step 4: Run all tests**

```bash
cd "/Users/mats/Downloads/testt kopie" && python3 -m pytest tests/ -v
```
Expected: all 24 tests PASSED

- [ ] **Step 5: Commit and push**

```bash
cd "/Users/mats/Downloads/testt kopie" && git add templates/index.html && git commit -m "feat: add file upload button and handleFileUpload to frontend" && git push origin main
```

---

## Self-Review

**Spec coverage:**
- [x] POST /api/upload endpoint — Task 3
- [x] extract_text() for PDF, DOCX, TXT — Task 2
- [x] 400 on no file / unsupported type / empty text — Task 3
- [x] pypdf + python-docx in requirements.txt — Task 1
- [x] Paperclip button always visible — Task 4
- [x] Hidden file input with accept filter — Task 4
- [x] Upload adds to history as user message — Task 4 (handleFileUpload)
- [x] Calls runSummary in supervisor mode after upload — Task 4
- [x] Files not saved to disk — extract_text works on bytes in memory

**Type consistency:**
- `extract_text(file_bytes: bytes, filename: str) -> str` defined Task 2, used in Task 3 (/api/upload) ✓
- `ALLOWED_EXTENSIONS` set defined Task 3, used in /api/upload route ✓
- `handleFileUpload(event)` defined Task 4, wired to `onchange` in same task ✓
- `history`, `mode`, `runSummary` referenced in Task 4 — all defined in earlier frontend tasks ✓
