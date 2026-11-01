"""Generate a tailored, department-wise AI adoption strategy from client inputs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from knowledge_base import (
    DEPARTMENT_PLAYBOOKS,
    INDUSTRY_CONTEXT,
    INDUSTRY_TASK_OVERLAYS,
    MATURITY_POSTURE,
    OBJECTIVE_EMPHASIS,
    REGION_CONTEXT,
    size_band,
)


@dataclass
class ClientProfile:
    name: str
    industry: str
    business_context: str
    region: str
    employees: int
    departments: list[str]
    maturity: str
    objective: str
    challenges: list[str]
    additional_notes: str = ""


@dataclass
class DepartmentStrategy:
    name: str
    mission: str
    priority: str
    rationale: str
    tasks: list[dict[str, str]]
    tools: list[str]
    skills: list[str]
    change_actions: list[str]
    kpis: list[str]


@dataclass
class AdoptionStrategy:
    client: ClientProfile
    generated_on: str
    size_label: str
    executive_summary: str
    operating_model: list[str]
    regional_considerations: list[str]
    challenge_responses: list[str]
    departments: list[DepartmentStrategy]
    training_program: list[dict[str, str]]
    change_management: list[str]
    roadmap: dict[str, list[str]]
    risks: list[dict[str, str]]
    success_metrics: list[str]


PRIORITY_ORDER = {
    "IT": 0,
    "Customer Support": 1,
    "Operations": 2,
    "Finance": 3,
    "Sales": 4,
    "HR": 5,
    "Legal": 6,
    "Procurement": 7,
    "Marketing": 8,
    "R&D / Product": 9,
}

OBJECTIVE_LEAD_DEPTS = {
    "Reduce operating cost": ["Finance", "Operations", "Customer Support", "IT", "Procurement"],
    "Increase productivity / capacity": ["IT", "Operations", "Sales", "Finance", "HR"],
    "Improve customer experience": ["Customer Support", "Sales", "Operations", "Marketing", "IT"],
    "Accelerate decision making": ["Finance", "Operations", "IT", "R&D / Product", "Sales"],
    "Strengthen compliance and risk control": ["Legal", "Finance", "IT", "HR", "Procurement"],
    "Grow revenue": ["Sales", "Marketing", "Customer Support", "R&D / Product", "IT"],
    "Improve employee experience": ["HR", "IT", "Customer Support", "Operations", "Finance"],
    "Modernize operations / digital transformation": ["IT", "Operations", "Finance", "HR", "Legal"],
}


def _priority_for(dept: str, selected: list[str], objective: str, maturity: str) -> str:
    leads = OBJECTIVE_LEAD_DEPTS.get(objective, [])
    if dept == "IT":
        return "Foundational — run in wave 1"
    if dept == "Legal" and maturity == "Beginner":
        return "Foundational (policy) — light wave 1, deeper wave 2"
    if dept in leads[:2] and dept in selected:
        return "Wave 1 — primary value"
    if dept in leads and dept in selected:
        return "Wave 1 / 2 — supporting value"
    if dept in ("Legal", "IT"):
        return "Enabling — parallel track"
    return "Wave 2 — after first wins"


def _task_count(maturity: str, employees: int) -> int:
    base = {"Beginner": 3, "Intermediate": 4, "Advanced": 5}.get(maturity, 4)
    if employees < 200:
        return min(base, 3)
    if employees >= 5000:
        return min(base + 1, 5)
    return base


def _merge_tasks(dept: str, industry: str, limit: int) -> list[dict[str, str]]:
    playbook = DEPARTMENT_PLAYBOOKS[dept]
    tasks = list(playbook["tasks"])
    overlays = INDUSTRY_TASK_OVERLAYS.get(industry, {}).get(dept, [])
    # Industry-specific tasks go first so the strategy feels tailored.
    merged: list[dict[str, str]] = []
    seen = set()
    for item in overlays + tasks:
        key = item["task"]
        if key in seen:
            continue
        seen.add(key)
        merged.append(item)
        if len(merged) >= limit:
            break
    return merged


def _department_rationale(
    dept: str, client: ClientProfile, priority: str
) -> str:
    challenge_hint = ""
    joined = " ".join(client.challenges).lower()
    if dept in ("Customer Support", "Sales") and "customer" in joined:
        challenge_hint = " This maps directly to the stated customer-experience pressure."
    elif dept in ("Finance", "Operations") and (
        "repetitive" in joined or "cost" in joined or "reporting" in joined
    ):
        challenge_hint = " This is a high-volume, measurable-hour opportunity given current operational challenges."
    elif dept == "IT" and ("fragmented" in joined or "skills" in joined):
        challenge_hint = " IT must also absorb platform, security, and enablement load so other functions can move."
    elif dept == "HR" and ("change" in joined or "skills" in joined):
        challenge_hint = " HR is both a use-case owner and the adoption engine for the rest of the organisation."
    elif dept == "Legal" and ("regulatory" in joined or "compliance" in joined):
        challenge_hint = " Legal is on the critical path because of the compliance pressure you flagged."

    return (
        f"{priority}. For a {size_band(client.employees).lower()} {client.industry.lower()} "
        f"organisation at {client.maturity.lower()} AI maturity, {dept} is sequenced this way "
        f"against the objective '{client.objective}'.{challenge_hint}"
    )


def _operating_model(client: ClientProfile, size: str) -> list[str]:
    posture = MATURITY_POSTURE[client.maturity]
    items = [
        f"**Ambition:** {posture['ambition']}",
        f"**Governance:** {posture['governance']}",
        f"**Architecture:** {posture['architecture']}",
        f"**Talent:** {posture['talent']}",
    ]
    if size in ("Small", "Mid-market"):
        items.append(
            "**Structure:** Do not create a large CoE. Name one executive sponsor, one AI product owner, "
            "and department champions. Review the portfolio every two weeks."
        )
    else:
        items.append(
            "**Structure:** Establish a lightweight AI Centre of Enablement (platform, risk, change) with "
            "federated department product owners. The CoE does not own every use case."
        )
    if client.region in ("EMEA", "Global / Multi-region"):
        items.append(
            "**Employee relations:** Build works-council / employee-representative consultation into the "
            "wave-1 calendar; it will set the critical path more than technology will."
        )
    return items


def _challenge_responses(client: ClientProfile) -> list[str]:
    mapping = {
        "High volume of repetitive manual work": "Target 2–3 processes with clear volume, standard work, and a system of record. Baseline minutes per transaction before the pilot.",
        "Slow or inconsistent decision making": "Stand up a governed knowledge or metrics assistant for the decision owners, then add exception recommendations — not autonomous decisions.",
        "Fragmented data and systems": "Pick use cases that can live on documents + one primary system first. Run a parallel data-product backlog; do not wait for a perfect lakehouse.",
        "Skills and talent gaps": "Fund role-based academies and champions before extra licences. Unused seats are more expensive than training.",
        "Regulatory / compliance pressure": "Legal and risk join wave 1. Every production use case gets a risk tier, logging, and an evaluation set.",
        "Inconsistent customer or employee experience": "Start with agent/employee assist (human sends) so quality lifts before any bot talks to customers or staff unattended.",
        "Limited process visibility and reporting lag": "Narrative generation only on a defined metric dictionary. Pair Copilot in BI with a semantic layer owner.",
        "Change resistance and low digital adoption": "Lead with time-back, not surveillance. Supervisors and team leads are the adoption channel; measure usage and sentiment.",
        "Cost pressure and resource constraints": "Cap wave 1 at three use cases. Prefer tools already in the estate (M365, Google, Salesforce, ServiceNow, ERP).",
        "Quality, error, or rework issues": "Use AI for classification, extraction, and first-draft documentation with mandatory review. Track first-time-right, not just speed.",
    }
    out = []
    for challenge in client.challenges:
        advice = mapping.get(challenge, "Treat this as a design constraint on sequencing and risk controls.")
        out.append(f"**{challenge}:** {advice}")
    return out


def _training_program(client: ClientProfile, depts: list[str]) -> list[dict[str, str]]:
    program = [
        {
            "audience": "All employees in scope",
            "focus": "What AI is allowed to do here, data-handling rules, how to prompt, and how to verify outputs.",
            "format": "90-minute live briefing + 30-minute refresher at day 60",
        },
        {
            "audience": "Department champions and people managers",
            "focus": "Coaching 'draft then verify', spotting bad outputs, and running 15-minute huddles on wins and failures.",
            "format": "Half-day workshop in week 2–3 of each wave",
        },
        {
            "audience": "IT / data / security",
            "focus": "Intake, risk tiers, logging, identity-aware retrieval, vendor review, and cost controls.",
            "format": "Technical deep-dive + working playbook",
        },
    ]
    if "Legal" in depts or "HR" in depts:
        program.append(
            {
                "audience": "Legal, HR, risk, and compliance",
                "focus": "DPIA/model-risk light, employment and monitoring rules, privileged data, and high-risk use-case veto criteria.",
                "format": "Working session before any HR screening or customer-facing bot",
            }
        )
    if client.maturity == "Beginner":
        program.append(
            {
                "audience": "Power users (8–12 people)",
                "focus": "Build the first prompt library and FAQ corpus for each wave-1 process.",
                "format": "Weekly clinic for six weeks",
            }
        )
    else:
        program.append(
            {
                "audience": "Domain builders / analysts",
                "focus": "Evaluation sets, retrieval quality, workflow integration, and human-in-the-loop design.",
                "format": "Enablement squad pairing on live use cases",
            }
        )
    if client.region in ("APAC", "LATAM", "EMEA", "Global / Multi-region"):
        program.append(
            {
                "audience": "Local market champions",
                "focus": "Language quality, local policy exceptions, and translation of the change story.",
                "format": "Train-the-trainer in local language",
            }
        )
    return program


def _change_management(client: ClientProfile) -> list[str]:
    size = size_band(client.employees)
    items = [
        f"Name a visible executive sponsor at {client.name} and a single AI product owner accountable for the 90-day outcomes.",
        "Frame the programme as time-back and quality-up. Do not lead with headcount reduction in the first 90 days — it will freeze adoption.",
        "Publish a one-page acceptable-use policy and an approved-tool list before licences are broadly issued.",
        "Create a champion network (one per selected department) with a 30-minute fortnightly forum to swap prompts, failures, and process tweaks.",
        "Instrument adoption: weekly active users, prompts per user, % outputs actually used, and a two-question sentiment pulse.",
    ]
    if size in ("Upper mid-market", "Enterprise"):
        items.append(
            "Run a formal change impact assessment per wave-1 process (roles, SOPs, controls, union/works-council implications)."
        )
    if client.region in ("EMEA", "Global / Multi-region"):
        items.append(
            "Schedule employee-representative consultation in days 1–30. HR/Legal AI use cases wait for that gate."
        )
    if "Change resistance and low digital adoption" in client.challenges:
        items.append(
            "Pilot with volunteers and respected team leads first. Publicise hour-saved stories; keep early QA non-punitive."
        )
    return items


def _roadmap(client: ClientProfile, dept_strats: list[DepartmentStrategy]) -> dict[str, list[str]]:
    wave1 = [d.name for d in dept_strats if "Wave 1" in d.priority or "Foundational" in d.priority]
    wave1_label = ", ".join(wave1[:5]) if wave1 else "selected functions"
    region = REGION_CONTEXT[client.region]
    maturity = client.maturity

    days_30 = [
        f"Kick off with {client.name} sponsor: confirm objective '{client.objective}', success metrics, and out-of-scope list.",
        "Complete an AI use-case intake for each selected department; score by value, feasibility, data readiness, and risk.",
        "Lock an approved-tool catalog (ideally estate-native copilots plus one knowledge assistant).",
        "Stand up governance: working group, risk tiers, logging/DLP baseline, and the acceptable-use policy.",
        f"Regional gate: {region['data_posture']}",
        "Baseline KPIs for the top 2–3 processes (time, volume, error/rework, CSAT or cycle time).",
        "Deliver all-staff briefing and champion nomination for " + wave1_label + ".",
        "Start one low-risk knowledge assistant (policy, SOP, or IT/HR FAQ) so people feel a win early.",
    ]
    if maturity == "Beginner":
        days_30.append(
            "Literacy over build: no custom models. Focus on prompts, templates, and clean source documents."
        )
    else:
        days_30.append(
            "Stand up the shared retrieval pattern (identity, corpus, evaluation questions) that later use cases will reuse."
        )

    days_60 = [
        "Go live with 2–3 wave-1 copilots or workflow assists in " + wave1_label + " (human-in-the-loop).",
        "Train power users; publish the first prompt and SOP library per live process.",
        "Run the first evaluation: sample outputs for accuracy, tone, policy fit, and leakage risk.",
        "IT implements intake-to-approved-pattern so new ideas do not become shadow AI.",
        "Change: supervisor huddles, office hours, and a visible 'what good looks like' gallery.",
        "Decision: kill, fix, or scale each pilot using pre-agreed KPI movement — not anecdotes alone.",
    ]
    if "Legal" in [d.name for d in dept_strats]:
        days_60.append(
            "Legal playbook: standard NDA/intake or DPIA first-draft live internally; still no unsupervised send."
        )
    if maturity == "Advanced":
        days_60.append(
            "Platform slice: model gateway, cost telemetry, and an eval harness on at least one agentic workflow in a sandbox."
        )

    days_90 = [
        "Scale the winning 1–2 use cases to the full in-scope teams; freeze the rest of the backlog.",
        "Add wave-2 departments only if wave-1 adoption and quality bars are met.",
        "Formalise the operating model (product owner, champions, review cadence, funding for licences + enablement).",
        "Produce a 6–12 month portfolio: next processes, data products, and (if justified) platform investment.",
        "Training refresh and a public readout of hours returned, quality movement, and lessons learned.",
        "Risk review: update the register, vendor DPAs, and residual high-risk items for the executive sponsor.",
    ]
    if client.employees >= 1000:
        days_90.append(
            "Propose the year-1 business case with benefits by department, licence true-up, and CoE/enablement headcount."
        )
    else:
        days_90.append(
            "Keep the footprint small: one owner, a short tool list, and a quarterly value review rather than a standing CoE."
        )

    return {"30 days": days_30, "60 days": days_60, "90 days": days_90}


def _risks(client: ClientProfile) -> list[dict[str, str]]:
    industry = INDUSTRY_CONTEXT.get(client.industry, {})
    risks = [
        {
            "risk": "Hallucinated or ungrounded outputs used as facts",
            "mitigation": "Human send for all external and control-impacting content; require citations to the system of record or approved corpus.",
        },
        {
            "risk": "Sensitive data leaving the tenant via consumer tools",
            "mitigation": "Block consumer AI on corporate data; enterprise contracts with no-training clauses; DLP on the approved channel.",
        },
        {
            "risk": "Licence sprawl and unused seats",
            "mitigation": "Stage rollouts by champion cohorts; review utilisation at day 45 and reclaim idle licences.",
        },
        {
            "risk": "Change resistance or fear of job loss",
            "mitigation": "Sponsor narrative is capacity and quality. Redesign roles with HR after value is proven, not before.",
        },
    ]
    if industry.get("risk"):
        risks.insert(
            0,
            {
                "risk": f"Industry-specific: {industry['risk']}",
                "mitigation": "Keep humans accountable for safety, conduct, clinical, credit, or regulated decisions in the 90-day window.",
            },
        )
    if client.region in ("EMEA", "Global / Multi-region"):
        risks.append(
            {
                "risk": "Works-council or employment-law delay",
                "mitigation": "Consult early; delay HR monitoring/screening use cases until the employee-relations gate is passed.",
            }
        )
    if client.maturity == "Advanced":
        risks.append(
            {
                "risk": "Agentic process actions without control",
                "mitigation": "Tool allow-lists, maker-checker for write actions, evals in CI, and kill switches before any production agent.",
            }
        )
    return risks


def _success_metrics(client: ClientProfile, depts: list[DepartmentStrategy]) -> list[str]:
    metrics = [
        "Programme: % of wave-1 users active weekly, % of outputs used without full rewrite, champion coverage by department.",
        f"Objective alignment: evidence that '{client.objective}' moved on at least two leading indicators by day 90.",
        "Risk: zero unapproved tools in the in-scope teams; 100% of production use cases logged in the register.",
    ]
    for dept in depts[:4]:
        if dept.kpis:
            metrics.append(f"{dept.name}: {', '.join(dept.kpis[:3])}.")
    return metrics


def _executive_summary(client: ClientProfile, size: str, depts: list[DepartmentStrategy]) -> str:
    industry = INDUSTRY_CONTEXT.get(client.industry, {})
    context = client.business_context.strip() or "the operating context provided"
    wave1 = [d.name for d in depts if "Wave 1" in d.priority or "Foundational" in d.priority]
    notes = f" Additional context from the client: {client.additional_notes.strip()}" if client.additional_notes.strip() else ""
    return (
        f"This 90-day AI adoption plan is tailored to **{client.name}**, a {size.lower()} "
        f"**{client.industry}** organisation with **{client.employees:,} employees** operating in "
        f"**{client.region}**, currently at **{client.maturity}** AI maturity. The primary objective is "
        f"**{client.objective}**. {industry.get('lens', '')} "
        f"Business context considered: {context}. "
        f"Wave-1 emphasis: {', '.join(wave1) if wave1 else 'the selected departments'}. "
        f"{OBJECTIVE_EMPHASIS.get(client.objective, '')} "
        f"The approach is reusable: same operating model and risk gates, different processes and tools per department.{notes}"
    )


def generate_strategy(client: ClientProfile) -> AdoptionStrategy:
    size = size_band(client.employees)
    selected = [d for d in client.departments if d in DEPARTMENT_PLAYBOOKS]
    if "IT" not in selected:
        # IT is always an enabling track even if not ticked — but only add if user selected departments.
        pass

    limit = _task_count(client.maturity, client.employees)
    dept_strats: list[DepartmentStrategy] = []
    for dept in sorted(selected, key=lambda d: PRIORITY_ORDER.get(d, 99)):
        playbook = DEPARTMENT_PLAYBOOKS[dept]
        priority = _priority_for(dept, selected, client.objective, client.maturity)
        tools = list(playbook["tools_by_maturity"].get(client.maturity, playbook["tools_by_maturity"]["Beginner"]))
        dept_strats.append(
            DepartmentStrategy(
                name=dept,
                mission=playbook["mission"],
                priority=priority,
                rationale=_department_rationale(dept, client, priority),
                tasks=_merge_tasks(dept, client.industry, limit),
                tools=tools,
                skills=list(playbook["skills"]),
                change_actions=list(playbook["change"]),
                kpis=list(playbook["kpis"]),
            )
        )

    region = REGION_CONTEXT[client.region]
    industry = INDUSTRY_CONTEXT.get(client.industry, {})
    regional = [
        region["data_posture"],
        region["works_council"],
        region["language"],
        region["vendors"],
    ]
    if industry.get("data_note"):
        regional.append(f"Industry data constraint: {industry['data_note']}")

    return AdoptionStrategy(
        client=client,
        generated_on=date.today().isoformat(),
        size_label=size,
        executive_summary=_executive_summary(client, size, dept_strats),
        operating_model=_operating_model(client, size),
        regional_considerations=regional,
        challenge_responses=_challenge_responses(client),
        departments=dept_strats,
        training_program=_training_program(client, selected),
        change_management=_change_management(client),
        roadmap=_roadmap(client, dept_strats),
        risks=_risks(client),
        success_metrics=_success_metrics(client, dept_strats),
    )


def strategy_to_markdown(strategy: AdoptionStrategy) -> str:
    c = strategy.client
    lines: list[str] = [
        f"# AI Adoption Strategy — {c.name}",
        "",
        f"*Generated {strategy.generated_on} · {c.industry} · {c.region} · {c.employees:,} employees · {strategy.size_label} · {c.maturity} maturity*",
        "",
        "## 1. Executive summary",
        "",
        strategy.executive_summary.replace("**", ""),
        "",
        "### Profile",
        "",
        f"- **Client:** {c.name}",
        f"- **Industry:** {c.industry}",
        f"- **Region:** {c.region}",
        f"- **Employees:** {c.employees:,} ({strategy.size_label})",
        f"- **AI maturity:** {c.maturity}",
        f"- **Primary objective:** {c.objective}",
        f"- **Departments in scope:** {', '.join(c.departments)}",
        f"- **Challenges:** {', '.join(c.challenges) if c.challenges else 'None specified'}",
        "",
        "### Business context",
        "",
        c.business_context.strip() or "Not provided.",
        "",
    ]
    if c.additional_notes.strip():
        lines += ["### Additional notes", "", c.additional_notes.strip(), ""]

    lines += ["## 2. Operating model", ""]
    for item in strategy.operating_model:
        lines.append(f"- {item}")
    lines += ["", "## 3. Regional and industry constraints", ""]
    for item in strategy.regional_considerations:
        lines.append(f"- {item}")

    if strategy.challenge_responses:
        lines += ["", "## 4. Response to stated challenges", ""]
        for item in strategy.challenge_responses:
            lines.append(f"- {item}")

    lines += ["", "## 5. Department-wise strategy", ""]
    for dept in strategy.departments:
        lines += [
            f"### {dept.name}",
            "",
            f"**Priority:** {dept.priority}",
            "",
            dept.mission,
            "",
            dept.rationale,
            "",
            "#### Repetitive / time-consuming work to automate",
            "",
            "| Task | Pain today | AI pattern |",
            "| --- | --- | --- |",
        ]
        for task in dept.tasks:
            lines.append(f"| {task['task']} | {task['pain']} | {task['ai_pattern']} |")
        lines += ["", "#### Recommended tools", ""]
        for tool in dept.tools:
            lines.append(f"- {tool}")
        lines += ["", "#### Skills required", ""]
        for skill in dept.skills:
            lines.append(f"- {skill}")
        lines += ["", "#### Training and change actions", ""]
        for action in dept.change_actions:
            lines.append(f"- {action}")
        lines += ["", "#### KPIs", ""]
        for kpi in dept.kpis:
            lines.append(f"- {kpi}")
        lines.append("")

    lines += ["## 6. Skills, training, and change management", "", "### Cross-organisation training", ""]
    for row in strategy.training_program:
        lines.append(f"- **{row['audience']}:** {row['focus']} *({row['format']})*")
    lines += ["", "### Change management initiatives", ""]
    for item in strategy.change_management:
        lines.append(f"- {item}")

    lines += ["", "## 7. 30-60-90 day implementation roadmap", ""]
    for horizon, items in strategy.roadmap.items():
        lines += [f"### {horizon}", ""]
        for i, item in enumerate(items, 1):
            lines.append(f"{i}. {item}")
        lines.append("")

    lines += ["## 8. Risks and mitigations", ""]
    for row in strategy.risks:
        lines.append(f"- **{row['risk']}:** {row['mitigation']}")

    lines += ["", "## 9. Success metrics (day 90)", ""]
    for item in strategy.success_metrics:
        lines.append(f"- {item}")

    lines += [
        "",
        "---",
        "",
        "*Reusable generator output. Tailor named vendors to the client's existing estate during discovery. "
        "This is an operating strategy, not legal, clinical, or investment advice.*",
        "",
    ]
    return "\n".join(lines)
