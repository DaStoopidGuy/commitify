#!/usr/bin/env python3
import subprocess
import ollama

MODEL = "gemma4:e2b"

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
    if len(diff) > 4000:
        diff = diff[:4000] + "\n[Diff truncated...]"

    prompt = (
        "TASK: Generate a git commit message for the diff below.\n"
        "RULES:\n"
        "1. Output ONLY the raw commit message text.\n"
        "2. Maximum 50 characters.\n"
        "3. Imperative mood (e.g., 'Add feature', 'Fix bug').\n"
        "4. NO thoughts, NO markdown quotes, NO extra chatter.\n\n"
        f"Diff:\n{diff}"
    )

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        message = response['message']['content']
        return message.strip().strip('"').strip("'")
    except Exception as e:
        print(f"❌ Ollama Local Error: {e}")
        return ""

def commit_with_message(message: str):
    try:
        subprocess.run(
            ['git', 'commit', '-m', message],
            capture_output=True,
            text=True,
            check=True
        )
        print("🚀 Changes committed successfully!")
    except subprocess.CalledProcessError as e:
        print("❌ Git commit failed!")
        print("Error: ", e.stderr.strip())

def main():
    print("🔍 Reading code changes...")
    diff = get_staged_diff()
    if not diff.strip():
        print("❌ No staged changes found! Run 'git add <files>' first.")
        return
    
    print("🤖 Local Gemma 4 (E2B) is writing your commit message...")
    message = generate_commit_message(diff)
    
    if not message:
        print("❌ Failed to generate a commit message.")
        return

    print(f"\nCommit Message:\n> {message}\n")

    confirm = input("Do you want to commit with this message? (y/n): ").strip().lower()
    if confirm == 'y':
        commit_with_message(message)
    else:
        print("🛑 Commit cancelled")

if __name__ == "__main__":
    main()
