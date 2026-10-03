# 0001. Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-10-03

## Context

An AI agent team built the platform quickly, and it is now being handed to a new CTO and their agents. Decisions that live only in chat transcripts or commit messages get lost at handover.

## Decision

Record every significant technical decision as an ADR in `docs/adr/`, in the same PR as the change.

## Consequences

Agents and new engineers can see why the system looks the way it does. Reversing a decision takes a new ADR, which makes the reversal explicit.
