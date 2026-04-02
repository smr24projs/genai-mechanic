# """
# Enhanced Vehicle Diagnostic Platform - v2.0
# Streamlit application with advanced error handling, data persistence, and UI/UX improvements
# """
# import streamlit as st
# import time
# import os
# import sys
# import json
# import base64
# import re
# from datetime import datetime
# from io import BytesIO
# from pathlib import Path
# from PIL import Image
# import io
# from dotenv import load_dotenv
# import pandas as pd

# from langchain_core.messages import HumanMessage
# from langchain_google_genai import ChatGoogleGenerativeAI
# from pydantic import BaseModel, Field
# from langchain_core.output_parsers import PydanticOutputParser

# # --- ENHANCED CONFIG & IMPORTS ---
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# load_dotenv()

# # Import utility modules
# try:
#     from src.utils import (
#         CONFIG, setup_logging, get_logger, perf_logger, retry_with_backoff,
#         handle_streamlit_error, validate_sensor_value, validate_all_sensors,
#         validate_dtc_code, validate_vehicle_model, extract_json_from_response,
#         InputValidator, VisionExtractionError, AgentExecutionError, DataValidationError,
#         diagnostic_history,
#     )
#     from src.agents.advisor import langgraph_app, parser
#     logger = setup_logging()
#     logger.info("Enhanced application started")
# except ImportError as e:
#     st.error(f"Critical Import Error: {e}")
#     logger = None

# # ==========================================
# # ENHANCED: UI CONFIG & ENTERPRISE THEME
# # ==========================================
# st.set_page_config(
#     page_title="Tata Technologies | Smart Diagnostics",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Professional CSS with Aggressive Light Mode Overrides
# st.markdown("""
#     <style>
#     /* Force Light White-Blue Theme across the app */
#     .stApp { background-color: #FFFFFF !important; }
#     [data-testid="stAppViewContainer"] { background: #FFFFFF !important; }
#     [data-testid="stSidebar"] { background-color: #F8FCFF !important; border-right: 1px solid #E2E8F0 !important; }
    
#     /* Global Text Overrides */
#     h1, h2, h3, h4, h5, h6, label { color: #001F5B !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; }
#     p, span, li { color: #1F2937 !important; }

#     /* AGGRESSIVE INPUT BOX OVERRIDES */
#     div[data-baseweb="input"] > div, 
#     div[data-baseweb="textarea"], 
#     div[data-baseweb="select"] > div {
#         background-color: #FFFFFF !important;
#         border: 1px solid #A5C8ED !important;
#         border-radius: 6px !important;
#     }
    
#     input[type="text"], input[type="number"], textarea, select, div[data-baseweb="select"] span {
#         color: #001F5B !important;
#         -webkit-text-fill-color: #001F5B !important;
#         background-color: transparent !important;
#         font-weight: 600 !important;
#     }
    
#     ::placeholder, ::-webkit-input-placeholder {
#         color: #9CA3AF !important;
#         -webkit-text-fill-color: #9CA3AF !important;
#         font-weight: 400 !important;
#         opacity: 1 !important;
#     }
    
#     [data-testid="stChatInput"] {
#         background-color: #F8FCFF !important;
#         border: 1px solid #A5C8ED !important;
#         border-radius: 12px !important;
#         padding: 6px 15px !important;
#         box-shadow: 0 4px 12px rgba(0, 82, 204, 0.05) !important;
#     }
#     [data-testid="stChatInput"] textarea {
#         background-color: transparent !important;
#         color: #001F5B !important;
#         font-weight: 500 !important;
#     }
    
#     [data-testid="stFileUploader"] {
#         background-color: #F0F7FF !important;
#         border: 1px dashed #0052CC !important;
#         border-radius: 8px !important;
#         padding: 10px !important;
#     }
#     [data-testid="stFileUploader"] section { color: #001F5B !important; }
    
#     /* Fix Expanders */
#     [data-testid="stExpander"] details {
#         border: 1px solid #A5C8ED !important;
#         border-radius: 8px !important;
#         background-color: #FFFFFF !important;
#     }
#     [data-testid="stExpander"] summary {
#         background-color: #F0F7FF !important;
#         color: #001F5B !important;
#         font-weight: 700 !important;
#     }
#     [data-testid="stExpander"] summary:hover { background-color: #E6F2FF !important; }
#     [data-testid="stExpander"] svg { color: #001F5B !important; }

#     /* Clean Enterprise Header */
#     .custom-header {
#         background: linear-gradient(135deg, #FFFFFF 0%, #F0F7FF 100%);
#         padding: 35px 45px;
#         border-radius: 12px;
#         border: 2px solid #0052CC;
#         box-shadow: 0 4px 15px rgba(0, 31, 91, 0.05);
#         margin-bottom: 30px;
#         display: flex;
#         justify-content: space-between;
#         align-items: center;
#         position: relative;
#     }
#     .custom-header::before {
#         content: '';
#         position: absolute;
#         top: 0; left: 0; right: 0; bottom: 0;
#         background-image: url('https://upload.wikimedia.org/wikipedia/commons/8/8e/Tata_logo.svg');
#         background-repeat: no-repeat;
#         background-position: right -30px center;
#         background-size: 350px;
#         opacity: 0.06; 
#         z-index: 1;
#         pointer-events: none;
#     }
#     .header-main-title { margin: 0; color: #001F5B !important; font-size: 2.6rem !important; font-weight: 900; letter-spacing: -0.5px; position: relative; z-index: 2;}
#     .header-subtitle { margin: 8px 0 0 0; color: #0052CC !important; font-size: 1.1rem !important; font-weight: 700; position: relative; z-index: 2;}
    
#     /* Metrics inside Header */
#     .top-metrics-container {
#         display: flex; gap: 20px;
#         background: #FFFFFF;
#         padding: 15px 25px; border-radius: 10px;
#         border: 1px solid #A5C8ED;
#         box-shadow: 0 2px 8px rgba(0, 82, 204, 0.05);
#         position: relative; z-index: 2;
#     }
#     .top-metric-item { text-align: center; min-width: 90px; }
#     .top-metric-label { color: #64748B !important; font-size: 0.75rem; text-transform: uppercase; font-weight: 800; letter-spacing: 1px; }
#     .top-metric-value { color: #001F5B !important; font-size: 1.8rem; font-weight: 900; line-height: 1.2; }
#     .top-metric-unit { font-size: 0.8rem; color: #0052CC !important; font-weight: 800; }

#     /* General UI Elements */
#     .step-container {
#         background-color: #FFFFFF; padding: 16px; border-left: 5px solid #0052CC;
#         margin-bottom: 12px; border-radius: 0 8px 8px 0; border: 1px solid #E2E8F0;
#         color: #1F2937 !important; box-shadow: 0 2px 5px rgba(0,0,0,0.02);
#     }
#     .step-number { font-weight: 900; color: #0052CC !important; margin-right: 10px; }
    
#     .confidence-card {
#         padding: 15px; border-radius: 10px; border: 1px solid #A5C8ED;
#         background: #FFFFFF; text-align: center; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
#     }
#     .card-label { font-weight: 800; font-size: 0.75rem; color: #64748B !important; text-transform: uppercase; display: block; margin-bottom: 4px; }
#     .card-score { color: #10B981 !important; font-weight: 900; font-size: 1.6rem; line-height: 1; }
    
#     /* BUTTON VISIBILITY FIX */
#     div[data-testid="stButton"] button {
#         border-radius: 8px !important; 
#         font-weight: 700 !important; 
#         width: 100% !important; 
#         border: 1px solid #001F5B !important;
#         background-color: #001F5B !important; 
#         transition: all 0.2s ease !important;
#     }
#     div[data-testid="stButton"] button p {
#         color: #FFFFFF !important;
#         font-weight: 700 !important;
#     }
#     div[data-testid="stButton"] button:hover { 
#         background-color: #0052CC !important; 
#         border-color: #0052CC !important;
#         transform: translateY(-1px); 
#         box-shadow: 0 4px 10px rgba(0, 82, 204, 0.3); 
#     }
#     div[data-testid="stButton"] button:hover p { color: #FFFFFF !important; }
#     </style>
#     """, unsafe_allow_html=True)

# # ==========================================
# # ENHANCED: SESSION STATE INITIALIZATION
# # ==========================================
# if 'messages' not in st.session_state: st.session_state.messages = []
# if 'processed_images' not in st.session_state: st.session_state.processed_images = set()
# if 'session_id' not in st.session_state: st.session_state.session_id = str(datetime.now().timestamp())
# if 'vision_calls' not in st.session_state: st.session_state.vision_calls = 0
# if 'agent_latency_ms' not in st.session_state: st.session_state.agent_latency_ms = 0

# defaults = {
#     'rpm_val': 0, 'speed_val': 0, 'load_val': 0, 'temp_val': 0, 
#     'dtc_val': "", 'car_model_val': "", 'symptom_val': "", 'condition_val': ""
# }
# for key, val in defaults.items():
#     if key not in st.session_state: st.session_state[key] = val

# # Initialize LLM
# llm_flash = ChatGoogleGenerativeAI(model=CONFIG.model_name, temperature=CONFIG.temperature)

# # ==========================================
# # ENHANCED: UTILITY FUNCTIONS
# # ==========================================
# def clean_industry_text(text):
#     return re.sub(r'^[\d\.\s\-*]+', '', text).strip()

# def safe_int_extract(val):
#     if val is None: return 0
#     nums = re.findall(r'-?\d+', str(val))
#     return int(nums[0]) if nums else 0

