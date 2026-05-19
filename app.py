#!/usr/bin/env python3
"""
Process Optimization Agent — Web Interface
Start: python3 app.py  →  open http://localhost:5000
"""

import os
import json
import re
from pathlib import Path
from flask import Flask, render_template, request, Response, stream_with_context
import anthropic
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

app = Flask(__name__)

BEDRIJVEN_DIR = Path("bedrijven")
AGENT_DIR = Path("agent")

REQUIRED_FIELDS = ["bedrijfsnaam", "branche", "bedrijfsgrootte", "kernprocessen", "bekende_knelpunten"]


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r'\.(?=[a-z0-9])', '', s)  # remove dots in abbreviations like b.v. → bv
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    s = re.sub(r'\s+', '_', s.strip())
    return s


def parse_summary_response(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return {"missing_fields": REQUIRED_FIELDS, "intake_complete": False, "md_content": ""}


def load_system_prompt() -> str:
    return (AGENT_DIR / "system_prompt.md").read_text(encoding="utf-8")


def list_companies() -> list[dict]:
    companies = []
    for f in sorted(BEDRIJVEN_DIR.glob("*.md")):
        if f.name == "template.md":
            continue
        label = f.stem.replace("_", " ").replace("-", " ").title()
        companies.append({"value": f.stem, "label": label})
    return companies


def load_company(stem: str) -> str:
    path = BEDRIJVEN_DIR / f"{stem}.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_supervisor_prompt() -> str:
    return (AGENT_DIR / "supervisor_prompt.md").read_text(encoding="utf-8")


def load_summary_prompt() -> str:
    return (AGENT_DIR / "summary_prompt.md").read_text(encoding="utf-8")


def call_summary_agent(history: list, company_slug: str) -> dict:
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    summary_prompt = load_summary_prompt()

    history_text = "\n".join([
        f"{'KLANT' if m['role'] == 'user' else 'SUPERVISOR'}: {m['content']}"
        for m in history
    ])

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=summary_prompt,
        messages=[{"role": "user", "content": f"GESPREKSHISTORIE:\n{history_text}"}],
    )

    result = parse_summary_response(message.content[0].text)

    return {
        "missing_fields": result.get("missing_fields", REQUIRED_FIELDS),
        "intake_complete": result.get("intake_complete", False),
        "md_content": result.get("md_content", ""),
    }


@app.route("/")
def index():
    return render_template("index.html", companies=list_companies())


@app.route("/api/companies")
def companies_list():
    return {"companies": list_companies()}


@app.route("/api/new-company", methods=["POST"])
def new_company():
    data = request.get_json()
    name = (data.get("name") or "").strip()
    if not name:
        return {"error": "Naam is verplicht"}, 400

    slug = slugify(name)
    path = BEDRIJVEN_DIR / f"{slug}.md"

    if not path.exists():
        path.write_text(
            f"# Bedrijfsprofiel — {name}\n\n*Profiel wordt aangemaakt via intake gesprek.*\n",
            encoding="utf-8",
        )

    return {"slug": slug, "name": name}


@app.route("/api/summary", methods=["POST"])
def summary():
    data = request.get_json()
    company_slug = data.get("company_slug", "")
    history = data.get("history", [])

    if not company_slug or not history:
        return {"error": "company_slug en history zijn verplicht"}, 400

    result = call_summary_agent(history, company_slug)

    md_content = result.get("md_content", "")
    if md_content:
        (BEDRIJVEN_DIR / f"{company_slug}.md").write_text(md_content, encoding="utf-8")

    return {
        "missing_fields": result.get("missing_fields", REQUIRED_FIELDS),
        "intake_complete": result.get("intake_complete", False),
    }


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    company_stem = data.get("company", "")
    user_message = data.get("message", "").strip()
    history = data.get("history", [])

    if not user_message:
        return {"error": "Geen bericht ontvangen"}, 400

    system_prompt = load_system_prompt()
    company_context = load_company(company_stem)

    # Build messages: history + new user message
    messages = []
    for turn in history:
        messages.append({"role": turn["role"], "content": turn["content"]})

    full_user_content = (
        f"BEDRIJFSCONTEXT:\n{company_context}\n\nVRAAG VAN DE CONSULTANT:\n{user_message}"
        if not history
        else user_message
    )
    messages.append({"role": "user", "content": full_user_content})

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    def generate():
        try:
            with client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=2000,
                system=system_prompt,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    yield f"data: {json.dumps(text)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps(f'[FOUT: {str(e)}]')}\n\n"
            yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    print("\n  Process Optimization Agent")
    print("  Open: http://localhost:8080\n")
    app.run(debug=False, port=8080)
