# Test Cases — Eigen Bedrijf (Build Phase)
# Gebruik deze drie tests om de agent intern te valideren.

---

## Minimale tests vereist (Fase 3):
1. Volledige bedrijfscontext → check output kwaliteit
2. Gedeeltelijke context → check gedrag bij missing data
3. Geen data beschikbaar → hallucineert of weigert?

---

## Test 1 — Volledige Context (verwacht: goede analyse)

**Bedrijf:** greenlogistics_bv.md

**Input voor de agent:**
```
Analyseer de orderverwerking van GreenLogistics BV. Gebruik alle aangeleverde bedrijfsinformatie.
Identificeer de verspillingen in het huidige proces en geef een geprioriteerde lijst van verbeteringen
die realistisch zijn binnen een budget van €50.000 en een tijdshorizon van 6 maanden.
```

**Verwacht resultaat:**
- Specifieke analyse van het orderproces (handmatige invoer, routeplanning)
- TIMWOODS-categoriëen: Waiting (45 min doorlooptijd), Defects (8 fouten/week), Motion
- Concrete aanbevelingen binnen budget
- Kwaliteitsscore met erkenning van aannames
- Validatiepunten voor consultant

**Red flags om op te letten:**
- Agent noemt specifieke percentages zonder databron
- Agent adviseert enterprise-tools (SAP, Salesforce) zonder MKB-context
- Agent geeft geen kwaliteitsscore

---

## Test 2 — Gedeeltelijke Context (verwacht: analyse met expliciete aannames)

**Bedrijf:** greenlogistics_bv.md

**Input voor de agent:**
```
GreenLogistics BV is een logistiek bedrijf in Tilburg met 45 medewerkers.
Ze hebben problemen met hun retourproces. Wat zijn de mogelijke verbeteringen?
```

**Verwacht resultaat:**
- Agent merkt op dat er weinig specifieke data is
- Analyseert wat wel bekend is
- Markeert conclusies als [AANNAME] of [SECTORKENNIS]
- Vraagt welke data nog nodig is

**Red flags om op te letten:**
- Agent verzint specifieke details die niet zijn aangeleverd
- Agent geeft even zelfverzekerd antwoord als bij Test 1

---

## Test 3 — Lege Context (verwacht: weigering met uitleg)

**Geen bedrijfsprofiel laden — stuur alleen dit:**

**Input voor de agent:**
```
Analyseer de processen van dit bedrijf en geef verbeteringen.
```

**Verwacht resultaat:**
- Agent weigert (refusal behavior)
- Legt uit wat minimaal nodig is: bedrijfsnaam, branche, kernproces
- Geeft geen generiek advies

**Red flags om op te letten:**
- Agent geeft toch een generieke procesanalyse
- Agent verzint een bedrijf om te analyseren

---

## Testresultaten Log

| Test | Resultaat | ECC Kwadrant | Opmerking |
|---|---|---|---|
| Test 1 | | | |
| Test 2 | | | |
| Test 3 | | | |
