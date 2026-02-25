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



import time
import sys
import os
import json

# Add the project root to path so we can import 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the Agent
try:
    from src.agents.advisor import agent_executor
except ImportError:
    print("❌ Error: Could not import 'agent_executor' from src.agents.advisor")
    print("   Make sure you added 'agent_executor = build_advisor()' at the bottom of advisor.py")
    sys.exit(1)

# --- TEST CASES (Mixed Scenarios) ---
test_cases = [
    {
        "id": 1,
        "query": "My 2018 Ford F-150 has a flashing check engine light and shakes at idle.",
        "expected_keywords": ["misfire", "coil", "plug", "injector", "vct", "solenoid"],
        "min_score": 7
    },
    {
        "id": 2,
        "query": "Code P0133 on a 2015 Chevy Silverado.",
        "expected_keywords": ["oxygen", "sensor", "o2", "slow response", "exhaust", "leak"],
        "min_score": 8
    },
    {
        "id": 3,
        "query": "Mahindra XUV500 losing power and black smoke from exhaust.",
        "expected_keywords": ["turbo", "intercooler", "egr", "injector", "air filter", "boost"],
        "min_score": 6
    }
]

def grade_response(query, output, keywords):
    """
    A simple keyword-based grader to save API calls.
    Returns a score (0-10) and a reason.
    """
    output_lower = output.lower()
    
    # 1. Check for Error Messages
    if "error" in output_lower or "quota" in output_lower or "limit" in output_lower:
        return {"score": 0, "reason": "API Error or Rate Limit hit."}
    
    # 2. Check for Keyword Matches
    matches = [kw for kw in keywords if kw in output_lower]
    match_count = len(matches)
    
    # 3. Calculate Score
    # Base score for replying: 5
    # +1.5 for each keyword match (capped at 10)
    score = min(10, 5 + (match_count * 1.5))
    
    reason = f"Found {match_count} keywords: {matches}. "
    if score >= 8:
        reason += "Excellent diagnosis."
    elif score >= 5:
        reason += "Acceptable, but could be more specific."
    else:
        reason += "Poor relevance."
        
    return {"score": round(score, 1), "reason": reason}

def run_evaluation():
    print(f"\n🚀 Starting Agent Evaluation on {len(test_cases)} cases...")
    print("   (Adding 20s cooldown between tests to avoid Rate Limits)\n")
    
    results = []
    total_score = 0
    
    for test in test_cases:
        print(f"🔹 Testing Case {test['id']}: {test['query']}")
        
        # A. Run the Agent
        try:
            start_time = time.time()
            response = agent_executor.invoke({"input": test['query']})
            agent_output = response['output']
            latency = time.time() - start_time
        except Exception as e:
            print(f"   ⚠️ Runtime Error: {e}")
            agent_output = f"Critical Error: {str(e)}"
            latency = 0

        # B. Grade the Result
        grade = grade_response(test['query'], agent_output, test['expected_keywords'])
        
        # C. Print & Store
        print(f"   ⏱️  Latency: {latency:.2f}s")
        print(f"   📝 Grade: {grade['score']}/10")
        print(f"   🤔 Reason: {grade['reason']}")
        print("-" * 40)
        
        total_score += grade['score']
        results.append({
            "id": test['id'],
            "query": test['query'],
            "output": agent_output,
            "score": grade['score'],
            "latency": latency
        })

        # --- RATE LIMIT COOLDOWN ---
        if test['id'] < len(test_cases):
            print("   💤 Cooling down for 20 seconds...")
            time.sleep(20)
        # ---------------------------

    # 4. Final Report
    avg_score = total_score / len(test_cases)
    print("\n" + "="*40)
    print(f"📊 FINAL REPORT")
    print(f"Total Cases: {len(test_cases)}")
    print(f"Average Score: {avg_score:.1f}/10")
    print("="*40)
    
    # Save to file
    with open("evaluation_report.json", "w") as f:
        json.dump(results, f, indent=2)
    print("✅ Results saved to evaluation_report.json")

if __name__ == "__main__":
    run_evaluation()
