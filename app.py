"""
Streamlit UI for Procure-Price-Agent.

A single-page chat application with configuration sidebar and tool visibility toggles.
"""

import time
import sqlite3
import streamlit as st
from pathlib import Path

# Check if database exists, prompt to seed if not
DB_PATH = Path(__file__).parent / "data" / "procurement.db"


def check_database():
    """Check if database exists and has data."""
    if not DB_PATH.exists():
        st.error(
            "⚠️ Database not found! Please run the seed script first:\n\n"
            "```bash\npython -m data.seed\n```"
        )
        st.stop()
    
    # Verify database has items
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM items")
        count = cursor.fetchone()[0]
        conn.close()
        if count == 0:
            st.error("⚠️ Database is empty! Please run: `python -m data.seed`")
            st.stop()
    except Exception as e:
        st.error(f"⚠️ Database error: {e}")


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "orchestrator" not in st.session_state:
        from agent.orchestrator import Orchestrator

        st.session_state.orchestrator = Orchestrator()

    if "show_tool_calls" not in st.session_state:
        st.session_state.show_tool_calls = False

    if "show_notes" not in st.session_state:
        st.session_state.show_notes = False

    if "last_tool_calls" not in st.session_state:
        st.session_state.last_tool_calls = []

    if "last_notes" not in st.session_state:
        st.session_state.last_notes = []


def render_sidebar():
    """Render the configuration sidebar."""
    st.sidebar.title("⚙️ Configuration")

    # Scenario picker
    st.sidebar.subheader("📋 Demo Scenarios")

    scenarios = {
        "--- Procurement ---": None,
        "Procure EPDM Rubber": (
            "Procure 5000 kg of EPDM rubber compound for our automotive sealing line, "
            "delivery within 4 weeks, prefer reliable vendors with volume discounts."
        ),
        "MRO - Hydraulic Seals": (
            "Source 25 hydraulic seal kits for press maintenance, balanced cost and lead time."
        ),
        "--- Pricing ---": None,
        "Set Sell Price - EPDM": (
            "Set sell price for EPDM rubber compound with 35% target margin, "
            "considering competitor prices and the current high demand signal."
        ),
        "Set Sell Price - Carbon Black": (
            "Recommend a sell price for Carbon Black N550 with 30% target margin."
        ),
        "--- Analytics & Insights ---": None,
        "Spending Analysis": (
            "Show me our spending summary across all categories and vendors."
        ),
        "Vendor Performance": (
            "Which vendors have the best on-time delivery performance? Rank our vendors."
        ),
        "Margin Analysis": (
            "Analyze our margins across items - where do we have room to price higher?"
        ),
        "Savings Opportunities": (
            "Where are we overpaying? Find cost savings opportunities in our procurement."
        ),
        "Price Trends": (
            "Show me price trends from our purchase history - which items have volatile pricing?"
        ),
    }

    # Filter out section headers for selectbox display
    scenario_options = [k for k in scenarios.keys()]
    
    selected_scenario = st.sidebar.selectbox(
        "Select a scenario",
        options=scenario_options,
        index=1,  # Default to first actual scenario
        format_func=lambda x: x if not x.startswith("---") else x,
    )

    # Only show button if not a section header
    if not selected_scenario.startswith("---") and scenarios.get(selected_scenario):
        if st.sidebar.button("📝 Load Scenario", use_container_width=True):
            st.session_state.pending_prompt = scenarios[selected_scenario]
    elif selected_scenario.startswith("---"):
        st.sidebar.caption("↑ Select a scenario above")

    st.sidebar.divider()

    # Settings
    st.sidebar.subheader("🌍 Settings")

    region = st.sidebar.selectbox(
        "Region",
        options=["US-West", "US-East", "EU", "APAC", "Global"],
        index=0,
    )

    currency = st.sidebar.selectbox(
        "Currency",
        options=["USD", "EUR", "GBP", "JPY"],
        index=0,
    )

    target_margin = st.sidebar.slider(
        "Target Margin (%)",
        min_value=10,
        max_value=60,
        value=30,
        step=5,
    )

    shipping_pref = st.sidebar.selectbox(
        "Shipping Preference",
        options=["standard", "express", "economy"],
        index=0,
    )

    # Update orchestrator settings
    st.session_state.orchestrator.update_settings(
        region=region,
        currency=currency,
        target_margin=float(target_margin),
        shipping_preference=shipping_pref,
    )

    st.sidebar.divider()

    # Display toggles
    st.sidebar.subheader("👁️ Display Options")

    st.session_state.show_tool_calls = st.sidebar.toggle(
        "Show tool calls",
        value=st.session_state.show_tool_calls,
        help="Display the tools called during processing",
    )

    st.session_state.show_notes = st.sidebar.toggle(
        "Show chain of thought",
        value=st.session_state.show_notes,
        help="Display the agent's reasoning process",
    )

    st.sidebar.divider()

    # Reset button
    if st.sidebar.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.orchestrator.reset()
        st.session_state.last_tool_calls = []
        st.session_state.last_notes = []
        st.rerun()


