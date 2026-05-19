# Design: Multi-Agent Procesoptimalisatie Systeem

**Datum:** 2026-05-19  
**Status:** Goedgekeurd

---

## Samenvatting

Uitbreiding van de bestaande procesoptimalisatie-app naar een multi-agent architectuur. Doel: elke organisatie kan procesoptimalisatieadvies krijgen, ook zonder vooraf aangemaakt bedrijfsprofiel. Nieuwe bedrijven doorlopen een gestructureerde intake via een supervisor agent. Bestaande bedrijven slaan de intake over en gaan direct naar de advies agent.

---

## Architectuur

Drie agents, één Flask backend, zelfde frontend.

```
Nieuw bedrijf selected
    └─► Supervisor agent (conversatie)
            │
            │ na elke exchange
            ▼
        Summary agent (achtergrond)
            │ schrijft naar bedrijven/<slug>.md
            │ retourneert missing_fields lijst
            ▼
        Supervisor krijgt missing_fields geïnjecteerd in volgende beurt
            │
            │ missing_fields leeg?
            ▼
        Advisory agent neemt over

Bestaand bedrijf selected
    └─► Advisory agent (laadt .md direct, stelt procesvragen, geeft advies)
```

---

## De drie agents

### Supervisor agent
- Voert een natuurlijk gesprek met de gebruiker om alle benodigde bedrijfsinformatie te verzamelen
- Ontvangt na elke beurt een `missing_fields` lijst van de summary agent, geïnjecteerd in de system prompt
- Gebruikt die lijst om gericht door te vragen zonder velden dubbel te stellen
- Weet wanneer de intake klaar is: summary agent meldt `missing_fields: []`
- Stelt vragen gegroepeerd en conversationeel — niet als formulier
- Mag doorvragen op interessante antwoorden

### Summary agent
- Wordt aangeroepen na elke gebruikersreactie (niet gestreamd — pure extractie)
- Ontvangt de volledige gesprekshistorie
- Taak: extraheer alleen wat expliciet bevestigd is in het gesprek
- Schrijft/update `bedrijven/<slug>.md` op basis van het template
- Retourneert een `missing_fields` lijst: velden die nog leeg of onbeantwoord zijn
- "Weet ik niet" / "wil ik niet zeggen" = geldig antwoord, wordt letterlijk opgeslagen
- Fabriceert nooit iets — als iets niet gezegd is, blijft het leeg of "onbekend"

### Advisory agent
- Zelfde logica als de huidige agent in `app.py`
- Laadt alle content van `bedrijven/<slug>.md` als context voordat hij vragen stelt
- Stelt eerst gerichte procesvragen op basis van de bedrijfscontext
- Geeft daarna gestructureerd advies (TIMWOODS, prioriteiten, vervolgacties)
- Werkt voor zowel net-afgeronde intake als terugkerende bedrijven

---

## Data flow per beurt (nieuw bedrijf)

1. Gebruiker stuurt bericht → frontend POST `/api/chat` met `mode: "supervisor"` en `company_slug`
2. Backend roept supervisor agent aan → streaming response naar frontend
3. Na voltooide stream: backend roept summary agent aan (niet gestreamd)
4. Summary agent schrijft/update `bedrijven/<slug>.md`
5. Summary retourneert `{ missing_fields: [...], intake_complete: bool }`
6. Backend slaat `missing_fields` op in sessie/state voor volgende beurt
7. Volgende supervisor-beurt: `missing_fields` geïnjecteerd in system prompt
8. Als `intake_complete: true` → backend stuurt signaal naar frontend → advisory agent actief

---

## API endpoints

| Endpoint | Methode | Beschrijving |
|---|---|---|
| `GET /` | GET | Hoofdpagina met dropdown van bedrijven |
| `POST /api/chat` | POST | Chat endpoint, handelt alle drie modes af |
| `POST /api/new-company` | POST | Maakt nieuwe bedrijfsslug aan, start intake |
| `GET /api/companies` | GET | Geeft lijst van beschikbare bedrijven terug |

### POST /api/chat body
```json
{
  "mode": "supervisor" | "advisory",
  "company_slug": "bouwbedrijf_vanderberg",
  "message": "...",
  "history": [...],
  "missing_fields": [...]
}
```

---

## Bestandsstructuur wijzigingen

```
agent/
  system_prompt.md          (bestaand — advisory agent)
  supervisor_prompt.md      (nieuw)
  summary_prompt.md         (nieuw)
bedrijven/
  template.md               (bestaand — basis voor summary agent output)
  bouwbedrijf_vanderberg.md (bestaand)
  <nieuwe bedrijven>.md     (aangemaakt door summary agent)
app.py                      (uitgebreid met drie agent modes)
templates/
  index.html                (uitgebreid met nieuw bedrijf flow + UI signalen)
```

---

## UI wijzigingen

- Dropdown: onderaan optie "Nieuw bedrijf toevoegen..."
- Bij keuze: inline invoer voor bedrijfsnaam → start supervisor flow
- Nieuw bedrijf verschijnt direct in dropdown (grijs/italic totdat intake klaar is)
- Bij intake complete: systeembericht in chat "Intake afgerond — adviseur is nu actief"
- Bestaand bedrijf: geen wijziging in bestaande flow

---

## Constraints

- Summary agent fabriceert nooit: alleen expliciet bevestigde feiten worden opgeslagen
- "Weet ik niet" en "wil ik niet zeggen" zijn geldige antwoorden en worden als zodanig opgeslagen
- Intake is klaar wanneer alle velden een antwoord hebben gekregen — ook al is dat "onbekend"
- Supervisor stelt elke vraag maximaal één keer (missing_fields voorkomt herhaling)
- MKB-focus blijft behouden in alle agents
- Geen enterprise-tools, geen zes-cijferige ROI-claims zonder onderbouwing
