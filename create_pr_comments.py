import requests
import json
import os
import logging
from dotenv import load_dotenv
from run_gemini import get_review

logger = logging.getLogger(__name__)
logging.basicConfig(encoding="utf-8", level=logging.DEBUG)

load_dotenv(override=True)


def create_pull_request_comment(
    repository, pair_number, github_api_token, body, commit_id, path, line, side
):

    pr_url = f"https://api.github.com/repos/{repository}/pulls/{pair_number}/comments"
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
    github_api_token = os.environ["GITHUB_API_TOKEN"]
    pr_number = os.environ["PULL_REQUEST_NUMBER"]
    commit_id = os.environ["COMMIT_ID"]
    pr_repository = os.environ["PR_REPO_NAME"]
    pr_branch_name = os.environ["PR_BRANCH_NAME"]
    base_branch_name = os.environ["BASE_BRANCH_NAME"]
    google_api_key = os.environ["GOOGLE_API_KEY"]

    raw_review = get_review(
        google_api_key, pr_branch_name, f"origin/{base_branch_name}", logger
    )
    review_comments = parse_comments(raw_review)

    for comment in review_comments:

        try:
            comment_data = create_pull_request_comment(
                pr_repository,
                pr_number,
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
