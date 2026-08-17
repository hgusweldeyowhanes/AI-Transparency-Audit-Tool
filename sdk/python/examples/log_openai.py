"""Log a mock (or real) OpenAI-style call into a local audit-ai API.

Usage:
  python examples/log_openai.py
  OPENAI_API_KEY=sk-... python examples/log_openai.py
"""

from __future__ import annotations

import os
import sys

# Allow running without installing the package.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from audit_ai import AuditClient


def mock_complete(prompt):
    return {
        "model": "gpt-4o",
        "content": "Card declined in Austin; customer requests same-day replacement and fee waiver. "
        "Next step: verify identity, then route to the card-ops queue.",
        "prompt_tokens": 210,
        "completion_tokens": 48,
    }


def openai_complete(prompt):
    from openai import OpenAI

    client = OpenAI()
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Summarize bank support tickets faithfully. Never invent policy IDs."},
            {"role": "user", "content": prompt},
        ],
    )
    choice = resp.choices[0].message.content or ""
    usage = resp.usage
    return {
        "model": resp.model,
        "content": choice,
        "prompt_tokens": usage.prompt_tokens if usage else 0,
        "completion_tokens": usage.completion_tokens if usage else 0,
    }


def main():
    prompt = (
        "Summarize this customer support ticket:\n\n"
        "Ticket 8812: customer says their debit card was declined twice at a grocery store in Austin. "
        "They want a same-day replacement and a fee waiver."
    )
    audit = AuditClient()
    with audit.trace(
        model="gpt-4o",
        prompt=prompt,
        prompt_version="v1",
        tags=["customer-support", "example"],
        metadata={"source": "sdk-example"},
    ) as span:
        result = openai_complete(prompt) if os.environ.get("OPENAI_API_KEY") else mock_complete(prompt)
        span.log(
            model=result["model"],
            completion=result["content"],
            prompt_tokens=result["prompt_tokens"],
            completion_tokens=result["completion_tokens"],
        )
    print("Logged event. Open http://localhost:5173/app/events")


if __name__ == "__main__":
    main()
