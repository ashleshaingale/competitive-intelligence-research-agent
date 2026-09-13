import streamlit as st

from graph import research_graph


st.set_page_config(
    page_title="Competitive Intelligence Research Agent",
    page_icon="🔎",
    layout="wide",
)


st.title("Competitive Intelligence Research Agent")

st.write(
    "Enter a company name to discover its top competitors "
    "and generate a structured competitive intelligence report."
)


company_name = st.text_input(
    "Company Name",
    placeholder="Example: Snowflake",
)


if st.button("Run Research"):
    if not company_name.strip():
        st.warning("Please enter a company name.")

    else:
        initial_state = {
            "company_name": company_name.strip(),
            "competitors": [],
            "remaining_competitors": [],
            "current_competitor": "",
            "current_research": {},
            "reports": [],
            "final_briefing": "",
            "errors": [],
        }

        with st.spinner("Running competitor research..."):
            try:
                result = research_graph.invoke(initial_state)

                st.success("Research completed.")

                st.subheader("Competitors Identified")

                for competitor in result["competitors"]:
                    st.write(f"- {competitor}")

                st.subheader("Competitor Reports")

                for report in result["reports"]:
                    with st.expander(report["competitor_name"]):
                        st.markdown("**Why It Competes**")
                        st.write(report["why_competitor"])

                        st.markdown("**Pricing / Business Model**")
                        st.write(report["pricing_model"])

                        st.markdown("**Key Features**")
                        for feature in report["key_features"]:
                            st.write(f"- {feature}")

                        st.markdown("**Market Positioning**")
                        st.write(report["market_positioning"])

                        st.markdown("**Recent Developments**")
                        st.write(report["recent_developments"])

                st.subheader("Final Competitive Intelligence Brief")
                st.text(result["final_briefing"])

                if result["errors"]:
                    st.subheader("Warnings")

                    for error in result["errors"]:
                        st.warning(error)

            except Exception as error:
                st.error(f"Research failed: {error}")