# Video Sample Contract

This reference defines the current collector-facing video sample contract for discovery.

## Purpose

This contract exists to keep `collector_public_tiktok` output aligned with the discovery ingest seam.

It should be used when:

- a collector needs to emit sampled public TikTok videos
- discovery needs stable video evidence objects
- the team wants one shared field contract before the real collector is wired in

## Scope

This contract covers the `videoSamples` artifact that discovery consumes.

It does **not** cover:

- `topicId`
- `topicFingerprint`
- `topicTitle`
- `topicSummary`
- `keywords`
- `contentAngles`
- `recommendedMode`
- `recommendedFormats`
- `requiredAssets`
- `requiredCapabilities`
- `productionComplexity`
- `executionNotes`

Those fields belong to discovery abstraction and packaging, not to the collector.

## Current Source Of Truth

The current committed sample is:

- [../fixtures/video-samples.sample.json](../fixtures/video-samples.sample.json)

The higher-level storage guidance in the shared technical plan is:

- [../../autotiktok/docs/technical-plan.md](../../autotiktok/docs/technical-plan.md)

## Envelope Shape

The top-level artifact should look like this:

```json
{
  "schemaVersion": "discovery-video-samples.v1",
  "snapshotId": "snap.public-video.us.2026-04-20",
  "market": "US",
  "language": "en",
  "capturedAt": "2026-04-20T05:12:00Z",
  "videoSamples": []
}
```

Top-level fields:

| Field           | Type            | Required | Notes                                                             |
| --------------- | --------------- | -------- | ----------------------------------------------------------------- |
| `schemaVersion` | `string`        | yes      | Use `discovery-video-samples.v1` for the canonical runtime shape. |
| `snapshotId`    | `string`        | yes      | Discovery-level snapshot id for the full artifact.                |
| `market`        | `string`        | yes      | Market like `US`.                                                 |
| `language`      | `string`        | yes      | Language like `en`.                                               |
| `capturedAt`    | `string`        | yes      | ISO 8601 timestamp for artifact capture time.                     |
| `videoSamples`  | `array<object>` | yes      | The collected video sample rows.                                  |

## Required Fields Per Video

Each `videoSamples[*]` item should contain at least:

| Field              | Type            | Required | Notes                                                                          |
| ------------------ | --------------- | -------- | ------------------------------------------------------------------------------ |
| `videoSampleId`    | `string`        | yes      | Stable discovery-facing id. Prefer deterministic generation.                   |
| `sourceSnapshotId` | `string`        | yes      | Must point to a `sourceSnapshots[*].sourceSnapshotId`.                         |
| `publishedAt`      | `string`        | yes      | ISO 8601 publish timestamp.                                                    |
| `title`            | `string`        | yes      | Video title. Empty string is acceptable only when the platform gives no title. |
| `desc`             | `string`        | yes      | Video description text. Empty string is acceptable.                            |
| `hashtags`         | `array<string>` | yes      | Ordered hashtag list. Use an empty list when absent.                           |
| `authorId`         | `string`        | yes      | Stable author id from the source.                                              |
| `metrics.views`    | `number`        | yes      | View count at capture time.                                                    |
| `metrics.likes`    | `number`        | yes      | Like count at capture time.                                                    |
| `metrics.shares`   | `number`        | yes      | Share count at capture time.                                                   |

Minimal item example:

```json
{
  "videoSampleId": "tt:749123456789",
  "sourceSnapshotId": "snap.public-video.us.2026-04-20",
  "publishedAt": "2026-04-20T03:40:00Z",
  "title": "Wired earbuds outfit check is back",
  "desc": "Street-style clip showing why wired earbuds became a nostalgia accessory again.",
  "hashtags": ["wiredearbuds", "nostalgia"],
  "authorId": "7123456789",
  "metrics": {
    "views": 182000,
    "likes": 13200,
    "shares": 740
  }
}
```

## Recommended Optional Fields

These are not currently hard-required by discovery, but they are recommended now so the collector does not need a later contract expansion for obvious video facts.

