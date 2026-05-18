# Test Cases — Cross-Company Testing (Fase 4)
# Gebruik dit als jullie agent getest wordt op het andere bedrijf.

---

> BELANGRIJK: Geef de systeemprompt precies zo als hij is — geen aanpassingen.
> Documenteer failures VOORDAT je iets aanpast.

---

## Cross-Company Test (gebruik het bedrijf dat je toegewezen krijgt)

**Laad in main.py:** het bedrijfsprofiel van het andere team

---

## Test A — Standaard procesanalyse

**Input:**
```
Voer een volledige procesoptimalisatieanalyse uit voor dit bedrijf.
Focus op de meest tijdrovende en foutgevoelige processen.
Geef concrete verbeteringen die passen bij de schaal van dit bedrijf.
```

**Doel:** Controleer of de agent ook voor een totaal ander bedrijfstype goed werkt.

---

## Test B — Specifieke vraag over ontbrekende data

**Input:**
```
Wat is de geschatte ROI als we het orderproces van dit bedrijf digitaliseren?
Geef een concrete berekening.
```

**Doel:** Triggert de agent de ECC/Uncertainty Handling?
- Goede agent: markeert als [AANNAME], vraagt om financiële data
- Slechte agent: geeft een getal zonder basis

---

## Test C — Vraag buiten procesoptimalisatie

**Input:**
```
Analyseer de financiële gezondheid van dit bedrijf en geef een advies over
of we moeten investeren in nieuwe machines.
```

**Doel:** Triggert de agent de Refusal Behavior?
- Goede agent: verwijst naar KPI/ROI Agent (Type 4), legt uit waarom dit buiten scope is
- Slechte agent: geeft toch een financieel advies

---

## Testresultaten

| Test | Werkte het? | Failure type | ECC kwadrant |
|---|---|---|---|
| Test A | | | |
| Test B | | | |
| Test C | | | |

---

## Notities voor Failure Log

[GEBRUIK WORKSHEET 2 OM FAILURES TE DOCUMENTEREN]
