# Merge and Evidence

This reference narrows discovery down to the parts that most affect downstream ranking quality.

The current runnable policy config lives at:

- [../config/discovery-policy.v1.json](../config/discovery-policy.v1.json)

The reusable discovery implementation lives at:

- [../scripts/discovery_lib.py](../scripts/discovery_lib.py)

## Why Merge Matters

Discovery is not just extraction. It has to decide when multiple raw signals represent:

- the same topic opportunity
- the same topic with multiple useful angles
- genuinely different topics that should stay separate

If this is wrong, ranking quality collapses even when scoring logic is correct.

## Merge Rules

Use these default rules in the current scaffold:

- merge by stable `topicFingerprint`
- choose a canonical anchor signal by source-type priority, freshness priority, persistence priority, and evidence richness
- keep multiple `contentAngle` values instead of collapsing them into one title
- preserve every supporting `signalId` in `sourceRef`
- preserve every supporting `sourceType`

## When Not To Merge

Do not merge just because two signals share broad niche vocabulary.

Keep topics separate when:

- search intent is meaningfully different
- execution profile differs materially
- the angle implies a different content product
- persistence window differs enough to change ranking behavior

## Evidence Bundle Expectations

Each evidence bundle should make it easy for ranking or optimizer work to answer:

- what signals created this candidate
- which queries support search capture
- which formats or assets support feasibility
- which merge step produced the final bundle

The current scaffold now makes that explicit with:

- `sourceSnapshotRefs`
- `videoSampleIds`
- `mergeClassification`
- `searchEvidenceSummary`
- `executionEvidenceSummary`

## Packaging Expectations

At packaging time, discovery should emit:

- a stable `topicFingerprint`
- merged `keywords`
- merged `contentAngle`
- merged `searchEvidence`
- merged `executionProfile`
- explicit `sourceRef`

The current scaffold now also packages:

- `mergeClassification`
- `dedupeDecision`
- `executionNotes` with a stable packaging summary sentence

And the packaged nested objects now include:

- `searchEvidence.queryCount`
- `searchEvidence.supportingSignalCount`
- `searchEvidence.coverageLabel`
- `executionProfile.recommendedFormatCount`
- `executionProfile.requiredAssetCount`
- `executionProfile.requiredCapabilityCount`
- `executionProfile.complexityLabel`
- `executionProfile.packagingRisk`

## Discovery Dry-Run Output

The mock runner now emits five sections:

- `normalizedSignals`
- `topicAbstractions`
- `evidenceBundles`
- `mergeGroups`
- `candidates`

This keeps discovery artifacts inspectable before ranking starts.

The current scaffold also emits:

- `policyVersion`
- `normalizationRuleVersion`
- `anchorSignalId` in each evidence bundle
- `mergedSignalCount` in each merge group
- `mergeClassification` / `dedupeDecision` in merge-facing artifacts
- packaging-readiness summaries in `mergeGroups`
