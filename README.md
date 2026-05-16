# GitHub Issue Triage Agent

A small AI agent that classifies open GitHub issues into categories using Google's Gemini API.

Built as a weekend project to learn the practical side of agent engineering: prompting, structured output, rate-limiting, evaluation.

## What it does

Given a GitHub repository, the agent:

1. Fetches the most recent open issues via the GitHub API
2. Filters out pull requests (GitHub returns PRs as issues by default)
3. Sends each issue's title and body to Gemini with a classification prompt
4. Asks Gemini to return structured JSON with a category and reasoning
5. Prints a clean summary table

Categories: bug, feature, question, other.

## Stack

- Python 3.11+
- google-genai (Gemini API)
- requests (GitHub API)
- python-dotenv (API key management)

## Setup

Clone the repo, create a virtual environment, install dependencies, add your API keys to a `.env` file, then run `python agent.py`.

You will need:
- A Gemini API key from https://aistudio.google.com
- A GitHub personal access token from https://github.com/settings/tokens (with `public_repo` scope)

See `example_output.txt` for sample output from a real run against the langchain-ai/langchain repository.

## What I learned

A few real things that came up while building this:

**Rate limiting is unavoidable, and there's more than one kind.** Gemini's free tier has both a per-minute limit (5/min) and a per-day limit (20/day on gemini-flash-latest). The first crash hit the per-minute limit; the second crash, the next day, hit the per-day one. Added a 13-second sleep between calls to handle the per-minute limit. The per-day one needs either a paid tier or a switch to a model with a larger daily quota (gemini-2.0-flash). In a production system this would be proper retry-with-backoff plus model fallback.

**LLMs don't always return clean JSON.** Despite the prompt explicitly asking for "only JSON, nothing else", Gemini sometimes wrapped responses in markdown code blocks. Added a small parser that strips those before calling json.loads(), and a try/except fallback in case the LLM returns something unparseable.

**The interesting work isn't the model call.** The actual generate_content() call is one line. The work is around it: prompt design, output parsing, rate limit handling, evaluation. This is the part most "build an agent" tutorials skip.

**Evaluation requires looking at outputs.** I read through the classifications by hand. They were mostly right but I noticed Gemini overuses "bug" for issues that are arguably configuration questions. A proper evaluation set would catch this.

## Next steps

- Add a `--repo` CLI argument instead of hardcoding the repo
- Add proper retry-with-backoff for rate limits using tenacity
- Build a small evaluation set with human-labeled issues and measure agreement rate
- Try the same prompt with a different model and compare outputs

## Why I built this

I was preparing for an internship application that asked for experience with AI agents and rapid prototyping. This felt like the canonical "boring task worth automating" — exactly the kind of thing agentic AI should be good at. Building it taught me more about the practical side of LLM engineering than reading another paper would have.