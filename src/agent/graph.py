from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from src.agent.nodes import create_planner_node, create_agent_node
from src.agent.state import AgentState
from src.tools.definitions import ALL_TOOLS

from src.core.config import config
from src.core.llm_factory import get_llm


def build_agent_graph():
    # 1. Pobierz skonfigurowany model (Factory)
    llm = get_llm(config.llm)

    # 2. Bind tools
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    # 3. Zbuduj graf
    workflow = StateGraph(AgentState)

    # Przekazujemy LLM do węzłów (Dependency Injection)
    workflow.add_node("planner", create_planner_node(llm))
    workflow.add_node("agent", create_agent_node(llm_with_tools))
    workflow.add_node("tools", ToolNode(ALL_TOOLS))

    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "agent")

    workflow.add_conditional_edges(
        "agent",
        tools_condition,
        {"tools": "tools", END: END}
    )

    workflow.add_edge("tools", "agent")

    return workflow.compile()
