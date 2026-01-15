from langchain_core.messages import SystemMessage
from src.core.prompt_manager import prompt_manager
from src.agent.state import AgentState
from langchain_core.language_models import BaseChatModel


def create_planner_node(llm: BaseChatModel):
    def planner_node(state: AgentState):
        # 1. Pobieramy ostatnią wiadomość
        user_query = state["messages"][-1].content

        # 2. Formatujemy historię (zabezpieczenie przed brakiem historii)
        history_msgs = state["messages"][:-1]
        chat_history_str = ""

        # Bierzemy ostatnie 10 wiadomości
        for msg in history_msgs[-10:]:
            # Proste mapowanie ról na czytelny tekst
            role = "User" if msg.type == "human" else "Assistant"
            chat_history_str += f"{role}: {msg.content}\n"

        if not chat_history_str:
            chat_history_str = "Brak wcześniejszej historii."

        # 3. Ładowanie promptu
        prompt_template = prompt_manager.load_template("planner")

        # Dynamiczna lista miast
        cities_str = "Paris, London, Rome, Barcelona, New York, Tokyo, Berlin, Warsaw"

        chain = prompt_template | llm

        response = chain.invoke({
            "user_query": user_query,
            "cities_list": cities_str,
            "chat_history": chat_history_str
        })

        return {
            "plan": response.content,
            "logs": [f"Planner: Stworzono plan (kontekst historii: {len(history_msgs)} wiadomości)."]
        }

    return planner_node


def create_agent_node(llm_with_tools):
    def agent_node(state: AgentState):
        plan = state.get("plan", "Brak planu")

        template = prompt_manager.load_template("agent")

        # Dodajemy instrukcję systemową do listy wiadomości
        messages = [SystemMessage(content=template.format(plan=plan))] + state["messages"]

        response = llm_with_tools.invoke(messages)

        if response.tool_calls:
            log = f"Agent: Decyzja -> Używam narzędzi: {[t['name'] for t in response.tool_calls]}"
        else:
            log = "Agent: Generowanie odpowiedzi końcowej."

        return {"messages": [response], "logs": [log]}

    return agent_node