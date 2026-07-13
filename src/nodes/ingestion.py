import requests
from typing import Dict
# pyrefly: ignore [missing-import]
from src.state import AgentState

def github_ingestion_node(state: AgentState) -> Dict:
    """
    Fetches the latest commit history for a given GitHub repository
    """

    repo = state["repo_name"]
    url = f"https://api.github.com/repos/{repo}/commits"

    headers = {
        "Accept": "application/vnd.github+json"
    }

    try:
        response = requests.get(url, headers = headers)
        response.raise_for_status()
        commits = response.json()

        data = []

        for c in commits[:5]:
            raw_message = c["commit"]["message"]

            lines = [l for l in raw_message.split("\n") if l.strip()]

            title = lines[0]
            body = " ".join(lines[1:])[:100] if len(lines) > 1 else ""

            data.append({
                "sha": c["sha"][:7],
                "author": c["commit"]["author"]["name"],
                "message": title,
                "body": body,
                "date": c["commit"]["author"]["date"][:10]
            })

        print(f"-- Successful vectorless RAG extration : Fetched {len(data)} commits")
        return {"raw_git_data": data}

    except Exception as e:
        print(f"-- Error fetching commit data from {repo} : {e}")
        return {"raw_git_data": [{"error": f"Failed to fetch data: {str(e)}"}]}

