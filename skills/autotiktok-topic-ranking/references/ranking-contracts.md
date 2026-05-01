# Ranking Contracts

This reference focuses on the ranking-owned contracts and fixture surface.

## Core Objects

Ranking currently depends on these shared schema drafts:

- `TopicCandidateSchema`
- `ScoringContextSchema`
- `FeatureVectorSchema`
- `ScoringProfileSchema`
- `TopicScoreSchema`
- `PredictionRunSchema`

## What Ranking Must Trust

Ranking should trust upstream discovery for:

- stable `topicFingerprint`
- evidence packaging
- `searchEvidence`
- `executionProfile`

Ranking should not re-invent those fields from scratch.

## What Ranking Produces

At minimum, ranking should produce:

- `featureVector`
- `scoreBreakdown`
- `scoreTotal`
- `priorityLevel`
- `recommendedUse`
- `scoreReason`
- `riskFlags`
- `nextAction`

## Optimizer-Facing Contract Subset

The optimizer does not consume the full ranking payload equally. The current integration contract depends directly on:

- `profileSelection`
- `candidateSource`
- `scores[*].topicId`
- `scores[*].topicFingerprint`
- `scores[*].priorityLevel`
- `scores[*].recommendedUse`
- `scores[*].scoreBreakdown.feasibility`
- `scores[*].rerankAdjustedScore`
- `scores[*].isRejected`
- `scores[*].rerankReasons`
- `predictionRun`
- `rankingSummary`
- `rerankDiagnostics`

During the `vNext preview` migration rehearsal, ranking now dual-writes that subset in two places:

- legacy top-level fields on `ranking-output.v1`
- canonical preview envelope at `optimizerHandoff`

The preview envelope carries:

- `optimizerHandoff.schemaVersion = ranking-optimizer-handoff.v2-preview`
- `optimizerHandoff.deprecatedTopLevelFields`
- `optimizerHandoff.deprecationPolicy`
- mirrored copies of `profileId`, `profileSelection`, `candidateSource`, `scores`, `predictionRun`, `rankingSummary`, and `rerankDiagnostics`

That lets module 2 start consuming `optimizerHandoff` without dropping replay support for the current top-level shape.

The deprecation policy makes the migration rule explicit:

- phase: `dual_write_preview`
- canonical surface: `optimizerHandoff`
- preview exact path still requires top-level mirrors
- preview compat path may reconstruct `optimizerHandoff` from legacy top-level fields
- next hard-fail target: `ranking-optimizer-contract.v2`

Validate that subset with:

```bash
python3 skills/autotiktok/scripts/validate_ranking_optimizer_contract.py
```

The same shared helper is now used by `skills/autotiktok-strategy-optimizer/scripts/daily_review_mock.py`,
so optimizer entrypoints fail fast when the ranking handoff contract is broken.

That helper now exposes an evolvable contract surface, not just a single version string:

- `rankingOptimizerContractId`
- `rankingOptimizerContractVersion`
- `rankingOptimizerContractValidationMode`
- `rankingOptimizerContractValidated`
- `rankingOptimizerSurfaceSource`
- `rankingOptimizerDeprecationPhase`
- `rankingOptimizerCanonicalSurface`
- `rankingOptimizerDeprecatedTopLevelFields`
- `rankingOptimizerNextHardFailContractVersion`

The current rehearsal gate for the next contract step is:

```bash
python3 skills/autotiktok/scripts/validate_ranking_optimizer_contract_rehearsal.py
```

That gate now defaults to `vNext-preview/exact`, which means:

- the committed ranking sample must carry the canonical `optimizerHandoff`
- `optimizerHandoff` must stay byte-for-byte mirrored with the legacy top-level fields
- module 2 can read the preview handoff surface directly instead of relying on legacy top-level fields

You can still rehearse legacy fallback behavior explicitly with:

```bash
python3 skills/autotiktok/scripts/validate_ranking_optimizer_contract_rehearsal.py \
  --validation-mode compat
```

## Fixture Inventory

Use the committed discovery artifact as the default ranking input surface for local development, and keep the shared candidates fixture only as a compatibility surface:

- direct discovery input:
  - [../../autotiktok-topic-discovery/fixtures/discovery-dry-run.sample.json](../../autotiktok-topic-discovery/fixtures/discovery-dry-run.sample.json)
- candidates:
  - [../../autotiktok/fixtures/topic-candidates.fixture.json](../../autotiktok/fixtures/topic-candidates.fixture.json)
- context:
  - [../../autotiktok/fixtures/scoring-context.fixture.json](../../autotiktok/fixtures/scoring-context.fixture.json)
- profiles:
  - [../../autotiktok/fixtures/scoring-profiles.fixture.json](../../autotiktok/fixtures/scoring-profiles.fixture.json)

## Freeze Checklist

Before changing a ranking contract, check:

1. Is the field ranking-owned or optimizer-owned?
2. Will the change break replay of old prediction runs?
3. Can the field remain deterministic?
4. Does the change belong in fixtures as well?

## Shared Schema Draft

For the full schema draft, read:

- [../../autotiktok/docs/module2-schema-draft.md](../../autotiktok/docs/module2-schema-draft.md)
