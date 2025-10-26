import streamlit as st
import requests
import json
import os
import vertexai
from vertexai.generative_models import GenerativeModel
import google.auth
from google.auth import default
from google.auth.transport.requests import Request

# ============================================
# Configuration
# ============================================
PROJECT_ID = os.getenv("PROJECT_ID", "nuk-datatech-poc")
LOCATION = os.getenv("LOCATION", "us-central1")
REGION = os.getenv("REGION", "us-central1")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://your-mcp-server-url.run.app")
DATASET_ID = os.getenv("DATASET_ID", "sales_data")
TABLE_ID = os.getenv("TABLE_ID", "orders")
VERTEX_AI_MODEL = os.getenv("VERTEX_AI_MODEL", "gemini-1.5-flash")

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel(VERTEX_AI_MODEL)


# ============================================
# Helper Functions
# ============================================
def get_id_token():
    """Get ID token for authenticated requests to Cloud Run"""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2 import service_account
        import google.auth
        import os

        # Try to get credentials
        credentials, project = google.auth.default()

        # For service accounts, we need to create ID token credentials
        if hasattr(credentials, 'service_account_email'):
            # This is a service account
            target_audience = MCP_SERVER_URL

            # Import ID token credentials
            try:
                from google.oauth2 import id_token
                from google.auth.transport import requests

                # Get ID token for the target audience
                request = requests.Request()
                id_token_val = id_token.fetch_id_token(request, target_audience)
                return id_token_val
            except Exception as e:
                print(f"ID token fetch failed: {e}")
                return None
        else:
            print("Not running with service account credentials")
            return None

    except Exception as e:
        st.warning(f"Could not get ID token: {e}. Proceeding without authentication.")
        return None


def validate_question(question):
    """Validate if question is relevant to the sales dataset"""
    validation_prompt = f"""
You are a data analyst. Determine if this question is relevant to a sales order dataset.

Dataset Schema:
- order_id, customer_name, product, quantity, price, order_date, region

User Question: {question}

Answer with ONLY "YES" if the question is about sales data, orders, customers, products, revenue, or dates.
Answer with ONLY "NO" if the question is a greeting, irrelevant, or not about the dataset.

Examples:
- "hello" -> NO
- "what's the weather?" -> NO
- "total sales by region" -> YES
- "top customers" -> YES
"""
    response = model.generate_content(validation_prompt)
    is_valid = response.text.strip().upper()
    return "YES" in is_valid


def generate_sql(question):
    """Generate SQL query from natural language question"""
    prompt = f"""
You are a SQL expert. Convert this natural language question to a BigQuery SQL query.

Dataset: {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}
Schema:
- order_id (STRING)
- customer_name (STRING)
- product (STRING)
- quantity (INTEGER)
- price (FLOAT)
- order_date (DATE)
- region (STRING)

Question: {question}

IMPORTANT RULES:
1. Return ONLY the SQL query without any explanation or markdown formatting
2. Do not include ```sql or ``` markers
3. ALWAYS use column aliases (AS clause) for all calculated columns and aggregations
4. Use descriptive alias names (e.g., total_revenue, customer_count, avg_price)

Example: SELECT SUM(price * quantity) AS total_revenue FROM ...
"""
    response = model.generate_content(prompt)
    sql_query = response.text.strip()
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    return sql_query


def execute_query(sql_query):
    """Execute SQL query via MCP Server"""
    id_token = get_id_token()
    headers = {"Content-Type": "application/json"}
    if id_token:
        headers["Authorization"] = f"Bearer {id_token}"

    response = requests.post(
        f"{MCP_SERVER_URL}/query_bigquery",
        json={"sql": sql_query, "project_id": PROJECT_ID},
        headers=headers,
        timeout=30,
    )
    print(f"Request Headers: {headers}")
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    print(f"MCP Server URL: {MCP_SERVER_URL}/query_bigquery")
    return response


def generate_summary(question, data):
    """Generate natural language summary of query results"""
    summary_prompt = f"""
Based on this data, provide a brief natural language summary of the results:

Question: {question}
Results: {json.dumps(data[:5])}

Give a concise 2-3 sentence summary.
"""
    response = model.generate_content(summary_prompt)
    return response.text


def render_sidebar():
    """Render sidebar with examples and configuration"""
    with st.sidebar:
        st.header("� Example Questions")
        st.markdown("""
    - What are the total sales by region?
    - Who are the top 3 customers by revenue?
    - How many laptops were sold?
    - What was the total revenue in February?
    - Show me all orders from the North region
    """)

        st.markdown("---")
        st.markdown(f"**Dataset:** `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`")
        st.markdown("""
    **Schema:**
    - order_id (STRING)
    - customer_name (STRING)
    - product (STRING)
    - quantity (INTEGER)
    - price (FLOAT)
    - order_date (DATE)
    - region (STRING)
    """)

        st.markdown("---")
        st.markdown("**Configuration:**")
        st.code(f"""
Project: {PROJECT_ID}
Region: {REGION}
Location: {LOCATION}
Model: {VERTEX_AI_MODEL}
MCP Server: {MCP_SERVER_URL}
    """)


def process_question(user_question):
    """Main processing logic for user question"""
    # Step 1: Validate question
    with st.spinner("🔍 Validating question..."):
        if not validate_question(user_question):
            st.error("❌ Your question doesn't seem to be related to the sales data.")
            st.info("💡 Try asking about sales, customers, products, revenue, or orders.")
            return

    # Step 2: Generate SQL
    with st.spinner("🤔 Generating SQL query..."):
        sql_query = generate_sql(user_question)
        if not sql_query:
            st.error("❌ Failed to generate SQL query. Please try rephrasing your question.")
            return

    st.subheader("📊 Generated SQL Query")
    st.code(sql_query, language="sql")

    # Step 3: Execute query
    with st.spinner("📡 Executing query via MCP Server..."):
        mcp_response = execute_query(sql_query)

        if mcp_response.status_code == 200:
            result = mcp_response.json()
            st.success(f"✅ Query executed successfully! Found {result['row_count']} rows")

            if result["data"]:
                st.subheader("📈 Results")
                st.dataframe(result["data"], use_container_width=True)

                # Step 4: Generate summary
                with st.spinner("💭 Generating summary..."):
                    summary = generate_summary(user_question, result["data"])
                    st.subheader("💡 Summary")
                    st.info(summary)
            else:
                st.info("No results found for your query.")
        else:
            st.error(f"❌ MCP Server Error: {mcp_response.text}")
            if mcp_response.status_code == 403:
                st.error("Authentication failed. The service account may not have permission to invoke the MCP server.")


# ============================================
# Main App
# ============================================
def main():
    st.set_page_config(page_title="Natural Language to BigQuery", page_icon="🔍")
    st.title("🔍 Ask Questions About Your Data")
    st.markdown("Ask questions in plain English and get insights from BigQuery!")

    render_sidebar()

    user_question = st.text_input(
        "Ask your question:",
        placeholder="e.g., What are the total sales by region?"
    )

    if st.button("🚀 Get Answer", type="primary"):
        if not user_question:
            st.warning("Please enter a question!")
        else:
            try:
                process_question(user_question)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.exception(e)

    st.markdown("---")
    st.markdown(f"**Powered by:** Streamlit + Vertex AI ({VERTEX_AI_MODEL}) + MCP Server + BigQuery")


if __name__ == "__main__":
    main()
