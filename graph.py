from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from schemas import CompetitorList, CompetitorReport
from search_tools import web_search, news_search


load_dotenv()


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)

class ResearchState(TypedDict):
    """Shared state passed between agents in the LangGraph workflow."""

    company_name: str

    competitors: list[str]

    remaining_competitors: list[str]

    current_competitor: str

    current_research: dict

    reports: list[dict]

    final_briefing: str

    errors: list[str]

def discover_competitors(company_name: str) -> CompetitorList:
    """Find exactly three major competitors for the given company."""

    search_results = web_search.invoke(
        {"query": f"{company_name} top competitors alternatives"}
    )

    structured_llm = llm.with_structured_output(
    CompetitorList,
    method="json_schema",
    strict=True,
)

    prompt = f"""
You are a competitive intelligence researcher.

Company being researched:
{company_name}

Below are current web search results:

{search_results}

Using only the information available in the search results,
identify exactly three major competitors of {company_name}.

Requirements:
- Return exactly three company names.
- Choose companies that directly compete with {company_name}.
- Do not include {company_name} itself.
- Do not invent competitors that are unsupported by the search results.
"""

    return structured_llm.invoke(prompt)

def discovery_node(state: ResearchState) -> dict:
    """LangGraph node that discovers competitors and updates shared state."""

    result = discover_competitors(state["company_name"])

    competitors = result.competitors

    return {
        "competitors": competitors,
        "remaining_competitors": competitors.copy(),
    }

def research_competitor(competitor_name: str) -> dict:
    """Gather current web and news information for one competitor."""

    errors = []

    try:
        web_results = web_search.invoke(
            {"query": f"{competitor_name} pricing products features market positioning"}
        )
    except Exception as error:
        web_results = "Web research unavailable."
        errors.append(
            f"Web search failed for {competitor_name}: {error}"
        )

    try:
        news_results = news_search.invoke(
            {"query": competitor_name}
        )
    except Exception as error:
        news_results = "News research unavailable."
        errors.append(
            f"News search failed for {competitor_name}: {error}"
        )

    return {
        "competitor_name": competitor_name,
        "web_results": web_results,
        "news_results": news_results,
        "errors": errors,
    }

def research_node(state: ResearchState) -> dict:
    """LangGraph node that researches the next competitor in the queue."""

    remaining = state["remaining_competitors"]

    current_competitor = remaining[0]

    research_data = research_competitor(current_competitor)

    updated_errors = (
        state.get("errors", [])
        + research_data.get("errors", [])
    )

    return {
        "current_competitor": current_competitor,
        "current_research": research_data,
        "remaining_competitors": remaining[1:],
        "errors": updated_errors,
    }

def analyze_competitor(
    company_name: str,
    research_data: dict,
) -> CompetitorReport:
    """Convert raw research into a structured competitor report."""

    structured_llm = llm.with_structured_output(
        CompetitorReport,
        method="json_schema",
        strict=True,
    )

    prompt = f"""
You are a competitive intelligence analyst.

Our company:
{company_name}

Competitor:
{research_data["competitor_name"]}

Web research:
{research_data["web_results"]}

Recent news:
{research_data["news_results"]}

Create a concise competitor intelligence report.

Requirements:
- Use only the information available in the research above.
- Do not invent facts.
- If pricing or another detail is unavailable, say "Data not found".
- Explain briefly why this company competes with {company_name}.
- Include 3 to 5 important features or capabilities when supported by the research.
- Keep the output factual and concise.
"""

    return structured_llm.invoke(prompt)

def analysis_node(state: ResearchState) -> dict:
    """LangGraph node that analyzes the current competitor research."""

    report = analyze_competitor(
        company_name=state["company_name"],
        research_data=state["current_research"],
    )

    updated_reports = state.get("reports", []) + [report.model_dump()]

    return {
        "reports": updated_reports
    }

def orchestrator_node(state: ResearchState) -> dict:
    """Coordinate the workflow and compile the final briefing when research is complete."""

    if state["remaining_competitors"]:
        return {}

    briefing_lines = [
        f"Competitive Intelligence Brief: {state['company_name']}",
        "",
    ]

    for report in state["reports"]:
        briefing_lines.extend(
            [
                f"Competitor: {report['competitor_name']}",
                f"Why it competes: {report['why_competitor']}",
                f"Pricing / Business Model: {report['pricing_model']}",
                f"Key Features: {', '.join(report['key_features'])}",
                f"Market Positioning: {report['market_positioning']}",
                f"Recent Developments: {report['recent_developments']}",
                "",
            ]
        )

    return {
        "final_briefing": "\n".join(briefing_lines)
    }


def orchestrator_router(state: ResearchState) -> str:
    """Decide whether another competitor should be researched or the workflow should finish."""

    if state["remaining_competitors"]:
        return "research"

    return "end"

def build_graph():
    """Build and compile the competitive intelligence workflow."""

    workflow = StateGraph(ResearchState)

    # Add the agents/nodes
    workflow.add_node("discovery", discovery_node)
    workflow.add_node("research", research_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("orchestrator", orchestrator_node)

    # Define the main workflow
    workflow.add_edge(START, "discovery")
    workflow.add_edge("discovery", "research")
    workflow.add_edge("research", "analysis")
    workflow.add_edge("analysis", "orchestrator")

    # Orchestrator decides whether to continue or finish
    workflow.add_conditional_edges(
        "orchestrator",
        orchestrator_router,
        {
            "research": "research",
            "end": END,
        },
    )

    return workflow.compile()


research_graph = build_graph()