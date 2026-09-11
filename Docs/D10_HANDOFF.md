# D10 Historical Snapshot — Game Presentation + Tool UX

> **Historical milestone record.** This document captures the project state at the end of Day 10, before the later D11 QA fixes and D12 measurement pass. It is **not** the current Pipeline specification. For the current project state, see the root README and [`Pipeline_Case_Study.md`](Pipeline_Case_Study.md).

## Status at D10

Day 10 was completed and sealed on 2026-09-10.

The milestone included:

- third-person camera + player-relative movement;
- indoor spatial restructure;
- pacing measurement and scope decision;
- materials + lighting + static readability;
- visible completion states;
- Objective / Prompt / Feedback polish;
- Windows standalone build + full smoke test;
- unified Tool UX CLI;
- explicit decision to skip unjustified Unity Editor GUI integration.

---

## Stable Gameplay Chain at D10

```text
PowerCell
→ PlayerInventory
→ PowerNode
→ ControlTerminal
→ ExitDoor
→ EndMarker
→ Mission Complete
```

Stable configured interaction counts:

```text
power_node        = 3
control_terminal  = 2
```

The normal source baseline was restored after Batch / validation verification.

---

## Pipeline V2 State at D10

Designer-facing source:

```text
ConfigSource/
├── items.csv
├── objectives.csv
├── interactables.csv
└── batch_interaction_updates.csv
```

D10 Pipeline flow:

```text
CSV source
→ parse-once SourceTable
→ schema / type / range / duplicate validation
→ typed ContentModel
→ interactionType / Item cross-reference validation
→ ERROR gate
→ interactables.json + objectives.json
→ Unity configuration databases
→ runtime gameplay + HUD
→ standalone demo
```

Generated data:

```text
Assets/Data/interactables.json
Assets/Data/objectives.json
```

Generated JSON was treated as derived Pipeline output rather than hand-edited source data.

D10 verified:

- multi-table `items + objectives + interactables` content;
- parse-once loading;
- typed `ItemConfig`, `ObjectiveConfig`, `InteractableConfig`, and `ContentModel`;
- schema / type / range / duplicate-ID validation;
- legal `interactionType` validation;
- Item registry and `requiredItemId` / `grantedItemId` cross-reference validation;
- fail-safe generation;
- config-driven Objective descriptions;
- validated Batch Preview / atomic Apply.

The Day 8 `fake_cell` failure remained the key V1 → V2 cross-table validation case:

```text
power_node.requiredItemId = fake_cell
→ Python ERROR
→ generation blocked
→ previous valid JSON preserved
→ invalid dependency never reaches runtime
```

### Historical limitation later fixed in D11

At D10, Unity Scene reference validation still reflected the earlier V1 boundary. D11 QA later reproduced and fixed the active V2 Scene-reference coverage gap.

Current fix:

```text
97b24be fix: validate active scene config references
```

See [`D11_QA.md`](D11_QA.md) for the full reproduction and regression evidence.

---

## Third-Person Camera + Movement

The V2 presentation Scene used:

- mouse-controlled yaw / pitch;
- clamped pitch;
- third-person follow camera;
- camera shortening against solid geometry;
- player-relative W/S movement and A/D strafe;
- forward-Ray `E` interaction aligned with player facing;
- cursor lock / hide with Escape release.

The movement mode was opt-in for `VerticalSlice_01`, preserving the V1 baseline Scene.

---

## Indoor Spatial Restructure

The open graybox was replaced with an enclosed industrial facility using primitive geometry:

- ceilings;
- room boundaries;
- real door openings;
- short turns / returns;
- occlusion between task stages;
- distinct Storage / Maintenance / Control / Exit spaces.

Route:

```text
Airlock
→ Main Connector
→ Storage
→ Maintenance
→ Control
→ Exit Vestibule
→ EndMarker
```

The structure improved readability without padding duration through long empty corridors.

---

## Timing / Pacing Decision

Original open-graybox timing:

```text
PowerCell:         0:09
PowerNode:         0:16
ControlTerminal:   0:22
Mission Complete:  0:27
```

After camera + spatial restructure:

