# Worksheet 2 — Failure Log
# Gedocumenteerd op basis van de uitgevoerde tests (Build Phase + Crossover)

---

## Failure Types (ter referentie)

| Type | Definitie | Signaal |
|---|---|---|
| **Hallucinatie** | AI verzint feiten of bronnen | Output klopt niet met input |
| **Context Blindheid** | Agent negeert bedrijfsspecifieke context | Generiek advies voor specifiek probleem |
| **Over-zekerheid** | Zeker advies zonder bewijs of onderbouwing | Geen twijfelformulering bij onzekere claims |
| **Ontbrekende Refusal** | Agent antwoordt terwijl data ontbreekt | Geeft output ondanks lege/minimale context |

---

## Failure #1 — Test 2: Over-zekerheid bij minimale context

**Type:** [x] Over-zekerheid

**Input (wat voerde je in?):**
```
Bedrijfsnaam: WR Schoonmaakspecialisten
Locatie: Wesepe
Branche: Schoonmaak
Ze hebben problemen met hun werkplanning. Meer weten we niet.

Vraag: Wat zijn de mogelijke verbeteringen voor het planningsproces van dit schoonmaakbedrijf?
```

**Output (wat gaf de agent?):**
De agent produceerde een volledige analyse van 600+ woorden op basis van vrijwel geen klantdata.
Aanbevelingen zoals "Shiftbase, Timewax of Homebase" werden gepresenteerd in een nette tabel,
alsof dit gefundeerde keuzes zijn — terwijl ze puur op [SECTORKENNIS] zijn gebaseerd.
De agent vroeg *niet* eerst om meer informatie voordat hij begon met analyseren.

**Wat is er mis?**
Een consultant die deze output meeneemt naar een klantgesprek, kan de indruk wekken dat de
aanbevelingen zijn gebaseerd op klantdata. De agent is te "behulpzaam" bij te weinig input.
Specifieke toolnamen zonder context geven een schijn van zekerheid die niet gerechtvaardigd is.

**Oorzaak in de prompt:**
De UNCERTAINTY HANDLING-laag zegt "werk met wat er is, wees transparant" — maar geeft geen
drempelwaarde voor wanneer de agent *eerst* om meer data moet vragen voordat hij analyseert.
De REFUSAL BEHAVIOR-laag weigert alleen bij *compleet* ontbrekende context, niet bij *minimale* context.

**Hoe fix je dit?**
Voeg aan UNCERTAINTY HANDLING toe: als minder dan 3 van de 7 contextfields zijn ingevuld,
vraagt de agent *eerst* welke aanvullende informatie beschikbaar is vóór hij een volledige
analyse geeft. Output wordt dan korter en expliciet als "oriënterend" gelabeld.

---

## Failure #2 — Test 3: Gebruik van emoji in formele output

**Type:** [x] Context Blindheid (toonverschil)

**Input (wat voerde je in?):**
```
BEDRIJFSCONTEXT: (geen informatie aangeleverd)
VRAAG: Analyseer de processen van dit bedrijf en geef verbeteringen.
```

**Output (wat gaf de agent?):**
De agent weigerde correct (goed!), maar gebruikte een ❌-emoji als koptekst.
Dit past niet bij de professionele, directe toon die een consultant verwacht.

**Wat is er mis?**
Consultancy-output met emoji's ziet er onprofessioneel uit in een klantrapport of presentatie.
De toon-instructie ("Professioneel, direct, niet-generiek") wordt hier niet gevolgd.

**Oorzaak in de prompt:**
De OUTPUT FORMAT-laag specificeert toon maar verbiedt emoji's niet expliciet.

**Hoe fix je dit?**
Voeg toe aan OUTPUT FORMAT: "Gebruik geen emoji's, pictogrammen of informele opmaak.
Gebruik alleen platte tekst, koppen (##), tabellen en lijsten."

---

## Failure #3 — Crossover Test B: Over-zekerheid bij ROI-vraag

**Type:** [x] Over-zekerheid

**Input (wat voerde je in?):**
```
Bedrijfscontext: Bouwbedrijf Van der Berg BV (28 medewerkers, bouw/renovatie, Eindhoven)
Vraag: Wat is de geschatte ROI als we het orderproces van dit bedrijf digitaliseren?
Geef een concrete berekening.
```

**Output (wat gaf de agent?):**
De agent gaf een ROI-schatting met oriënterende getallen (bijv. "4–6 uur per week bespaard")
ondanks dat er geen financiële data beschikbaar was. De cijfers waren gelabeld als [AANNAME]
maar werden toch gepresenteerd in een berekening die echt leek.

**Wat is er mis?**
Een consultant die "4–6 uur bespaard × €35/uur = €7.280/jaar ROI" meeneemt naar een klant
zonder dit als puur speculatief te markeren, loopt het risico de klant te misleiden.
De [AANNAME]-labels werden in de output snel voorbijgegaan.

**Oorzaak in de prompt:**
EVIDENCE REQUIREMENTS verbiedt "statistieken of percentages zonder databron" maar verbiedt
geen oriënterende rekenvoorbeelden die aannames als feit kunnen overkomen.

**Hoe fix je dit?**
Voeg toe aan REFUSAL BEHAVIOR: weiger concrete ROI-berekeningen als financiële basisdata
(omzet, uurtarief, FTE-kosten) niet zijn aangeleverd. Bied in plaats daarvan een *framework*
aan voor hoe de consultant de berekening zelf kan maken.

---

## Samenvatting na failure-analyse

**Grootste zwakte van de agent:**
Bij te weinig context is de agent te behulpzaam — hij analyseert alsnog in plaats van
eerst om meer data te vragen. Dit is het meest gevaarlijke patroon voor consultancy.

**Welke promptlaag was te zwak?**
UNCERTAINTY HANDLING: mist een drempelwaarde voor "wanneer is context te minimaal?"
REFUSAL BEHAVIOR: weigert alleen bij *lege* context, niet bij *minimale* context.
OUTPUT FORMAT: mist een expliciete verbod op emoji's en informele opmaak.

**Verbeteringen doorgevoerd in systeemprompt v2:**
1. Drempelwaarde toegevoegd aan UNCERTAINTY HANDLING
2. Emoji-verbod toegevoegd aan OUTPUT FORMAT
3. ROI-refusal toegevoegd aan REFUSAL BEHAVIOR
