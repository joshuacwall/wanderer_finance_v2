from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.chat_models import ChatLiteLLM
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode
from langchain import hub

def invoke_agent(prompt_name: str, user_variables: dict, system_variables: dict = None, tools: list = [], model: str = "groq/llama-3.3-70b-versatile", temperature: float = 0.1) -> dict:
    """
    Invokes a LangGraph agent with flexible system prompt handling.
    """

    llm = ChatLiteLLM(model=model, temperature=temperature)
    llm_with_tools = llm.bind_tools(tools)

    prompt = hub.pull(prompt_name)
    system_message_template = prompt.messages[0]
    human_message_template = prompt.messages[1]

    # Handle system prompt formatting based on system_variables
    if system_variables:
        system_message = system_message_template.format(**system_variables)
    else:
        system_message = system_message_template.format()

    human_message = human_message_template.format(**user_variables)

    sys_msg = SystemMessage(content=system_message.content)
    user_msg = HumanMessage(content=human_message.content)

    def assistant(state: MessagesState):
        messages = [sys_msg, user_msg] + state["messages"][1:]
        return {"messages": [llm_with_tools.invoke(messages)]}

    builder = StateGraph(MessagesState)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
    )
    builder.add_edge("tools", "assistant")
    graph = builder.compile()

    state = MessagesState(messages=[user_msg])
    result = graph.invoke(state)
    return result