import streamlit as st
import asyncio
from src.state import AgentState
from main import build_app
from src.langflow_client import run_langflow

# Page Config
st.set_page_config(page_title="GenAI Mechanic", page_icon="🚗", layout="wide")

st.title("🚗 AI Vehicle Diagnostic Assistant")
st.markdown("---")

# --- Sidebar: The "OBD-II Port" Simulator ---
with st.sidebar:
    st.header("🔌 OBD-II Simulator")
    st.info("Simulate the data coming from the car's computer.")
    
    # 1. DTC Selector
    selected_dtcs = st.multiselect(
        "Active Fault Codes (DTCs)",
        ["P0300", "P0171", "P0420", "P0442", "OEM-991"],
        default=[]
    )
    
    # 2. Sensor Sliders
    st.subheader("Live Sensor Data")
    rpm = st.slider("Engine RPM", 0, 8000, 850)
    fuel_trim = st.slider("Fuel Trim (STFT %)", -25, 25, 0)
    temp = st.slider("Coolant Temp (°F)", 0, 250, 195)
    
    # Pack sensor data into a dict
    sensor_snapshot = {
        "rpm": rpm,
        "fuel_trim": f"{fuel_trim}%",
        "coolant_temp": f"{temp}°F"
    }
    
    st.write("### Current Car State:")
    st.json({"codes": selected_dtcs, "sensors": sensor_snapshot})

# --- Main Chat Interface ---

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "app" not in st.session_state:
    st.session_state.app = build_app()

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle User Input
# Handle User Input
if prompt := st.chat_input("Describe the problem (e.g., 'My car is shaking')..."):
    # 1. Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Prepare the State for the Agents
    # We inject the sidebar data so the agents can "read" the car
    initial_state = {
        "messages": [prompt],
        "user_complaint": prompt,
        "dtc_codes": selected_dtcs,
        "sensor_data": sensor_snapshot,
        # Initialize empty fields
        "root_causes": [],
        "repair_plan": {},
        "next_step": ""
    }

    # 3. Run the Agent Graph
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # We use a status container to show the "Thinking" process
        with st.status("🤖 AI Agents working...", expanded=True) as status:
            app = st.session_state.app
            
            try:
                # Stream events from LangGraph
                for event in app.stream(initial_state):
                    for key, value in event.items():
                        
                        # Service Advisor Log
                        if key == "advisor":
                            if value.get("next_step") == "ask_user":
                                status.write("❌ Advisor: Need more info.")
                                full_response = value["messages"][0]
                            else:
                                status.write("✅ Advisor: Data complete. Handing off to Diagnostics...")
                        
                        # Diagnostic Log
                        elif key == "diagnostic":
                            causes = value.get("root_causes", [])
                            if causes:
                                top_cause = causes[0].get('root_cause', 'Unknown')
                                status.write(f"🔧 Diagnostician: Identified root cause -> **{top_cause}**")
                        
                        # Repair Log
                        elif key == "repair":
                            status.write("🛠️ Technician: Drafting repair plan...")
                            full_response = value["messages"][0]

                status.update(label="Response Ready!", state="complete", expanded=False)
                
                # Show Final Output
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
            