from google.adk.agents.llm_agent import Agent

# import tools
from agent.tools.bq_tools import list_datasets, list_tables, get_table_schema
from agent.tools.gcs_tools import list_buckets, list_files

# Root agent definition
root_agent = Agent(
    model="gemini-2.5-flash",
    name="GCP Assistant",
    description="Internal GCP assistant for BigQuery, GCS, Pub/Sub and Cloud Run tasks.",
    instruction=(
        "You are a helpful GCP assistant. "
        'Always start the conversation with: "I\'m your GCP assistant. How can I help you today?" '
        "Help users with Google Cloud Platform operations including BigQuery, Cloud Storage, and other GCP services. "
        "Understand the user's request and choose the correct tool automatically. "
        "If no tool is needed, answer normally with helpful GCP guidance. "
        "Return structured output when calling tools."
    ),
    tools=[list_datasets, list_tables, get_table_schema, list_buckets, list_files],
)
