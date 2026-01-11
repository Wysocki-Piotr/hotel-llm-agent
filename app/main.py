import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from langchain_core.messages import HumanMessage
from src.database import init_db
from src.agent import app


def run_chat():
    init_db()
    
    print("--- ASYSTENT PODRÓŻY (wpisz 'q' aby wyjść) ---")

    chat_history = []
    
    while True:
        query = input("\nTy: ")
        if query.lower() in ['q', 'quit', 'exit']:
            break
            
        chat_history.append(HumanMessage(content=query))

        inputs = {
            "messages": chat_history,
            "plan": "",
            "logs": []
        }

        for output in app.stream(inputs):
            for key, value in output.items():

                if key == "planner" and "plan" in value:
                    print(f"\n[PLAN DZIAŁANIA]:\n{value['plan']}")

                if "logs" in value:
                    for log in value["logs"]:
                         print(f"[LOG]: {log}")

                if key == "tools":
                    for msg in value["messages"]:
                        print(f"[NARZĘDZIE]: {msg.content}")

                if key == "agent":
                    last_msg = value["messages"][-1]
                    if not last_msg.tool_calls:
                        print(f"\n[AGENT]: {last_msg.content}")

if __name__ == "__main__":
    run_chat()