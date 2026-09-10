# D10 Handoff — Game Presentation

## Current Milestone

Day 9 is complete and sealed.

D10 Tasks 1–4, Task 5A, and Task 5B are complete with user acceptance.

The current active task is:

**D10 Task 6 — Standalone Build + Full Smoke Test + Pipeline V2 Runtime Confirmation**

The stable gameplay chain is:

`PowerCell → PlayerInventory → PowerNode → ControlTerminal → ExitDoor → EndMarker → Mission Complete`

Pipeline V2 is already complete for the current scope and must not be redesigned during Day 10.

Current Pipeline V2 capabilities include:

- `items.csv + objectives.csv + interactables.csv` multi-table source data;
- parse-once loading;
- typed `ContentModel`;
- legal `interactionType` validation;
- Item cross-reference validation;
- config-driven Objective content;
- fail-safe generation;
- validated atomic batch modification.

---

## Measured D10 Timing

Original open-graybox baseline:

- PowerCell: `0:09`
- PowerNode: `0:16`
- ControlTerminal: `0:22`
- Mission Complete: `0:27`
- Total: `0:27`

Human re-test after camera + spatial restructure:

- PowerCell: `0:25`
- PowerNode: `0:32`
- ControlTerminal: `0:40`
- Mission Complete: `0:46`
- Total: `0:46`

Decision: D10 will not force the old 5–8 minute target through filler. Final unfamiliar-player duration is deferred to the later user-test stage.

---

## Completed D10 Work

### Task 1 — Third-Person Camera + Movement — Completed

User acceptance passed.

- mouse yaw / pitch with clamping;
- third-person follow camera with collision shortening;
- player-relative W/S movement and A/D strafe in `VerticalSlice_01`;
- existing forward-Ray `E` interaction preserved;
- cursor focus / lock behavior accepted;
- shared movement mode is opt-in for V2, preserving the V1 baseline behavior.

### Task 2 — Indoor Spatial Restructure — Completed

User acceptance passed.

The V2 scene is now an enclosed facility with ceilings, room boundaries, door openings, turns, returns, and occlusion.

Current route:

`Airlock → main connector → Storage → Maintenance → Control → Exit vestibule → EndMarker`

The complete gameplay chain passed after the restructure.

### Task 3 — Re-time + Pacing Diagnosis — Completed

Human re-test measured `0:46`. The project chose presentation quality over artificial duration padding.

### Task 4 — Materials + Lighting + Static Visual Readability — Completed

User acceptance passed.

- restrained industrial-facility material language;
- Storage / Maintenance / Control / Exit receive distinct but related visual treatment;
- seven local indoor lights;
- original Directional Light retained but disabled;
- PowerCell / PowerNode / ControlTerminal / Exit are visually readable;
- materials live under `Assets/Materials/D10Facility/`.

### Task 5A — Visible Completion States — Completed

User acceptance passed.

Added `Assets/Scripts/CompletionVisualFeedback.cs`, a small presentation-only component that subscribes to existing `DeviceInteractable.Completed` events and swaps assigned Renderer material references.

Accepted world-state feedback:

- PowerNode: warm amber → powered cyan;
- ControlTerminal: cyan → success green;
- Exit: Gate opens through existing `GateController`, while frame/header receive a persistent brighter unlocked-green cue.

No gameplay architecture, interaction counts, Pipeline files, or ConfigSource files were changed.

### Task 5B — Objective / Prompt / Feedback Polish — Completed

User manual acceptance passed on 2026-09-10.

Accepted HUD presentation:

- Objective: top-left config-driven card with static `OBJECTIVE` label;
- Prompt: compact bottom-center `[E] Interact` card;
- Feedback: separate transient upper-center card;
- Mission Complete: distinct persistent completion card plus existing final feedback;
- Canvas Scaler: Scale With Screen Size, `1920 × 1080`, match `0.5`.

Files changed in Task 5B:

- `Assets/Scenes/VerticalSlice_01.unity`
- `Assets/Scripts/PlayerHUD.cs`
- `Assets/Scripts/VerticalSliceFlowController.cs`
- this handoff document

`SimpleInteraction.cs` remained unchanged. Objective content remains config-driven. `VerticalSliceFlowController` only adds the small `hud.ShowMissionComplete()` presentation call after the existing final objective update. No new UI framework, results menu, restart flow, scene transition, or gameplay system was added.

---

## D10 Execution Order

1. Third-person camera + movement — **Completed**
2. Indoor spatial restructure — **Completed**
3. Re-time + pacing diagnosis — **Completed**
4. Materials + lighting + static readability — **Completed**
5. Presentation feedback:
   - 5A Visible Completion States — **Completed**
   - 5B Objective / Prompt / Feedback Polish — **Completed**
6. **Standalone Build + Full Smoke Test + Pipeline V2 runtime confirmation — Active**
7. Tool UX / optional Editor Integration decision — Pending; implementation only if a real workflow problem justifies it

Sound / VFX remain optional and must not displace core D10 acceptance work.

---

## Active Task

### D10 Task 6 — Standalone Build + Full Smoke Test + Pipeline V2 Runtime Confirmation

Task 6 is a delivery / regression task, not a feature-development task.

The goal is to prove that the current V2 slice works as a real standalone Windows demo, outside the Unity Editor, while remaining driven by the existing Pipeline V2 output.

### Primary goals

