import sys
import os

# Dodaj folder src do ścieżki
sys.path.append(os.path.join(os.getcwd(), "src"))

from langchain_core.messages import HumanMessage
from src.utils import setup_env, setup_logging
from src.agent.graph import build_agent_graph
from src.core.database import init_db

# 1. Konfiguracja
print("--- Inicjalizacja środowiska ---")
setup_env()
setup_logging()
init_db()

# 2. Budowa Agenta
print("--- Budowanie grafu agenta ---")
app = build_agent_graph()

# 3. Testowe zapytanie
query = "Ile zapłacę za 5 nocy dla 2 osób w mieście Rome? Wynik w USD."
print(f"\n--- Wysyłam zapytanie: '{query}' ---\n")

inputs = {
    "messages": [HumanMessage(content=query)],
    "plan": "",
    "logs": []
}

# 4. Uruchomienie w trybie STREAM (pokazuje kroki na bieżąco)
print("⏳ Czekam na Plannera (to może potrwać chwilę)...")

try:
    for event in app.stream(inputs):
        for key, value in event.items():
            
            # Jeśli zakończył się etap PLANNERA
            if key == "planner":
                print("\n✅ [PLANNER] Zakończył pracę.")
                print(f"   Plan: {value.get('plan')}")
                print("⏳ Teraz Agent analizuje plan...")

            # Jeśli zakończył się etap AGENTA (decyzja lub odpowiedź)
            elif key == "agent":
                last_msg = value["messages"][-1]
                if last_msg.tool_calls:
                    tool_names = [t['name'] for t in last_msg.tool_calls]
                    print(f"\n🛠️ [AGENT] Decyzja: Uruchamiam narzędzia -> {tool_names}")
                    for t in last_msg.tool_calls:
                        print(f"   👉 Funkcja: {t['name']}")
                        print(f"      Parametry: {t['args']}")
                else:
                    print(f"\n🏁 [AGENT] Odpowiedź końcowa gotowa!")
                    print("-" * 40)
                    print(last_msg.content)
                    print("-" * 40)

            # Jeśli zakończył się etap NARZĘDZI (Tools)
            elif key == "tools":
                print("\n⚙️ [TOOLS] Narzędzia wykonały pracę. Wyniki przekazane do Agenta.")
                print("⏳ Agent generuje odpowiedź końcową...")

except Exception as e:
    print(f"\n❌ Wystąpił błąd: {e}")