# def extract_and_validate_vision_data(v_data: dict) -> dict:
#     try:
#         validated_data = {
#             'rpm': validate_sensor_value('rpm', v_data.get('rpm', 0)),
#             'speed': validate_sensor_value('speed', v_data.get('speed', 0)),
#             'load': validate_sensor_value('load', v_data.get('load', 0)),
#             'temp': validate_sensor_value('temp', v_data.get('temp', 0)),
#             'dtc': str(v_data.get('dtc') or ""),
#         }
#         if logger: logger.info(f"Vision data validated: {validated_data}")
#         return validated_data
#     except DataValidationError as e:
#         logger.warning(f"Validation error, using defaults: {str(e)}")
#         return {'rpm': 0, 'speed': 0, 'load': 0, 'temp': 0, 'dtc': ""}
#     except Exception as e:
#         raise VisionExtractionError(f"Data extraction failed: {str(e)}")

# @retry_with_backoff(max_attempts=3, exceptions=(Exception,))
# def call_vision_api(encoded_image: str):
#     st.session_state.vision_calls += 1
#     vision_prompt = """You MUST extract automotive sensor data from the image and return ONLY valid JSON.
#     Extract exactly these values:
#     - rpm: Engine RPM (integer, 0-8000)
#     - speed: Vehicle speed (integer, km/h, 0-300)
#     - load: Engine load (integer, 0-100%)
#     - temp: Coolant temperature (integer, Celsius, -40 to 130)
#     - dtc: Diagnostic code (string like P0100 or null)
    
#     CONVERSION RULES:
#     - mph to km/h: multiply by 1.609
#     - Fahrenheit to Celsius: (F-32) × 5/9
#     - Return null for missing values
#     - Numbers ONLY, no units
    
#     RESPOND WITH ONLY THIS JSON FORMAT:
#     {"rpm": number, "speed": number, "load": number, "temp": number, "dtc": null or string}"""
    
#     return llm_flash.invoke([HumanMessage(content=[
#         {"type": "text", "text": vision_prompt},
#         {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
#     ])])

# def generate_diagnostic_report_pdf(diagnosis_data: dict) -> bytes:
#     try:
#         from reportlab.lib.pagesizes import letter
#         from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
#         from reportlab.lib.styles import getSampleStyleSheet
#         from reportlab.lib import colors

#         buffer = BytesIO()
#         doc = SimpleDocTemplate(buffer, pagesize=letter)
#         elements = []
#         styles = getSampleStyleSheet()

#         elements.append(Paragraph(f"<b>Vehicle Diagnostic Report</b>", styles['Heading1']))
#         elements.append(Spacer(1, 12))

#         vehicle_model = diagnosis_data.get('vehicle_model', 'N/A')
#         dtc_codes = diagnosis_data.get('dtc_codes', 'N/A')
#         timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#         info_table = Table([
#             ['Vehicle Model:', vehicle_model],
#             ['DTC Codes:', dtc_codes],
#             ['Report Date:', timestamp],
#             ['Confidence:', f"{str(diagnosis_data.get('confidence_level', '0')).strip('%')}%"],
#         ])
#         info_table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
#             ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#             ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#             ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
#             ('FONTSIZE', (0, 0), (-1, -1), 10),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
#             ('GRID', (0, 0), (-1, -1), 1, colors.black)
#         ]))
#         elements.append(info_table)
#         elements.append(Spacer(1, 12))

#         elements.append(Paragraph("<b>Final Diagnosis:</b>", styles['Heading2']))
#         elements.append(Paragraph(diagnosis_data.get('diagnosis', 'N/A'), styles['Normal']))
#         elements.append(Spacer(1, 12))

#         elements.append(Paragraph("<b>Recommended Actions:</b>", styles['Heading2']))
#         for i, action in enumerate(diagnosis_data.get('action_plan', []), 1):
#             elements.append(Paragraph(f"{i}. {action}", styles['Normal']))
#         elements.append(Spacer(1, 12))

#         if diagnosis_data.get('safety_warning') and diagnosis_data['safety_warning'].lower() != 'none':
#             elements.append(Paragraph(f"<b>Safety Warning:</b>", styles['Heading3']))
#             elements.append(Paragraph(diagnosis_data['safety_warning'], styles['Normal']))

#         doc.build(elements)
#         return buffer.getvalue()
#     except Exception as e:
#         if logger: logger.error(f"Failed to generate PDF: {str(e)}")
#         st.warning("Could not generate PDF report")
#         return None

# # ==========================================
# # ENHANCED: SIDEBAR DATA INGESTION
# # ==========================================
# with st.sidebar:
#     st.subheader("Engineering Console", divider="blue")
    
#     with st.expander("Session Stats"):
#         col1, col2 = st.columns(2)
#         with col1:
#             st.metric("Vision Calls", st.session_state.vision_calls)
#             st.metric("Messages", len(st.session_state.messages))
#         with col2:
#             st.metric("Latency (ms)", int(st.session_state.agent_latency_ms))
#             st.metric("Session ID", str(st.session_state.session_id)[:8])

#     with st.expander("Automated Data Intake", expanded=True):
#         st.markdown("**Upload a diagnostic scanner image:**")
#         uploaded_image = st.file_uploader("Upload Scanner / Dashboard Image", type=["jpg", "png", "webp", "jpeg"])
        
#         if uploaded_image:
#             image_id = f"{uploaded_image.name}_{uploaded_image.size}"
#             if image_id not in st.session_state.processed_images:
#                 with st.spinner("Extracting Telemetry..."):
#                     try:
#                         if uploaded_image.size == 0:
#                             st.error("Image file is empty")
#                         else:
#                             try:
#                                 img = Image.open(uploaded_image).convert("RGB")
#                             except Exception as ie:
#                                 raise VisionExtractionError(f"Cannot read image: {str(ie)[:50]}")
                            
#                             if img.size[0] < 100 or img.size[1] < 100:
#                                 st.warning(f"Image resolution low ({img.size[0]}x{img.size[1]}). May be unclear.")

#                             buffered = io.BytesIO()
#                             img.save(buffered, format="JPEG", quality=95)
#                             buffered.seek(0)
#                             img_bytes = buffered.getvalue()
                            
#                             if not img_bytes:
#                                 raise VisionExtractionError("Image encoding failed")
                                
#                             encoded = base64.b64encode(img_bytes).decode('utf-8')
                            
#                             start_time = time.time()
#                             v_res = call_vision_api(encoded)
#                             duration_ms = (time.time() - start_time) * 1000
                            
#                             if not v_res or not v_res.content:
#                                 raise VisionExtractionError("API returned no response")
                            
#                             clean_json = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', v_res.content, re.DOTALL)
#                             if clean_json:
#                                 try:
#                                     v_data = json.loads(clean_json.group())
#                                     validated = extract_and_validate_vision_data(v_data)
                                    
#                                     st.session_state.rpm_val = validated['rpm']
#                                     st.session_state.speed_val = validated['speed']
#                                     st.session_state.load_val = validated['load']
#                                     st.session_state.temp_val = validated['temp']
#                                     st.session_state.dtc_val = validated['dtc']
#                                     st.session_state.processed_images.add(image_id)
                                    
#                                     if logger: 
#                                         perf_logger.log_execution_time("Vision_Extraction", duration_ms)
#                                     st.success(f"Extraction Complete ({duration_ms:.0f}ms)")
#                                     st.rerun()
#                                 except json.JSONDecodeError as je:
#                                     raise VisionExtractionError(f"Bad JSON: {str(je)[:80]}")
#                             else:
#                                 raise VisionExtractionError("No JSON detected.")
#                     except VisionExtractionError as e:
#                         st.error(f"Vision Error: {str(e)}")
#                     except Exception as e:
#                         st.error(f"Image Error: {str(e)[:150]}")

#     with st.expander("Image Not Recognized?", expanded=False):
#         st.markdown("""
#         **What makes a good diagnostic image?**
#         - Clear OBD-II scanner display or dashboard
#         - Shows RPM, Speed, Load, Temp, and DTC values
#         """)

#     with st.container(border=True):
#         st.markdown("**Manual Context**")
#         st.session_state.car_model_val = st.text_input(
#             "Vehicle Model", value=st.session_state.car_model_val, placeholder="e.g., Tata Safari"
#         )
#         st.session_state.dtc_val = st.text_input("Active Fault Codes (DTC)", value=st.session_state.dtc_val)
#         st.session_state.symptom_val = st.text_area("Symptom Description", value=st.session_state.symptom_val, height=60)
#         st.session_state.condition_val = st.text_input("Operating Condition", value=st.session_state.condition_val)

#     with st.expander("Live Sensor Data", expanded=True):
#         col_s1, col_s2 = st.columns(2)
#         with col_s1:
#             st.session_state.rpm_val = st.number_input("Engine RPM", value=int(st.session_state.rpm_val), min_value=0, max_value=8000)
#             st.session_state.load_val = st.number_input("Load %", value=int(st.session_state.load_val), min_value=0, max_value=100)
#         with col_s2:
#             st.session_state.speed_val = st.number_input("Speed km/h", value=int(st.session_state.speed_val), min_value=0, max_value=300)
#             st.session_state.temp_val = st.number_input("Temp °C", value=int(st.session_state.temp_val), min_value=-40, max_value=130)

#     if st.button("Reset Session", use_container_width=True):
#         for key, val in defaults.items(): st.session_state[key] = val
#         st.session_state.messages = []
#         st.session_state.processed_images = set()
#         st.session_state.vision_calls = 0
#         st.rerun()

