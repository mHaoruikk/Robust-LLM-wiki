# Wiki Article Writing Guide

Guidelines for writing high-quality wiki articles. Read before compiling a new concept or entity page.

## ⚠️ Permission rule for new PCMT pages

Before **creating** any new `problems/`, `concepts/`, `methods/`, or `theory/` page, you **must**
confirm with the user. Show them:
- The proposed page title and type
- The domain subdirectory it would go into
- A one-line justification (what paper introduced/requires it)

Only create the page after the user approves. Updating an *existing* page does not require confirmation.
This gate applies during `ingest`, `compile`, and any later promotion pass. Do not pre-create empty stubs to "reserve" a page name before approval.

---

## Length targets

| Page type | Target length | Notes |
|-----------|--------------|-------|
| Problem page | 300–800 words | Frames the question; maps contributing papers |
| Concept page | 400–1200 words | Dense, no padding. **Hard ceiling: 1200.** |
| Method page | 400–1200 words | Key insight + formal steps + theory rationale |
| Theory page | 400–1200 words | Formal statement + proof sketch + intuition |
| Folder-split `index.md` | 150–400 words | Definition + map of sub-pages |
| Sub-page under a folder-split | 400–1200 words | Covers one aspect |
| Entity page | 200–500 words | Factual, link-heavy |
| Summary page (paper) | 200–400 words | PCMT-structured; not a rewrite |

Avoid padding. A 400-word article that's dense beats an 800-word article with filler.

## Divide and conquer — when to split

If a page **would** exceed ~1200 words, do not write it as a single file. Split it:

1. Create `wiki/<type>/<domain>/<topic>/`.
2. Write `wiki/<type>/<domain>/<topic>/index.md`:
   ```markdown
   ---
   title: <Topic>
   type: concept   # or method / theory / problem
   ...
   ---

   # <Topic>

   <One-sentence definition.>

   ## What it is

   <150–300 words of overview.>

   ## Sub-pages

   - [[<topic>/<aspect-1>]] — <one-line summary>
   - [[<topic>/<aspect-2>]] — <one-line summary>
   - ...

   ## Sources

   - [[summaries/...]]
   ```
3. Write each `<aspect-N>.md` as a focused 400–1200 word page.
4. Do NOT edit `wiki/index.md` — use the `build-index` command to regenerate the index hierarchy.

Signs a page needs to be split:
- Word count creeping past 1000.
- Three or more `##` sections, each with its own sub-sections.
- Multiple distinct sub-concepts mentioned but not explored because there's no room.

---

## Problem page structure

Problem pages frame a research question and act as a hub linking to all papers and methods that address it.

```markdown
---
title: <problem-slug>
type: problem
domain: <domain>
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [slug1, slug2]
tags: [tag1, tag2]
---

# <Problem Title>

<One-sentence statement of the research question.>

## Why it's hard

<What makes this problem non-trivial. Assumptions that are difficult to satisfy, obstacles, etc.>

## Key sub-problems

- <Sub-problem 1> — brief description
- <Sub-problem 2> — brief description

## Approaches

Papers and methods that address this problem:
- [[summaries/author-keyword-year]] — [[methods/<domain>/<method>]] — one-line description

## Related problems

- [[problems/<domain>/<related-problem>]] — how they relate or differ

## Open questions

<What remains unsolved. Drives future ingest and brainstorm sessions.>

## Sources

- [[summaries/source-slug-1]] — (year) one-line description
```

---

## Concept page structure

Concept pages define named objects, quantities, phenomena, and assumptions a research domain reasons about.

```markdown
---
title: <concept-slug>
type: concept
domain: <domain>
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [slug1, slug2]
tags: [tag1, tag2]
---

# <Concept Title>

<One-sentence definition or core idea.>

## What it is

<Explain the concept clearly. Assume the reader is technically literate but unfamiliar with this specific topic.>

## Formal definition

<KaTeX block if the concept has a precise mathematical definition.>

$$
\text{Surrogate Index}: S_i = g(Y_{i,1}, \ldots, Y_{i,T})
$$

## Key properties / tradeoffs

<Bullet list or short paragraphs.>

## Relationship to other concepts

- [[concepts/<domain>/<related>]] — how they relate
- [[concepts/<domain>/<contrast>]] — contrast or connection

## Papers that introduced or formalized this concept

- [[summaries/author-keyword-year]] — first introduced / key development

## Open questions

<What this wiki doesn't yet know about this concept.>

## Sources

- [[summaries/source-slug-1]] — (year) one-line description
```

---

## Method page structure

