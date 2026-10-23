#!/usr/bin/env python3
import os
from google import genai
from dotenv import load_dotenv
import subprocess

load_dotenv()

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
                "Given to you, is the git diff of the staged files, "
                "you must read the diff, and generate a concise, imperative commit message (max 50 characters) "
                "which accurately describes the changes made in the following git diff. "
                f"DO NOT include any extra text, just the commit message. GOOD BOY.\n\nDiff:\n{diff}"
            )

        response = client.models.generate_content(
                model="gemma-4-26b-a4b-it",
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
