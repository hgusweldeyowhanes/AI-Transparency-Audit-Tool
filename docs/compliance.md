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

Free-tier default is **30 days** (`retention_days` in config). Raise it for regulated workloads. Deletion jobs are not implemented in the MVP — treat the SQLite file as the retention boundary.
