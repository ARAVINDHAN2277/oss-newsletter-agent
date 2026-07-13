from typing import Dict
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
# pyrefly: ignore [missing-import]
from src.state import AgentState

class checkerOutput(BaseModel):
    is_verified: bool = Field(description="True if the draft is 100% accurate without hallucinations, False otherwise.")
    feedback: str = Field(description="A detailed explanation of what needs to be fixed. If is_verified is true, leave this empty.")

load_dotenv()

def technical_checker_node(state: AgentState) -> Dict:
    """
    This agents audits the current draft against raw structural git inputs.
    Toggles the is_verified flag and writes constuctive feedback if errors exist.
    """

    #git_data = state.get("raw_git_data", [])

    #if git_data and isinstance(git_data, list) and "error" in git_data[0]:
    #    print(" -- Checker Agent Status: FAIL (Ingestion node failed to pull real data.)")
    #    return {
    #        "is_verified": False,
    #       "feedback": f"The ingestion node encountered an error fetching this repository: {git_data[0]['error']}. Please do not write a newsletter based on failed data."
    #   }

    llm = init_chat_model(
        model="google_genai:gemini-2.5-flash",
        temperature=0.7
    )

    system_prompt = (
    "You are a strict technical QA reviewer. Cross-check the newsletter draft "
    "against the raw commit data.\n\n"
    "Flag as unverified if:\n"
    "1. The draft invents features or exaggerates a small change into a major one.\n"
    "2. Names, numbers, hashes, or descriptions don't match the raw commit data.\n"
    "3. There are placeholders like '[Insert Link Here]' or unfinished sections."
    )

    human_content = (
        f"RAW TRUTH DATA FROM GITHUB:\n{state['raw_git_data']}\n\n"
        f"CURRENT WRITER DRAFT: \n{state['draft']}"
    )

    structured_llm = llm.with_structured_output(checkerOutput)

    try:
        evaluation = structured_llm.invoke(
            [SystemMessage(content=system_prompt),
            HumanMessage(content=human_content)]
        )
        
        if isinstance(evaluation, checkerOutput):
            is_verified = evaluation.is_verified
            feedback = evaluation.feedback
        else:
            raise ValueError("LLM did not return a valid CheckerOutput object...")
    
    except Exception as e:
        print(f"-- Error parsing JSON validation format: {e}. Defaulting to revision loop...")
        is_verified = False
        feedback = "Structural compilation error. Ensure all newsletter entires map accurately to commit histories."

    if is_verified:
        print(" --Checker Agent Status: PASS ✅ (Draft is 100% accurate!)")
    else:
        print(f" --Checker Agent Status: FAIL ❌ (Issue identified: {feedback})")

    return {
        "is_verified": is_verified,
        "feedback": feedback if not is_verified else None
    }
            
