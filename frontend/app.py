import streamlit as st
import requests
import json

st.set_page_config(page_title="AI Code Review Assistant", page_icon="🤖", layout="wide")

st.title("AI-Powered Code Review Assistant")
st.write("Analyze your code, detect issues, and get AI-driven recommendations instantly.")

# Sidebar
st.sidebar.header("Settings")
llm_mode = st.sidebar.radio("Mode", ["Demo", "Local LLM", "Remote API"])
api_url = st.sidebar.text_input("Backend URL", "http://localhost:8000/review")

st.sidebar.markdown("---")
st.sidebar.write("💡 Tip: Paste your code and click *Run Review* to get insights.")

# Main content
code = st.text_area("Paste your code here:", height=350, placeholder="def example_function():\n    pass")

col1, col2 = st.columns([1, 3])
with col1:
    run_button = st.button("Run Review")

# When button clicked
if run_button:
    if not code.strip():
        st.warning("Please paste some code first.")
    else:
        st.info("Reviewing code... please wait.")

        # Mocked AI review output for demo mode
        if llm_mode == "Demo":
            demo_response = {
                "lint_issues": [
                    {"line": 2, "type": "style", "message": "Function name should be lowercase (PEP8)."},
                    {"line": 3, "type": "logic", "message": "Function does not return any value."},
                ],
                "ai_feedback": [
                    {
                        "issue_type": "optimization",
                        "description": "Consider using list comprehension for better readability.",
                        "line_number": 5,
                        "suggested_fix": "Replace the for loop with a list comprehension."
                    }
                ]
            }
            response = demo_response
        elif llm_mode == "Local LLM":
            try:
                payload = {"prompt": f"Review this code:\n{code}"}
                r = requests.post(api_url, json=payload)
                response = r.json()
            except Exception as e:
                st.error(f"Error connecting to local backend: {e}")
                response = {}
        else:
            st.error("Remote API mode not yet implemented.")
            response = {}

        # Display results
        if response:
            st.subheader("🧾 Lint & Static Analysis")
            if "lint_issues" in response and response["lint_issues"]:
                for issue in response["lint_issues"]:
                    st.markdown(f"🔹 **Line {issue['line']}** — *{issue['type']}*: {issue['message']}")
            else:
                st.success("No linting issues detected ✅")

            st.subheader("💬 AI Suggestions")
            if "ai_feedback" in response and response["ai_feedback"]:
                for fb in response["ai_feedback"]:
                    st.markdown(f"""
                    **Issue Type:** {fb['issue_type']}  
                    **Line:** {fb['line_number']}  
                    **Description:** {fb['description']}  
                    **Suggested Fix:**  
                    ```python
                    {fb['suggested_fix']}
                    ```
                    """)
            else:
                st.success("No AI feedback generated ✅")
