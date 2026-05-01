# Topic Candidate Contract

This reference focuses on the discovery-owned contract that ranking depends on.

## Required Top-Level Fields

Every candidate should provide:

- `schemaVersion`
- `topicId`
- `topicFingerprint`
- `topicTitle`
- `topicSummary`
- `topicType`
- `sourceType`
- `sourceRef`
- `keywords`
- `contentAngle`
- `recommendedMode`
- `expandability`
- `freshnessWindow`
- `searchEvidence`
- `executionProfile`
- `executionNotes`

## Why This Contract Matters

Discovery can move independently only if the `topicCandidate` contract is stable enough for ranking and optimization to build against mock or recorded fixtures.

The two most important nested objects are:

- `searchEvidence`
- `executionProfile`

These are required because ranking already treats search capture and feasibility as first-class dimensions.

## `searchEvidence` Checklist

Keep these fields stable:

- `seedQueries`
- `relatedQueries`
- `contentGapQueries`
- `searchIntentType`
- `searchPersistenceHint`

## `executionProfile` Checklist

Keep these fields stable:

- `recommendedFormats`
- `requiredAssets`
- `requiredCapabilities`
- `productionComplexity`
- `dependencyRisk`
- `fastTurnaround`

## Freeze Checklist

Before changing the candidate contract, answer:

1. Does the new field belong to discovery, or is ranking trying to infer too much upstream?
2. Does ranking or optimization already consume this field?
3. Can old fixtures still replay with the new contract?
4. Is the field truly structured, or is it hiding a freeform reasoning problem?

## Shared Fixture

Use the shared candidate fixture at:

- [../../autotiktok/fixtures/topic-candidates.fixture.json](../../autotiktok/fixtures/topic-candidates.fixture.json)

The bundled script for this skill validates that fixture against the current discovery-owned contract.
