# # scripts/cli_chat.py
# import sys
# import os
# import time
# from dotenv import load_dotenv

# # Add the project root to python path so we can import 'src'
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# # Import the Agent Executor from your existing backend code
# from src.agents.advisor import agent_executor

# # Load environment variables (API Keys)
# load_dotenv()

# def start_chat_session():
#     print("\n" + "="*50)
#     print("🤖 AI Vehicle Diagnostic Agent (Backend CLI Mode)")
#     print("Type 'exit' or 'quit' to stop.")
#     print("="*50 + "\n")

#     while True:
#         try:
#             # 1. Get Input from User (Terminal)
#             user_query = input("🔧 You: ").strip()

#             # Check for exit command
#             if user_query.lower() in ['exit', 'quit', 'q']:
#                 print("\n👋 Exiting. Drive safely!")
#                 break
            
#             if not user_query:
#                 continue

#             print("\n⚙️  Agent is thinking...\n")
            
#             # 2. Send to Backend (Agent)
#             # This triggers the exact same flow as the Streamlit App
#             start_time = time.time()
#             response = agent_executor.invoke({"input": user_query})
#             end_time = time.time()

#             # 3. Print the Result
#             print("-" * 50)
#             print(f"🤖 Agent: {response['output']}")
#             print("-" * 50)
#             print(f"⏱️  Latency: {end_time - start_time:.2f}s\n")

#         except KeyboardInterrupt:
#             # Handle Ctrl+C gracefully
#             print("\n\n👋 Exiting...")
#             break
#         except Exception as e:
#             print(f"\n❌ Error: {str(e)}\n")

# if __name__ == "__main__":
#     start_chat_session()


import sys
import os
import time
from dotenv import load_dotenv

# 1. System Path Fix (Crucial for importing src modules)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Import the Agent
try:
    from src.agents.advisor import agent_executor
except ImportError:
    print("❌ Critical Error: Could not import 'agent_executor'.")
    print("   Ensure 'agent_executor = build_advisor()' is at the bottom of src/agents/advisor.py")
    sys.exit(1)

load_dotenv()

def start_chat():
    print("\n" + "="*60)
    print("🚗 AI Vehicle Diagnostic Agent (Interactive Mode)")
    print("   - Type 'exit' to quit.")
    print("   - Try inputs like: 'Tata Nexon P2463' or 'Ford F-150 shaking'")
    print("="*60 + "\n")

    while True:
        try:
            # Get User Input
            query = input("\n🔧 Enter Symptom/Code: ").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("👋 Exiting...")
                break
            
            if not query:
                continue

            print(f"\n⚙️  Analyzing '{query}'...")
            
            # Start Timer
            start = time.time()
            
            # Run Agent
            # The agent will automatically decide to use XGBoost, RAG, or Web Search
            response = agent_executor.invoke({"input": query})
            
            duration = time.time() - start

            # Output Result
            print("\n" + "-"*60)
            print("🤖 Agent Verdict:")
            print(response['output'])
            print("-"*60)
            print(f"⏱️  Time Taken: {duration:.2f}s")

        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    start_chat()
