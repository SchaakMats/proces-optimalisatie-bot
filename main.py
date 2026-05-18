#!/usr/bin/env python3
"""
Process Optimization Agent — Interactive CLI
Minor Digital Transformation & AI | Hackathon Dag
Agent Type 12: Procesoptimalisatie
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import anthropic
from dotenv import load_dotenv

load_dotenv()

AGENT_DIR = Path("agent")
BEDRIJVEN_DIR = Path("bedrijven")
LOGS_DIR = Path("logs")

HEADER = """
╔══════════════════════════════════════════════════════════════╗
║         PROCESS OPTIMIZATION AGENT  —  Type 12              ║
║         AI Consultant Co-Worker | Minor DT&AI                ║
╚══════════════════════════════════════════════════════════════╝
"""

DIVIDER = "─" * 64


def check_api_key():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key or not key.startswith("sk-ant"):
        print("FOUT: ANTHROPIC_API_KEY niet gevonden of ongeldig in .env")
        sys.exit(1)
    return key


def load_system_prompt():
    path = AGENT_DIR / "system_prompt.md"
    if not path.exists():
        print(f"FOUT: Systeemprompt niet gevonden op {path}")
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def load_company_profile(filename: str) -> str:
    path = BEDRIJVEN_DIR / filename
    if not path.exists():
        print(f"FOUT: Bedrijfsprofiel niet gevonden: {path}")
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def list_companies() -> list[str]:
    if not BEDRIJVEN_DIR.exists():
        return []
    return sorted(
        f.name for f in BEDRIJVEN_DIR.glob("*.md")
        if f.name != "template.md"
    )


def save_output(output: str, company: str, query: str):
    LOGS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = company.replace(".md", "").replace(" ", "_")[:30]
    filename = LOGS_DIR / f"{timestamp}_{safe_name}.md"
    content = (
        f"# Output Log — {timestamp}\n\n"
        f"**Bedrijf:** {company}\n\n"
        f"**Vraag:**\n```\n{query}\n```\n\n"
        f"## Agent Output\n\n{output}\n"
    )
    filename.write_text(content, encoding="utf-8")
    print(f"\nOutput opgeslagen in: {filename}")


def run_agent(system_prompt: str, company_context: str, query: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    user_message = f"""BEDRIJFSCONTEXT:
{company_context}

VRAAG VAN DE CONSULTANT:
{query}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


def select_company(companies: list[str]) -> str:
    print("\nBeschikbare bedrijfsprofielen:")
    for i, name in enumerate(companies, 1):
        marker = "  [eigen]" if "jouw_bedrijf" in name else ""
        print(f"  {i}. {name}{marker}")
    print()

    while True:
        raw = input("Kies bedrijfsnummer: ").strip()
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(companies):
                return companies[idx]
        print(f"Ongeldige keuze. Kies 1–{len(companies)}.")


def print_output(text: str):
    print(f"\n{DIVIDER}")
    print(text)
    print(DIVIDER)


def interactive_loop(system_prompt: str, company_file: str, company_context: str):
    print(f"\nBedrijfsprofiel geladen: {company_file}")
    print("Type je vraag (of 'help' voor voorbeelden, 'wissel' voor ander bedrijf, 'stop' om te stoppen)")

    while True:
        print()
        query = input("Jouw vraag: ").strip()

        if not query:
            continue

        if query.lower() in ("stop", "quit", "exit"):
            print("Afsluiten.")
            break

        if query.lower() == "help":
            print_help()
            continue

        if query.lower() == "wissel":
            return "wissel"

        print("\nAgent denkt na...\n")
        try:
            output = run_agent(system_prompt, company_context, query)
        except anthropic.APIError as e:
            print(f"API Fout: {e}")
            continue

        print_output(output)

        save = input("\nOutput opslaan in logs/? (j/n): ").strip().lower()
        if save == "j":
            save_output(output, company_file, query)

    return "stop"


def print_help():
    examples = [
        "Analyseer het orderproces van dit bedrijf en identificeer de grootste verspillingen.",
        "Welke drie procesverbeteringen leveren het meeste op binnen een budget van €30.000?",
        "Wat zijn de risico's als we het retourproces volledig automatiseren?",
        "Analyseer de processen van dit bedrijf (lege context — test refusal).",
        "Wat is de ROI van procesdigitalisering hier? Geef een getal. (test over-zekerheid)",
    ]
    print(f"\n{DIVIDER}")
    print("VOORBEELDVRAGEN (kopieer en pas aan):\n")
    for i, ex in enumerate(examples, 1):
        print(f"  {i}. {ex}")
    print(DIVIDER)


def main():
    print(HEADER)
    check_api_key()

    system_prompt = load_system_prompt()

    companies = list_companies()
    if not companies:
        print("Geen bedrijfsprofielen gevonden in /bedrijven/")
        print("Maak een profiel op basis van bedrijven/template.md")
        sys.exit(1)

    while True:
        company_file = select_company(companies)
        company_context = load_company_profile(company_file)

        result = interactive_loop(system_prompt, company_file, company_context)

        if result == "stop":
            break


if __name__ == "__main__":
    main()
