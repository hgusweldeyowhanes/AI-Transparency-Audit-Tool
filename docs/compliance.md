# Compliance notes

These guides describe **how the software helps you assemble evidence**. They are not legal advice and they do not certify conformity with any regulation.

## EU AI Act

The HTML pack (`GET /v1/reports/eu-ai-act?format=html`) maps engineering artifacts to common themes:

| Theme | What audit-ai stores |
|---|---|
| Art. 12 record-keeping | Timestamped prompt/completion, model id, flags |
| Art. 13 transparency | Model inventory, quality scores, failure taxonomy |
| Art. 14 human oversight | Search, drift incidents, prompt_version for rollback |

High-risk classification, DPIAs, and notified-body work remain yours.

## HIPAA

Self-host inside a covered-entity or BA environment. This MVP uses local SQLite and a static demo key. Do not send ePHI to a public managed service without a BAA. Detectors may flag SSN/email-like strings in completions; that is not a substitute for DLP or minimum-necessary review.

## SEC-style disclosure

The SEC pack is an internal evidence room: which models ran, how they were monitored, and that prompt changes are attributable. It is not a form, filing, or accountant letter.

## Retention

Free-tier default is **30 days** (`retention_days` in config). Raise it for regulated workloads.

`POST /v1/admin/retention/run` **soft-purges** events older than the window: prompt/completion are redacted in place, `purged_at` is set, and the original `event_hash` is kept. `GET /v1/integrity/verify` still checks the chain links and marks redacted rows separately (content digests no longer match after legal purge — by design).

## Hash chain

Every ingest seals `event_hash = sha256(prev_hash + canonical payload)`. Use `/v1/integrity/verify` before exporting evidence packs. Tip hash + tip index are returned for external anchoring (e.g. store the tip in a ticket or WORM store).

## Rubrics and groundedness

Events store `judge_rubric_version`, per-dimension `judge_scores`, and `groundedness_score`. Pass retrieved snippets as `sources` on ingest (or `metadata.sources`) so groundedness is scored against more than the raw prompt. Rubrics are versioned under `/v1/rubrics` so an auditor can see *which* rules produced a flag.

## Change management

Approved/deprecated **models** and **prompt versions** live in `/v1/registry/*`. Pair with `/v1/incidents` for severity, owner, RCA, and linked prompt versions when drift fires.
