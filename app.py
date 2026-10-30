
import streamlit as st
import re
import json
from datetime import datetime

st.set_page_config(
    page_title="PlanWise AI",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 PlanWise AI")
st.subheader("Agent Planning and Tool Selection Evaluator")
st.caption(
    "A local prototype inspired by research on agent planning "
    "and tool learning."
)

# ---------------- TOOL LIBRARY ----------------

TOOLS = {
    "calculator": {
        "description": "Performs arithmetic calculations",
        "keywords": ["calculate", "sum", "total", "budget", "cost", "price"],
    },
    "search": {
        "description": "Searches a small local knowledge base",
        "keywords": ["search", "find", "information", "research", "learn"],
    },
    "planner": {
        "description": "Organizes tasks into an ordered plan",
        "keywords": ["plan", "organize", "schedule", "steps", "trip"],
    },
    "checklist": {
        "description": "Creates a checklist of required actions",
        "keywords": ["checklist", "remember", "prepare", "requirements"],
    },
}

# ---------------- PLANNING ENGINE ----------------

def create_plan(task):
    text = task.lower()
    steps = []

    if any(word in text for word in ["trip", "travel", "journey", "vacation"]):
        steps = [
            ("Identify destination and travel requirements", "search"),
            ("Organize activities and travel steps", "planner"),
            ("Estimate costs and check the budget", "calculator"),
            ("Prepare a final travel checklist", "checklist"),
        ]

    elif any(word in text for word in ["budget", "cost", "calculate", "price", "sum"]):
        steps = [
            ("Identify the amounts and calculation needed", "search"),
            ("Calculate the total or estimated cost", "calculator"),
            ("Organize the result into a practical plan", "planner"),
        ]

    elif any(word in text for word in ["research", "study", "learn", "information"]):
        steps = [
            ("Identify the information required", "planner"),
            ("Search the available local knowledge base", "search"),
            ("Organize the findings into steps", "planner"),
            ("Create a checklist of follow-up actions", "checklist"),
        ]

    else:
        steps = [
            ("Analyze the requested goal", "planner"),
            ("Identify useful information", "search"),
            ("Organize the required actions", "checklist"),
        ]

    return steps


# ---------------- TOOL EXECUTION ----------------

def execute_tool(tool, task):
    if tool == "calculator":
        numbers = re.findall(r"\d+(?:\.\d+)?", task)
        if len(numbers) >= 2:
            total = sum(float(n) for n in numbers)
            return f"Sum of extracted numbers: {total:g}"
        return "Calculator ready. No two or more numbers were found."

    if tool == "search":
        return (
            "Local search tool selected. No external web search "
            "was performed in this prototype."
        )

    if tool == "planner":
        return "Planning tool selected to organize the task."

    if tool == "checklist":
        return "Checklist tool selected to track required actions."

    return "No matching tool available."


# ---------------- USER INTERFACE ----------------

task = st.text_area(
    "Enter a task for the agent",
    placeholder="Example: Plan a trip with a budget of 5000 and calculate costs",
    height=100,
)

scenario = st.selectbox(
    "Evaluation Scenario",
    [
        "Normal Execution",
        "Simulate Incorrect Tool Selection",
    ],
)


run = st.button("🚀 Plan and Execute", type="primary")

if run:
    if not task.strip():
        st.warning("Please enter a task first.")
    else:
        plan = create_plan(task)
        if scenario == "Simulate Incorrect Tool Selection":
            action, tool = plan[0]
            wrong_tool = "calculator" if tool != "calculator" else "search"
            plan[0] = (action, wrong_tool)

        st.markdown("## 1. Generated Plan")


        
        for index, (description, tool) in enumerate(plan, start=1):
            st.write(f"**Step {index}:** {description}")
            st.caption(f"Selected tool: {tool}")

        st.markdown("## 2. Tool Execution Trace")
        results = []

        for index, (description, tool) in enumerate(plan, start=1):
            output = execute_tool(tool, task)
            results.append({
                "step": index,
                "action": description,
                "tool": tool,
                "output": output,
            })

            with st.expander(f"Step {index}: {tool}", expanded=True):
                st.write("**Action:**", description)
                st.write("**Tool output:**", output)

        st.markdown("## 3. Evaluation Results")

        # Evaluate whether each selected tool matches its action
        def expected_tool(action):
            text = action.lower()

            if any(word in text for word in ["calculate", "cost", "budget", "total"]):
                return "calculator"

            if any(word in text for word in ["search", "information", "identify"]):
                return "search"

            if any(word in text for word in ["organize", "plan", "activities"]):
                return "planner"

            if any(word in text for word in ["checklist", "required actions"]):
                return "checklist"

            return None

        correct_selections = sum(
            item["tool"] == expected_tool(item["action"])
            for item in results
            if expected_tool(item["action"]) is not None
        )

        evaluated_steps = sum(
            expected_tool(item["action"]) is not None
            for item in results
        )

        tool_validity = (
            correct_selections / evaluated_steps * 100
            if evaluated_steps else 0.0
        )

        plan_complete = len(results) > 0
        plan_completion = 100.0 if plan_complete else 0.0

        # This measures execution coverage, not real-world task success.
        execution_coverage = (
            sum(bool(item["output"]) for item in results)
            / len(results) * 100
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Tool Validity", f"{tool_validity:.1f}%")
        col2.metric("Plan Completion", f"{plan_completion:.1f}%")
        col3.metric("Execution Coverage", f"{execution_coverage:.1f}%")

        st.info(
            "These are prototype metrics, not official PlanningArena "
            "benchmark scores. Execution coverage means each planned "
            "step returned an output; it does not prove the user's goal "
            "was achieved."
        )

        st.markdown("## 4. Export Execution Trace")

        report = {
            "project": "PlanWise AI",
            "task": task,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "plan": [
                {"step": i, "action": action, "tool": tool}
                for i, (action, tool) in enumerate(plan, start=1)
            ],
            "execution_trace": results,
            "metrics": {
                "tool_validity_percent": tool_validity,
                "plan_completion_percent": plan_completion,
                "execution_coverage_percent": execution_coverage,
            },
        }

        st.download_button(
            "Download JSON Report",
            data=json.dumps(report, indent=2),
            file_name="planwise_report.json",
            mime="application/json",
        )