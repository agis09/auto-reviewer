import google.generativeai as genai
import os
import subprocess
import logging
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
    if git_diff.stderr != b"":
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
    You are a highly skilled software engineer. Please review the provided code diff based on the following `git diff main..HEAD` results. 
    - Your review should identify areas that need correction, explaining what needs to be changed and why.
    - Include the following in your review:
    - **Interpretation:** How you understand the code.
    - **Reasoning:** Why the code is inappropriate or problematic.
    - **Suggestions:** Examples of how the code should be corrected.
    - Output your review results in the following JSONL (JSON Lines) format. Ensure each value is non-null and uses UTF-8 encoding:

    ```json
    {{“body”:“review comments”,“path”:“target filename”,“line”:“target line number (int)”,“side”:“whether comments are for deletions or additions (LEFT for comments on deleted sources, RIGHT for comments on added sources)”}}
    {{“body”:“review comments”,“path”:“target filename”,“line”:“target line number (int)”,“side”:“whether comments are for deletions or additions (LEFT for comments on deleted sources, RIGHT for comments on added sources)”}}
    ...
    ```
    Code diff:
    ```
    {git_diff.stdout}
    ```
    Please provide your review in the specified JSONL format. No additional text is required.
    """
    chat = model.start_chat()
    res = chat.send_message(content=content)

    return res.text


if __name__ == "__main__":
    load_dotenv(override=True)
    google_api_key = os.environ["GOOGLE_API_KEY"]
    logger = logging.getLogger(__name__)
    logging.basicConfig(encoding="utf-8", level=logging.DEBUG)
    res = get_review(google_api_key, "dev", "main", logger)
    logger.debug(res)
