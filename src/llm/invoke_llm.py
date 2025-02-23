from langchain_community.chat_models import ChatLiteLLM
from langchain_core.messages import HumanMessage, SystemMessage

def chat(system_prompt, human_prompt, model, temperature=0.7):

    chat = ChatLiteLLM(model=model, temperature=temperature)
    
    prompt = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ]

    response = chat.invoke(prompt)

    return response
