from langchain_core.messages import SystemMessage, AIMessage
from src.core.prompt_manager import prompt_manager
from src.agent.state import AgentState
from langchain_core.language_models import BaseChatModel
import re


def create_planner_node(llm: BaseChatModel):
    def planner_node(state: AgentState):
        # 1. Pobieramy ostatnią wiadomość
        user_query = state["messages"][-1].content

        # 2. Formatujemy historię (zabezpieczenie przed brakiem historii)
        history_msgs = state["messages"][:-1]
        chat_history_str = ""
        for msg in history_msgs[-10:]:
            role = "User" if msg.type == "human" else "Assistant"
            chat_history_str += f"{role}: {msg.content}\n"
        if not chat_history_str: chat_history_str = "Brak wcześniejszej historii."

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

        content = response.content.strip()
        
        mode = "chat"
        final_plan = content

        # 2. Szukamy wzorca "MODE: chat" lub "MODE: tools" (niewrażliwe na wielkość liter)
        mode_match = re.search(r"MODE:\s*(chat|tools)", content, re.IGNORECASE)
        
        if mode_match:
            # Znaleziono decyzję!
            found_mode = mode_match.group(1).lower()
            if "tools" in found_mode:
                mode = "tools"
            
            # 3. Czyścimy plan: Usuwamy linię MODE i wszystko przed nią (np. MYŚLENIE)
            # To regex, który wycina "wszystko aż do końca linii MODE"
            final_plan = re.sub(r".*?MODE:.*?\n", "", content, flags=re.DOTALL | re.IGNORECASE).strip()
            
            # Zabezpieczenie: Jeśli po wycięciu plan jest pusty (a tryb tools),
            # to znaczy, że model nie dał enterów. Spróbujmy po prostu usunąć sam tekst MODE.
            if not final_plan and mode == "tools":
                 final_plan = content.replace(mode_match.group(0), "").strip()

        return {
            "plan": final_plan,
            "mode": mode,  # Zapisujemy decyzję w stanie
            "logs": [f"Planner: Ustalono tryb -> {mode.upper()}"]
        }


    return planner_node


def create_agent_node(llm: BaseChatModel, llm_with_tools: BaseChatModel):
    def agent_node(state: AgentState):
        plan = state.get("plan", "")
        mode = state.get("mode", "chat")


        clean_message = re.sub(r"^(TREŚĆ:|SEKCJA \d+:|MODE:).*?", "", plan, flags=re.IGNORECASE).strip()
        
        # Jeśli czyszczenie usunęło wszystko (rzadkie), przywróć oryginał
        if not clean_message:
            clean_message = plan
        template = prompt_manager.load_template("agent")

        # Dodajemy instrukcję systemową do listy wiadomości
        messages = [SystemMessage(content=template.format(plan=plan))] + state["messages"]

        if mode == "chat":
            # 1. Tryb CHAT: Ładujemy prompt do rozmowy
            response = AIMessage(content=clean_message)
            log = "Agent: Przekazuję wiadomość Plannera bezpośrednio (bez użycia LLM)."
        else:
            # 2. Tryb TOOLS: Ładujemy prompt "Cichego Wykonawcy"
            template = prompt_manager.load_template("agent")
            messages = [SystemMessage(content=template.format(plan=plan))] + state["messages"]
            
            # Używamy modelu Z narzędziami
            response = llm_with_tools.invoke(messages)
            
            if response.tool_calls:
                tools = [t['name'] for t in response.tool_calls]
                log = f"Agent: Decyzja -> Używam narzędzi: {tools}"
            else:
                log = "Agent: Wykonano zadanie (bez użycia narzędzi)."
        return {"messages": [response], "logs": [log]}

    return agent_node