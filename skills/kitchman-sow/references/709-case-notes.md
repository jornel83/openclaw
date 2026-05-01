# 709 Riversdale Road Demo Case Notes

Use this reference only for the 709 Riversdale Road Camberwell demo. It helps the agent organize a realistic demo output. It is not a general rule engine and should not be treated as automatic drawing recognition.

## Demo Positioning

The 709 case should demonstrate:

- Feishu-triggered SOW creation.
- Structured room/area scope.
- Proposal-style client output.
- Open questions for estimator review.
- Revision flow in the same conversation.

## Likely Project Identity

```text
Project: 709 Riversdale Road, Camberwell
Project type: Residential joinery / custom cabinetry
Client name: TBC
Quote id: TBC
```

## Working Areas for Demo

Use these as demo working areas when consistent with the supplied case materials:

```text
GF Kitchen
Pantry
Living / TV Unit
Laundry
Master WIR
Bedroom Robe
Study / Desk
Bathroom / Powder Room Joinery
Garage / Storage
```

If an uploaded document contradicts this list, follow the uploaded document and mark differences in notes or open questions.

## GF Kitchen Demo Scope

Potential scope:

- Overhead cabinets.
- Base cabinets.
- Drawer units.
- Fridge cupboard.
- Oven tower.
- Wall panels.
- Island back curved structures.
- Pantry interface or adjacent cladding when shown.

Likely TBC:

- Door/panel finish.
- Stone benchtop inclusion.
- LED strip inclusion.
- Appliance supply and installation.
- Electrical/plumbing responsibility.

## Pantry Demo Scope

Potential scope:

- Pantry door cladding.
- Adjacent cabinetry or panels when shown.

Important caveat:

- If pantry door is cladding only, do not include door structure, hinges, tracks, handles, hardware, or automation unless explicitly confirmed.

Likely TBC:

- Door structure responsibility.
- Hardware responsibility.
- Finish continuity.

## Living / TV Unit Demo Scope

Potential scope:

- Low cabinet or TV unit.
- Wall panels or feature panels.
- Open shelving if shown.

Likely TBC:

- Cable management.
- LED lighting.
- Stone/top material.
- Wall fixing constraints.

## Laundry Demo Scope

Potential scope:

- Base cabinets.
- Overhead cabinets.
- Tall storage.
- Benchtop or sink cabinet when shown.

Likely TBC:

- Plumbing.
- Sink and tap supply.
- Appliance clearances.
- Stone or laminate benchtop responsibility.

## Master WIR Demo Scope

Potential scope:

- Wardrobe carcasses.
- Hanging rails.
- Shelves.
- Drawers.
- Mirror or feature doors if shown.

Likely TBC:

- Mirror inclusion.
- Drawer hardware.
- LED lighting.
- Door finish.

## Robe Demo Scope

Potential scope:

- Wardrobe internals.
- Shelves.
- Hanging rails.
- Drawers if shown.

Likely TBC:

- Sliding/hinged door responsibility.
- Handles and hardware.
- Finish.

## Open Questions to Consider

- Confirm project client name and quote id.
- Confirm which rooms are included in Kitchman's scope.
- Confirm door and panel finishes.
- Confirm carcass material and color.
- Confirm stone benchtop inclusion or exclusion.
- Confirm LED lighting inclusion or exclusion.
- Confirm appliance, plumbing, and electrical responsibility.
- Confirm whether pantry door is cladding only or includes door structure/hardware.
- Confirm mirror and glass responsibility for WIR/robe areas.

## Demo Revision Examples

Use these as examples for Feishu revision handling:

```text
Kitchen stone 全部排除
LED 也排除
Pantry 门只写 cladding
Master WIR mirror 改成 TBC
```

The agent should update the current SOW JSON and proposal, then return a concise change summary.
