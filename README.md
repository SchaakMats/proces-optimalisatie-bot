# Process Optimization Agent — Type 12
Minor Digital Transformation & AI | Hackathon Dag

---

## Snel Starten

```bash
# 1. Installeer dependencies (eenmalig)
pip3 install anthropic python-dotenv

# 2. Start de agent
python3 main.py
```

---

## Projectstructuur

```
testt/
├── main.py                          ← Start hier: interactieve agent CLI
├── .env                             ← API key (niet delen!)
├── requirements.txt
│
├── agent/
│   └── system_prompt.md             ← De 9-lagen systeemprompt (kern van de agent)
│
├── bedrijven/
│   ├── jouw_bedrijf.md              ← INVULLEN met jullie eigen bedrijf
│   ├── greenlogistics_bv.md         ← Testbedrijf voor Build Phase
│   ├── bouwbedrijf_vanderberg.md    ← Testbedrijf voor Cross-Company testing
│   └── template.md                  ← Leeg template voor nieuwe bedrijven
│
├── worksheets/
│   ├── 01_agent_design_canvas.md    ← Fase 2: invullen VOOR je bouwt
│   ├── 02_failure_log.md            ← Fase 5: documenteer failures
│   ├── 03_ecc_reflectie.md          ← ECC analyse per output
│   ├── 04_automation_vs_augmentation.md
│   └── 05_crossover_testing.md      ← Fase 4: cross-company test
│
├── test_cases/
│   ├── test_eigen_bedrijf.md        ← 3 verplichte tests voor Build Phase
│   └── test_crossover.md            ← 3 tests voor Cross-Company fase
│
└── logs/                            ← Auto-aangemaakt, opgeslagen outputs
```

---

## Hackathon Fases

| Fase | Tijd | Wat doen |
|------|------|----------|
| 1 Kick-off | 0–10 min | Lees dit README |
| 2 Agent Design | 10–20 min | Vul `worksheets/01_agent_design_canvas.md` in |
| 3 Build | 20–60 min | Vul `bedrijven/jouw_bedrijf.md` in, draai tests uit `test_cases/test_eigen_bedrijf.md` |
| 4 Cross-Test | 60–85 min | Laad een ander bedrijf in `main.py`, gebruik `worksheets/05_crossover_testing.md` |
| 5 Failure Log | 85–105 min | Documenteer failures in `worksheets/02_failure_log.md` |
| 6 Verbetering | 105–130 min | Pas `agent/system_prompt.md` aan (max 3 wijzigingen) |
| 7 Demo | 130–150 min | Live demo via `main.py` |

---

## Verplichte Tests (Fase 3)

Voer minimaal deze drie tests uit en documenteer de resultaten:

1. **Volledige context** → verwacht: gedetailleerde analyse met FEIT/INTERPRETATIE/AANNAME
2. **Gedeeltelijke context** → verwacht: analyse met expliciete aannames, vraagt om meer data
3. **Lege context** → verwacht: weigering (refusal), uitleg wat minimaal nodig is

Zie `test_cases/test_eigen_bedrijf.md` voor de exacte inputs.

---

## Hoe de Agent Werkt

De systeemprompt heeft 9 lagen (zie `agent/system_prompt.md`):

1. **ROLE** — Procesoptimalisatie-specialist voor MKB
2. **OBJECTIVE** — Analyseer processen, geef bruikbare output voor consultant
3. **CONTEXT** — Wordt per gesprek aangeleverd via het bedrijfsprofiel
4. **TASKS** — 7 stappen: contextcheck → proceskaart → TIMWOODS → optimalisatie → prioritering → vervolgacties → kwaliteitsscore
5. **OUTPUT FORMAT** — Vaste structuur, Nederlands, max 700 woorden
6. **UNCERTAINTY HANDLING** — Werkt ook bij onvolledige data, markeert aannames
7. **HUMAN VALIDATION** — Lijst van wat consultant zelf moet controleren
8. **REFUSAL BEHAVIOR** — Weigert bij lege context of buiten-scope vragen
9. **EVIDENCE REQUIREMENTS** — Elke aanbeveling heeft een onderbouwing

---

## Tips voor de Demo (Fase 7)

1. **Laat de agent LIVE werken** op het cross-company bedrijf (~60s)
2. **Wijs één failure aan** — type, oorzaak, impact (~45s)
3. **Toon de verbeterde versie** — voor/na vergelijking prompt (~45s)
4. **Automation of Augmentation?** — jouw positie op de matrix (~30s)
