from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes.ingestion import github_ingestion_node
from src.nodes.writer import technical_writer_node
from src.nodes.checker import technical_checker_node

def route_decision(state: AgentState) -> str:
    """
    The conditional router. Evaluates state flags to determine
    if we should break the loop or cycle back for a rewrite.
    """

    if state.get("is_verified") == True:
        return "end"

    if state.get("iteration_count", 0) >= 3:
        print(" -- Safety threshold reached: Forcing compilation breakdown...")
        return "end"

    return "rewrite"


def check_ingestion_success(state: AgentState) -> str:
    """
    Evaluates if the ingestion node successfully fetched data.
    """

    raw_data = state.get("raw_git_data",[])
    if raw_data and "error" in raw_data[0]:
        print(" --stopping graph: Failed to fetch Git Data")
        return "end"
    return "continue"

def build_workflow():
    """
    Wires nodes together into a compilation state graph...
    """

    workflow = StateGraph(AgentState)   # type: ignore

    ### nodes
    workflow.add_node("fetch_git_data", github_ingestion_node)
    workflow.add_node("write_newsletter", technical_writer_node)
    workflow.add_node("check_newsletter", technical_checker_node)

    ### Starting node
    workflow.set_entry_point("fetch_git_data")

    ### Edges
    workflow.add_conditional_edges(
        "fetch_git_data",
        check_ingestion_success,
        {
            "continue": "write_newsletter",
            "end": END
        }
    )

    workflow.add_edge("write_newsletter", "check_newsletter")

    ### Looping edge
    workflow.add_conditional_edges(
        "check_newsletter",
        route_decision,
        {
            "rewrite": "write_newsletter",
            "end": END
        }
    )

    # Compile the graph architecture into an operational state machine
    return workflow.compile()
