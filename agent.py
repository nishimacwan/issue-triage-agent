"""
GitHub Issue Triage Agent

Fetches open issues from a GitHub repository and uses Gemini to classify
each one as: bug, feature, question, or other.
"""

from dotenv import load_dotenv
import os
import requests
from google import genai
import json
import time

load_dotenv()

# ---- Setup ----
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


# ---- Function 1: Fetch issues from a repo ----
def fetch_issues(repo_owner, repo_name, limit=10):
    """Fetch open issues from a GitHub repo. Excludes pull requests."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    params = {"state": "open", "per_page": limit}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Error fetching issues: {response.status_code}")
        return []

    all_items = response.json()

    # Filter out pull requests (GitHub returns them as "issues" too)
    issues = [item for item in all_items if "pull_request" not in item]

    return issues


# ---- Function 2: Ask Gemini to classify a single issue ----
def classify_issue(title, body):
    """Use Gemini to classify a GitHub issue into a category."""
    # Limit the body length so we don't send huge prompts
    body_excerpt = (body or "")[:1000]

    prompt = f"""You are a GitHub issue triager. Classify the following issue
into exactly one of these categories:

- bug: something is broken or not working as expected
- feature: a request for new functionality
- question: someone asking how to use something
- other: anything that doesn't fit above

Return ONLY a JSON object with two fields:
- "category": one of the four labels above
- "reasoning": a short sentence explaining why

Issue title: {title}

Issue body:
{body_excerpt}

Return only the JSON, nothing else."""

    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    # Gemini sometimes wraps JSON in markdown code blocks. Strip that.
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        result = json.loads(text)
        return result
    except json.JSONDecodeError:
        return {"category": "other", "reasoning": f"Could not parse: {text[:100]}"}


# ---- Main script ----
def main():
    repo_owner = "langchain-ai"
    repo_name = "langchain"

    print(f"Fetching issues from {repo_owner}/{repo_name}...\n")
    issues = fetch_issues(repo_owner, repo_name, limit=10)
    print(f"Found {len(issues)} real issues (excluding pull requests).\n")

    results = []
    for i, issue in enumerate(issues):
        print(f"Classifying issue #{issue['number']}... ({i+1}/{len(issues)})")
        classification = classify_issue(issue['title'], issue['body'])
        results.append({
            "number": issue['number'],
            "title": issue['title'],
            "category": classification['category'],
            "reasoning": classification['reasoning']
        })
        # Stay under Gemini's free-tier rate limit (5 requests/minute)
        if i < len(issues) - 1:  # don't sleep after the last one
            time.sleep(13)

    # Print results as a table
    print("\n" + "=" * 80)
    print(f"{'#':<6} {'Category':<10} {'Title':<50}")
    print("=" * 80)
    for r in results:
        title = r['title'][:47] + "..." if len(r['title']) > 50 else r['title']
        print(f"{r['number']:<6} {r['category']:<10} {title:<50}")
    print("=" * 80)


if __name__ == "__main__":
    main()