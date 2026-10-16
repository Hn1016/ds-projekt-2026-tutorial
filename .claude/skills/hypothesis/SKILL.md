---
name: hypothesis
description: Test one hypothesis about the project's data and record it in docs/log.md as a Hypothesis entry, the same way every time.
argument-hint: <statement>
disable-model-invocation: true
---

# Hypothesis routine

The hypothesis: $ARGUMENTS

Run these steps in order. Where a step says wait, end your turn and wait for my answer. The rules in `CLAUDE.md` apply throughout.

## 1. Restate

Restate the hypothesis in one sentence, in the terms the project uses (places, years, dry weekdays, comparable, and so on, as in `docs/one-pager.md` and `docs/log.md`). If the statement is ambiguous, say what is unclear.

## 2. Ask for the expected result

Ask me for the expected result: a number, a threshold or a yes/no that a test can check. Wait for it. Never propose a value yourself. The expected result is mine and stays as I give it.

## 3. Propose the test

Propose the cheapest test that can break the hypothesis:

- which data it reads (prefer the tables in `data/derived`),
- what it counts or computes, and nothing beyond that,
- how the result could come out against the expectation.

Say what the test does not compute, for example "no change between the years". Wait for my go. If I change the test, use my version.

## 4. Run the test outside the pipeline

- Write the script in the session scratchpad, never in `src/`, `tests/` or a notebook.
- Read `data/derived` and `data/raw`; write nothing into `data/`.
- If the test needs a source that is not in `data/raw`, download it once into its own new folder in the scratchpad and do not add it to the pipeline.
- Compute only what the test needs.

## 5. Write the entries

**Branch.** When on `main`, create a branch `hypothesis-<slug>` first, where the slug is a few words of the hypothesis in lowercase with hyphens. On any other branch, write there.

**Hypothesis entry.** Append to `docs/log.md`, in the form of the existing Hypothesis entries:

```markdown
## Hypothesis · <today, YYYY-MM-DD> · <the hypothesis as restated>

**Expected:** <my expected result, as I gave it>

**Test:** <what was counted, on which data; what was not computed>

**Result:** <the numbers, against the expected value>

**Decision:**
```

Then report the Result to me in a few lines and ask me for the Decision. Wait. Write the Decision in my words, without rewording it.

**AI use entry.** After the Hypothesis entry, append a short entry in the form of the existing ones:

```markdown
## AI use · <today> · <the hypothesis, short>

**Delegated:** the test and writing the entry.

**Mine:** the hypothesis, the expected result and the decision.

**Checks passed:**
- <how the numbers were checked, for example a second route or a count by hand>
```

## 6. Stop

Stop after the two entries. Do not change `src/`, `tests/`, `CLAUDE.md`, `docs/one-pager.md` or the README, and do not commit; commit and push only when I say so. If the result suggests a change to the rules or the code, name it as an open point and leave it to me.
