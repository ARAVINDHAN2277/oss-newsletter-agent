import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage

class RouterOutput(BaseModel):
    repo_path: str = Field(description="The exact Github 'owner/repository' path. Example: 'langchain-ai/langchain'")


load_dotenv()

def translate_query_to_repo(user_prompt: str) -> str:
    """
    Uses and lightweight LLM model to extract the github 'owner/repository' path.
    """

    llm = init_chat_model(
        model="groq:llama-3.1-8b-instant",
        temperature=0.0
    )

    system_instructions = (
        "You are an expert systems router. Your only job is to scan a user's request "
        "and extract the official Github 'owner/repository' path for the framework they are asking about.\n\n"
        "Examples:\n"
        "- 'updates in langchain' -> langchain-ai/langchain\n"
        "- 'trending features of reactjs' -> facebook/react\n"
        "- 'tailwindcss latest' -> tailwindlabs/tailwindcss\n"
        "- 'nextjs updates' -> vercel/next.js\n\n"
        "Output only the raw string 'owner/repo'."
    )

    structured_llm = llm.with_structured_output(RouterOutput)
    response = structured_llm.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content=user_prompt)
    ])

    if isinstance(response, RouterOutput):
        return response.repo_path
    else :
        raise ValueError("LLM did not return a valid RouterOutput object...")

