# Feature Score Rubric

This reference defines the first-pass deterministic rubric used by the ranking dry-run runner.

The current runnable config lives at:

- [../config/feature-rubric.v1.json](../config/feature-rubric.v1.json)

The reusable scoring implementation lives at:

- [../scripts/ranking_lib.py](../scripts/ranking_lib.py)

It is not the final production scorer. Its job is to make ranking logic:

- runnable
- inspectable
- replayable
- easy to challenge later

## Scoring Shape

Each dimension should emit:

- `score`
- `confidence`
- `evidenceRefs`
- `reason`

The score range remains `1..5`.

The current implementation uses:

- config-driven coefficients in `feature-rubric.v1.json`
- reusable helpers in `ranking_lib.py`
- a thin CLI wrapper in `dry_run_ranking.py`

## `demand`

Question:

- does the topic show evidence of real user demand?

Main signals:

- search evidence richness
- source count
- freshness
- evergreen or search persistence

Heuristic direction:

- more seed and related queries raises demand
- multiple supporting sources raises demand
- search or evergreen persistence raises demand
- daily-only trend spikes may still score high, but with less persistence confidence

## `competition`

Question:

- is the topic likely to be crowded or generic?

Main signals:

- trend-style freshness
- broad generic topic wording
- high source density around a mainstream trend

Heuristic direction:

- daily trend topics tend to get higher competition scores
- generic titles and dense source support can imply crowding
- narrow evergreen or practical search topics tend to score lower here

Note:

- competition is the one dimension later subtracted in total score

## `fit`

Question:

- does this topic fit the target account and its recent winners?

Main signals:

- niche keyword match
- historical topic fingerprint hints
- accepted formats vs recommended formats
- asset and execution overlap

Heuristic direction:

- niche alignment and historical wins should push fit up
- historical weak topics should reduce fit
- format mismatch should hold fit down

## `rewrite`

Question:

- is there room to turn this into original, useful packaging instead of copying?

Main signals:

- number of content angles
- angle diversity
- explanation or diagnosis framing
- whether the topic naturally supports before/after or critique packaging

Heuristic direction:

- more varied angles raise rewrite potential
- mistake diagnosis and before/after framing often raise rewrite potential

## `series`

Question:

- can this topic become a repeatable series instead of a single post?

Main signals:

- `expandability`
- `recommendedMode`
- evergreen persistence
- angle count

Heuristic direction:

- high expandability is the biggest driver
- `recommendedMode = series` should strongly help
- evergreen topics generally serialise better than short-lived trend reactions

## `searchCapture`

Question:

- can the topic capture explicit search intent?

Main signals:

- query counts in `searchEvidence`
- search intent type
- persistence hint
- content-gap support

Heuristic direction:

- richer query evidence raises search capture
- evergreen or weekly persistence is stronger than daily-only search demand
- content-gap evidence increases confidence that search is under-served

## `longform`

Question:

- can the topic expand into longer, deeper educational or case-based content?

Main signals:

- `expandability`
- topic type
- case/comparison framing
- evergreen persistence

Heuristic direction:

- evergreen and high-expandability topics should usually outrank trend reactions here
- case and comparison style search topics often translate better into longform than hype reactions

## `feasibility`

Question:

- can this account actually produce the topic quickly and reliably?

Main signals:

- production complexity
- fast turnaround
- accepted format match
- asset availability
- creator capability overlap

Heuristic direction:

- lower complexity and fast turnaround raise feasibility
- strong format overlap raises feasibility
- missing assets or higher dependency risk should lower feasibility

## Confidence Guidance

Use higher confidence when:

- the dimension uses direct structured evidence
- signals align instead of conflict

Use lower confidence when:

- the decision leans heavily on title wording
- evidence is sparse
- freshness suggests a noisy spike

## Current Rerank Parameters

The current config also owns two rerank penalties:

- duplicate `recommendedUse` penalty
- low-feasibility top-slot penalty

Those values now live in the same rubric config so ranking behavior can be tuned without rewriting the main dry-run script.
