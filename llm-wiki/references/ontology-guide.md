# Ontology Guide — PCMT Decision Rules

This guide tells you exactly how to classify knowledge from an academic paper into the four
PCMT page types: **P**roblems, **C**oncepts, **M**ethods, **T**heory.

## The core question

When you encounter something new while ingesting a paper, ask:

> **What grammatical role does this play in research sentences?**

| If it is … | Then it is a … | Goes in |
|------------|---------------|---------|
| A research question — "How do we estimate/identify/predict X?" | **Problem** | `wiki/problems/<domain>/` |
| A named object, quantity, or assumption the domain reasons about | **Concept** | `wiki/concepts/<domain>/` |
| A reusable procedure applied to data — a method *family*, not a bespoke paper estimator | **Method** | `wiki/methods/<domain>/` |
| A theorem, bound, or proof technique used as a mathematical tool | **Theory** | `wiki/theory/<domain>/` |

---

## Detailed rules

### Problems

**What it is**: A research challenge that multiple papers collectively try to solve. Problems have a longer
lifespan than individual papers — they persist as open questions even as methods improve.

**Markers that something is a problem:**
- It is phrased as a question or challenge: "how to estimate X", "the difficulty of Y"
- Many papers cite it as the motivation for their work
- It has sub-problems and related problems
- Progress is measured (e.g., "we reduce the required sample size from N to n")

**Examples:**
- `long-term-treatment-effects` — how to estimate causal effects when outcomes are slow to observe
- `out-of-distribution-generalization` — why models fail when test distribution differs from train
- `high-dimensional-inference` — how to do valid inference when $p \gg n$

**Do NOT put here:**
- Named estimators or algorithms (those are methods)
- Mathematical tools like theorems (those are theory)

---

### Concepts

**What it is**: A named entity in the domain's vocabulary — a quantity, object, phenomenon, or assumption
that researchers define, reason about, and refer to by name. Concepts are the nouns of research language.

**Markers that something is a concept:**
- It has a formal or informal definition
- Researchers write sentences like "we estimate the X" or "assuming Y holds"
- It is introduced with a "we call this…" or "define X as…" construction
- It can be measured, estimated, or tested

**Examples:**
- `surrogate-index` — a scalar summary of short-term outcomes introduced by Athey et al.
- `average-treatment-effect` — $E[Y(1) - Y(0)]$, the fundamental causal quantity
- `surrogacy-assumption` — the condition that short-term outcomes mediate long-term effects
- `propensity-score` — $e(x) = P(D=1|X=x)$, the probability of treatment given covariates

**Distinction from methods**: A concept is *what you study or assume*; a method is *what you do*.
"Average treatment effect" is a concept (a quantity). "IPW estimation" is a method (a procedure to estimate it).

**Distinction from theory**: A concept names a domain object; a theorem names a mathematical truth.
"Semiparametric efficiency" is a concept. "The Cramér-Rao bound for semiparametric models" is theory.

---

### Methods

**What it is**: A reusable procedure, estimator family, or algorithm that is *applied to data* and has a
life **beyond a single paper**. Methods pages capture *method families*, not every paper's bespoke
construction.

**The key promotion rule:**

> Start a paper's specific estimator as a section inside the **summary page** or a note in the
> **concept page** it estimates. Promote it to `methods/` only when:
> - Another paper uses or cites it as a technique,
> - You want to compare it against alternative approaches, or
> - It becomes a recurring tool in your own research thinking.

`methods/` should contain **method families** (doubly-robust estimation, regularized regression,
cross-fitting), not every paper's ad-hoc variant.

**Markers that something is ready for its own method page:**
- It has a name used across multiple papers (e.g., "DML", "IPW", "LASSO")
- It is the answer to "how do you estimate X?" in a way that generalizes beyond one paper
- It has comparison-worthy variants and extensions
- It takes data as input and produces an estimate or decision as output

**Examples:**
- `doubly-robust-estimation` — combines outcome model and propensity score for robustness
- `cross-fitting` — sample-splitting technique that removes regularization bias; used in DML, AIPW, etc.
- `lasso-regression` — $\ell_1$-penalized linear regression for high-dimensional settings
- `inverse-probability-weighting` — reweighting by propensity score; foundational method family

**NOT yet a method page** (keep in summary until promoted):
- "The Athey et al. (2019) estimator for the surrogate index" — too paper-specific; stays in the summary
- "The specific cross-fitted version of IPW used in paper X" — stays as a note in the IPW method page

**Distinction from theory**: A method is a *procedure*; theory is a *mathematical result*.
"Doubly robust estimation" is a method. "The efficiency bound that DR achieves" is theory.
The method page should link to theory pages and explain *why* each theory is needed.

---

### Theory

**What it is**: A mathematical result, structure, or proof technique that is used as a *tool* to
construct, analyze, or justify methods. Theory is the machinery underlying methods — it explains
why a method works and what it achieves.