Method pages describe procedures, estimators, and algorithms. A method page must:
1. Convey the **key insight** — the high-level idea a reader should walk away with
2. Present each **essential step** with mathematical precision (equations, not pseudocode)
3. Explain **why** each theoretical tool is needed — not just that it's used, but what problem would arise without it

No mermaid flowcharts in method pages; the procedure should be expressed mathematically.

```markdown
---
title: <method-slug>
type: method
domain: <domain>
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [slug1, slug2]
tags: [tag1, tag2]
---

# <Method Title>

<One-sentence description of what this method does.>

## Key insight

<2–4 sentences: the high-level idea behind the method. What is the core intellectual move?
What would a researcher remember about this method after closing the paper? Avoid jargon where
possible; aim for the kind of summary you'd give in a seminar hallway.>

## Problem it solves

[[problems/<domain>/<problem-slug>]] — one-sentence connection.

## Procedure

Each essential step stated with mathematical precision:

**Step 1 — <name>**: <description>

$$
\hat{\mu}(x) = E[Y \mid X = x, D = d]
\quad \text{estimated on a held-out fold (cross-fitting)}
$$

**Step 2 — <name>**: <description>

$$
\hat{\psi}_i = \frac{D_i(Y_i - \hat{\mu}_1(X_i))}{e(X_i)}
             - \frac{(1-D_i)(Y_i - \hat{\mu}_0(X_i))}{1-e(X_i)}
             + \hat{\mu}_1(X_i) - \hat{\mu}_0(X_i)
$$

**Step 3 — <name>**: <description>

$$
\hat{\theta} = \frac{1}{n}\sum_{i=1}^n \hat{\psi}_i
$$

## Why these theoretical tools

For each theory page this method relies on, explain *why* that tool is necessary — what would
go wrong in the construction without it:

- [[theory/<domain>/<tool>]] — **Why needed**: <one or two sentences. E.g.: "Cross-fitting
  ensures the nuisance estimation error and the score are evaluated on independent samples,
  so their product is $o_p(n^{-1/2})$ even when each factor is only $o_p(n^{-1/4})$.">

- [[theory/<domain>/<tool2>]] — **Why needed**: <...>

## Key assumptions

<Bullet list of what must hold for the method to be valid.>

## Theoretical guarantees

<Formal statement of the main result.>

$$
\sqrt{n}(\hat{\theta} - \theta_0) \xrightarrow{d} \mathcal{N}(0, V^*)
$$

## Variants and extensions

- <Variant 1> — brief description

## Related methods

- [[methods/<domain>/<related>]] — how they compare

## Sources

- [[summaries/source-slug-1]] — (year) original paper
```

---

## Theory page structure

Theory pages cover mathematical foundations — theorems, bounds, inequalities, and proof
techniques used as tools across many methods. A good theory page gives both the rigorous
statement and the intuition behind it, making clear what the result *means* beyond the symbols.

```markdown
---
title: <theory-slug>
type: theory
domain: <domain>
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [slug1, slug2]
tags: [tag1, tag2]
---

# <Theory Title>

<One-sentence statement of what this result says or what this tool does.>

## Intuition

<2–4 sentences: the geometric, statistical, or information-theoretic interpretation.
What does the result *mean* beyond the formal symbols? What picture should a reader
carry in their head? Write this before the formal statement — it sets up the reader
to absorb the math.>

## Formal statement

<The theorem / definition / bound in precise mathematical form.>

**Theorem** (...). Under conditions $\mathcal{C}$,

$$
\sqrt{n}(\hat{\theta} - \theta_0) \xrightarrow{d} \mathcal{N}(0, V)
\quad \text{with} \quad V \geq V^* := E\bigl[\psi(Z;\theta_0)^2\bigr]^{-1}
$$

where $\psi(Z;\theta_0)$ is the **efficient influence function** and $V^*$ is the
semiparametric efficiency bound.

## Proof sketch / key ideas

<Outline of why the result holds — the essential steps without full formalism.>

- <Step 1>: ...
- <Step 2>: ...

## Conditions / assumptions

<What must hold for the result to apply.>

## How it's used in practice

<In what constructions or algorithms does this result appear? What does knowing this
theorem let you do that you couldn't otherwise? This is the bridge to method pages.>

## Methods that rely on this

- [[methods/<domain>/<method>]] — precisely how this result enters the construction

## Related theory

- [[theory/<domain>/<related>]] — connection (generalization, special case, dual)

## Sources

- [[summaries/source-slug-1]] — (year) original derivation or key reference
```

---

## Entity page structure

