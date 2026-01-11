import operator
from typing import Annotated, List, TypedDict, Union
from typing_extensions import TypedDict
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from src.tools import search_hotels, get_exchange_rate, calculate_trip_cost
from src.utils import setup_env, SYSTEM_PROMPT

setup_env() 

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

tools = [search_hotels, get_exchange_rate, calculate_trip_cost]
llm_with_tools = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    plan: str
    logs: Annotated[list[str], operator.add]

def planner_node(state: AgentState):
    """Analizuje zapytanie i tworzy plan działania."""
    print("--- PLANNER: TWORZENIE PLANU ---")
    
    user_query = state["messages"][-1].content

    planner_prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{query}")
    ])

    chain = planner_prompt | llm
    response = chain.invoke({"query": user_query})

    return {
        "plan": response.content,
        "logs": [f"Planner: Stworzono plan działania dla zapytania '{user_query}'."]
    }

def agent_node(state: AgentState):
    """Podejmuje decyzje o użyciu narzędzi na podstawie planu."""
    print("--- AGENT: PODEJMOWANIE DECYZJI ---")

    system_msg = SystemMessage(content=f"""
    Jesteś agentem podróżnym. Twoim celem jest wykonanie poniższego planu:
    
    PLAN:
    {state['plan']}
    
    ZASADY:
    1. Zawsze używaj dostępnych narzędzi, NIE zgaduj cen ani kursów.
    2. Po wykonaniu wszystkich kroków, udziel ostatecznej odpowiedzi.
    3. Loguj swoje działania.

    ZASADA WYBORU OFERTY (BARDZO WAŻNE):
    - Jeśli użytkownik prosił o 'najtańszy', wybierz ten z najniższą ceną.
    - Jeśli 'luksusowy', wybierz ten z najwyższą.
    - Jeśli 'optymalny', 'dobry' lub nie podano preferencji: ZIGNORUJ KOLEJNOŚĆ na liście. Przeanalizuj wszystkie ceny i wybierz ofertę ze ŚRODKA stawki (medianę). Nie bierz pierwszego z brzegu, chyba że jest to uzasadnione ceną.
    """)

    messages = [system_msg] + state["messages"]
    response = llm_with_tools.invoke(messages)

    log_entry = "Agent: Decyzja podjęta."
    if response.tool_calls:
        tool_names = [t['name'] for t in response.tool_calls]
        log_entry = f"Agent: Wybrano narzędzia: {', '.join(tool_names)}"
    else:
        log_entry = "Agent: Generowanie odpowiedzi końcowej."

    return {
        "messages": [response],
        "logs": [log_entry]
    }

workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "planner")

workflow.add_edge("planner", "agent")

workflow.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "tools", 
        END: END        
    }
)

workflow.add_edge("tools", "agent")

app = workflow.compile()