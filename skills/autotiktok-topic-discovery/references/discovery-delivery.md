# Discovery Delivery

This reference extracts the discovery-relevant parts of the shared development plan.

## Primary Owner Scope

Discovery work spans two owners in the shared plan:

- discovery inputs and infrastructure
- module-1 topic candidate generation

That means discovery work often touches both:

- signal collection
- candidate packaging

## Early Milestones

### Week 1

Freeze the contracts that discovery must expose:

- `signalItem`
- `videoSample`
- `topicCandidate`

### Week 2

Discovery needs the first usable daily snapshot:

- Creative Center MVP
- Search Insights MVP
- first recorded snapshot

### Week 3

Discovery should be able to generate:

- 15 to 30 structured candidates from a snapshot
- acceptable duplicate control
- full evidence links

## Discovery Exit Criteria

Discovery is healthy when:

- candidates are evidence-backed
- similar candidates merge correctly
- angle differences are still preserved when they matter
- ranking receives `searchEvidence` and `executionProfile` without guessing

## Main Risks

- collector instability breaks replay
- topic abstraction becomes too freeform
- merge logic collapses distinct angles
- contract drift blocks ranking and optimizer work

## Related Shared Docs

- Shared delivery plan: [../../autotiktok/docs/development-plan.md](../../autotiktok/docs/development-plan.md)
