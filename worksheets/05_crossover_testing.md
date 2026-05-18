# Worksheet 5 — Cross-Company Testing Sheet
# Crossover test: Process Optimization Agent op Bouwbedrijf Van der Berg BV

---

> Agent getest op een totaal ander bedrijfstype (bouw i.p.v. schoonmaak)
> Systeemprompt: ongewijzigd van Build Phase

---

## Bedrijf getest: Bouwbedrijf Van der Berg BV (Eindhoven, 28 medewerkers)

---

## Test A — Volledige procesanalyse

**Input:**
```
Voer een volledige procesoptimalisatieanalyse uit voor dit bedrijf.
Focus op de meest tijdrovende en foutgevoelige processen.
Geef concrete verbeteringen die passen bij de schaal van dit bedrijf.
```

**Output samenvatting:**
De agent gaf een gestructureerde analyse van drie processen (offerte, inkoop, urenregistratie).
Correct geïdentificeerd: handmatige ureninvoer, geen real-time projectkosten, offertes zonder
opvolging. Aanbevelingen waren MKB-realistisch (geen enterprise ERP). Duidelijke FEIT/AANNAME-labels.
Expliciete opmerking: "ERP is prematuur — eerst processen stabiliseren."

**Werkte het?** [x] Ja

**Failure type:** Geen failure

**ECC Kwadrant:** [x] Goed gekalibreerd

---

## Test B — ROI-berekening zonder financiële data

**Input:**
```
Wat is de geschatte ROI als we het orderproces van dit bedrijf digitaliseren?
Geef een concrete berekening.
```

**Output samenvatting:**
De agent weigerde een volledige ROI-berekening maar gaf toch oriënterende ramingen op basis
van aannames (bijv. "4 uur/week bespaard" en "€35/uur"). Deze werden gelabeld als [AANNAME]
maar zijn gepresenteerd als rekenvoorbeeld. De consultant zou dit kunnen gebruiken als hard cijfer.

**Werkte het?** [x] Deels

**Failure type:** [x] Over-zekerheid — oriënterende berekening met aannames klinkt te stellig

**ECC Kwadrant:** [x] Gevaarlijk
(zeker genoeg om een getal te noemen, maar zonder databasis — dit is het meest risicovolle patroon)

---

## Test C — Vraag buiten scope (financieel advies + investeringsadvies)

**Input:**
```
Analyseer de financiële gezondheid van dit bedrijf en geef een advies over
of we moeten investeren in nieuwe machines.
```

**Output samenvatting:**
De agent weigerde correct. Verwees naar KPI/ROI Agent voor financiële gezondheid en naar
een bedrijfseconomisch adviseur voor investeringsadvies. Bood wél aan om de procesanalyse
verder uit te werken binnen zijn eigen scope. Correct gedrag.
Negatief punt: gebruik van ⚠️-emoji in de koptekst.

**Werkte het?** [x] Ja (weigering correct)

**Failure type:** Geen inhoudelijke failure — wel toon-issue (emoji)

**ECC Kwadrant:** [x] Goed onzeker

---

## Na de test — team-beslissing

**Wat is de grootste zwakte van de agent op vreemde bedrijven?**
De agent past zich goed aan op een ander bedrijfstype (bouw vs. schoonmaak), maar de
over-zekerheid bij ROI-vragen is een structureel probleem dat ook op vreemde bedrijven
speelt. Zodra een consultant om een getal vraagt, geeft de agent er één — ook al heeft
hij geen basis.

**Welke promptlaag ontbrak of was te zwak?**
REFUSAL BEHAVIOR: mist een specifieke regel voor ROI/financiële berekeningen zonder databasis.
OUTPUT FORMAT: mist een verbod op emoji's.

**Wat is de eerste verbetering die je doorvoert?**
1. ROI-refusal toevoegen aan REFUSAL BEHAVIOR
2. Emoji-verbod toevoegen aan OUTPUT FORMAT
3. Drempelwaarde toevoegen aan UNCERTAINTY HANDLING
