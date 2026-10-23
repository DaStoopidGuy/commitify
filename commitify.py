#!/usr/bin/env python3
import os
from google import genai
from dotenv import load_dotenv
import subprocess

load_dotenv()

MODEL = "gemma-4-26b-a4b-it"
APIKEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=APIKEY)

def get_staged_diff() -> str:
    """Captures the diff of currently staged git files."""
    result = subprocess.run(
        ["git", "diff", "--staged"],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout

def generate_commit_message(diff: str):
    try:
        prompt = (
                "TASK: Generate a git commit message for the diff below.\n"
                "RULES:\n"
                "1. Output ONLY the raw commit message text.\n"
                "2. Maximum 50 characters.\n"
                "3. Imperative mood (e.g., 'Add feature', 'Fix bug').\n"
                "4. NO thoughts, NO markdown quotes, NO extra chatter.\n\n"
                f"Diff:\n{diff}"
                )

        response = client.models.generate_content(
                model=MODEL,
                contents=prompt
                )
        
        # print("Response")
        # print("========")
        # print(response)
        if response.text != None:
            return response.text.strip()
        return ""
    except Exception as e:
        print(f"API Error: {e}")
        return ""

def commit_with_message(message: str):
    try:
        result = subprocess.run(
                ['git', 'commit', '-m', message],
                capture_output=True,
                text=True,
                check=True
                )
        print("Changes commited!")
    except subprocess.CalledProcessError as e:
        print("❌ Git commit failed!")
        print("Error: ", e.stderr.strip())

def main():
    # Get diff
    print("Reading code changes...")
    diff = get_staged_diff()
    if not diff.strip():
        print("❌ No staged changes found! Run 'git add <files>' first.")
        return
    
    # Generate commit message
    print("Generative commit message...")
    message = generate_commit_message(diff)
    print(f"Commit Message:\n> {message}\n")

    # Commit this shit
    confirm = input("Do you want to commit with this message? (y/n): ")
    if confirm == 'y':
        commit_with_message(message)
    else:
        print("Commit cancelled")

if __name__ == "__main__":
    main()