**Markers that something is theory:**
- It is a theorem, lemma, corollary, or formal definition
- It has assumptions and a conclusion with mathematical precision (quantifiers, convergence rates)
- It is used *across many methods and papers* — it is a reusable tool, not a one-off result
- It often appears in the "Theoretical analysis" or "Asymptotic properties" section of a paper

**Examples:**
- `efficient-influence-function` — the score that achieves the semiparametric efficiency bound
- `semiparametric-efficiency-bound` — the minimum asymptotic variance for a class of estimators
- `cross-fitting-bias-bound` — the product-bias argument showing cross-fitting yields $o_p(n^{-1/2})$ remainder
- `rademacher-complexity` — a measure of function class richness used to prove generalization bounds
- `delta-method` — technique for deriving asymptotic distributions of smooth functionals

**Distinction from methods**: Theory *justifies* methods; it is not itself applied to data.
"The efficient influence function" is a mathematical object (theory). "Using the EIF to construct
a one-step estimator" is a method.

**Paper-specific lemmas**: If a theorem is specific to one paper's setup and unlikely to be reused,
include it as a subsection in the summary page (under "Key result") rather than creating a theory page.
Promote to `theory/` when you see it appear in a second paper.

---

## Spanning multiple types — the primary role rule

Some things genuinely fit two categories. Use the **primary role** rule:

> Put the page in the category that reflects how the paper *primarily introduces* the thing.
> Add a "Related" link to the secondary role.

**Common ambiguous cases:**

| Thing | Primary role | Why | Secondary role |
|-------|-------------|-----|----------------|
| Propensity score | Concept | It is a quantity ($P(D=1|X=x)$) that is defined and assumed | Method: estimating it via logistic regression |
| LASSO | Method | It is primarily a procedure applied to data | Theory: the KKT conditions that characterize it |
| Efficient influence function | Theory | It is a mathematical object with formal properties | Method: using it to construct one-step estimators |
| Cross-fitting | Method | It is a specific reusable procedure | Theory: the bias bound that justifies it |

---

## Domain subdirectory assignment

The `<domain>/` prefix is a namespace — it prevents naming collisions and makes cross-domain
traversal legible. Assign a domain based on where the concept/method/theory *originates*,
not where it is applied.

| Thing | Domain | Reasoning |
|-------|--------|-----------|
| Surrogate index | `causal-inference` | Introduced in the causal inference literature |
| Efficient influence function | `statistics` | A semiparametric statistics result, used across many domains |
| Rademacher complexity | `machine-learning` | Originated in statistical learning theory |
| KKT conditions | `optimization` | Originate in constrained optimization |
| Average treatment effect | `causal-inference` | Core causal inference concept |

If something is genuinely cross-domain, put it in its origin domain and add cross-links from
the other domain's pages.

---

## Worked example — Athey et al. "The Surrogate Index" (2019)

Reading the paper:

| Element | Type | Action |
|---------|------|--------|
| Long-term effects slow to observe — how to speed up? | Problem | New page: `problems/causal-inference/long-term-treatment-effects.md` |
| The "surrogate index" $S_i = g(Y_{i,1},\ldots,Y_{i,T})$ | Concept | New page: `concepts/causal-inference/surrogate-index.md` |
| The surrogacy assumption | Concept | New page: `concepts/causal-inference/surrogacy-assumption.md` |
| The paper's specific efficient estimator | *(paper-specific)* | Section in `summaries/athey-surrogate-index-2019.md` only — do **not** create a method page yet |
| Cross-fitting | Method | New page if not exists: `methods/statistics/cross-fitting.md` (reusable family) |
| Efficient influence function | Theory | New page if not exists: `theory/statistics/efficient-influence-function.md` |
| Semiparametric efficiency bound | Theory | New page if not exists: `theory/statistics/semiparametric-efficiency-bound.md` |
| Susan Athey | Entity | New page: `entities/Susan-Athey.md` |
| The paper | Summary | New page: `summaries/athey-surrogate-index-2019.md` |

The paper's bespoke estimator stays in the summary. If a later paper by Imbens et al. extends
the surrogate index estimation approach to a new setting, *that* is when a method page
`methods/causal-inference/surrogate-index-estimation.md` earns its place.

---

## Edge cases

**"This theorem appears in only this paper — does it deserve its own theory page?"**
Only if it is a general result that could apply elsewhere. Paper-specific lemmas stay in the summary.
Promote when you see it reused.

**"This concept is barely mentioned — should I create a page?"**
Only create a page if the concept appears in multiple papers or is likely to recur.
Define it inline in the summary for now; promote when it's linked 3+ times.

**"The paper introduces a new method AND a new theory result."**
Create the theory page (reusable). For the method, follow the promotion rule: start it in the summary,
promote to `methods/` only when a second paper uses it.
