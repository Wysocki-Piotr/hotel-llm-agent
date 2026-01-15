import streamlit as st
import sys
import os

# Dodanie root do path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.messages import HumanMessage, AIMessage
from src.core.database import init_db
from src.agent.graph import build_agent_graph
from src.utils import setup_env, setup_logging

# 1. Konfiguracja strony
st.set_page_config(page_title="Agent Podróży PRO", layout="wide")

# 2. Inicjalizacja środowiska (logi, .env, baza)
if "env_initialized" not in st.session_state:
    setup_env()
    setup_logging()
    init_db()
    st.session_state["env_initialized"] = True

# 3. Budowa grafu (tylko raz)
if "agent_app" not in st.session_state:
    st.session_state["agent_app"] = build_agent_graph()

# 4. Historia wiadomości
if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("✈Asystent Podróży")

# Sidebar - Debug
with st.sidebar:
    st.header("Debug Info")
    plan_box = st.empty()
    logs_expander = st.expander("Logi systemowe", expanded=True)
    logs_box = logs_expander.empty()

# Wyświetlanie czatu
for msg in st.session_state["messages"]:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    st.chat_message(role).write(msg.content)

# Obsługa wejścia
if user_input := st.chat_input("Gdzie jedziemy?"):
    # Zapisz pytanie użytkownika
    st.session_state["messages"].append(HumanMessage(content=user_input))
    st.chat_message("user").write(user_input)

    inputs = {
        "messages": st.session_state["messages"],
        "plan": "",
        "logs": []
    }

    app = st.session_state["agent_app"]

    # Kontenery na odpowiedź asystenta
    with st.chat_message("assistant"):

        status_container = st.empty()
        message_placeholder = st.empty()  # Na ostateczną treść

        full_response = ""
        logs_text = ""

        with st.spinner("Analizuję..."):
            # Pętla po zdarzeniach z grafu
            for output in app.stream(inputs):
                for key, value in output.items():

                    # A. Planner
                    if key == "planner" and "plan" in value:
                        plan_box.info(f"📋 PLAN:\n{value['plan']}")

                    # B. Logi
                    if "logs" in value:
                        for log in value["logs"]:
                            logs_text += f"🔹 {log}\n"
                            logs_box.text(logs_text)

                    # C. Agent
                    if key == "agent":
                        last_msg = value["messages"][-1]

                        # Sprawdzamy czy to narzędzie, czy odpowiedź
                        if last_msg.tool_calls:
                            # Wyświetl status (zamiast JSONa)
                            tool_names = ", ".join([t["name"] for t in last_msg.tool_calls])
                            status_container.info(f"🛠️ Uruchamiam: {tool_names}...")
                        else:
                            # To jest odpowiedź końcowa
                            content = last_msg.content
                            # Zabezpieczenie przed listą
                            if isinstance(content, list) and len(content) > 0:
                                full_response = str(content[0])
                            else:
                                full_response = str(content)

                            message_placeholder.markdown(full_response)
                            status_container.empty()  # Czyścimy status po zakończeniu

    # Zapisanie odpowiedzi w historii
    if full_response:
        st.session_state["messages"].append(AIMessage(content=full_response))