# Competitive Intelligence Research Agent

A simple multi-agent competitive intelligence system built using LangGraph, Groq, You.com Search API, and Streamlit.

The application accepts a company name, discovers three major competitors, gathers current web and news information for each competitor, analyzes the findings, and produces a structured competitive intelligence briefing for human review.

## Project Overview

The goal of this project is to demonstrate a basic agentic AI workflow that uses:

- Multiple specialized agents
- External search tools
- Shared state
- Conditional routing
- Structured LLM output
- Error handling
- Human review

The workflow is intentionally focused on research and analysis only. It does not send emails, update databases, modify external systems, or make business decisions automatically.

## Architecture

The system contains three specialized agents and one orchestrator.

### 1. Discovery Agent

The Discovery Agent identifies three major competitors of the company entered by the user.

It uses the You.com Search API to retrieve current web information and then uses the LLM to return exactly three competitors in a structured format.

### 2. Research Agent

The Research Agent gathers current information for each competitor.

For every competitor, it performs:

- Web research for pricing, products, features, and market positioning
- News research for recent developments

The web and news searches are handled independently so that the workflow can continue even if one search fails.

### 3. Analyst Agent

The Analyst Agent converts the raw research into a structured competitor report.

Each report contains:

- Competitor Name
- Why It Competes
- Pricing / Business Model
- Key Products and Features
- Market Positioning
- Recent Developments

Pydantic models are used to enforce a consistent structured output.

### 4. Orchestrator

The Orchestrator coordinates the complete research workflow using LangGraph state.

It:

- Checks whether competitors are still waiting to be researched
- Routes the workflow back to the Research Agent when additional competitors remain
- Ends the workflow when all competitors have been processed
- Compiles the completed competitor reports into a final competitive intelligence briefing

## Workflow

```text
User enters company name
        |
        v
Discovery Agent
        |
        v
Find 3 Competitors
        |
        v
Research Agent
        |
        +-------------------+
        |                   |
        v                   v
   Web Search          News Search
        |                   |
        +---------+---------+
                  |
                  v
             Analyst Agent
                  |
                  v
         Structured Report
                  |
                  v
            Orchestrator
             /        \
            /          \
More competitors?      No competitors left
      |                       |
      v                       v
Research Agent          Final Briefing
                              |
                              v
                         Human Review
```

## Shared State

LangGraph uses shared state to pass information between the agents.

The state contains information such as:

- Company name
- List of discovered competitors
- Remaining competitors
- Current competitor
- Current research results
- Completed competitor reports
- Final briefing
- Errors

Example:

```python
{
    "company_name": "Snowflake",
    "competitors": [
        "Databricks",
        "Amazon Redshift",
        "Google BigQuery"
    ],
    "remaining_competitors": [
        "Amazon Redshift",
        "Google BigQuery"
    ],
    "current_competitor": "Databricks",
    "current_research": {},
    "reports": [],
    "final_briefing": "",
    "errors": []
}
```

The `remaining_competitors` list works like a queue. Each competitor is processed one at a time until the list becomes empty.

## Competitor Report Structure

Each competitor report contains the following fields:

```text
Competitor Name
Why It Competes
Pricing / Business Model
Key Products and Features
Market Positioning
Recent Developments
```

Example structure:

```python
{
    "competitor_name": "Databricks",
    "why_competitor": "...",
    "pricing_model": "...",
    "key_features": [
        "...",
        "...",
        "..."
    ],
    "market_positioning": "...",
    "recent_developments": "..."
}
```

## Technology Stack

- Python
- LangGraph
- LangChain
- Groq
- You.com Search API
- Pydantic
- Streamlit
- httpx
- python-dotenv
- uv
- Git
- GitHub

## Project Structure

```text
competitive-intelligence-research-agent/
│
├── app.py
├── graph.py
├── search_tools.py
├── schemas.py
├── .env
├── .env.example
├── .gitignore
├── .python-version
├── pyproject.toml
├── uv.lock
└── README.md
```

### app.py

Contains the Streamlit user interface.

Responsibilities:

- Accept company name from the user
- Create the initial LangGraph state
- Invoke the research workflow
- Display identified competitors
- Display structured competitor reports
- Display the final competitive intelligence briefing
- Display warnings when errors occur

### graph.py

Contains the main agentic workflow.

Responsibilities:

- Groq LLM configuration
- Shared LangGraph state
- Discovery Agent
- Research Agent
- Analyst Agent
- Orchestrator
- Conditional routing
- Final LangGraph compilation