```text
PowerCell:         0:25
PowerNode:         0:32
ControlTerminal:   0:40
Mission Complete:  0:46
```

The earlier 5–8 minute target was intentionally retired for the current slice.

D10 explicitly rejected:

- slower movement solely to inflate duration;
- long empty corridors;
- inflated `requiredInteractions`;
- arbitrary hiding / searching;
- new gameplay systems added only to increase playtime.

---

## Materials + Lighting + Readability

Presentation included:

- restrained industrial-facility URP materials;
- separate floor / wall / ceiling / structure roles;
- cooler Storage treatment;
- warmer Maintenance treatment;
- cleaner cool-gray Control treatment;
- restrained green Exit accents;
- readable PowerCell / PowerNode / ControlTerminal / Exit objects;
- local indoor lights;
- disabled original Directional Light.

Materials live under:

```text
Assets/Materials/D10Facility/
```

No external art pack, custom shader, Shader Graph, or large art-production scope was introduced.

---

## Visible Completion States

`CompletionVisualFeedback.cs` was added as a presentation-only component subscribing to existing `DeviceInteractable.Completed` events and swapping assigned Renderer materials.

Accepted state changes:

```text
PowerNode:
warm amber → powered cyan

ControlTerminal:
cyan → success green

Exit:
Gate opens through existing GateController
+ surrounding frame/header remains brighter unlocked green
```

No core Device / Gate / Objective / Pipeline architecture was rewritten for this presentation pass.

---

## HUD / Prompt / Feedback

Final D10 HUD presentation:

- top-left config-driven Objective card;
- bottom-center `[E] Interact` card;
- upper-center transient Feedback card;
- persistent Mission Complete card;
- Canvas scaling configured for screen-size adaptation.

Objective descriptions remained configuration-driven.

No quest log, inventory UI, results menu, restart flow, scene transition, or large UI framework was introduced.

---

## Standalone Build Verification

D10 produced a Windows x86-64 standalone build with `VerticalSlice_01.unity` as the startup Scene.

Manual smoke test confirmed:

- direct V2 startup;
- materials / lighting / HUD;
- mouse look / camera / WASD;
- PowerCell pickup;
- PowerNode `1/3 → 2/3 → 3/3` and item consumption;
- PowerNode completion visual;
- ControlTerminal `1/2 → 2/2` and completion visual;
- Exit Gate / unlocked cue;
- EndMarker;
- Mission Complete.

The final public build was later repackaged as the tested `v1.0.0` Windows x64 Release.

---

## Tool UX CLI

D10 added a thin `argparse` command layer over the existing Python tool.

Commands:

```powershell
py Tools/config_tool.py --help
py Tools/config_tool.py
py Tools/config_tool.py generate
py Tools/config_tool.py batch-preview
py Tools/config_tool.py batch-apply
```

Verified behavior:

- no-argument invocation remains equivalent to normal Generation;
- `generate` uses existing Pipeline business logic;
- `batch-preview` reports validated updates and confirms no source files changed;
- `batch-apply` performs real source updates after validation;
- source and generated data were restored to the intended baseline after verification.

### Unity Editor Integration Decision

Editor Integration was evaluated and intentionally skipped.

Reason: the CLI already provided discoverable Generate / Preview / Apply operations, while an Editor GUI would add process invocation, PATH / working-directory handling, output capture, Editor-only code, and maintenance cost without demonstrated proportional workflow benefit.

---

## D10 Outcome

By the end of D10 the project had:

- a playable indoor Vertical Slice;
- third-person presentation;
- readable materials / lighting / room identity;
- visible interactable and completion states;
- polished Objective / Prompt / Feedback / Mission Complete UI;
- real multi-table Pipeline V2 integration;
- cross-table / fail-safe validation behavior;
- validated Batch workflow;
- unified designer-facing CLI;
- a verified Windows standalone build;
- explicit scope decisions against filler and unjustified GUI expansion.

D11 subsequently shifted the project from presentation work to systematic QA and Scale Test. The final current evidence is documented in `D11_QA*.md` and `Pipeline_Case_Study*.md`.