# # ==========================================
# # ENHANCED: MAIN DASHBOARD
# # ==========================================
# st.markdown(f"""
#     <div class="custom-header">
#         <div class="header-title-container">
#             <h1 class="header-main-title">Smart Vehicle Diagnostic</h1>
#         </div>
#         <div class="top-metrics-container">
#             <div class="top-metric-item">
#                 <div class="top-metric-label">RPM</div>
#                 <div class="top-metric-value">{st.session_state.rpm_val}</div>
#             </div>
#             <div class="top-metric-item">
#                 <div class="top-metric-label">Speed</div>
#                 <div class="top-metric-value">{st.session_state.speed_val} <span class="top-metric-unit">km/h</span></div>
#             </div>
#             <div class="top-metric-item">
#                 <div class="top-metric-label">Load</div>
#                 <div class="top-metric-value">{st.session_state.load_val} <span class="top-metric-unit">%</span></div>
#             </div>
#             <div class="top-metric-item">
#                 <div class="top-metric-label">Temp</div>
#                 <div class="top-metric-value">{st.session_state.temp_val} <span class="top-metric-unit">°C</span></div>
#             </div>
#         </div>
#     </div>
# """, unsafe_allow_html=True)

# # ==========================================
# # ENHANCED: CHAT INTERFACE WITH HISTORY
# # ==========================================
# USER_AVATAR = None 
# AI_AVATAR = None

# for idx, msg in enumerate(st.session_state.messages):
#     with st.chat_message(msg["role"], avatar=USER_AVATAR if msg["role"] == "user" else AI_AVATAR):
#         if msg["type"] == "text":
#             st.markdown(msg["content"])
        
#         elif msg["type"] == "conversational_diagnostic":
#             d = msg["data"]
#             st.markdown(d["diagnosis"])
#             if d.get("action_plan"):
#                 st.markdown("**Details & Steps:**")
#                 for step in d["action_plan"]:
#                     st.markdown(f"- {clean_industry_text(step)}")
                    
#         elif msg["type"] == "structured":
#             d = msg["data"]
#             st.subheader(f"{d['main_heading']}", divider="blue")
            
#             safe_conf = str(d.get('confidence_level', '90')).replace('%', '').strip()
            
#             c1, c2, c3 = st.columns(3)
#             with c1: st.markdown(f"<div class='confidence-card'><span class='card-label'>RAG Knowledge</span><span class='card-score'>{d.get('rag_score', 92)}%</span></div>", unsafe_allow_html=True)
#             with c2: st.markdown(f"<div class='confidence-card'><span class='card-label'>ML Predictive</span><span class='card-score'>{d.get('ml_score', 88)}%</span></div>", unsafe_allow_html=True)
#             with c3: st.markdown(f"<div class='confidence-card'><span class='card-label'>Overall</span><span class='card-score'>{safe_conf}%</span></div>", unsafe_allow_html=True)
            
#             st.markdown(f"**Final Verdict:** {d['diagnosis']}")
#             with st.expander("View Technical Evidence"):
#                 st.write("**Manual Database (RAG):**", d["rag_evidence"])
#                 st.write("**Live Web Reports:**", d["web_evidence"])
            
#             st.subheader(f"{d['steps_heading']}")
#             for i, step in enumerate(d["action_plan"], 1):
#                 clean_step = clean_industry_text(step)
#                 st.markdown(f"""<div class='step-container'><span class='step-number'>Step {i}:</span>{clean_step}</div>""", unsafe_allow_html=True)
            
#             if d.get("safety_warning") and d["safety_warning"].lower() != "none":
#                 st.error(f"Safety Alert: {d['safety_warning']}")
            
#             col1, col2, col3 = st.columns([1, 1, 1])
#             with col1:
#                 if st.button("Mark as Helpful", key=f"helpful_{idx}"):
#                     diagnostic_history.update_resolution(d.get('id', str(idx)), "User marked as helpful", feedback_score=5)
#                     st.success("Thank you for the feedback.")
#             with col2:
#                 if st.button("Download PDF", key=f"download_{idx}"):
#                     pdf_bytes = generate_diagnostic_report_pdf(d)
#                     if pdf_bytes:
#                         st.download_button(label="Click to Download", data=pdf_bytes, file_name=f"diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", mime="application/pdf")
#             with col3:
#                 if st.button("Save to History", key=f"save_{idx}"):
#                     d['id'] = str(idx)
#                     d['sensor_readings'] = { 'rpm': st.session_state.rpm_val, 'speed': st.session_state.speed_val, 'load': st.session_state.load_val, 'temp': st.session_state.temp_val }
#                     diagnostic_history.save_diagnosis(d)
#                     st.success("Saved to history.")

# if user_text := st.chat_input("Enter diagnostic query or request procedure..."):
#     with st.chat_message("user"):
#         st.markdown(user_text)
    
#     with st.spinner("Synthesizing Diagnostic Insights..."):
#         try:
#             class Triage(BaseModel):
#                 is_diagnostic: bool = Field(description="True ONLY if user reports a NEW vehicle issue.")
#                 is_follow_up: bool = Field(description="True if user asks a follow-up question.")
#                 is_sufficient: bool = Field(description="True ONLY if enough specific technical info is provided.")
#                 response: str = Field(description="If is_diagnostic is False, OR if is_sufficient is False, put your conversational answer or clarifying question here.")
#                 missing: list = Field(default=[], description="List of specific missing data points.")
#                 ui_main_heading: str = Field(default="", description="Main heading for UI display (optional)")
#                 ui_steps_heading: str = Field(default="", description="Steps heading for UI display (optional)")
                
#             t_parser = PydanticOutputParser(pydantic_object=Triage)
            
#             history_context = "No previous diagnosis."
#             if st.session_state.messages:
#                 last_msg = st.session_state.messages[-1]
#                 if last_msg["role"] == "assistant" and last_msg["type"] == "structured":
#                     history_context = f"Previous Diagnosis: {last_msg['data'].get('diagnosis')}\nSteps: {last_msg['data'].get('action_plan')}"
            
#             t_prompt = (
#                 f"Context from previous turn:\n{history_context}\n\n"
#                 f"User Input: '{user_text}' | Vehicle: {st.session_state.car_model_val} | DTC: {st.session_state.dtc_val} | "
#                 f"Sensors: RPM={st.session_state.rpm_val}, Speed={st.session_state.speed_val}, Load={st.session_state.load_val}%, Temp={st.session_state.temp_val}C\n"
#                 "CRITICAL RULES:\n"
#                 "1. If user describes a NEW issue, set is_diagnostic=True and is_follow_up=False.\n"
#                 "2. If user asks a FOLLOW-UP question, set is_diagnostic=False, is_follow_up=True, and write the answer in 'response'.\n"
#                 "3. If general chat, set is_diagnostic=False and reply in 'response'.\n"
#                 "4. If is_diagnostic=True BUT the input is vague and lacks technical details, set is_sufficient=False. In 'response', act as a helpful mechanic and ask a specific CLARIFYING QUESTION.\n"
#                 f"{t_parser.get_format_instructions()}"
#             )
            
#             t_res = llm_flash.invoke(t_prompt)
#             intent = t_parser.parse(t_res.content.replace('```json','').replace('```','').strip())

#             if not intent.is_diagnostic or not intent.is_sufficient:
#                 st.session_state.messages.append({"role": "user", "content": user_text, "type": "text"})
#                 st.session_state.messages.append({"role": "assistant", "content": intent.response, "type": "text"})
#                 st.rerun()

#             full_input = (
#                 f"Vehicle: {st.session_state.car_model_val} | DTC: {st.session_state.dtc_val} | "
#                 f"Symptom: {st.session_state.symptom_val} | Condition: {st.session_state.condition_val} | "
#                 f"Sensors: RPM={st.session_state.rpm_val}, Speed={st.session_state.speed_val}, "
#                 f"Load={st.session_state.load_val}%, Temp={st.session_state.temp_val}C | User: {user_text}"
#             )
            
#             flow_container = st.empty()
#             current_path = "Live Path: START"
#             flow_container.markdown(current_path)
            
#             # ---------------------------------------------------------
#             # TERMINAL SHOWCASE: WORKFLOW START
#             # ---------------------------------------------------------
#             print(f"\n{'='*70}")
#             print(f"🚀 INITIATING TATA TECHNOLOGIES AGENTIC WORKFLOW")
#             print(f"   Session ID: {st.session_state.session_id}")
#             print(f"   Input: {user_text[:50]}...")
#             print(f"{'='*70}")
            
#             # Initialize raw_output before try block to prevent NameError in except block
#             raw_output = ""
#             start_time = time.time()
#             final_state = None
            
#             for output in langgraph_app.stream({"messages": [HumanMessage(content=full_input)]}):
#                 for node_name, state_update in output.items():
#                     # Update UI
#                     current_path += f" ➔ `{node_name.upper()}`"
#                     flow_container.markdown(current_path)
                    
#                     # Update Terminal
#                     t_stamp = datetime.now().strftime("%H:%M:%S")
#                     print(f"[{t_stamp}] ⚙️  NODE EXECUTED: {node_name.upper()}")
                    
#                     final_state = state_update
            
#             duration_ms = (time.time() - start_time) * 1000
#             st.session_state.agent_latency_ms = duration_ms
            
#             if final_state and "messages" in final_state:
#                 raw_content = final_state["messages"][-1].content
#                 if isinstance(raw_content, list):
#                     raw_output = "".join([item.get("text", str(item)) if isinstance(item, dict) else str(item) for item in raw_content])
#                 else:
#                     raw_output = str(raw_content)
#             else:
#                 raise AgentExecutionError("Agent flow failed to return messages.")
            
