import requests
import json
import os
import logging
from dotenv import load_dotenv
from run_gemini import get_review

logger = logging.getLogger(__name__)
logging.basicConfig(encoding="utf-8", level=logging.DEBUG)

load_dotenv(override=True)

github_api_token = os.environ["GITHUB_API_TOKEN"]


def create_pull_request_comment(
    repository, pull_number, github_api_token, body, commit_id, path, line, side
):

    pr_url = f"https://api.github.com/repos/{repository}/pulls/{pull_number}/comments"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {github_api_token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    data = {
        "body": body,
        "commit_id": commit_id,
        "path": path,
        "line": int(line),
        "side": side,
    }

    response = requests.post(pr_url, headers=headers, json=data)
    try:
        response.raise_for_status()
    except:
        logger.exception(response)

    return response.json()


def parse_comments(text):
    comments = []
    lines = text.splitlines()
    for line in lines:
        if line[0] == "{" and line[-1] == "}":
            try:
                comment = json.loads(line)
                if not all(key in comment for key in ["body", "path", "line", "side"]):
                    raise ValueError("Invalid format: Required key does not exist.")
                comments.append(comment)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid format: {line}")
    return comments


if __name__ == "__main__":
    raw_review = get_review("dev", "main")
    review_comments = parse_comments(raw_review)

    repository = "agis09/auto-reviewer"  # TODO: get from ci envs
    pull_number = "2"  # TODO: get from ci envs
    commit_id = "e10a08a212a1eee2f171b6a4058633b193d167b6"  # TODO: get from ci envs

    for comment in review_comments:

        try:
            comment_data = create_pull_request_comment(
                repository,
                pull_number,
                github_api_token,
                comment["body"],
                commit_id,
                comment["path"],
                comment["line"],
                comment["side"],
            )
            logger.info(comment_data)
        except:
            logger.exception(comment)