def render_tool_calls(tool_calls: list):
    """Render tool calls in an expandable section."""
    if not tool_calls:
        return

    with st.expander(f"🔧 Tool Calls ({len(tool_calls)})", expanded=False):
        for i, call in enumerate(tool_calls, 1):
            col1, col2 = st.columns([1, 3])
            with col1:
                status = "✅" if call.get("success", True) else "❌"
                st.markdown(f"**{status} {call['tool_name']}**")
            with col2:
                st.markdown(f"*{call['result_summary']}*")

            # Show arguments
            if call.get("arguments"):
                st.code(str(call["arguments"]), language="json")

            if i < len(tool_calls):
                st.divider()


def render_notes(notes: list):
    """Render chain of thought in an expandable section."""
    if not notes:
        return

    with st.expander(f"💭 Chain of Thought ({len(notes)})", expanded=False):
        for note in notes:
            # Clean up the note display
            if note.startswith("💭 "):
                st.markdown(f"{note}")
            else:
                st.markdown(f"• {note}")


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Procure-Price Agent",
        page_icon="🛒",
        layout="wide",
    )

    # Check database
    check_database()

    # Initialize state
    initialize_session_state()

    # Render sidebar
    render_sidebar()

    # Main area
    st.title("🛒 Procure-Price Agent")
    st.markdown(
        "A procurement and pricing copilot. Ask me to source items, compare vendor quotes, "
        "recommend awards, or set sell prices."
    )

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show tool calls and notes for assistant messages
            if message["role"] == "assistant":
                if st.session_state.show_tool_calls and message.get("tool_calls"):
                    render_tool_calls(message["tool_calls"])
                if st.session_state.show_notes and message.get("notes"):
                    render_notes(message["notes"])

    # Check for pending prompt from scenario button
    pending_prompt = st.session_state.pop("pending_prompt", None)

    # Chat input
    prompt = st.chat_input("What would you like to procure or price?")

    # Use pending prompt if available
    if pending_prompt and not prompt:
        prompt = pending_prompt

    if prompt:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response from orchestrator with live updates
        with st.chat_message("assistant"):
            # Create placeholders for status and response
            status_placeholder = st.empty()
            response_placeholder = st.empty()
            
            accumulated_response = ""
            tool_calls = []
            thinking_steps = []  # Capture chain of thought
            
            def on_status(status_type: str, message: str | None):
                """Callback to update status in real-time."""
                if message:
                    status_placeholder.markdown(f"*{message}*")
                    # Capture thinking messages for chain of thought
                    if message.startswith("💭"):
                        thinking_steps.append(message)
            
            try:
                # Stream the response with status callbacks
                for chunk in st.session_state.orchestrator.chat_with_callbacks(
                    prompt, 
                    on_status=on_status
                ):
                    accumulated_response += chunk
                    response_placeholder.markdown(accumulated_response + "▌")
                    time.sleep(0.01)  # Small delay for smooth streaming effect
                
                # Clear status and show final response
                status_placeholder.empty()
                response_placeholder.markdown(accumulated_response)
                
                tool_calls = st.session_state.orchestrator.get_tool_calls_log()
                # Use captured thinking steps instead of intermediate notes
                notes = thinking_steps if thinking_steps else st.session_state.orchestrator.get_intermediate_notes()
                
            except Exception as e:
                status_placeholder.empty()
                accumulated_response = f"❌ Error: {str(e)}"
                response_placeholder.markdown(accumulated_response)
                tool_calls = []
                notes = [f"Error occurred: {str(e)}"]

            # Show tool calls and notes
            if st.session_state.show_tool_calls and tool_calls:
                render_tool_calls(tool_calls)
            if st.session_state.show_notes and notes:
                render_notes(notes)

        # Save to message history
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": accumulated_response,
                "tool_calls": tool_calls,
                "notes": notes,
            }
        )

        st.session_state.last_tool_calls = tool_calls
        st.session_state.last_notes = notes


if __name__ == "__main__":
    main()