#             validated = parser.parse(raw_output.replace("```json", "").replace("```", "").strip())
            
#             # ---------------------------------------------------------
#             # TERMINAL SHOWCASE: DIAGNOSTIC RESULTS
#             # ---------------------------------------------------------
#             safe_conf_term = str(validated.confidence_level).replace('%', '').strip()
#             print(f"\n{'-'*70}")
#             print(f"✅ WORKFLOW COMPLETE ({duration_ms:.0f}ms)")
#             print(f"   Confidence Score : {safe_conf_term}%")
#             print(f"{'-'*70}")
#             print(f"DIAGNOSIS:\n{validated.diagnosis}\n")
#             print(f"ACTION PLAN:")
#             for i, step in enumerate(validated.action_plan, 1):
#                 print(f"  {i}. {clean_industry_text(step)}")
#             print(f"{'='*70}\n")
            
#             structured_data = {
#                 "id": str(datetime.now().timestamp()),
#                 "main_heading": intent.ui_main_heading or "Diagnostic Analysis Results",
#                 "diagnosis": validated.diagnosis,
#                 "rag_evidence": validated.rag_evidence,
#                 "web_evidence": validated.web_evidence,
#                 "steps_heading": intent.ui_steps_heading or "Action Plan",
#                 "action_plan": validated.action_plan,
#                 "safety_warning": validated.safety_warning,
#                 "confidence_level": validated.confidence_level,
#                 "vehicle_model": st.session_state.car_model_val,
#                 "dtc_codes": st.session_state.dtc_val,
#                 "symptoms": st.session_state.symptom_val,
#             }
            
#             diagnostic_history.save_diagnosis(structured_data)
#             diagnostic_history.log_analytics_event({
#                 'session_id': st.session_state.session_id, 'vehicle_model': st.session_state.car_model_val,
#                 'dtc_count': 1 if st.session_state.dtc_val else 0, 'vision_calls': st.session_state.vision_calls,
#                 'agent_latency_ms': duration_ms,
#             })
            
#             if logger: 
#                 perf_logger.log_execution_time("Agent_Execution", duration_ms)
            
#             st.session_state.messages.append({"role": "user", "content": user_text, "type": "text"})
            
#             if intent.is_follow_up:
#                 st.session_state.messages.append({"role": "assistant", "type": "conversational_diagnostic", "data": structured_data})
#             else:
#                 st.session_state.messages.append({"role": "assistant", "type": "structured", "data": structured_data})
                
#             st.rerun()
            
#         except AgentExecutionError as e:
#             st.error(handle_streamlit_error(e, "Agent Error"))
#         except DataValidationError as e:
#             st.error(handle_streamlit_error(e, "Validation Error"))
#         except Exception as e:
#             st.session_state.messages.append({"role": "user", "content": user_text, "type": "text"})
#             st.session_state.messages.append({"role": "assistant", "content": raw_output, "type": "text"})
#             st.rerun()

# # ==========================================
# # FOOTER: STATISTICS
# # ==========================================
# with st.expander("Platform Statistics"):
#     stats = diagnostic_history.get_statistics()
#     col1, col2, col3 = st.columns(3)
#     with col1: st.metric("Total Diagnostics", stats.get('total_diagnostics', 0))
#     with col2: st.metric("Avg Confidence", f"{stats.get('avg_confidence', 0):.1f}%")
#     with col3: st.metric("Avg User Rating", stats.get('avg_feedback', 'N/A'))

# st.markdown("---")
# st.markdown("<div style='text-align: center; color: #001F5B; font-weight: 900; font-size: 14px;'>Powered by Tata Technologies | Smart Vehicle Diagnostic Platform</div>", unsafe_allow_html=True)


"""
Enhanced Vehicle Diagnostic Platform - v2.0
Streamlit application with advanced error handling, data persistence, and UI/UX improvements
"""
import streamlit as st
import time
import os
import sys
import json
import base64
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path
from PIL import Image
import io
from dotenv import load_dotenv
import pandas as pd

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

# --- ENHANCED CONFIG & IMPORTS ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

# Import utility modules
try:
    from src.utils import (
        CONFIG, setup_logging, get_logger, perf_logger, retry_with_backoff,
        handle_streamlit_error, validate_sensor_value, validate_all_sensors,
        validate_dtc_code, validate_vehicle_model, extract_json_from_response,
        InputValidator, VisionExtractionError, AgentExecutionError, DataValidationError,
        diagnostic_history,
    )
    from src.agents.advisor import langgraph_app, parser, DiagnosticResponse
    logger = setup_logging()
    logger.info("Enhanced application started")
except ImportError as e:
    st.error(f"Critical Import Error: {e}")
    logger = None

