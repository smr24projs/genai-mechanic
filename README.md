# 🚗 GenAI Mechanic

An Agentic RAG application that diagnoses vehicle issues using a Multi-Agent System.
It combines a **Streamlit** dashboard with a local **LangGraph** Multi-Agent System.

## 🌟 Features
- **OBD-II Simulator:** Simulates engine codes (e.g., P0300) and sensor data.
- **Local Agents:** Runs entirely on your machine using LangGraph.
- **Google Gemini:** Powered by Gemini 1.5 Pro/Flash.

## 🛠️ Tech Stack
- **Frontend:** Streamlit (Python)
- **Backend Logic:** LangGraph
- **LLM:** Google Gemini
- **Database:** Mock Pandas DB for parts lookup

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/smr24projs/genai-mechanic.git
cd genai-mechanic
```

### 2. Create a Virtual Environment (Recommended)
```bash
# Create venv
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory (you can copy `.env.example`).
Add your Google Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Initialize Data
Generate the necessary dummy data (DTC codes and parts catalog):
```bash
python setup_data.py
```

### 6. Verify Setup
Run the test script to ensure everything is configured correctly:
```bash
python test_setup.py
```

### 7. Run the Application
Start the Streamlit dashboard:
```bash
streamlit run app.py
```
The application should open automatically in your browser at `http://localhost:8501`.

## 🖥️ CLI Mode
You can also run the agent logic directly in the terminal:
```bash
python main.py
```