| Field               | Type      | Notes                                                                                   |
| ------------------- | --------- | --------------------------------------------------------------------------------------- |
| `platformVideoId`   | `string`  | Raw TikTok video id.                                                                    |
| `authorHandle`      | `string`  | Creator handle.                                                                         |
| `authorDisplayName` | `string`  | Creator display name.                                                                   |
| `durationSec`       | `number`  | Video duration in seconds.                                                              |
| `coverUrl`          | `string`  | Cover image URL.                                                                        |
| `shareUrl`          | `string`  | Canonical public video URL.                                                             |
| `metrics.comments`  | `number`  | Comment count.                                                                          |
| `metrics.favorites` | `number`  | Favorite count if available.                                                            |
| `metrics.bookmarks` | `number`  | Bookmark/save count if available.                                                       |
| `audio.audioId`     | `string`  | Audio id.                                                                               |
| `audio.title`       | `string`  | Audio title.                                                                            |
| `audio.isOriginal`  | `boolean` | Whether the audio is original.                                                          |
| `region`            | `string`  | Region code if the collector provides it.                                               |
| `rawMeta`           | `object`  | Collector-specific raw fields that should not pollute the canonical top-level contract. |

## Naming Guidance

Use two ids when possible:

- `videoSampleId`: discovery-facing stable id
- `platformVideoId`: upstream TikTok-native id

Recommended pattern:

```json
{
  "videoSampleId": "tt:749123456789",
  "platformVideoId": "749123456789"
}
```

If the team wants to keep only one id early on, it is acceptable to set:

- `videoSampleId == platformVideoId`

as long as the choice is consistent everywhere.

## Mapping To Storage Layer

The shared technical plan currently describes storage-oriented fields like:

- `video_id`
- `snapshot_id`
- `hashtags_json`
- `author_id`
- `published_at`
- `metrics_json`

Recommended mapping:

| Storage Layer   | Discovery Artifact                   |
| --------------- | ------------------------------------ |
| `video_id`      | `videoSampleId` or `platformVideoId` |
| `snapshot_id`   | `sourceSnapshotId`                   |
| `title`         | `title`                              |
| `desc`          | `desc`                               |
| `hashtags_json` | `hashtags`                           |
| `author_id`     | `authorId`                           |
| `published_at`  | `publishedAt`                        |
| `metrics_json`  | `metrics`                            |

Recommended rule:

- keep `snake_case` in storage if that is what the storage layer already uses
- keep `camelCase` in discovery artifacts
- do the translation in one adapter layer

## Boundary Rule

Collector output should contain **video facts**.

Discovery should derive **topic semantics**.

That means a collector should emit things like:

- publish time
- author id
- hashtags
- metrics
- duration
- audio

It should not emit:

- inferred topic abstractions
- candidate packaging hints
- execution profile recommendations
- ranking or optimization metadata

## Full Suggested Example

```json
{
  "schemaVersion": "discovery-video-samples.v1",
  "snapshotId": "snap.public-video.us.2026-04-20",
  "market": "US",
  "language": "en",
  "capturedAt": "2026-04-20T05:12:00Z",
  "videoSamples": [
    {
      "videoSampleId": "tt:749123456789",
      "platformVideoId": "749123456789",
      "sourceSnapshotId": "snap.public-video.us.2026-04-20",
      "publishedAt": "2026-04-20T03:40:00Z",
      "title": "Wired earbuds outfit check is back",
      "desc": "Street-style clip showing why wired earbuds became a nostalgia accessory again.",
      "hashtags": ["wiredearbuds", "nostalgia"],
      "authorId": "7123456789",
      "authorHandle": "creator_demo",
      "authorDisplayName": "Creator Demo",
      "durationSec": 19,
      "coverUrl": "https://example.com/cover.jpg",
      "shareUrl": "https://www.tiktok.com/@creator_demo/video/749123456789",
      "metrics": {
        "views": 182000,
        "likes": 13200,
        "shares": 740,
        "comments": 412
      },
      "audio": {
        "audioId": "aud:998877",
        "title": "original sound - creator_demo",
        "isOriginal": true
      },
      "region": "US",
      "rawMeta": {}
    }
  ]
}
```

## Related Discovery Docs

- [discovery-scope.md](discovery-scope.md)
- [discovery-dry-run.md](discovery-dry-run.md)
- [merge-and-evidence.md](merge-and-evidence.md)
- [topic-candidate-contract.md](topic-candidate-contract.md)