# ==========================================
# ENHANCED: UI CONFIG & ENTERPRISE THEME
# ==========================================
st.set_page_config(
    page_title="Tata Technologies | Smart Diagnostics",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Force Light White-Blue Theme across the app */
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stAppViewContainer"] { background: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #F8FCFF !important; border-right: 1px solid #E2E8F0 !important; }
    
    /* Global Text Overrides */
    h1, h2, h3, h4, h5, h6, label { color: #001F5B !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; }
    p, span, li { color: #1F2937 !important; }

    /* AGGRESSIVE INPUT BOX OVERRIDES */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="textarea"], 
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #A5C8ED !important;
        border-radius: 6px !important;
    }
    
    input[type="text"], input[type="number"], textarea, select, div[data-baseweb="select"] span {
        color: #001F5B !important;
        -webkit-text-fill-color: #001F5B !important;
        background-color: transparent !important;
        font-weight: 600 !important;
    }
    
    ::placeholder, ::-webkit-input-placeholder {
        color: #9CA3AF !important;
        -webkit-text-fill-color: #9CA3AF !important;
        font-weight: 400 !important;
        opacity: 1 !important;
    }
    
    [data-testid="stChatInput"] {
        background-color: #F8FCFF !important;
        border: 1px solid #A5C8ED !important;
        border-radius: 12px !important;
        padding: 6px 15px !important;
        box-shadow: 0 4px 12px rgba(0, 82, 204, 0.05) !important;
    }
    [data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #001F5B !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stFileUploader"] {
        background-color: #F0F7FF !important;
        border: 1px dashed #0052CC !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    [data-testid="stFileUploader"] section { color: #001F5B !important; }
    
    /* Fix Expanders */
    [data-testid="stExpander"] details {
        border: 1px solid #A5C8ED !important;
        border-radius: 8px !important;
        background-color: #FFFFFF !important;
    }
    [data-testid="stExpander"] summary {
        background-color: #F0F7FF !important;
        color: #001F5B !important;
        font-weight: 700 !important;
    }
    [data-testid="stExpander"] summary:hover { background-color: #E6F2FF !important; }
    [data-testid="stExpander"] svg { color: #001F5B !important; }

    /* Clean Enterprise Header */
    .custom-header {
        background: linear-gradient(135deg, #FFFFFF 0%, #F0F7FF 100%);
        padding: 35px 45px;
        border-radius: 12px;
        border: 2px solid #0052CC;
        box-shadow: 0 4px 15px rgba(0, 31, 91, 0.05);
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
    }
    .custom-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/8/8e/Tata_logo.svg');
        background-repeat: no-repeat;
        background-position: right -30px center;
        background-size: 350px;
        opacity: 0.06; 
        z-index: 1;
        pointer-events: none;
    }
    .header-main-title { margin: 0; color: #001F5B !important; font-size: 2.6rem !important; font-weight: 900; letter-spacing: -0.5px; position: relative; z-index: 2;}
    .header-subtitle { margin: 8px 0 0 0; color: #0052CC !important; font-size: 1.1rem !important; font-weight: 700; position: relative; z-index: 2;}
    
    /* Metrics inside Header */
    .top-metrics-container {
        display: flex; gap: 20px;
        background: #FFFFFF;
        padding: 15px 25px; border-radius: 10px;
        border: 1px solid #A5C8ED;
        box-shadow: 0 2px 8px rgba(0, 82, 204, 0.05);
        position: relative; z-index: 2;
    }
    .top-metric-item { text-align: center; min-width: 90px; }
    .top-metric-label { color: #64748B !important; font-size: 0.75rem; text-transform: uppercase; font-weight: 800; letter-spacing: 1px; }
    .top-metric-value { color: #001F5B !important; font-size: 1.8rem; font-weight: 900; line-height: 1.2; }
    .top-metric-unit { font-size: 0.8rem; color: #0052CC !important; font-weight: 800; }

    /* General UI Elements */
    .step-container {
        background-color: #FFFFFF; padding: 16px; border-left: 5px solid #0052CC;
        margin-bottom: 12px; border-radius: 0 8px 8px 0; border: 1px solid #E2E8F0;
        color: #1F2937 !important; box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .step-number { font-weight: 900; color: #0052CC !important; margin-right: 10px; }
    
    .confidence-card {
        padding: 15px; border-radius: 10px; border: 1px solid #A5C8ED;
        background: #FFFFFF; text-align: center; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
    }
    .card-label { font-weight: 800; font-size: 0.75rem; color: #64748B !important; text-transform: uppercase; display: block; margin-bottom: 4px; }
    .card-score { color: #10B981 !important; font-weight: 900; font-size: 1.6rem; line-height: 1; }
    
    /* BUTTON VISIBILITY FIX */
    div[data-testid="stButton"] button {
        border-radius: 8px !important; 
        font-weight: 700 !important; 
        width: 100% !important; 
        border: 1px solid #001F5B !important;
        background-color: #001F5B !important; 
        transition: all 0.2s ease !important;
    }
    div[data-testid="stButton"] button p {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    div[data-testid="stButton"] button:hover { 
        background-color: #0052CC !important; 
        border-color: #0052CC !important;
        transform: translateY(-1px); 
        box-shadow: 0 4px 10px rgba(0, 82, 204, 0.3); 
    }
    div[data-testid="stButton"] button:hover p { color: #FFFFFF !important; }

    /* =============================================
       WORKFLOW TRACKER (Light Enterprise Theme)
       ============================================= */
    .workflow-tracker-wrap {
        background: linear-gradient(135deg, #F0F7FF 0%, #FFFFFF 100%);
        border: 1.5px solid #A5C8ED;
        border-radius: 12px;
        padding: 18px 22px;
        margin: 8px 0 16px 0;
        font-family: 'Segoe UI', sans-serif;
        box-shadow: 0 2px 12px rgba(0,31,91,0.06);
    }
    .workflow-tracker-wrap.wf-success {
        border-color: #10B981;
        background: linear-gradient(135deg, #ECFDF5 0%, #FFFFFF 100%);
    }
    .workflow-tracker-wrap.wf-error {
        border-color: #EF4444;
        background: linear-gradient(135deg, #FEF2F2 0%, #FFFFFF 100%);
    }
    .wf-header {
        display: flex; align-items: center; gap: 10px; margin-bottom: 18px;
    }
    .wf-header-icon { font-size: 1.1rem; }
    .wf-header-title {
        font-size: 0.85rem; font-weight: 800; text-transform: uppercase;
        letter-spacing: 0.8px; color: #001F5B !important; margin: 0;
    }
    .wf-header-title.wf-title-success { color: #059669 !important; }
    .wf-header-title.wf-title-error   { color: #DC2626 !important; }
    .wf-path {
        display: flex; align-items: center; flex-wrap: nowrap;
        overflow-x: auto; gap: 6px; padding-bottom: 4px;
    }
    .wf-node {
        display: flex; align-items: center; gap: 6px;
        padding: 7px 14px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 700; letter-spacing: 0.6px;
        text-transform: uppercase; white-space: nowrap;
        background: #EFF6FF; border: 1px solid #BFDBFE; color: #64748B !important;
        transition: all 0.3s ease;
    }
    .wf-node.wf-completed { color: #059669 !important; border-color: #6EE7B7; background: #ECFDF5; }
    .wf-node.wf-active { color: #2563EB !important; border-color: #3B82F6; background: #DBEAFE; box-shadow: 0 0 12px rgba(59,130,246,0.20); }
    .wf-connector { height: 2px; width: 18px; background: #CBD5E1; flex-shrink: 0; }
    .wf-spinner {
        width: 10px; height: 10px;
        border: 2px solid rgba(59,130,246,0.3); border-right-color: #3B82F6;
        border-radius: 50%; display: inline-block;
        animation: wfspin 0.9s linear infinite; margin-left: 4px; vertical-align: middle;
    }
    @keyframes wfspin { to { transform: rotate(360deg); } }
    .wf-decisions {
        margin-top: 14px; padding-top: 12px; border-top: 1px solid #E2E8F0;
    }
    .wf-decision-item {
        display: flex; align-items: flex-start; gap: 8px; padding: 5px 0;
        font-size: 0.73rem; color: #475569 !important;
        font-family: 'Segoe UI', monospace; line-height: 1.4;
    }
    .wf-decision-icon { flex-shrink: 0; font-size: 0.75rem; }
    .wf-decision-text { color: #334155 !important; }
    .wf-decision-text strong { color: #001F5B !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# ENHANCED: SESSION STATE INITIALIZATION
# ==========================================
if 'messages' not in st.session_state: st.session_state.messages = []
if 'processed_images' not in st.session_state: st.session_state.processed_images = set()
if 'session_id' not in st.session_state: st.session_state.session_id = str(datetime.now().timestamp())
if 'vision_calls' not in st.session_state: st.session_state.vision_calls = 0
if 'agent_latency_ms' not in st.session_state: st.session_state.agent_latency_ms = 0
if 'reset_count' not in st.session_state: st.session_state.reset_count = 0
if 'uploaded_image_data' not in st.session_state: st.session_state.uploaded_image_data = None

defaults = {
    'rpm_val': 0, 'speed_val': 0, 'load_val': 0, 'temp_val': 0, 
    'dtc_val': "", 'car_model_val': "", 'symptom_val': "", 'condition_val': ""
}
for key, val in defaults.items():
    if key not in st.session_state: st.session_state[key] = val

# Initialize LLM
llm_flash = ChatGoogleGenerativeAI(model=CONFIG.model_name, temperature=CONFIG.temperature)

# ==========================================
# ENHANCED: UTILITY FUNCTIONS
# ==========================================

# --- BUG FIX: BULLETPROOF TEXT CLEANER ---
def clean_industry_text(text):
    """Safely cleans text, even if the LLM hallucinates a dictionary/list instead of a string."""
    if isinstance(text, dict):
        text = text.get("step", text.get("action", text.get("description", text.get("text", str(text)))))
    elif isinstance(text, list):
        text = " ".join([str(x) for x in text])
    else:
        text = str(text)
    return re.sub(r'^[\d\.\s\-*]+', '', text).strip()

def safe_int_extract(val):
    if val is None: return 0
    nums = re.findall(r'-?\d+', str(val))
    return int(nums[0]) if nums else 0

def extract_and_validate_vision_data(v_data: dict) -> dict:
    try:
        validated_data = {
            'rpm': validate_sensor_value('rpm', v_data.get('rpm', 0)),
            'speed': validate_sensor_value('speed', v_data.get('speed', 0)),
            'load': validate_sensor_value('load', v_data.get('load', 0)),
            'temp': validate_sensor_value('temp', v_data.get('temp', 0)),
            'dtc': str(v_data.get('dtc') or ""),
        }
        if logger: logger.info(f"Vision data validated: {validated_data}")
        return validated_data
    except DataValidationError as e:
        logger.warning(f"Validation error, using defaults: {str(e)}")
        return {'rpm': 0, 'speed': 0, 'load': 0, 'temp': 0, 'dtc': ""}
    except Exception as e:
        raise VisionExtractionError(f"Data extraction failed: {str(e)}")

@retry_with_backoff(max_attempts=3, exceptions=(Exception,))
def call_vision_api(encoded_image: str):
    st.session_state.vision_calls += 1
    vision_prompt = """You MUST extract automotive sensor data from the image and return ONLY valid JSON.
    Extract exactly these values:
    - rpm: Engine RPM (integer, 0-8000)
    - speed: Vehicle speed (integer, km/h, 0-300)
    - load: Engine load (integer, 0-100%)
    - temp: Coolant temperature (integer, Celsius, -40 to 130)
    - dtc: Diagnostic code (string like P0100 or null)
    
    CONVERSION RULES:
    - mph to km/h: multiply by 1.609
    - Fahrenheit to Celsius: (F-32) × 5/9
    - Return null for missing values
    - Numbers ONLY, no units
    
    RESPOND WITH ONLY THIS JSON FORMAT:
    {"rpm": number, "speed": number, "load": number, "temp": number, "dtc": null or string}"""
    
    return llm_flash.invoke([HumanMessage(content=[
        {"type": "text", "text": vision_prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
    ])])

def generate_diagnostic_report_pdf(diagnosis_data: dict) -> bytes:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=40, bottomMargin=40, leftMargin=40, rightMargin=40)
        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle('ReportTitle', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor('#001F5B'), alignment=TA_CENTER, spaceAfter=20)
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#64748B'), alignment=TA_CENTER)
        h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#0F172A'), spaceBefore=15, spaceAfter=8)
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#334155'))

        elements.append(Paragraph("<b>SMART VEHICLE DIAGNOSTIC REPORT</b>", title_style))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
        elements.append(Spacer(1, 20))

        vehicle_model = str(diagnosis_data.get('vehicle_model', 'N/A')).strip() or 'N/A'
        dtc_codes = str(diagnosis_data.get('dtc_codes', 'N/A')).strip() or 'N/A'
        symptoms = str(diagnosis_data.get('symptoms', 'N/A')).strip() or 'N/A'
        conf_score = diagnosis_data.get('confidence_score', diagnosis_data.get('confidence_level', 'N/A'))
        rag_score = diagnosis_data.get('rag_score', 'N/A')
        ml_score = diagnosis_data.get('ml_score', 'N/A')

        info_rows = [
            ['Vehicle Model', vehicle_model],
            ['DTC Codes', dtc_codes],
            ['Symptoms', symptoms[:200] + '...' if len(symptoms) > 200 else symptoms],
            ['ML Predictive Score', f"{ml_score}%" if isinstance(ml_score, (int, float)) else str(ml_score)],
            ['RAG Knowledge Score', f"{rag_score}%" if isinstance(rag_score, (int, float)) else str(rag_score)],
            ['Overall Confidence', f"{conf_score}%" if isinstance(conf_score, (int, float)) else str(conf_score)],
        ]
        info_table = Table(info_rows, colWidths=[150, 370])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F7FF')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#001F5B')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#334155')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))

        elements.append(Paragraph("<b>Final Diagnosis</b>", h2_style))
        diagnosis_text = Paragraph(diagnosis_data.get('diagnosis', 'N/A'), body_style)
        diag_table = Table([[diagnosis_text]], colWidths=[520])
        diag_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ECFDF5')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#10B981')),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(diag_table)
        elements.append(Spacer(1, 15))

        elements.append(Paragraph("<b>Recommended Action Plan</b>", h2_style))
        for i, action in enumerate(diagnosis_data.get('action_plan', []), 1):
            if isinstance(action, dict):
                action_str = action.get("step", action.get("action", action.get("description", str(action))))
            else:
                action_str = str(action)
            step_text = Paragraph(f"<b>Step {i}:</b> {action_str}", body_style)
            step_table = Table([[step_text]], colWidths=[520])
            step_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ]))
            elements.append(KeepTogether([step_table, Spacer(1, 8)]))

        if diagnosis_data.get('decision_path'):
            elements.append(Paragraph("<b>Agent Execution Log</b>", h2_style))
            node_labels = {"START": "INITIALIZE", "reasoner": "REASONING", "tools": "TOOL EXEC", "logger": "PARSE DATA", "__end__": "COMPLETE", "END": "COMPLETE"}
            wf_history = diagnosis_data.get('wf_history', [])
            pipeline_table = None
            if wf_history:
                row_data = []
                clean_nodes = [n.replace('__START__', 'START').replace('__END__', 'END') for n in wf_history]
                if len(clean_nodes) > 5:
                    clean_nodes = clean_nodes[:2] + ["..."] + clean_nodes[-2:]
                node_font = ParagraphStyle('NodeF', fontSize=7, alignment=TA_CENTER, textColor=colors.HexColor('#059669'))
                arrow_font = ParagraphStyle('ArrowF', fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor('#CBD5E1'))
                for i_n, node in enumerate(clean_nodes):
                    label = node_labels.get(node, node.upper())
                    row_data.append(Paragraph(f"<b>{label}</b>", node_font))
                    if i_n < len(clean_nodes) - 1:
                        row_data.append(Paragraph("<b>--</b>", arrow_font))
                if row_data:
                    pipeline_table = Table([row_data], colWidths=None, hAlign='LEFT')
                    style_cmds = [('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]
                    for ci in range(len(row_data)):
                        if ci % 2 == 0:
                            style_cmds.extend([
                                ('BACKGROUND', (ci, 0), (ci, 0), colors.HexColor('#ECFDF5')),
                                ('BOX', (ci, 0), (ci, 0), 1, colors.HexColor('#6EE7B7')),
                                ('TOPPADDING', (ci, 0), (ci, 0), 6), ('BOTTOMPADDING', (ci, 0), (ci, 0), 6),
                                ('LEFTPADDING', (ci, 0), (ci, 0), 8), ('RIGHTPADDING', (ci, 0), (ci, 0), 8),
                            ])
                    pipeline_table.setStyle(TableStyle(style_cmds))

            log_mono_style = ParagraphStyle('LogMono', fontName='Courier-Bold', fontSize=8, textColor=colors.HexColor('#334155'), leading=12)
            styled_logs = []
            for step in diagnosis_data['decision_path']:
                styled_logs.append(Paragraph(f"<font color='#F97316'>* </font> {step}", log_mono_style))
            log_table = Table([[line] for line in styled_logs], colWidths=[500])
            log_table.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))

            container_elements_pdf = []
            header_style = ParagraphStyle('UIHeader', fontSize=10, textColor=colors.HexColor('#059669'), spaceAfter=12)
            container_elements_pdf.append(Paragraph("<b>AGENT EXECUTION COMPLETE</b>", header_style))
            if pipeline_table:
                container_elements_pdf.append(pipeline_table)
                container_elements_pdf.append(Spacer(1, 14))
            container_elements_pdf.append(log_table)
            master_table = Table([[container_elements_pdf]], colWidths=[520])
            master_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FAFAFA')),
                ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#6EE7B7')),
                ('TOPPADDING', (0,0), (-1,-1), 16), ('BOTTOMPADDING', (0,0), (-1,-1), 16),
                ('LEFTPADDING', (0,0), (-1,-1), 16), ('RIGHTPADDING', (0,0), (-1,-1), 16),
            ]))
            elements.append(KeepTogether([master_table]))

        if diagnosis_data.get('safety_warning') and diagnosis_data['safety_warning'].lower() != 'none':
            elements.append(Paragraph("<b>Safety Warning</b>", h2_style))
            elements.append(Paragraph(diagnosis_data['safety_warning'], body_style))

        # --- Embed Confusion Matrix Heatmap ---
        cm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'confusion_matrix.png')
        if os.path.exists(cm_path):
            from reportlab.platypus import Image as RLImage
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("<b>Model Performance (Confusion Matrix)</b>", h2_style))
            
            try:
                img = RLImage(cm_path)
                # Scale image to fit within the PDF margins
                aspect = img.imageHeight / float(img.imageWidth)
                img.drawWidth = 400
                img.drawHeight = 400 * aspect
                img.hAlign = 'CENTER'
                
                cm_table = Table([[img]], colWidths=[520])
                cm_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FAFAFA')),
                    ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (-1,-1), 10),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ]))
                elements.append(KeepTogether([cm_table]))
            except Exception as e:
                pass # Fail silently if image can't be drawn so PDF still generates

        elements.append(Spacer(1, 25))
        elements.append(Paragraph("<i>Powered by Tata Technologies | Smart Vehicle Diagnostic Platform</i>", subtitle_style))

        doc.build(elements)
        return buffer.getvalue()
    except Exception as e:
        if logger: logger.error(f"Failed to generate PDF: {str(e)}")
        st.warning(f"Could not generate PDF report: {str(e)}")
        return None

# ==========================================
# WORKFLOW TRACKER RENDER HELPER
# ==========================================
NODE_ICONS = {"START": "⚡", "reasoner": "🧠", "tools": "🔧", "logger": "📋", "__end__": "✅", "END": "✅"}
NODE_LABELS = {"START": "Initialize", "reasoner": "Reasoning", "tools": "Tool Exec", "logger": "Parse Data", "__end__": "Complete", "END": "Complete"}

def render_workflow_tracker(history: list, active_node: str | None, is_complete: bool, is_error: bool = False, decisions: list | None = None) -> str:
    if not history:
        return ""
    if is_error:
        wrap_cls, icon, title_cls, title = "workflow-tracker-wrap wf-error", "❌", "wf-title-error", "Agent Execution Failed"
    elif is_complete:
        wrap_cls, icon, title_cls, title = "workflow-tracker-wrap wf-success", "✅", "wf-title-success", "Agent Execution Complete"
    else:
        wrap_cls, icon, title_cls, title = "workflow-tracker-wrap", "⚙️", "", "Agent Execution Live"

    nodes_html = ""
    for i, node in enumerate(history):
        is_active = (node == active_node and not is_complete and not is_error)
        node_cls = "wf-node wf-active" if is_active else "wf-node wf-completed"
        icon_str = NODE_ICONS.get(node, "🔹")
        label = NODE_LABELS.get(node, node.upper())
        spinner = '<span class="wf-spinner"></span>' if is_active else ""
        nodes_html += f'<div class="{node_cls}">{icon_str} {label}{spinner}</div>'
        if i < len(history) - 1:
            nodes_html += '<div class="wf-connector"></div>'

    decisions_html = ""
    if decisions:
        entries = ""
        for d in decisions:
            if isinstance(d, str) and '→' in d:
                parts = d.split('→', 1)
                entry_text = f'<strong>{parts[0].strip()}</strong> → {parts[1].strip()}'
            else:
                entry_text = str(d)
            entries += f'<div class="wf-decision-item"><span class="wf-decision-icon">🔸</span><span class="wf-decision-text">{entry_text}</span></div>'
        decisions_html = f'<div class="wf-decisions">{entries}</div>'

    return f"""
    <div class="{wrap_cls}">
        <div class="wf-header">
            <span class="wf-header-icon">{icon}</span>
            <p class="wf-header-title {title_cls}">{title}</p>
        </div>
        <div class="wf-path">{nodes_html}</div>
        {decisions_html}
    </div>
    """

# ==========================================
# ENHANCED: SIDEBAR DATA INGESTION
# ==========================================
with st.sidebar:
    st.subheader("Engineering Console", divider="blue")
    
    with st.expander("Session Stats"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Vision Calls", st.session_state.vision_calls)
            st.metric("Messages", len(st.session_state.messages))
        with col2:
            st.metric("Latency (ms)", int(st.session_state.agent_latency_ms))
            st.metric("Session ID", str(st.session_state.session_id)[:8])

    with st.expander("Automated Data Intake", expanded=True):
        st.markdown("**Upload a diagnostic scanner image:**")
        uploaded_image = st.file_uploader(
            "Upload Scanner / Dashboard Image", 
            type=["jpg", "png", "webp", "jpeg"],
            key=f"file_uploader_{st.session_state.reset_count}"
        )
        
        if uploaded_image:
            image_id = f"{uploaded_image.name}_{uploaded_image.size}"
            if image_id not in st.session_state.processed_images:
                with st.spinner("Extracting Telemetry..."):
                    try:
                        if uploaded_image.size == 0:
                            st.error("Image file is empty")
                        else:
                            try:
                                img = Image.open(uploaded_image).convert("RGB")
                            except Exception as ie:
                                raise VisionExtractionError(f"Cannot read image: {str(ie)[:50]}")
                            
                            if img.size[0] < 100 or img.size[1] < 100:
                                st.warning(f"Image resolution low ({img.size[0]}x{img.size[1]}). May be unclear.")

                            buffered = io.BytesIO()
                            img.save(buffered, format="JPEG", quality=95)
                            buffered.seek(0)
                            img_bytes = buffered.getvalue()
                            
                            if not img_bytes:
                                raise VisionExtractionError("Image encoding failed")
                                
                            encoded = base64.b64encode(img_bytes).decode('utf-8')
                            
                            start_time = time.time()
                            v_res = call_vision_api(encoded)
                            duration_ms = (time.time() - start_time) * 1000
                            
                            if not v_res or not v_res.content:
                                raise VisionExtractionError("API returned no response")
                            
                            clean_json = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', v_res.content, re.DOTALL)
                            if clean_json:
                                try:
                                    v_data = json.loads(clean_json.group())
                                    validated = extract_and_validate_vision_data(v_data)
                                    
                                    st.session_state.rpm_val = validated['rpm']
                                    st.session_state.speed_val = validated['speed']
                                    st.session_state.load_val = validated['load']
                                    st.session_state.temp_val = validated['temp']
                                    st.session_state.dtc_val = validated['dtc']
                                    st.session_state.processed_images.add(image_id)
                                    
                                    if logger: 
                                        perf_logger.log_execution_time("Vision_Extraction", duration_ms)
                                    st.success(f"Extraction Complete ({duration_ms:.0f}ms)")
                                    st.rerun()
                                except json.JSONDecodeError as je:
                                    raise VisionExtractionError(f"Bad JSON: {str(je)[:80]}")
                            else:
                                raise VisionExtractionError("No JSON detected.")
                    except VisionExtractionError as e:
                        st.error(f"Vision Error: {str(e)}")
                    except Exception as e:
                        st.error(f"Image Error: {str(e)[:150]}")

    with st.expander("Image Not Recognized?", expanded=False):
        st.markdown("""
        **What makes a good diagnostic image?**
        - Clear OBD-II scanner display or dashboard
        - Shows RPM, Speed, Load, Temp, and DTC values
        """)

    with st.container(border=True):
        st.markdown("**Manual Context**")
        st.session_state.car_model_val = st.text_input(
            "Vehicle Model", value=st.session_state.car_model_val, placeholder="e.g., Tata Safari"
        )
        st.session_state.dtc_val = st.text_input("Active Fault Codes (DTC)", value=st.session_state.dtc_val)
        st.session_state.symptom_val = st.text_area("Symptom Description", value=st.session_state.symptom_val, height=60)
        st.session_state.condition_val = st.text_input("Operating Condition", value=st.session_state.condition_val)

    with st.expander("Live Sensor Data", expanded=True):
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.session_state.rpm_val = st.number_input("Engine RPM", value=int(st.session_state.rpm_val), min_value=0, max_value=8000)
            st.session_state.load_val = st.number_input("Load %", value=int(st.session_state.load_val), min_value=0, max_value=100)
        with col_s2:
            st.session_state.speed_val = st.number_input("Speed km/h", value=int(st.session_state.speed_val), min_value=0, max_value=300)
            st.session_state.temp_val = st.number_input("Temp °C", value=int(st.session_state.temp_val), min_value=-40, max_value=130)

    if st.button("Reset Session", use_container_width=True):
        # Reset all sensor values
        for key, val in defaults.items(): st.session_state[key] = val
        
        # Reset conversation and diagnostics
        st.session_state.messages = []
        st.session_state.processed_images = set()
        st.session_state.vision_calls = 0
        st.session_state.uploaded_image_data = None
        st.session_state.agent_latency_ms = 0
        
        # Increment reset counter to force file_uploader widget to reset
        st.session_state.reset_count += 1
        
        st.success("✅ Session reset successfully! All data and images cleared.")
        st.rerun()

# ==========================================
# ENHANCED: MAIN DASHBOARD
# ==========================================
st.markdown(f"""
    <div class="custom-header">
        <div class="header-title-container">
            <h1 class="header-main-title">Smart Vehicle Diagnostic</h1>
        </div>
        <div class="top-metrics-container">
            <div class="top-metric-item">
                <div class="top-metric-label">RPM</div>
                <div class="top-metric-value">{st.session_state.rpm_val}</div>
            </div>
            <div class="top-metric-item">
                <div class="top-metric-label">Speed</div>
                <div class="top-metric-value">{st.session_state.speed_val} <span class="top-metric-unit">km/h</span></div>
            </div>
            <div class="top-metric-item">
                <div class="top-metric-label">Load</div>
                <div class="top-metric-value">{st.session_state.load_val} <span class="top-metric-unit">%</span></div>
            </div>
            <div class="top-metric-item">
                <div class="top-metric-label">Temp</div>
                <div class="top-metric-value">{st.session_state.temp_val} <span class="top-metric-unit">°C</span></div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# CHAT INTERFACE & EXECUTION LOOP
# ==========================================
USER_AVATAR = None 
AI_AVATAR = None

for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"], avatar=USER_AVATAR if msg["role"] == "user" else AI_AVATAR):
        if msg["type"] == "text":
            st.markdown(msg["content"])
        
        elif msg["type"] == "conversational_diagnostic":
            d = msg["data"]
            st.markdown(d.get("diagnosis", ""))
            if d.get("action_plan"):
                st.markdown("**Details & Steps:**")
                for step in d["action_plan"]:
                    st.markdown(f"- {clean_industry_text(step)}")
                    
        elif msg["type"] == "structured":
            d = msg["data"]
            # Render the completed workflow tracker if available
            if d.get('wf_history'):
                st.markdown(render_workflow_tracker(d['wf_history'], None, True, decisions=d.get('decision_path')), unsafe_allow_html=True)

            st.subheader(f"{d.get('main_heading', 'Diagnostic Results')}", divider="blue")
            
            rag_s = d.get('rag_score', 0)
            ml_s = d.get('ml_score', 0)
            web_s = d.get('web_score', 0)
            # Ensure they are ints for comparison
            rag_s = int(rag_s) if isinstance(rag_s, (int, float)) else 0
            ml_s = int(ml_s) if isinstance(ml_s, (int, float)) else 0
            web_s = int(web_s) if isinstance(web_s, (int, float)) else 0
            overall = max(rag_s, ml_s, web_s)
            
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='confidence-card'><span class='card-label'>RAG Knowledge</span><span class='card-score'>{rag_s}%</span></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='confidence-card'><span class='card-label'>ML Predictive</span><span class='card-score'>{ml_s}%</span></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='confidence-card'><span class='card-label'>Overall Score</span><span class='card-score'>{overall}%</span></div>", unsafe_allow_html=True)
            
            st.markdown(f"**Final Verdict:** {d.get('diagnosis', '')}")
            with st.expander("View Technical Evidence"):
                st.write("**Manual Database (RAG):**", d.get("rag_evidence", "N/A"))
                st.write("**Live Web Reports:**", d.get("web_evidence", "N/A"))
            
            if d.get("action_plan") and len(d["action_plan"]) > 0:
                st.subheader(f"{d.get('steps_heading', 'Action Plan')}")
                for i, step in enumerate(d["action_plan"], 1):
                    clean_step = clean_industry_text(step)
                    st.markdown(f"""<div class='step-container'><span class='step-number'>Step {i}:</span>{clean_step}</div>""", unsafe_allow_html=True)
            
            if d.get("safety_warning") and str(d.get("safety_warning")).lower() != "none":
                st.error(f"Safety Alert: {d['safety_warning']}")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("Mark as Helpful", key=f"helpful_{idx}"):
                    if diagnostic_history:
                        diagnostic_history.update_resolution(d.get('id', str(idx)), "User marked as helpful", feedback_score=5)
                    st.success("Thank you for the feedback.")
            with col2:
                if st.button("Download PDF", key=f"download_{idx}"):
                    pdf_bytes = generate_diagnostic_report_pdf(d)
                    if pdf_bytes:
                        st.download_button(label="Click to Download", data=pdf_bytes, file_name=f"diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", mime="application/pdf")
            with col3:
                if st.button("Save to History", key=f"save_{idx}"):
                    d['id'] = str(idx)
                    d['sensor_readings'] = { 'rpm': st.session_state.rpm_val, 'speed': st.session_state.speed_val, 'load': st.session_state.load_val, 'temp': st.session_state.temp_val }
                    if diagnostic_history:
                        diagnostic_history.save_diagnosis(d)
                    st.success("Saved to history.")

if user_text := st.chat_input("Enter diagnostic query or request procedure..."):
    with st.chat_message("user"):
        st.markdown(user_text)
    
    with st.spinner("Synthesizing Diagnostic Insights..."):
        try:
            class Triage(BaseModel):
                is_diagnostic: bool = Field(description="True ONLY if user reports a NEW vehicle issue.")
                is_follow_up: bool = Field(description="True if user asks a follow-up question.")
                is_sufficient: bool = Field(description="True ONLY if enough specific technical info is provided.")
                response: str = Field(description="If is_diagnostic is False, OR if is_sufficient is False, put your conversational answer or clarifying question here.")
                missing: list = Field(default=[], description="List of specific missing data points.")
                ui_main_heading: str = Field(default="", description="Main heading for UI display (optional)")
                ui_steps_heading: str = Field(default="", description="Steps heading for UI display (optional)")
                
            t_parser = PydanticOutputParser(pydantic_object=Triage)
            
            history_context = "No previous diagnosis."
            if st.session_state.messages:
                last_msg = st.session_state.messages[-1]
                if last_msg["role"] == "assistant" and last_msg["type"] == "structured":
                    history_context = f"Previous Diagnosis: {last_msg['data'].get('diagnosis')}\nSteps: {last_msg['data'].get('action_plan')}"
            
            t_prompt = (
                f"Context from previous turn:\n{history_context}\n\n"
                f"User Input: '{user_text}' | Vehicle: {st.session_state.car_model_val} | DTC: {st.session_state.dtc_val} | "
                f"Sensors: RPM={st.session_state.rpm_val}, Speed={st.session_state.speed_val}, Load={st.session_state.load_val}%, Temp={st.session_state.temp_val}C\n"
                "CRITICAL RULES:\n"
                "1. If user describes a NEW issue, set is_diagnostic=True and is_follow_up=False.\n"
                "2. If user asks a FOLLOW-UP question, set is_diagnostic=False, is_follow_up=True, and write the answer in 'response'.\n"
                "3. If general chat, set is_diagnostic=False and reply in 'response'.\n"
                "4. If is_diagnostic=True BUT the input is vague and lacks technical details, set is_sufficient=False. In 'response', act as a helpful mechanic and ask a specific CLARIFYING QUESTION.\n"
                f"{t_parser.get_format_instructions()}"
            )
            
            t_res = llm_flash.invoke(t_prompt)
            try:
                intent = t_parser.parse(t_res.content.replace('```json','').replace('```','').strip())
            except Exception as e:
                # Schema mismatch - try manual JSON parsing and field mapping
                try:
                    import json
                    parsed_json = json.loads(t_res.content.replace('```json','').replace('```','').strip())
                    
                    # Create Triage object with defaults for missing fields
                    intent = Triage(
                        is_diagnostic=parsed_json.get('is_diagnostic', False),
                        is_follow_up=parsed_json.get('is_follow_up', False),
                        is_sufficient=parsed_json.get('is_sufficient', False),
                        response=parsed_json.get('response', ''),
                        missing=parsed_json.get('missing', []),
                        ui_main_heading=parsed_json.get('ui_main_heading', ''),
                        ui_steps_heading=parsed_json.get('ui_steps_heading', '')
                    )
                except:
                    # Last resort - create default response
                    intent = Triage(
                        is_diagnostic=False,
                        is_follow_up=True,
                        is_sufficient=False,
                        response=str(t_res.content),
                        missing=[]
                    )

            if not intent.is_diagnostic or not intent.is_sufficient:
                st.session_state.messages.append({"role": "user", "content": user_text, "type": "text"})
                st.session_state.messages.append({"role": "assistant", "content": intent.response, "type": "text"})
                st.rerun()

            full_input = (
                f"Vehicle: {st.session_state.car_model_val} | DTC: {st.session_state.dtc_val} | "
                f"Symptom: {st.session_state.symptom_val} | Condition: {st.session_state.condition_val} | "
                f"Sensors: RPM={st.session_state.rpm_val}, Speed={st.session_state.speed_val}, "
                f"Load={st.session_state.load_val}%, Temp={st.session_state.temp_val}C | User: {user_text}"
            )

            # Live workflow tracker
            flow_container = st.empty()
            wf_history = ["START"]
            all_decisions = [f"TRIAGE → Routed to Full Diagnostic Pipeline (is_diagnostic={intent.is_diagnostic}, is_sufficient={intent.is_sufficient})"]
            flow_container.markdown(render_workflow_tracker(wf_history, "START", False, decisions=all_decisions), unsafe_allow_html=True)

            print(f"\n{'='*70}")
            print(f"INITIATING TATA TECHNOLOGIES AGENTIC WORKFLOW")
            print(f"   Session ID: {st.session_state.session_id}")
            print(f"   Input: {user_text[:50]}...")
            print(f"{'='*70}")

            start_time = time.time()
            final_state = None

            for output in langgraph_app.stream({"messages": [HumanMessage(content=full_input)], "decision_log": []}):
                for node_name, state_update in output.items():
                    if not wf_history or wf_history[-1] != node_name:
                        wf_history.append(node_name)
                    new_decisions = state_update.get('decision_log', [])
                    if new_decisions:
                        all_decisions.extend(new_decisions)
                    flow_container.markdown(
                        render_workflow_tracker(wf_history, node_name, False, decisions=all_decisions),
                        unsafe_allow_html=True
                    )
                    t_stamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{t_stamp}] NODE EXECUTED: {node_name.upper()}")
                    final_state = state_update

            duration_ms = (time.time() - start_time) * 1000
            st.session_state.agent_latency_ms = duration_ms

            if final_state and "messages" in final_state:
                raw_content = final_state["messages"][-1].content
                if isinstance(raw_content, list):
                    raw_output = "".join([item.get("text", str(item)) if isinstance(item, dict) else str(item) for item in raw_content])
                else:
                    raw_output = str(raw_content)
            else:
                raise AgentExecutionError("Agent flow failed to return messages.")

            # Mark workflow complete
            all_decisions.append(f"COMPLETE → Agent finished in {duration_ms:.0f}ms")
            if not wf_history or wf_history[-1] not in ("END", "__end__"):
                wf_history.append("END")
            flow_container.markdown(
                render_workflow_tracker(wf_history, None, True, decisions=all_decisions),
                unsafe_allow_html=True
            )

            validated = None
            try:
                validated = parser.parse(raw_output.replace("```json", "").replace("```", "").strip())
            except Exception as parse_error:
                # Schema mismatch - try manual JSON parsing and field mapping
                try:
                    import json
                    parsed_json = json.loads(raw_output.replace("```json", "").replace("```", "").strip())
                    
                    # Create DiagnosticResponse object with defaults for missing fields
                    validated = DiagnosticResponse(
                        needs_more_info=parsed_json.get('needs_more_info', False),
                        clarifying_questions=parsed_json.get('clarifying_questions', []),
                        diagnosis=parsed_json.get('diagnosis', parsed_json.get('response', '')),
                        confidence_level=parsed_json.get('confidence_level', 'Medium'),
                        confidence_score=parsed_json.get('confidence_score', 0),
                        rag_score=parsed_json.get('rag_score', 0),
                        ml_score=parsed_json.get('ml_score', 0),
                        web_score=parsed_json.get('web_score', 0),
                        ml_evidence=parsed_json.get('ml_evidence', ''),
                        rag_evidence=parsed_json.get('rag_evidence', ''),
                        web_evidence=parsed_json.get('web_evidence', ''),
                        action_plan=parsed_json.get('action_plan', []),
                        safety_warning=parsed_json.get('safety_warning', 'None')
                    )
                except Exception as fallback_error:
                    st.error(f"Failed to parse diagnostic response: {str(parse_error)}")
                    validated = None

            print(f"\n{'-'*70}")
            if validated:
                print(f"WORKFLOW COMPLETE ({duration_ms:.0f}ms)")
                print(f"   Confidence: {validated.confidence_level} ({validated.confidence_score}%)")
                print(f"   RAG Score : {validated.rag_score}%")
                print(f"   ML Score  : {validated.ml_score}%")
                print(f"   Web Score : {validated.web_score}%")
            else:
                print(f"WORKFLOW COMPLETE - Parsing failed ({duration_ms:.0f}ms)")
            print(f"{'-'*70}")
            
            # Handle case where validation failed
            if not validated:
                st.error("Failed to generate diagnostic response. Please try again.")
                validated = DiagnosticResponse(
                    needs_more_info=True,
                    clarifying_questions=["Please provide more specific details about your vehicle issue."],
                    diagnosis="Diagnostic processing failed. Please retry your request.",
                    confidence_level="Low",
                    confidence_score=0,
                    rag_score=0,
                    ml_score=0,
                    web_score=0,
                    ml_evidence="",
                    rag_evidence="",
                    web_evidence="",
                    action_plan=[],
                    safety_warning="None"
                )

            structured_data = {
                "id": str(datetime.now().timestamp()),
                "main_heading": intent.ui_main_heading or "Diagnostic Analysis Results",
                "diagnosis": validated.diagnosis,
                "rag_evidence": validated.rag_evidence,
                "web_evidence": validated.web_evidence,
                "steps_heading": intent.ui_steps_heading or "Action Plan",
                "action_plan": getattr(validated, "action_plan", []),
                "safety_warning": validated.safety_warning,
                "confidence_level": validated.confidence_level,
                "confidence_score": validated.confidence_score,
                "rag_score": validated.rag_score,
                "ml_score": validated.ml_score,
                "web_score": validated.web_score,
                "vehicle_model": st.session_state.car_model_val,
                "dtc_codes": st.session_state.dtc_val,
                "symptoms": st.session_state.symptom_val,
                "decision_path": all_decisions,
                "wf_history": wf_history,
            }

            if diagnostic_history:
                diagnostic_history.save_diagnosis(structured_data)

            st.session_state.messages.append({"role": "user", "content": user_text, "type": "text"})

            if intent.is_follow_up:
                st.session_state.messages.append({"role": "assistant", "type": "conversational_diagnostic", "data": structured_data})
            else:
                st.session_state.messages.append({"role": "assistant", "type": "structured", "data": structured_data})

            st.rerun()
            
        except AgentExecutionError as e:
            st.error(handle_streamlit_error(e, "Agent Error"))
        except DataValidationError as e:
            st.error(handle_streamlit_error(e, "Validation Error"))
        except Exception as e:
            st.session_state.messages.append({"role": "user", "content": user_text, "type": "text"})
            st.session_state.messages.append({"role": "assistant", "content": str(e), "type": "text"})
            st.rerun()

# ==========================================
# FOOTER: STATISTICS
# ==========================================
with st.expander("Platform Statistics"):
    stats = diagnostic_history.get_statistics() if diagnostic_history else {}
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total Diagnostics", stats.get('total_diagnostics', 0))
    with col2: st.metric("Avg Confidence", f"{stats.get('avg_confidence', 0):.1f}%")
    with col3: st.metric("Avg User Rating", stats.get('avg_feedback', 'N/A'))

st.markdown("---")
st.markdown("<div style='text-align: center; color: #001F5B; font-weight: 900; font-size: 14px;'>Powered by Tata Technologies | Smart Vehicle Diagnostic Platform</div>", unsafe_allow_html=True)

