# Design: Bestandsupload

**Datum:** 2026-05-19
**Status:** Goedgekeurd

---

## Samenvatting

Voeg een bestandsupload-functie toe aan de procesoptimalisatie-app. Gebruikers kunnen PDF, DOCX of TXT bestanden uploaden die automatisch worden verwerkt en als context in het gesprek worden opgenomen — zowel tijdens supervisor intake als tijdens advies gesprekken.

---

## Backend

**Nieuw endpoint:** `POST /api/upload`

- Accepteert een multipart form upload met veld `file`
- Ondersteunde extensies: `.pdf`, `.docx`, `.txt`
- Extraheert tekst:
  - `.txt` — direct lezen
  - `.pdf` — via `pypdf`
  - `.docx` — via `python-docx`
- Retourneert `{ filename: str, text: str, chars: int }`
- Retourneert 400 bij: geen bestand, ongeldig type, geen leesbare tekst
- Retourneert 500 bij verwerkingsfout

**Nieuwe hulpfunctie:** `extract_text(file_bytes, filename) -> str`
- Geïsoleerde extractielogica, los van de route handler
- Makkelijk testbaar zonder HTTP

**Nieuwe dependencies** (toevoegen aan `requirements.txt`):
- `pypdf>=4.0.0`
- `python-docx>=1.0.0`

---

## Frontend

**Upload knop** — paperclip-knop (`📎`) links van de textarea in de input bar, altijd zichtbaar ongeacht mode.

**Hidden file input** — `<input type="file" accept=".pdf,.docx,.txt">`, wordt getriggerd door de knop.

**Flow:**
1. Gebruiker klikt paperclip → file picker opent
2. Bestand geselecteerd → upload naar `/api/upload` via fetch (multipart)
3. Tijdens upload: knop toont loading state (disabled)
4. Na succesvolle upload: voeg bericht toe aan chat als user message:
   `[Bijlage: bestandsnaam.pdf]\n\n[geëxtraheerde tekst]`
5. Dit bericht wordt toegevoegd aan `history` — de agent ziet het als context
6. Bij fout: toon foutmelding in chat

**Geen aparte UI per mode** — de knop werkt identiek in supervisor en advisory mode. De agent past zijn gedrag automatisch aan op basis van de context.

---

## Gedrag per mode

- **Supervisor mode:** summary agent verwerkt de documentinhoud bij de volgende samenvatting en extraheert velden die in het document staan
- **Advisory mode:** advisory agent gebruikt de documentinhoud als extra bedrijfscontext voor zijn analyse

---

## Bestandsstructuur wijzigingen

```
app.py              — extract_text() functie + /api/upload endpoint
requirements.txt    — pypdf en python-docx toevoegen
templates/index.html — paperclip knop + file input + upload logica
tests/test_upload.py — tests voor extract_text en /api/upload
```

---

## Constraints

- Max bestandsgrootte: geen expliciete limiet (Flask default ~16MB is voldoende)
- Alleen `.pdf`, `.docx`, `.txt` geaccepteerd
- Tekst die leeg is na extractie geeft een 400 terug
- Geüploade bestanden worden niet opgeslagen op schijf — alleen tekst wordt geretourneerd