```markdown
---
title: <Name>
type: entity
entity_type: person | tool | dataset | organization
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [slug1]
tags: [tag1]
---

# <Name>

<One-sentence description.>

## Key contributions / features

<What this entity is known for in the context of this wiki's topic.>

## Related concepts

- [[concepts/<domain>/<concept>]] — connection

## Papers / sources

- [[summaries/source-slug]]
```

---

## Summary page structure (academic paper)

Paper summary pages are structured around the PCMT decomposition. They are not rewrites — they are maps.

```markdown
---
title: summaries/<slug>
type: summary
source_type: paper
paper_id: <slug>
authors: [LastName1, LastName2]
venue: <Journal / Conference / ArXiv>
year: YYYY
ingested: YYYY-MM-DD
domains: [domain1, domain2]
tags: [tag1, tag2]
---

# <Paper Title>

**Authors**: <Author1>, <Author2> et al. · <venue> · <year>

## Problem addressed

[[problems/<domain>/<problem-slug>]] — one-sentence framing of what question this paper answers.

## Core contribution

<2–3 sentences: what is new about this paper and why it matters. Be specific.>

## Novel concepts introduced

- [[concepts/<domain>/<concept-slug>]] — one-sentence definition of what it is
- *(if none, write "None — builds on existing concepts")*

## Method proposed

- [[methods/<domain>/<method-slug>]] — one-sentence description of what it does
- *(if none, write "None — theoretical / empirical result without a new estimator")*

## Theory / tools used

- [[theory/<domain>/<tool-slug>]] — one sentence on how it's applied in this paper
- [[theory/<domain>/<tool2-slug>]] — ...

## Key result

<Main theorem or empirical finding. Use KaTeX for formal statements.>

$$
\hat{\theta}_{SI} \text{ is semiparametrically efficient under the surrogacy assumption.}
$$

## Connections and prior work

- Builds on: [[summaries/<prior-slug>]] — brief description
- Contrast with: [[summaries/<competing-slug>]] — what differs

## Open questions

<What the paper leaves open. Drives future ingest and brainstorm.>

## Sources

- [[raw/papers/<slug>]] — converted markdown
- [[raw/refs/<slug>]] — PDF pointer
```

---

## Summary page structure (web article / gist / other)

```markdown
---
title: summaries/<slug>
type: summary
source_url: https://...
source_type: article | gist | video | podcast | ref
date: YYYY-MM-DD
ingested: YYYY-MM-DD
tags: [tag1]
---

# <Source Title>

**Source**: [<Author/Org>](<URL>) · <date>

## Key takeaways

- <Most important insight 1>
- <Most important insight 2>
- <Most important insight 3>

## Core claims

<2–4 sentences on the main argument or findings.>

## Notable quotes

> "<exact quote>" — <attribution>

## Concepts introduced / referenced

- [[concepts/<domain>/<concept>]]
- [[entities/<Name>]]
```

---

## Formulas — always KaTeX

Inline: `The efficient influence function is $\psi(Z;\theta) = \ell(Z;\theta) - E[\ell(Z;\theta)]$.`

Block:
```markdown
$$
\hat{\theta}_{DR} = \frac{1}{n}\sum_{i=1}^n \left[
  \frac{D_i(Y_i - \mu_1(X_i))}{e(X_i)} - \frac{(1-D_i)(Y_i - \mu_0(X_i))}{1-e(X_i)}
  + \mu_1(X_i) - \mu_0(X_i)
\right]
$$
```

Use mermaid only in concept and problem pages where a **structural or relational diagram**
genuinely helps (not in method pages).

## Wikilink rules

1. **Link first mention** of every entity or concept — don't wait for "a natural place".
2. **Link maximum twice per article** — don't over-link the same page.
3. **Use relative path form for PCMT pages**: `[[concepts/causal-inference/surrogate-index]]` not just `[[surrogate-index]]`.
4. **For folder-split pages**, link the index with an alias: `[[concepts/causal-inference/foo/index|Foo]]`.
5. **Backlink audit** — after writing a new article, grep existing articles for the new page's title and add incoming links.

## Handling contradictions between sources

When two sources contradict each other:

1. State both claims explicitly.
2. Note which source supports each claim.
3. Add to the article's "Open questions" section **and** the wiki's `CLAUDE.md` research questions.
4. Do NOT silently pick one — contradictions are valuable signal.

## Incorporating audit feedback

When processing an open audit that targets an article you're editing:

1. Locate the anchor using `anchor_before` / `anchor_text` / `anchor_after`.
2. Apply the correction in the smallest edit that fixes the issue.
3. Bump the `updated:` field in the frontmatter.
4. Add a line to the `# Resolution` section of the audit file explaining what changed.
5. Move the audit file to `audit/resolved/`.
6. Log the resolution under the current day's `log/YYYYMMDD.md`.
