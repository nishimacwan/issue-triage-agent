from dotenv import load_dotenv
import os
import requests

load_dotenv()

# Read GitHub token from .env
github_token = os.getenv("GITHUB_TOKEN")

# Pick a repo to fetch issues from — try OpenAI's Python library
repo_owner = "openai"
repo_name = "openai-python"

# Build the API URL
url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"

# Set up the request headers — this is how we send our token
headers = {
    "Authorization": f"Bearer {github_token}",
    "Accept": "application/vnd.github+json"
}

# Ask GitHub for issues. state=open means we only want open ones.
# per_page=5 means we only want 5 results (keep it small while testing).
params = {"state": "open", "per_page": 5}

# Make the actual API call
response = requests.get(url, headers=headers, params=params)

# Print how the request went
print(f"Status code: {response.status_code}")

# Convert the response from JSON into a Python list
issues = response.json()

# Loop through each issue and print key info
print(f"\nFound {len(issues)} issues:\n")
for issue in issues:
    print(f"#{issue['number']}: {issue['title']}")
    print(f"  Author: {issue['user']['login']}")
    print(f"  URL: {issue['html_url']}")
    print()