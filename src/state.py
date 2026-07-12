from typing import TypedDict, List, Dict, Optional

class AgentState(TypedDict):
    """
    The shared state memory of the agentic workflow...
    """

    user_query: str
    repo_name: str
    raw_git_data: List[Dict]
    draft: str
    feedback: Optional[str]
    iteration_count: int
    is_verified: bool

