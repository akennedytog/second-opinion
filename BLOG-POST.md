# DRAFT — DO NOT POST

**Hold: this post describes a claim we made and then withdrew. It should only be published after
an independent reviewer has checked the null test, and only if we decide the credibility of
admitting the error outweighs the cost of having made it.**

---

# We shipped a validation that couldn't fail

Last night we published a small open-source tool for checking the arithmetic inside medical
meta-analyses, along with a number: **136 of 137 published estimates reproduced within 0.01.**

That number was wrong. Not slightly wrong — structurally meaningless. Here is what happened, because
the failure is more useful than the tool.

## The claim

A study released trial-level data for 6,173 trials across 46 Cochrane diagnostic reviews, with
reported pooled estimates per meta-analysis. The meta-analyses were anonymised: "Meta ID 1" through
"Meta ID 137". No names, no mapping to reviews.

We pooled every meta-analysis ourselves from the trial cells, then matched each published value to
the *nearest* value we had computed, within a tolerance of one percentage point, and counted the
matches.

99.3% of sensitivity values matched. 100% of specificity values matched.

That looked like excellent validation. It was arithmetic theatre.

## Why it couldn't fail

We had 137 published numbers and 437 computed numbers, all spread across the same range. If you drop
137 darts into a field where 437 targets are packed tightly, almost every dart lands near something.

We measured it. Replace the published values with random draws from our own computed values —
destroying any real correspondence — and rerun the match. The hit rate is **1.000**. Every time.

Our observed rate was *below* the null.

We then tried the obvious fix: match on sensitivity and specificity jointly, requiring a unique
assignment. That gave 50 of 137. The null distribution for that same procedure has a mean of 40.9
and a maximum of 53.

Still inside the noise.

## The uncomfortable part

The tool's front page said "PASS". It printed PASS because the test it ran — does a nearby value
exist — could not fail. We had built a validation whose only failure mode was a crash.

This is exactly the failure mode we started the project to criticise. The whole premise was that
people ship plausible numbers that nobody inspected. Then we shipped one.

## What we're doing about it

- The claims are withdrawn, with a correction notice in the repo that preserves the history.
- The nearest-match test is now in the repository as a test that runs and prints the null
  distribution, so anyone can see why the original number meant nothing.
- The validation status is now **BLOCKED**, not "passing". The build fails rather than lie.
- The one worked example we published — a trial whose cells looked wrong — we re-checked against the
  original paper. The paper reports accuracy as the average of three readers, so no single 2×2 table
  reproduces its published figures. Our example doesn't hold. It's withdrawn too.

## What survives

Very little, and that's the honest state:

- The released dataset's counts match the paper's own reported counts. That's a direct recount, not
  a matching exercise.
- A negative methodological result: if you cannot verify the mapping, you cannot verify the
  reproduction, and no amount of statistical machinery fixes that.
- A bound on the genre: in the papers we read, 96% of table rows contained no contingency cells at
  all. Modern reviews print percentages. A wrong percentage and a right percentage look identical
  without the primary document.

## The lesson I'd actually write down

If your validation can pass while the thing it validates is broken, it isn't a validation. Before
you report any agreement statistic, generate the null distribution for the same procedure. If your
observed value sits inside it, you have measured nothing.

---

*Code and correction notice: [repo]. The tool is not ready and this post is not a launch.*
