import google.generativeai as genai
import os
import subprocess
from dotenv import load_dotenv


def get_review(api_key, commit_branch, main_branch, logger):
    subprocess.run(
        f"git fetch origin {main_branch} && git fetch origin {commit_branch} && git checkout {commit_branch}",
        shell=True,
        check=True,
    )
    git_diff = subprocess.run(
        f"git diff origin/{main_branch}..origin/{commit_branch}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    logger.error(f"stderr:{git_diff.stderr}")

    genai.configure(api_key=api_key)
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    model = genai.GenerativeModel(
        "gemini-1.5-flash-latest", safety_settings=safety_settings
    )

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
