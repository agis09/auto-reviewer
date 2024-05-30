import google.generativeai as genai
import os
import subprocess
from dotenv import load_dotenv

load_dotenv(override=True)

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash-latest")


def start_chat(content):
    chat = model.start_chat()
    response = chat.send_message(content=content)
    return response


command = "git fetch origin main && git fetch origin dev"
subprocess.run(command, shell=True, check=True)
command = "git diff main..dev"
git_diff = subprocess.run(command, shell=True, stdout=subprocess.PIPE, check=True)

content = f"""
You are a great software engineer. Please review my code based on the following `git diff main..HEAD` results and changed source code. The review should state what needs to be corrected and why for the areas that need to be corrected. Then, please output the review results in the following json format
```json
{{“body”: “review comments”, “path”: “target filename”, “line”: “target line number”, “side”: “whether comments are for deletions or additions (LEFT for comments on deleted sources, RIGHT for comments on added sources)”}},
{{“body”: “review comments”, “path”: “target filename”, “line”: “target line number”, “side”: “whether comments are for deletions or additions (LEFT for comments on deleted sources, RIGHT for comments on added sources)”}},
...
```
Results of git diff:
```
{git_diff.stdout}
```
No additional text is required. Only output the above json format.
"""
res = start_chat(content)
print(res.text)
