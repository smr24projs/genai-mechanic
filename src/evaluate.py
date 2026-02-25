# import pandas as pd
# import time
# from src.agents.advisor import build_advisor_agent

# # 1. Load Data
# df = pd.read_csv("DTC_CODES_Dataset.csv") # Columns: Code, Symptom, Real_Cause

# # 2. Initialize Agent
# agent = build_advisor_agent()
# correct_count = 0
# total = 5 # Test on 5 rows first

# print("--- Starting Evaluation ---")

# for index, row in df.head(total).iterrows():
#     code = row['Code']
#     symptom = row['Symptom']
#     real_cause = row['Real_Cause']
    
#     prompt = f"Diagnose code {code} with symptom '{symptom}'. What is the root cause? Answer in 1 short sentence."
    
#     try:
#         response = agent.invoke({"input": prompt}, config={"configurable": {"session_id": "eval_bot"}})
#         output = response["output"]
        
#         print(f"\nTest {index+1}: Code {code}")
#         print(f"Expected: {real_cause}")
#         print(f"Agent: {output}")
        
#         # Simple Keyword Check (You can make this smarter later)
#         if real_cause.lower() in output.lower():
#             print("✅ PASS")
#             correct_count += 1
#         else:
#             print("❌ FAIL")
            
#     except Exception as e:
#         print(f"Error: {e}")
#         time.sleep(5) # Wait if rate limited

# accuracy = (correct_count / total) * 100
# print(f"\n--- Final Accuracy: {accuracy}% ---")



# scripts/evaluate.py
import sys
import os
import json
import time
from dotenv import load_dotenv

# Add the project root to path so we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents.advisor import agent_executor

load_dotenv()

# 1. Setup the "Judge" LLM
# We use a strict temperature (0.0) so the grading is consistent
evaluator_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0
)

# 2. Define Test Cases (Ground Truth)
test_cases = [
    {
        "id": 1,
        "query": "My 2018 Ford F-150 has a flashing check engine light and shakes at idle.",
        "expected_code": "P0300",
        "expected_cause": "Misfire",
        "critical_info": "Catalytic converter damage risk"
    },
    {
        "id": 2,
        "query": "Code P0133 on a 2015 Chevy Silverado.",
        "expected_code": "P0133",
        "expected_cause": "O2 Sensor Slow Response",
        "critical_info": "Check for exhaust leaks"
    },
    {
        "id": 3,
        "query": "Mahindra XUV500 losing power and black smoke from exhaust.",
        "expected_code": "P0299",
        "expected_cause": "Turbocharger/Boost Leak",
        "critical_info": "Intercooler hose"
    }
]

def grade_response(query, agent_response, expected):
    """
    Uses Gemini to grade the Agent's response against the expected ground truth.
    """
    grading_prompt = f"""
    You are a Senior Technical Instructor grading a student mechanic's diagnosis.
    
    ### SCENARIO:
    User Query: "{query}"
    
    ### STUDENT ANSWER (Agent Output):
    "{agent_response}"
    
    ### EXPECTED FACTS (Ground Truth):
    - Likely Code: {expected['expected_code']}
    - Root Cause: {expected['expected_cause']}
    - Critical Info: {expected['critical_info']}
    
    ### YOUR TASK:
    Grade the Student Answer on a scale of 0 to 10 based on:
    1. **Accuracy (0-4)**: Did they identify the correct cause/code?
    2. **Safety (0-3)**: Did they mention critical warnings (e.g., flashing light)?
    3. **Clarity (0-3)**: Is the advice actionable?
    
    Return ONLY a valid JSON object like this:
    {{
        "score": 8,
        "reason": "Correctly identified misfire but missed safety warning."
    }}
    """
    
    try:
        result = evaluator_llm.invoke(grading_prompt)
        # Clean up code blocks if Gemini returns markdown
        clean_json = result.content.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        return {"score": 0, "reason": f"Grading Error: {str(e)}"}

# 3. Main Evaluation Loop
def run_evaluation():
    print("🚀 Starting Agent Evaluation...\n")
    total_score = 0
    max_score = len(test_cases) * 10
    results = []

    for test in test_cases:
        print(f"Testing Case {test['id']}: {test['query']}")
        
        # A. Run the Agent
        try:
            start_time = time.time()
            response = agent_executor.invoke({"input": test['query']})
            agent_output = response['output']
            latency = time.time() - start_time
        except Exception as e:
            agent_output = f"Error: {str(e)}"
            latency = 0

        # B. Grade the Result
        grade = grade_response(test['query'], agent_output, test)
        
        # C. Print & Store
        print(f"   ⏱️  Latency: {latency:.2f}s")
        print(f"   📝 Grade: {grade['score']}/10")
        print(f"   🤔 Reason: {grade['reason']}\n")
        
        total_score += grade['score']
        results.append({
            "id": test['id'],
            "score": grade['score'],
            "latency": latency,
            "output": agent_output
        })

    # 4. Final Report
    avg_score = total_score / len(test_cases)
    print("="*40)
    print(f"📊 FINAL REPORT")
    print(f"Total Cases: {len(test_cases)}")
    print(f"Average Score: {avg_score:.1f}/10")
    print("="*40)

    # Save to file for your project report
    with open('evaluation_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("✅ Results saved to evaluation_report.json")

if __name__ == "__main__":
    run_evaluation()
