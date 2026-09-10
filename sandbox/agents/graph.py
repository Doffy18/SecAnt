from langgraph.graph import StateGraph, END , START
from sandbox.agents.nodes import AgentState
from sandbox.agents.nodes import (coder_node,sandbox_tool_node, validator_node, constitutional_node)
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


def should_continue(state: AgentState) -> str:
    """Conditional Edge Router: Checks Validator feedback to retry or complete."""
    feedback = state.get("feedback", {})
    is_successful = feedback.get("is_successful", False)
    iteration = state.get("iteration_count", 0)
    max_retries = state.get("max_retries", 3)

    if is_successful or iteration >= max_retries:
        return "constitutional_node"

    return "coder_node"

def secant_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node('coder_node', coder_node)
    graph.add_node('sandbox_tool_node', sandbox_tool_node)
    graph.add_node('validator_node', validator_node)
    graph.add_node('constitutional_node', constitutional_node)

    graph.set_entry_point('coder_node')
    graph.add_edge('coder_node', 'sandbox_tool_node')
    graph.add_edge('sandbox_tool_node', 'validator_node')

    graph.add_conditional_edges('validator_node', should_continue,{
        'coder_node': 'coder_node',
        'constitutional_node': 'constitutional_node'
    })
    graph.add_edge('constitutional_node', END)

    return graph.compile()