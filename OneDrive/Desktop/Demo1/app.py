"""Interactive Streamlit app: reusable AI adoption strategy generator."""

from __future__ import annotations

import streamlit as st

from knowledge_base import (
    CHALLENGES,
    DEPARTMENTS,
    INDUSTRIES,
    MATURITY_LEVELS,
    OBJECTIVES,
    REGIONS,
)
from strategy_engine import ClientProfile, generate_strategy, strategy_to_markdown

st.set_page_config(
    page_title="AI Adoption Strategy Generator",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .block-container { padding-top: 1.4rem; max-width: 1400px; }
    .hero {
        background: linear-gradient(135deg, #0f2c4c 0%, #1a4f7a 55%, #0e7c7b 100%);
        color: #fff; padding: 1.4rem 1.6rem; border-radius: 16px; margin-bottom: 1.1rem;
    }
    .hero h1 { color: #fff !important; font-size: 1.7rem; margin: 0 0 0.35rem 0; }
    .hero p { margin: 0; opacity: 0.92; }
    .metric-card, .dept-card, .phase-card {
        border: 1px solid #e2e8f0; border-radius: 14px; padding: 0.95rem 1.1rem;
        background: #fff; margin-bottom: 0.75rem;
    }
    .dept-card h3 { margin-top: 0; }
    .pill {
        display: inline-block; background: #e8f1f8; color: #0f2c4c;
        border-radius: 999px; padding: 0.15rem 0.65rem; font-size: 0.78rem;
        margin-right: 0.35rem; margin-bottom: 0.25rem;
    }
    .pill-wave { background: #d7f3ee; color: #0b4f4a; }
    .phase-30 { border-left: 5px solid #1a4f7a; }
    .phase-60 { border-left: 5px solid #0e7c7b; }
    .phase-90 { border-left: 5px solid #c47b17; }
    [data-testid="stSidebar"] { background: #f4f7fb; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def _init_state() -> None:
    if "strategy" not in st.session_state:
        st.session_state.strategy = None
    if "markdown" not in st.session_state:
        st.session_state.markdown = ""


def _profile_from_form(values: dict) -> ClientProfile:
    return ClientProfile(
        name=values["name"].strip(),
        industry=values["industry"],
        business_context=values["business_context"].strip(),
        region=values["region"],
        employees=int(values["employees"]),
        departments=list(values["departments"]),
        maturity=values["maturity"],
        objective=values["objective"],
        challenges=list(values["challenges"]),
        additional_notes=values["additional_notes"].strip(),
    )


def render_sidebar() -> dict | None:
    with st.sidebar:
        st.markdown("### Client intake")
        st.caption("Complete the profile, then generate a department-wise 90-day plan.")

        with st.form("client_intake", clear_on_submit=False):
            name = st.text_input("Client name", placeholder="e.g. Northwind Logistics")
            industry = st.selectbox("Industry", INDUSTRIES, index=INDUSTRIES.index("Manufacturing"))
            region = st.selectbox("Operating region", REGIONS, index=REGIONS.index("EMEA"))
            employees = st.number_input(
                "Number of employees", min_value=10, max_value=500_000, value=2500, step=50
            )
            maturity = st.radio("Current AI maturity", MATURITY_LEVELS, horizontal=True)
            objective = st.selectbox("Primary business objective", OBJECTIVES)

            departments = st.multiselect(
                "Departments in scope",
                DEPARTMENTS,
                default=["HR", "Finance", "Sales", "Operations", "IT", "Customer Support"],
                help="IT is strongly recommended so platform, security, and intake are covered.",
            )
            challenges = st.multiselect(
                "Operational challenges",
                CHALLENGES,
                default=["High volume of repetitive manual work", "Skills and talent gaps"],
            )
            business_context = st.text_area(
                "Industry and business context",
                height=120,
                placeholder="What the organisation does, where value is created, systems in play (ERP, CRM, ITSM), and any constraints.",
            )
            additional_notes = st.text_area(
                "Additional notes (optional)",
                height=70,
                placeholder="Existing Copilot licences, unionised workforce, recent transformation, etc.",
            )
            generate = st.form_submit_button(
                "Generate strategy", type="primary", use_container_width=True
            )

        reset = st.button("Clear results", use_container_width=True)
        if reset:
            st.session_state.strategy = None
            st.session_state.markdown = ""
            st.rerun()

        st.caption("Reusable internally: same engine, different client profiles. No model API required.")

        if generate:
            return {
                "name": name,
                "industry": industry,
                "region": region,
                "employees": employees,
                "maturity": maturity,
                "objective": objective,
                "departments": departments,
                "challenges": challenges,
                "business_context": business_context,
                "additional_notes": additional_notes,
            }
    return None


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>AI Adoption Strategy Generator</h1>
            <p>Interactive, reusable playbook for client organisations — department-wise automation,
            tools, skills, change management, and a 30-60-90 day roadmap.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview(strategy) -> None:
    c = strategy.client
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Client", c.name)
    m2.metric("Industry", c.industry)
    m3.metric("Region", c.region)
    m4.metric("Employees", f"{c.employees:,}")
    m5.metric("Maturity", c.maturity)

    st.markdown("#### Executive summary")
    st.markdown(strategy.executive_summary)

    left, right = st.columns(2)
    with left:
        st.markdown("#### Operating model")
        for item in strategy.operating_model:
            st.markdown(f"- {item}")
        st.markdown("#### Success metrics by day 90")
        for item in strategy.success_metrics:
            st.markdown(f"- {item}")
    with right:
        st.markdown("#### Regional and industry constraints")
        for item in strategy.regional_considerations:
            st.markdown(f"- {item}")
        if strategy.challenge_responses:
            st.markdown("#### Challenge responses")
            for item in strategy.challenge_responses:
                st.markdown(f"- {item}")


def render_departments(strategy) -> None:
    names = [d.name for d in strategy.departments]
    tabs = st.tabs(names)
    for tab, dept in zip(tabs, strategy.departments):
        with tab:
            st.markdown(
                f"<span class='pill pill-wave'>{dept.priority}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**{dept.mission}**")
            st.caption(dept.rationale)

            st.markdown("##### Repetitive and time-consuming work for AI")
            st.dataframe(
                [
                    {
                        "Task": t["task"],
                        "Pain today": t["pain"],
                        "Recommended AI pattern": t["ai_pattern"],
                    }
                    for t in dept.tasks
                ],
                use_container_width=True,
                hide_index=True,
            )

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("##### Recommended tools")
                for tool in dept.tools:
                    st.markdown(f"- {tool}")
                st.markdown("##### KPIs")
                for kpi in dept.kpis:
                    st.markdown(f"- {kpi}")
            with col_b:
                st.markdown("##### Skills required")
                for skill in dept.skills:
                    st.markdown(f"- {skill}")
                st.markdown("##### Training and change (this function)")
                for action in dept.change_actions:
                    st.markdown(f"- {action}")


def render_enablement(strategy) -> None:
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Cross-organisation training")
        st.dataframe(
            strategy.training_program,
            use_container_width=True,
            hide_index=True,
        )
    with col_b:
        st.markdown("#### Change management initiatives")
        for item in strategy.change_management:
            st.markdown(f"- {item}")

    st.markdown("#### Risk register")
    st.dataframe(strategy.risks, use_container_width=True, hide_index=True)


def render_roadmap(strategy) -> None:
    phases = [
        ("30 days", "phase-30", "Foundation, policy, baselines, first knowledge win"),
        ("60 days", "phase-60", "Wave-1 copilots live, evaluate, decide scale vs kill"),
        ("90 days", "phase-90", "Scale winners, lock operating model, 6–12 month portfolio"),
    ]
    cols = st.columns(3)
    for col, (horizon, css, caption) in zip(cols, phases):
        with col:
            st.markdown(
                f"<div class='phase-card {css}'><strong>{horizon}</strong><br>"
                f"<span style='font-size:0.85rem;color:#475569'>{caption}</span></div>",
                unsafe_allow_html=True,
            )
            for i, item in enumerate(strategy.roadmap[horizon], 1):
                st.markdown(f"**{i}.** {item}")


def render_empty() -> None:
    st.info(
        "Use the **Client intake** panel on the left, then click **Generate strategy**. "
        "You can change any field and generate again for a different organisation."
    )
    c1, c2, c3 = st.columns(3)
    c1.markdown(
        "**1. Profile the client**  \nName, industry, region, size, maturity, objective, departments, and challenges."
    )
    c2.markdown(
        "**2. Generate the playbook**  \nDepartment tasks, tools, skills, training, change, risks, and KPIs — sequenced by objective."
    )
    c3.markdown(
        "**3. Export and reuse**  \nDownload Markdown for decks, SOWs, or SharePoint. Re-run for the next client without changing code."
    )


def main() -> None:
    _init_state()
    render_hero()
    values = render_sidebar()

    if values is not None:
        if not values["name"].strip():
            st.error("Enter a client name to generate a named strategy.")
        elif not values["departments"]:
            st.error("Select at least one department.")
        elif not values["business_context"].strip():
            st.error("Add industry and business context so the plan can be tailored.")
        else:
            strategy = generate_strategy(_profile_from_form(values))
            st.session_state.strategy = strategy
            st.session_state.markdown = strategy_to_markdown(strategy)

    strategy = st.session_state.strategy
    if strategy is None:
        render_empty()
        return

    file_stub = strategy.client.name.lower().replace(" ", "-")
    st.download_button(
        label="Download strategy (Markdown)",
        data=st.session_state.markdown.encode("utf-8"),
        file_name=f"{file_stub}-ai-adoption-strategy.md",
        mime="text/markdown",
        type="secondary",
    )

    overview, departments, enablement, roadmap, raw = st.tabs(
        [
            "Overview",
            "Department strategy",
            "Skills, training & change",
            "30-60-90 roadmap",
            "Export preview",
        ]
    )
    with overview:
        render_overview(strategy)
    with departments:
        render_departments(strategy)
    with enablement:
        render_enablement(strategy)
    with roadmap:
        render_roadmap(strategy)
    with raw:
        st.caption("Same content as the downloadable Markdown file.")
        st.code(st.session_state.markdown, language="markdown")


if __name__ == "__main__":
    main()
