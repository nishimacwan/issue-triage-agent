# GitHub Issue Triage Agent

A small AI agent that classifies open GitHub issues into categories using Google's Gemini API.

Built as a weekend project to learn the practical side of agent engineering: prompting, structured output, rate-limiting, evaluation.

## What it does

Given a GitHub repository, the agent:
1. Fetches the most recent open issues via the GitHub API
2. Filters out pull requests (GitHub returns PRs as issues by default)
3. Sends each issue's title and body to Gemini with a classification prompt
4. Asks Gemini to return structured JSON: {category, reasoning}
5. Prints a clean summary table

Categories: bug, feature, question, other.

## Stack

- Python 3.11+
- google-genai for Gemini API
- requests for the GitHub API
- python-dotenv for managing API keys

## Setup

1. Clone this repo:
   git clone git@github.com:nishimacwan/issue-triage-agent.git
   cd issue-triage-agent

2. Create a virtual environment and install dependencies:
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

3. Create a .env file at the project root with your API keys:
   GEMINI_API_KEY=your_gemini_key_here
   GITHUB_TOKEN=your_github_token_here

   Get a Gemini API key at https://aistudio.google.com
   Generate a GitHub token at https://github.com/settings/tokens with public_repo scope

4. Run the agent:
   python agent.py

## Example output

Fetching issues from langchain-ai/langchain...

Found 6 real issues (excluding pull requests).

Classifying issue #37452... (1/6)
Classifying issue #37442... (2/6)
...

#      Category   Title
37452  bug        Chroma.update_document() fails when Document...
37442  feature    feat(langchain): add fork_agent for spawning id...
37438  bug        grep_search: Python fallback skips valid UTF-8...
37426  feature    Add tool_call_id to on_tool_start event's data
37423  bug        HTMLSemanticPreservingSplitter processes malfor...
37421  bug        ChatOpenAI.with_structured_output(..., method="...

## What I learned

A few real things that came up while building this:

- Rate limiting is unavoidable, and there's more than one kind. Gemini's free tier has both a per-minute limit (5/min) and a per-day limit (20/day on gemini-flash-latest). The first crash hit the per-minute limit; the second crash, the next day, hit the per-day one. Added a 13-second sleep between calls to handle the per-minute limit. The per-day one needs either a paid tier or a switch to a model with a larger daily quota (gemini-2.0-flash). In a production system this would be proper retry-with-backoff plus model fallback.

- LLMs don't always return clean JSON. Despite the prompt explicitly asking for "only JSON, nothing else", Gemini sometimes wrapped responses in markdown code blocks. Added a small parser that strips those before calling json.loads(), and a try/except fallback in case the LLM returns something unparseable.

- The interesting work isn't the model call. The actual generate_content() call is one line. The work is around it: prompt design, output parsing, rate limit handling, evaluation. This is the part most "build an agent" tutorials skip.

- Evaluatio