# Worksheet 1 — Agent Design Canvas
# Process Optimization Agent (Type 12)
# Ingevuld op basis van de Build Phase

---

| Dimensie | Jouw invulling |
|---|---|
| **Agent Type** | Process Optimization Agent (Type 12) |
| **Bedrijfsnaam** | WR Schoonmaakspecialisten, Wesepe |
| **Doelgebruiker** | Junior/medior consultant bij een MKB-digitalisatietraject in de facilitaire sector |
| **Exacte taak van de agent** | Analyseer bedrijfsprocessen van een schoonmaakbedrijf, identificeer verspillingen via de TIMWOODS-methode, en lever concrete, haalbare verbeterprioriteiten voor de consultant |
| **Welke bedrijfsdata heeft de agent nodig?** | Bedrijfsnaam, branche, bedrijfsgrootte, beschrijving kernprocessen (planning, uitvoering, urenregistratie, materiaalbe heer), bekende knelpunten, beschikbare data, specifieke consultant-focus |
| **Wat mag de agent NOOIT doen?** | Specifieke percentages of ROI-cijfers verzinnen zonder databron; tools aanbevelen als "de beste keuze" zonder onderbouwing; strategische beslissingen nemen (bijv. "jullie moeten iemand ontslaan"); financiële claims maken zonder financiële data |
| **Wanneer moet de agent stoppen/weigeren?** | Als minder dan bedrijfsnaam + branche + één concreet proces is aangeleverd. Als de vraag buiten procesoptimalisatie valt (bijv. financiële audit of HR-conflicten). |
| **Hoe ziet goede output eruit?** | Gestructureerd rapport: samenvatting (5 regels), contextcheck, proceskaart per proces, TIMWOODS-tabel, optimalisatiepotentieel per knelpunt, top 3 prioriteiten, vervolgacties voor consultant, kwaliteitsscore 1–5 |
| **Hoe weet de gebruiker wanneer de output klopt?** | Output bevat alleen claims die zijn gelabeld als FEIT (traceerbaar naar aangeleverde data), INTERPRETATIE of AANNAME/SECTORKENNIS. Geen ongedekte statistieken of ROI-berekeningen. |
| **Welke ECC-momenten zijn verwacht?** | Bij ontbrekende tijdschattingen per processtap, bij ROI-claims, bij aannames over aantal medewerkers of contractvorm, bij aanbevelingen van specifieke softwaretools zonder klantdata |

---

## Notities Build Phase

- Agent weigert correct bij lege context (Test 3 geslaagd)
- Agent markeert aannames bij gedeeltelijke context (Test 2 geslaagd)
- **Gevonden zwakte:** bij gedeeltelijke context produceert de agent toch 600+ woorden op basis van [SECTORKENNIS] — dit voelt overmatig zelfverzekerd voor zo weinig input
