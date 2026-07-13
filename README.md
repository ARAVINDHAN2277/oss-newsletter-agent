# OSS Newsletter Agent

A small multi-agent system that watches a GitHub repo and writes you a changelog-style newsletter about its recent commits — except it doesn't just trust the first draft it writes. There's a second agent whose whole job is to fact-check the first one against the raw commit data before anything gets saved.

I built this to actually learn LangGraph properly, not just follow a tutorial and forget it a week later. Everything here is written by me, one node at a time, tested standalone before it ever touched the graph.

## What it actually does

You type something like `"recent updates in tailwindcss"`, and it:

1. Figures out the real GitHub `owner/repo` for what you asked (a small, fast LLM does this — no need for a big model on such a simple task)
2. Pulls the last 5 commits straight from the GitHub REST API
3. Writes a first draft newsletter from that data
4. Runs a second agent that cross-checks the draft against the raw commits — checking for invented features, exaggerated impact, wrong names/hashes, that kind of thing
5. If it fails the check, the writer gets the feedback and rewrites — up to 3 tries, then it gives up rather than loop forever
6. Saves the final draft to `output/`, and if it was never actually verified, it says so right in the file instead of pretending everything's fine

## Why two agents instead of one

The first version I sketched out was just one LLM call — "here's some commits, write me a newsletter." It worked, but there was nothing stopping it from turning a one-line typo fix into "a major overhaul." An LLM writing marketing-flavored copy from technical data will happily embellish if you let it.

So instead of trusting one pass, there's a writer and a checker in a loop — the checker's only job is to be annoying and literal about what's actually true. If it's not happy, it sends feedback back and the writer tries again. This is basically a reflection pattern — I didn't invent it, but building it myself (instead of just reading about it) is what actually made it click.

## Architecture

```
user query
   │
   ▼
router (small/fast model → owner/repo)
   │
   ▼
ingestion (GitHub REST API → cleaned commit list)
   │
   ├─ ingestion failed? → stop here, don't waste an LLM call
   │
   ▼
writer (drafts the newsletter)
   │
   ▼
checker (fact-checks draft against raw commits)
   │
   ├─ verified → done
   ├─ not verified, under 3 tries → back to writer with feedback
   └─ not verified, hit 3 tries → stop, save with a warning
```

Built with LangGraph as a state machine — every node reads from and writes to one shared state object, and a couple of conditional edges decide whether to loop, continue, or bail out early.

## Stack

- **LangGraph** for the state machine / agent loop
- **LangChain** for the model-calling layer
- **Gemini 2.5 Flash** for the writer and checker (needs actual reasoning about accuracy)
- **Groq (Llama 3.1 8B)** for the router (it's a trivial extraction task, no reason to pay for a bigger model there)
- **Pydantic** for structured outputs, so I'm never parsing raw JSON strings out of an LLM response by hand
- Plain `requests` for the GitHub API — no need for anything heavier

## Running it

```bash
git clone <your-repo-url>
cd oss-newsletter-agent
uv sync
```

You'll need a `.env` file with:
```
GOOGLE_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

Then:
```bash
python main.py
```

It'll ask what you want to track, do its thing, and drop a markdown file in `output/`.

## Things I'd flag if someone reviewed this

- **The router can hallucinate a repo that doesn't exist.** I fed it a vague query once ("recent satellite launches") and it confidently returned a repo path that 404'd on GitHub. The ingestion node catches that failure and the graph stops cleanly before wasting an LLM call on garbage data — but the router itself has no idea it guessed wrong. A `confidence` field on the router's output would be the next real improvement here, not a new feature, just tightening what's already there.
- **No auth on the GitHub API call** — works fine at this scale but you'll hit the 60 requests/hour unauthenticated limit if you hammer it. Adding a token is a five-minute fix, just didn't feel urgent for a demo project.
- **Unverified drafts still get saved**, just with a warning banner at the top of the file. I went back and forth on whether to refuse to save entirely instead — decided a flagged draft you can review is more useful than nothing, but I can see the argument either way.

## What I'd do differently at scale

If this needed to serve more than one person hitting "run" at a time, I'd move it off a CLI script into something async and queue-based, add real retry/backoff on the LLM calls instead of assuming they'll just work, and probably cache commit data instead of refetching on every run.

---

Built as a learning project to actually understand agentic workflows past the "watch a YouTube video" stage. Happy to walk through any part of the design if you're reading this before an interview with me.