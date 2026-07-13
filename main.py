import os
from dotenv import load_dotenv
from src.router import translate_query_to_repo
from src.graph import build_workflow

load_dotenv()

def main():
    print("--- Welcome to Agentic Newsletter Engine ---")

    user_prompt = input("\nEnter what you what to track (e.g., 'updates in langchain' or 'trending features of react'): ")
    if not user_prompt.strip():
        print("Query can't be empty. Exiting...")
        return
        
    print("\n Step 1: Translate user prompt to Github repo format...")
    try:
        repo_name = translate_query_to_repo(user_prompt)
        print(f"-> Target Repo Identified: {repo_name}")
    except Exception as e:
        print(f" Failed to translate query via LLM: {e}")
        return

    ### Compile our langgraph state machine workflow
    print("\n Step 2: Compiling multi-agent state graph architecture....")
    app = build_workflow()

    ### Initialize the starting state
    initial_state = {
        "user_query": user_prompt,
        "repo_name": repo_name,
        "raw_git_data": [],
        "draft": "",
        "feedback": None,
        "iterations": 0,
        "is_verified": False
    }

    ### Invoke the graph workflow
    print("\n Step 3: Triggering Agentic loop (Data Fetching -> Writing -> QA Verification)...")
    final_state = app.invoke(initial_state)

    ### Extract and save the validated output
    newsletter_output = final_state.get("draft")
    verified = final_state.get("is_verified")

    if newsletter_output:
        # Create a filename out of the repository name
        filename = f"{repo_name.replace('/','_').replace('.','_')}_newsletter.md"

        # Create and Route to Output folder
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True) 
        target_path = os.path.join(output_dir, filename)

        if not verified:
            warning = (
                " xxx -> This draft did not pass automated verfication against the raw commit data."
                "Review before publishing.\n\n"
            )
            newsletter_output = warning + newsletter_output
            print("\nWARNING: Draft was NOT verified. Saving with a warning...")
        else:
            print("\nSUCCESS: Draft has been verified against the raw commit data...")

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(newsletter_output)

        print("\n")
        print(f" SUCCESS: Your newletter has been created...")
        print(f"File saved as: {target_path}")

    else:
        print("\n Error: Could not compile verfied newsletter output")

if __name__ == "__main__":
    main()


