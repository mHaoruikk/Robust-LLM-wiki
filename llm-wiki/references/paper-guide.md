# Paper Ingestion Guide

Rules for ingesting academic papers into the llm-wiki. Read alongside `references/ontology-guide.md`.

---

## Paper naming convention (slug)

Every paper gets a stable, human-readable slug used as its filename across the whole wiki.

**Format**: `{first-author-lastname}-{core-keyword(s)}-{year}`

**Rules:**
- All lowercase, hyphen-separated
- First author's last name only (no initials, no "et al")
- Core keyword = 1–3 most distinctive words from the title; skip stop words ("a", "the", "with", "on", "for", "of")
- Year = publication year; use ArXiv submission year for preprints
- Disambiguation: if two papers share the same slug, add the second author's last name or an extra keyword

**Examples:**

| Paper | Slug |
|-------|------|
| Athey, Chetty, Imbens, Kang (2019) "The Surrogate Index…" | `athey-surrogate-index-2019` |
| Vaswani et al. (2017) "Attention Is All You Need" | `vaswani-attention-2017` |
| Chernozhukov et al. (2018) "Double/Debiased Machine Learning…" | `chernozhukov-double-debiased-ml-2018` |
| Pearl (1995) "Causal diagrams for empirical research" | `pearl-causal-diagrams-1995` |
| Two papers by Chen, both 2020 on DML | `chen-dml-panel-2020` and `chen-dml-binary-2020` |

The slug extracted by the agent during pre-processing should be reviewed and corrected if needed before the ingest proceeds.

---

## Paper pre-processing (incoming markdown)

Convert the PDF to markdown yourself and place it under `raw/incoming/some-messy-name.md`.
When given the ingest command, the agent will:

1. Read the incoming markdown file
2. Extract metadata (title, authors, year, venue, domains, slug)
3. Create `raw/papers/<slug>.md` by copying the **entire incoming markdown body** into the new file and prepending a YAML front matter header
4. Delete the original file from `raw/incoming/`

This copy-and-rename is the **only** agent write allowed inside `raw/`. During this step, the full incoming paper content must be preserved in `raw/papers/<slug>.md`; do not clean, summarize, or rewrite the paper body. After `raw/papers/<slug>.md` is created, files under `raw/` are immutable and must not be edited in place.

Invocation forms:
- `"ingest all the incoming papers"` — process every `.md` file in `raw/incoming/`
- `"ingest paper <filename> in the incoming folder"` — process a specific file

**If the markdown looks garbled** (common with scanned PDFs or heavy multi-column layouts):
- Note it in the summary's "Sources" section
- For critical equations, transcribe them manually into the summary or theory page

---

## The ingest operation for papers

After pre-processing, the agent continues with `raw/papers/<slug>.md` automatically. You can also trigger the downstream steps directly: `"ingest raw/papers/<slug>.md"`.

The agent will work through these steps. **For each new PCMT page, it must propose and get your
approval before writing.**

### Step 1 — Read

Read `raw/papers/<slug>.md` in full. Then read `CLAUDE.md` and `wiki/index.md` to understand
what already exists.

### Step 2 — Summary page

Create `wiki/summaries/<slug>.md` using the paper summary template from `references/article-guide.md`.

The summary page is the map. It links outward to PCMT pages; it does not duplicate their content.
Key points:
- "Problem addressed" links to the problem page (create or identify one)
- "Novel concepts introduced" links to concept pages
- "Method proposed" — **use judgment**: if the paper's estimator is bespoke, describe it here
  and do not create a method page. Promote to `methods/` only per the rule in `ontology-guide.md`.
- "Theory / tools used" links to theory pages

### Step 3 — PCMT page decisions

For each item extracted from the paper, decide its fate using `references/ontology-guide.md`:

**For problems**: Check if an existing problem page already covers it. If yes, update
the "Approaches" section to add this paper. If no, propose a new problem page.

**For concepts**: Check if the concept exists in `wiki/concepts/`. If yes, update or extend
the existing page (adding the new paper to "Sources"). If no, propose a new concept page.

**For methods**: Apply the promotion rule. Start in the summary. Only propose a method page if
the procedure is reusable across papers or you are comparing alternatives.

**For theory**: Check if the theory tool exists in `wiki/theory/`. If yes, link; do not duplicate.
If no, propose a new theory page.

### Step 4 — Propose, then create

Present the user with a list of proposed changes before writing:

```
Proposed changes for ingest: athey-surrogate-index-2019

New pages (need approval):
  [1] problems/causal-inference/long-term-treatment-effects.md
      Type: problem · Reason: the paper's core challenge
  [2] concepts/causal-inference/surrogate-index.md
      Type: concept · Reason: novel quantity introduced by paper
  [3] concepts/causal-inference/surrogacy-assumption.md
      Type: concept · Reason: key assumption defined by paper

Existing pages to update:
  [4] theory/statistics/efficient-influence-function.md — add to "Methods that rely on this"
  [5] entities/Susan-Athey.md — add paper to "Papers / sources"

Summary page (always created):
  [6] summaries/athey-surrogate-index-2019.md

No new method page proposed: the paper's estimator is specific to the surrogate setting.
  → Will be described in the summary. Promote to methods/ if cited as a technique by other papers.

Approve all / select items to skip / cancel?
```

### Step 5 — Write approved pages

Write each approved new PCMT page using the templates in `references/article-guide.md`, then apply the planned updates to existing pages. Do not modify `raw/papers/<slug>.md` after pre-processing.

### Step 6 — Update bookkeeping

- Add the paper to `wiki/index.md` under "Summaries" and list new PCMT pages under their sections
- Append to `CLAUDE.md` papers registry:
  ```yaml
  - slug: athey-surrogate-index-2019
    title: "The Surrogate Index: Combining Short-Term Proxies..."
    authors: [Athey, Chetty, Imbens, Kang]
    venue: NBER Working Paper
    year: 2019
    domains: [causal-inference, statistics]
    status: ingested
  ```
- Log: `## [HH:MM] ingest | athey-surrogate-index-2019 — surrogate index for long-term effects (N pages touched)`

---

## Papers registry status values

| Status | Meaning |
|--------|---------|
| `incoming` | Markdown dropped in `raw/incoming/`, not yet ingested |
| `ingested` | `ingest` op complete; summary + PCMT stubs created |
| `compiled` | PCMT pages fully written and cross-linked; wiki/index.md updated |

---

## Scaling to 1000+ papers

With many papers, keep the wiki tractable:

- **One summary per paper** — always. The summary is cheap to write and provides the entry point.
- **PCMT pages are shared** — many papers contribute to the same problem/concept/theory page.
  These pages should grow richer over time, not multiply.
- **Prefer updating over creating** — before proposing a new concept page, search existing pages.
  It's better to add a "Papers that use this" section to an existing page than to create a near-duplicate.
- **Domain dirs keep namespaces clean** — `concepts/causal-inference/` and `concepts/machine-learning/`
  can both have a page called `unconfoundedness.md` if needed; the domain prefix disambiguates.
- **Run lint after every 10 papers** — `python3 scripts/lint_wiki.py <wiki-root>` to catch dead
  links and orphans before they accumulate.