1. Inspect the current Unity 6 build configuration.
2. Make `Assets/Scenes/VerticalSlice_01.unity` the startup scene for the standalone demo.
3. Produce a Windows standalone build in a clearly ignored local build directory.
4. Launch the standalone build and complete the demo from start to Mission Complete.
5. Confirm the standalone build does not depend on the Unity Console or Editor-only state.
6. Re-run the normal Pipeline V2 validation / generation workflow using the documented project command.
7. Confirm the generated data remains the data consumed by the real V2 demo; do not manually edit generated JSON.
8. Record build / smoke-test results and any real regression found.

### Build-scene rule

`Prototype_01.unity` remains a protected V1 baseline asset and must not be edited.

The final standalone demo should start directly in `VerticalSlice_01` because there is no menu / scene-selection flow. Inspect the current Unity 6 build profile / EditorBuildSettings configuration first and make the smallest appropriate build-scene change. Do not delete or modify the V1 scene asset.

### Build-output rule

Build output is a local verification artifact, not source content.

Use an existing ignored build directory if one already exists. Otherwise use a clear local path such as `Builds/Windows/` and ensure the build output itself is not accidentally committed. Do not add large binaries to Git.

### Pipeline confirmation

Before the final standalone smoke test, read the current README / project documentation and use the repository's documented normal Pipeline V2 command rather than inventing a new invocation.

The final check should establish:

`ConfigSource/*.csv → Tools/config_tool.py validation/generation → Assets/Data/*.json → Unity runtime → standalone demo`

Do not manually edit `Assets/Data/*.json`.

Do not expand Pipeline V2. If normal generation fails, diagnose the actual regression and make only the narrowest justified fix.

### Full smoke-test route

The final standalone test should cover, by normal player input:

1. launch the executable;
2. verify camera / mouse look;
3. verify WASD movement;
4. verify `[E] Interact` Prompt;
5. pick up PowerCell;
6. confirm Objective advances;
7. use PowerNode for the configured 3 interactions;
8. confirm PowerCell is consumed correctly;
9. confirm PowerNode completion visual state;
10. use ControlTerminal for the configured 2 interactions;
11. confirm ControlTerminal completion visual state;
12. confirm Exit Gate opens and unlocked frame cue remains;
13. reach EndMarker;
14. confirm Mission Complete presentation;
15. confirm transient Feedback and persistent UI states behave normally.

### Manual-test-first principle

Do **not** waste time forcing brittle automation for the actual standalone player experience.

Unity MCP / Unity CLI may be used for reliable preparation and inspection:

- build configuration;
- compilation;
- build invocation;
- Console / build-log inspection;
- missing-reference audits;
- checking that the expected executable / data folder was produced.

However, the final executable launch and real keyboard / mouse smoke test may be handed directly to the user if automation would require fragile input injection, focus routing, window automation, or custom test harnesses.

If the build succeeds, ask the user to manually launch the executable and run the smoke-test route above. Manual user testing is the preferred final acceptance evidence for real standalone controls, presentation, and feel.

Do not create an automation framework merely to prove that a human can move and press E in the built executable.

### Protected scope

Do not:

- modify `Assets/Scenes/Prototype_01.unity`;
- redesign the V2 scene;
- rework Task 4 lighting / materials;
- rework Task 5A presentation unless a real build regression requires it;
- rework Task 5B HUD unless a real build regression requires it;
- add gameplay systems;
- add menus, restart systems, loading screens, scene transitions, or settings UI;
- alter interaction counts;
- pad duration;
- add new content tables;
- redesign Pipeline V2;
- build a generalized automated gameplay-test framework;
- start Task 7 Tool UX work.

### Minimum reliable validation before handing off to the user

- project compiles successfully;
- no new red Unity Console errors;
- build configuration starts in `VerticalSlice_01`;
- Windows standalone build completes successfully;
- expected executable and supporting data files exist;
- no build output is accidentally staged for source control;
- normal Pipeline V2 validation / generation succeeds;
- generated JSON remains produced by the Pipeline rather than manual editing;
- `Prototype_01.unity` remains unchanged.

### User acceptance

The user should manually verify the built executable from launch to Mission Complete.

The final acceptance report should explicitly distinguish:

- checks performed reliably through Unity MCP / CLI / build logs;
- checks performed manually by the user in the standalone executable;
- anything not verified.

Do not claim the standalone route passed until the user actually reports that it passed.

### Handoff maintenance

After implementation / build preparation and reliable checks, update this document with:

- build configuration change;
- build target and output path;
- Pipeline V2 generation command/result;
- build result;
- Git status / whether build artifacts are ignored;
- any regression fixed;
- items awaiting standalone user testing.

Until the user reports the standalone smoke test passed, Task 6 status should be:

**implementation/build complete — awaiting user standalone acceptance**

Do not advance to Task 7 automatically.

---

## Remaining D10 Work After Task 6

### Task 7 — Tool UX / Optional Editor Integration Decision

This is primarily a decision task. Inspect the real designer workflow first. If the current CLI output / steps are already clear and Unity MCP has removed the practical authoring bottleneck, explicitly record that further Editor GUI work is not justified.

Only implement a small UX improvement if a concrete workflow problem is demonstrated.

After Task 7, synchronize `TODO.md`, `STATUS.md`, `README.md`, and this handoff for D10 closure.

---

## Repository-wide protected scope

Do not:

- edit the V1 baseline scene;
- expand Pipeline V2 without a demonstrated regression;
- add new gameplay merely to satisfy the old duration target;
- add new content tables;
- build a generalized quest framework;
- create dependency visualization;
- build a broad Editor GUI without a demonstrated workflow need;
- conflate user manual acceptance with automated-test evidence.