### search_tools.py

Contains the You.com Search API integration.

Responsibilities:

- Call the You.com Search API
- Perform web searches
- Perform news searches
- Format search results
- Retry failed HTTP requests

### schemas.py

Contains Pydantic models used for structured LLM output.

The main models are:

- `CompetitorList`
- `CompetitorReport`

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd competitive-intelligence-research-agent
```

### 2. Install Dependencies

This project uses `uv` for Python environment and dependency management.

Run:

```bash
uv sync
```

### 3. Create Environment Variables

Create a `.env` file in the project folder.

Add:

```text
GROQ_API_KEY=your_groq_api_key
YDC_API_KEY=your_youcom_api_key
```

Do not upload the `.env` file to GitHub.

The `.gitignore` file is configured to exclude it.

### 4. Run the Application

Run:

```bash
uv run python -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

in your browser if Streamlit does not open automatically.

## Example Use Case

Enter:

```text
Snowflake
```

The system will:

1. Search for Snowflake's competitors.
2. Identify three major competitors.
3. Research the first competitor using web and news searches.
4. Analyze the research and create a structured report.
5. Check whether another competitor remains.
6. Repeat the research and analysis process for the remaining competitors.
7. Compile all competitor reports into a final competitive intelligence briefing.
8. Display the results in Streamlit for human review.

## Error Handling

The project includes basic error handling so that temporary tool failures do not immediately terminate the workflow.

### API Retry

You.com search requests automatically retry once if an HTTP request fails.

The process is:

```text
You.com Request
      |
      v
    Failed?
     /   \
   No     Yes
   |       |
Continue   Wait
            |
            v
        Retry Once
```

### Independent Web and News Searches

Web and news searches are executed independently.

For example:

```text
Web Search
    |
    v
Fails
    |
    v
"Web research unavailable"

News Search
    |
    v
Works
    |
    v
News results available

        |
        v
Analyst continues
```

If one search fails, the error is stored in the LangGraph state while the workflow continues using the information that is still available.

If both searches fail, the system records the failures and continues with limited information instead of immediately crashing the entire workflow.

## Human-in-the-Loop

The human review point occurs after the research workflow is complete.

The workflow performs:

```text
Discover Competitors
        |
        v
Research Competitors
        |
        v
Analyze Findings
        |
        v
Generate Final Briefing
        |
        v
Display Results
        |
        v
Human Review
        |
        v
STOP
```

The application does not:

- Send emails
- Save results to a database
- Modify business records
- Make purchases
- Approve business decisions
- Trigger external actions

The final interpretation and decision-making remain with the human user.

## Why This Is an Agentic Workflow

This application is more than a single LLM call.

The system:

- Uses multiple specialized agents
- Calls external tools
- Maintains shared state across multiple steps
- Routes tasks conditionally
- Repeats actions until all competitors are processed
- Handles tool failures
- Produces structured outputs
- Hands the final result to a human for review

The overall workflow is coordinated using LangGraph.

## Sample Agent Flow

```text
START
  |
  v
Discovery Agent
  |
  v
Research Agent
  |
  v
Analyst Agent
  |
  v
Orchestrator
  |
  +---- Competitors Remaining? ---- YES ----> Research Agent
  |
  NO
  |
  v
Final Competitive Intelligence Brief
  |
  v
Human Review
  |
  v
END
```

## Current Scope

This project is intentionally kept simple and focused on the core assignment requirements.

### Included

- Competitor discovery
- Current web research
- Current news research
- Structured competitor analysis
- Multi-step LangGraph workflow
- Shared state
- Conditional routing
- Error handling
- Streamlit user interface
- Human review

### Not Included

- Persistent database storage
- PDF export
- Email delivery
- CRM integration
- Historical competitor tracking
- Vector databases
- RAG
- Cloud deployment
- Automated business actions

These could be added as future enhancements.

## Possible Future Improvements

Possible future enhancements include:

- Exporting reports to PDF or CSV
- Storing historical competitor reports
- Comparing competitor results over time
- Adding source citations to each report
- Adding charts for pricing or feature comparison
- Using asynchronous API calls for faster research
- Adding persistent memory
- Deploying the application to the cloud
- Integrating with CRM or collaboration tools

## Conclusion

The Competitive Intelligence Research Agent demonstrates a simple but complete agentic AI workflow.

It combines external search tools, LLM-based analysis, structured output, shared state, conditional routing, error handling, orchestration, and human review into one end-to-end competitive research application.
