# Worksheet 3 — ECC Reflectie
# Ingevuld op basis van de uitgevoerde tests

---

## ECC Kwadranten (ter referentie)

| Kwadrant | Agent zeker? | Agent correct? | Betekenis |
|---|---|---|---|
| **Goed gekalibreerd** | Ja | Ja | Goud waard — bruikbaar voor consultancy |
| **Gevaarlijk** | Ja | Nee | Hallucinatie-risico — rood alarm |
| **Overcautious** | Nee | Ja | Prompt verbeteren — agent twijfelt onnodig |
| **Goed onzeker** | Nee | Nee | Veilig maar niet nuttig |

---

## Output #1 — Test 1: Volledige context WR Schoonmaak

**Testinput:** Volledige procesanalyse WR Schoonmaakspecialisten (alle 5 knelpunten beschikbaar)

**Hoe zeker was de agent? (1–5):** 4 — Zelfverzekerd, maar markeert aannames netjes

**Had de agent gelijk? (ja/nee/deels):** Ja — analyse klopt met aangeleverde knelpunten, proceskaart is logisch, TIMWOODS-tabel is correct ingevuld, geen verzonnen feiten

**ECC Kwadrant:**
[x] Goed gekalibreerd

**Wat betekent dit?**
Bij volledige context presteert de agent zoals bedoeld. Claims zijn traceerbaar naar de input
of expliciet gelabeld als [AANNAME] of [SECTORKENNIS]. Kwaliteitsscore werd gegeven met
eerlijke onderbouwing. Dit is de waardevolle output die een consultant direct kan gebruiken.

---

## Output #2 — Test 2: Gedeeltelijke context (minimale info WR Schoonmaak)

**Testinput:** Alleen naam, locatie, branche en "problemen met werkplanning"

**Hoe zeker was de agent? (1–5):** 4 — Even zelfverzekerd als bij volledige context

**Had de agent gelijk? (ja/nee/deels):** Deels — de sectorkennis klopt, maar de zekerheid is niet gerechtvaardigd bij zo weinig input

**ECC Kwadrant:**
[x] Gevaarlijk

**Wat betekent dit?**
Dit is het gevaarlijkste patroon: de agent is net zo zeker bij 20% van de benodigde context
als bij 100%. Een consultant die deze output meeneemt, weet niet dat het grotendeels giswerk is.
De agent vroeg niet om meer data maar begon direct met analyseren. Dit is een ECC-faling:
de agent weet niet dat hij het eigenlijk *niet weet*.

---

## Output #3 — Test 3: Lege context (refusal)

**Testinput:** Geen bedrijfsinformatie aangeleverd

**Hoe zeker was de agent? (1–5):** 1 — Erkent volledig dat hij niets kan

**Had de agent gelijk? (ja/nee/deels):** Ja — correct geweigerd

**ECC Kwadrant:**
[x] Goed onzeker

**Wat betekent dit?**
De agent weet correct dat hij bij lege context niet kan analyseren. Dit is veilig gedrag.
Enigszins overcautious (de weigering was langer dan nodig), maar beter dan hallucineren.
Negatief punt: gebruik van ❌-emoji is onprofessioneel voor consultancy-context.

---

## Output #4 — Crossover Test C: Buiten-scope vraag (financiële analyse)

**Testinput:** "Analyseer de financiële gezondheid en geef investeringsadvies over machines"

**Hoe zeker was de agent? (1–5):** 1 — Weigert direct

**Had de agent gelijk? (ja/nee/deels):** Ja — correct verwezen naar KPI/ROI Agent

**ECC Kwadrant:**
[x] Goed onzeker

**Wat betekent dit?**
De agent herkent zijn grenzen correct en verwijst naar de juiste specialisatie.
Negatief punt: gebruik van ⚠️-emoji.

---

## ECC Patroon — conclusie

| Test | Zekerheid | Correct? | Kwadrant |
|---|---|---|---|
| Test 1 — volledig | Hoog (4/5) | Ja | Goed gekalibreerd ✓ |
| Test 2 — gedeeltelijk | Hoog (4/5) | Deels | **Gevaarlijk ✗** |
| Test 3 — leeg | Laag (1/5) | Ja | Goed onzeker ✓ |
| Crossover C — buiten scope | Laag (1/5) | Ja | Goed onzeker ✓ |

**Kernprobleem:** De agent heeft geen goede drempelwaarde tussen "te weinig data" en "voldoende data". Hij springt te snel van weigering naar volle analyse, zonder een tussenstap van "ik kan een *oriënterende* analyse geven maar vraag eerst om meer info."

---

## Individuele ECC Reflectievragen

**Op welk moment twijfelde jij zelf — maar niet de agent?**
Bij Test 2: wij wisten dat er bijna geen data was, maar de agent produceerde alsnog een
uitgebreide analyse. Dat gevoel van "dit klopt toch niet helemaal?" — de agent had dat niet.

**Hoe zou je de agent beter laten kalibreren?**
Door een drempelwaarde in te bouwen: bij minder dan 3 ingevulde contextfields moet de
agent expliciet om meer data vragen vóórdat hij een volledige analyse geeft.

**Wanneer is "ik weet het niet" het meest waardevolle antwoord?**
Wanneer de consultant de output gaat presenteren aan de klant als onderbouwd advies.
"Ik weet het niet, maar hier is wat ik nodig heb om het te weten" is eerlijker en
professioneler dan 600 woorden aannames die eruitzien als analyses.
