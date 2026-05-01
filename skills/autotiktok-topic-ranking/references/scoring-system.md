# Scoring System

This reference narrows the shared plan to ranking-only decisions.

## Ranking Goal

Ranking is an explainable score and rerank layer. It should not behave like an unconstrained freeform idea generator.

## Score Object

Rank `topicCandidate`, not individual hot videos.

Video samples and raw search signals are evidence. The ranking unit is the packaged topic candidate.

## Eight Dimensions

The shared plan locks ranking to these dimensions:

1. `demand`
2. `competition`
3. `fit`
4. `rewrite`
5. `series`
6. `searchCapture`
7. `longform`
8. `feasibility`

## Weight Profiles

The plan currently uses three profiles:

- `growth-default`
- `scale-default`
- `search-priority-default`

Interpretation:

- growth mode emphasizes demand, fit, rewrite, and practical production
- scale mode raises the importance of series and longform expansion
- search-priority mode raises the importance of search capture

The current runner can auto-select a profile from `scoringContext.stageMode`:

- `growth -> growth-default`
- `scale -> scale-default`
- `search_priority -> search-priority-default`

The ranking matrix runner replays these three modes side by side so profile-sensitive behavior can be regression-checked without diffing full ranking payloads.

The hub-level expectation validator turns that matrix into a semantic gate, for example making sure the search-led candidate stays weaker in growth mode than in search-priority mode while the weak trend candidate remains rejected in every stage.

## Score Aggregation

Use weighted positive dimensions and subtract competition pressure.

That keeps the model oriented around:

- opportunity
- account fit
- repeatability
- production reality

instead of raw hype alone.

## Rerank Intent

Do not treat raw weighted score as the final answer.

Rerank should suppress:

- duplicates
- over-concentration in one topic type
- over-concentration in one content angle
- weak feasibility candidates crowding the top slots
- candidates that already fall below the profile's `rejectBelow` floor

## Shared Fixture Inputs

- [../../autotiktok/fixtures/topic-candidates.fixture.json](../../autotiktok/fixtures/topic-candidates.fixture.json)
- [../../autotiktok/fixtures/scoring-context.fixture.json](../../autotiktok/fixtures/scoring-context.fixture.json)
- [../../autotiktok/fixtures/scoring-context-matrix.fixture.json](../../autotiktok/fixtures/scoring-context-matrix.fixture.json)
- [../../autotiktok/fixtures/scoring-profiles.fixture.json](../../autotiktok/fixtures/scoring-profiles.fixture.json)
