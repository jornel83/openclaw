# Ranking Delivery

This reference extracts the ranking-relevant parts of the shared development plan.

## Primary Owner Scope

Ranking maps to the shared plan's module-2 owner scope:

- feature builder
- score engine
- rerank
- explanation generation
- score output contracts

## Milestone Order

### Week 1

Freeze ranking-side contracts:

- `topicScore`
- `predictionRun`
- eval v1 assumptions that ranking must preserve

### Week 2

Ranking should be able to load:

- account profile shape
- scoring profile shape
- mock ranking fixtures

### Week 3

Ranking should review whether module-1 outputs already satisfy:

- feature extraction needs
- `searchEvidence` completeness
- `executionProfile` completeness

### Week 4

Ranking MVP should produce:

- scored candidates
- ordered outputs
- explanation fields
- reranked top results

## Healthy Integration Signals

- candidate fixtures parse cleanly
- weights are explicit and versioned
- rerank logic is separate from raw score aggregation
- score output stays explainable enough for later evaluation

## Main Risks

- ranking becomes too subjective
- profile drift breaks comparability
- rerank hides bugs in feature scoring
- contract changes block optimizer work

## Related Shared Docs

- Shared delivery plan: [../../autotiktok/docs/development-plan.md](../../autotiktok/docs/development-plan.md)
