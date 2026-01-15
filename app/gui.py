import streamlit as st
import sys
import os

# 1. Dodajemy katalog główny do ścieżki, aby widzieć moduł 'src'
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from langchain_core.messages import HumanMessage
from src.database import init_db
from src.agent import app  # Importujemy skompilowany graf agenta

# 2. Konfiguracja strony
st.set_page_config(
    page_title="Agent Podróży AI",
    page_icon="✈️",
    layout="wide"
)

# 3. Inicjalizacja bazy danych przy starcie
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state["db_initialized"] = True

# 4. Inicjalizacja historii czatu w sesji
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 5. UI - Pasek boczny (Mózg Agenta)
with st.sidebar:
    st.title("🧠 Mózg Agenta")
    st.markdown("---")

    # Placeholder na Plan
    st.subheader("📋 Plan Działania")
    plan_container = st.empty()
    plan_container.info("Czekam na zadanie...")

    st.markdown("---")

    # Placeholder na Logi (Debug)
    st.subheader("Rx Logi / Debug")
    logs_expander = st.expander("Pokaż logi systemowe", expanded=True)
    with logs_expander:
        logs_container = st.empty()
        logs_text = ""  # Zmienna do akumulacji logów

# 6. UI - Główny ekran (Czat)
st.title("✈️ Asystent Podróży")
st.caption("Zapytaj o hotele, koszty i waluty w miastach z bazy danych.")

# Wyświetlanie historii wiadomości
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

# 7. Logika Główna - Obsługa wejścia użytkownika
if user_input := st.chat_input("Gdzie chcesz jechać?"):
    # Dodaj wiadomość użytkownika do historii
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Przygotowanie wejścia dla LangGraph
    # Konwertujemy historię Streamlit na format LangChain (HumanMessage/AIMessage)
    # Dla uproszczenia w tym demo wysyłamy całą historię jako listę,
    # ale w tym miejscu Agent oczekuje listy obiektów BaseMessage.
    # Żeby nie komplikować, tworzymy nową listę wiadomości na podstawie historii sesji.
    langchain_messages = [HumanMessage(content=m["content"]) for m in st.session_state["messages"] if
                          m["role"] == "user"]

    # Można też przekazać po prostu ostatnią wiadomość i pozwolić LangGraph zarządzać historią wewnątrz,
    # ale w Twoim kodzie src/agent.py stan 'messages' jest typu 'add_messages', więc historia się kumuluje.
    # Bezpieczniej przekazać pełną historię z sesji Streamlit, jeśli chcemy mieć kontekst.
    inputs = {
        "messages": langchain_messages,
        "plan": "",
        "logs": []
    }

    # Uruchomienie Agenta (Streaming)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Spinner sygnalizujący myślenie
        with st.spinner("Agent analizuje zapytanie..."):

            # Pętla po zdarzeniach z grafu (Planner -> Agent -> Tools -> Agent)
            for output in app.stream(inputs):
                for node_name, value in output.items():

                    # A. Aktualizacja Planu (jeśli Planner skończył pracę)
                    if node_name == "planner" and "plan" in value:
                        plan_container.success(value["plan"])

                    # B. Aktualizacja Logów (jeśli przyszły nowe logi)
                    if "logs" in value:
                        for log in value["logs"]:
                            # Dodajemy nowy log do widoku
                            logs_text += f"🔹 {log}\n"
                            logs_container.text(logs_text)

                    # C. Wyłapywanie odpowiedzi końcowej
                    if node_name == "agent":
                        last_msg = value["messages"][-1]

                        # Sprawdzamy, czy to odpowiedź końcowa (nie wywołanie narzędzia)
                        if not last_msg.tool_calls:
                            content = last_msg.content

                            # Obsługa przypadku, gdy Gemini zwraca listę słowników (Twój przypadek z surowym JSON)
                            if isinstance(content, list) and len(content) > 0 and isinstance(content[0],
                                                                                             dict) and "text" in \
                                    content[0]:
                                full_response = content[0]["text"]
                            else:
                                full_response = str(content)

                            message_placeholder.markdown(full_response)

    # Zapisanie odpowiedzi asystenta w historii sesji
    if full_response:
        st.session_state["messages"].append({"role": "assistant", "content": full_response})
    else:
        # Fallback, gdyby coś poszło nie tak i response był pusty
        st.error("Nie udało się uzyskać odpowiedzi od agenta.")