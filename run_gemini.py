import google.generativeai as genai
import os
import subprocess
from dotenv import load_dotenv

load_dotenv(override=True)

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]
model = genai.GenerativeModel(
    "gemini-1.5-flash-latest", safety_settings=safety_settings
)


def get_review(commit_branch="dev", main_branch="main"):
    command = "git fetch origin main && git fetch origin dev"
    subprocess.run(command, shell=True, check=True)
    command = f"git diff origin/{main_branch}..{commit_branch}"
    git_diff = subprocess.run(command, shell=True, stdout=subprocess.PIPE, check=True)

    content = f"""
    You are a great software engineer. Please review my code based on the following `git diff main..HEAD` results and changed source code. 
    - The review should state what needs to be corrected and why for the areas that need to be corrected. 
    - Output the review results in the following jsonl (json line) format. 
    - Do not use "null" in each value
    - Do not use ASCII codes, use only 'utf-8'.
    ```json
    {{“body”:“review comments”,“path”:“target filename”,“line”:“target line number (int)”,“side”:“whether comments are for deletions or additions (LEFT for comments on deleted sources, RIGHT for comments on added sources)”}}
    {{“body”:“review comments”,“path”:“target filename”,“line”:“target line number (int)”,“side”:“whether comments are for deletions or additions (LEFT for comments on deleted sources, RIGHT for comments on added sources)”}}
    ...
    ```
    Results of git diff:
    ```
    {git_diff.stdout}
    ```
    No additional text is required. Only output the above json format.
    """
    chat = model.start_chat()
    res = chat.send_message(content=content)

    return res.text


if __name__ == "__main__":
    get_review()
