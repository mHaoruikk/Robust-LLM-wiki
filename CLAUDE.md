# Causal ML Knowledge Base

> Schema document — read at the start of every session together with `wiki/index.md`.
> Update after every major compile, ingest batch, or structural change.

## Scope

What this wiki covers:
- causal machine learning
- statistical inference
- decision making, reinforcement learning
- LLMs and Agents


## Operations

This wiki follows the llm-wiki skill's seven operations: `compile`, `ingest`, `query`, `lint`, `audit`, `brainstorm`, `build-index`.
Every operation appends an entry to `log/YYYYMMDD.md`.

## Naming conventions (PCMT ontology)

- **Problem pages** (`wiki/problems/<domain>/`): kebab-case noun phrases naming a research challenge.
  E.g., `long-term-treatment-effects.md`
- **Concept pages** (`wiki/concepts/<domain>/`): kebab-case noun phrases naming a domain object.
  E.g., `surrogate-index.md`, `average-treatment-effect.md`
- **Method pages** (`wiki/methods/<domain>/`): kebab-case noun phrases naming a procedure.
  E.g., `doubly-robust-estimation.md`
- **Theory pages** (`wiki/theory/<domain>/`): kebab-case noun phrases naming a mathematical tool.
  E.g., `efficient-influence-function.md`
- **Entity pages** (`wiki/entities/`): Proper names. E.g., "Susan Athey".
- **Summary pages** (`wiki/summaries/`): paper slug `{author}-{keyword}-{year}`.

**Domain subdirectories** are namespace prefixes within each PCMT type dir. Start with the most
relevant domain name (e.g., `causal-inference`, `statistics`, `machine-learning`). Create new
domains freely; no registration needed.

**⚠️ Agent must ask user permission before creating any new problem/concept/method/theory page.**

All pages require YAML frontmatter: `title`, `type`, `domain`, `created`, `updated`, `sources`, `tags`.

### Diagrams and formulas
- All structural diagrams are **mermaid**. No ASCII art.
- All formulas are **KaTeX** (inline `$...$` or block `$$...$$`).
- Method pages use mathematical equations, not mermaid flowcharts.

### Raw file policy
- Small text sources → copy into `raw/<subfolder>/`.
- PDFs ≤10 MB → run `scripts/ingest_pdf.py --pdf raw/incoming/<file>.pdf` → `raw/papers/<slug>.md`.
- Large binaries / PDFs >10 MB → create a pointer file at `raw/refs/<slug>.md` with `kind: ref`
  and `external_path` fields. Do not copy the binary.

## Open research questions
- How should we perform LLM routing with pairwise comparison data?
- How could we develop principled way to evaluate the LLM agents?
- How should we do a hierarchical PPI for longitudinal outcome prediction? 

## Research gaps
- No works has proposed policy learning with preference data under **partial identification / uncertainty**. Partial identification is a causality-related term, could be due to unmeasured confounding. Uncertainity is a more general way of stating that the pairwise win-rate is not point-estimable.
- Current PPI is not multi-step, it does **NOT** address the outcome estimation with **sequential actions**, i.e. the time-varying confounding problem which means the future time-varying covariates become a unseen confounder for the final outcome.

Sources to ingest:
- [ ] <author-keyword-year or URL> — why it's relevant

## Audit backlog

*(none — run `python3 scripts/audit_review.py <wiki-root> --open` to refresh)*

## General Behavioral guidelines

### 1. Think before Writing
**Do NOT assume. Do NOT hide confusion.** If you are uncertain about something, e.g. whether you should create a new domain, ask the user.

### 2. Think Deep. Extract the core novelty of the ingested papers
For each ingested papers, think deeply: **Does this paper propose something truly novel?** Is it a concept? Is it a general way to solve the scheme? How possible is this novel thing being applied to a general class of problems?

### 3. Brainstorm actively. 
You are **NOT** a coding slave. Instead, you are a **creative, thoughtful, active research-copilot** that helps the user doing his research. When you realize any exciting novel angles, new ideas, implicit connections e.t.c., tell the user.


## Notes for the LLM

- Language: english
- Tone: neutral, candid, academic
- Depth: Deep, theoretic
- Handling contradictions: state both, cite each, add to Open Research Questions.
