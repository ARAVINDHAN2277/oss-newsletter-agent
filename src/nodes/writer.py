import os
from typing import Dict
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState 

load_dotenv()

def technical_writer_node(state: AgentState) -> Dict:
    """
    This agent processes raw git logs into a engaging, structured newsletter.
    If feedback exists, self-corrects the existing draft.
    """

    iterations = state.get("iterations", 0) + 1

    llm = init_chat_model(
        model="google_genai: gemini-2.5-flash",
        temperature=0.7
    )

    system_prompt = (
        "You are a developer relations engineer. Your goal is to write a highly engaging,"
        "professional markdown newsletter tracking the latest changes in an open-source codebase.\n\n"
        "Instructions:\n"
        "1. Group entries under: '🚀 Features', '🛠️ Fixes', '📝 Docs'.\n"
        "2. Base every line strictly on the given commit data (message + body). "
        "Never invent scope, impact, or severity not evidenced by the data.\n"
        "3. Use the 'body' field for extra context when present.\n"
        "4. One concise bullet per commit. Explain developer impact, not raw hashes/names.\n"
        "5. Keep the whole newsletter under 300 words."
    )

    if state.get("feedback") and state.get("draft"):
        human_content = (
            f"REPOSITORY: {state['repo_name']}\n"
            f"RAW TRUTH DATA FROM GITHUB: {state['raw_git_data']}\n\n"
            f"YOUR PREVIOUS DRAFT: {state['draft']}\n\n"
            f"CRITICAL EDITOR FEEDBACK YOU MUST FIX: {state['feedback']}\n\n"
            "Task: Rewrite your previous draft completely addressing the Editor Feedback."
            "Ensure everything matches the Raw Truth Date perfectly."
        )
    else:
        human_content = (
            f"REPOSITORY: {state['repo_name']}\n"
            f"RAW TRUTH DATA FROM GITHUB: {state['raw_git_data']}\n\n"
            "Task: Generate the first draft of the markdown newsletter using the provided data."
        ) 
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_content)
    ])

    print(f"-- Writer Agent processed version (Iteration {iterations}).")

    return {
        "draft": response.content,
        "iterations": iterations
    }
    