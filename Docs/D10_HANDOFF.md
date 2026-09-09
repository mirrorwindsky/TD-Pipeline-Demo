# D10 Handoff — Game Presentation

## Current Milestone

Day 9 is complete and sealed.

The current stable gameplay chain is:

`PowerCell → PlayerInventory → PowerNode → ControlTerminal → ExitDoor → EndMarker → Mission Complete`

Pipeline V2 is already complete for the current scope and must not be rebuilt during Day 10.

Current completed Pipeline V2 capabilities include:

- `items.csv + objectives.csv + interactables.csv` multi-table source data
- parse-once source loading
- typed `ContentModel`
- legal `interactionType` validation
- Item cross-reference validation
- config-driven Objective content
- fail-safe generation
- validated atomic batch modification

Do not redesign these systems during Day 10 unless a task explicitly targets a real regression.

## Measured D10 Baseline

The first full Vertical Slice timing was measured as:

- PowerCell: `0:09`
- PowerNode: `0:16`
- ControlTerminal: `0:22`
- Mission Complete: `0:27`
- Total: `0:27`

This timing revealed a presentation and spatial-structure problem more than a content-count problem.

## Current Key Problem

The current camera is a fixed high follow camera with no mouse-controlled view rotation.

In Play Mode, the opening view can see nearly the entire map from start to finish. The current scene still reads as an open graybox test space rather than an enclosed facility-style game environment.

Therefore, the 27-second timing should **not** be corrected by artificial padding such as:

- reducing movement speed only to increase duration;
- adding long empty corridors;
- increasing interaction counts for no gameplay reason;
- adding new gameplay systems only to satisfy the 5–8 minute target.

The current priority is to make the existing slice feel like a real playable space first, then re-measure pacing.

## D10 Execution Order

Proceed in this order unless a verified blocker requires otherwise:

1. third-person mouse camera + natural movement;
2. restructure `VerticalSlice_01` for real indoor spatial separation using occlusion, walls, ceilings, turns, doorways, and room boundaries;
3. re-time the complete flow and adjust pacing from measured results;
4. add basic materials, room/area visual differentiation, lighting, and interactable readability;
5. add necessary visible completion-state changes for PowerNode / ControlTerminal / ExitDoor and polish Objective / Prompt / Feedback;
6. produce a standalone Build and run the full Smoke Test while confirming Pipeline V2 still drives the real Demo;
7. improve Tool UX only for real operation problems; add Editor Integration only if it demonstrably shortens the workflow.

Do not jump directly to later presentation tasks before validating earlier structural changes.

## Active Task

### D10 Task 1 — Third-Person Camera + Movement

Current relevant scripts include:

- `Assets/Scripts/SimpleCameraFollow.cs`
- `Assets/Scripts/SimplePlayerController.cs`
- `Assets/Scripts/SimpleInteraction.cs`

Task 1 acceptance criteria:

- mouse yaw works naturally;
- mouse pitch works and is clamped to a usable range;
- WASD movement is natural relative to the player's / view direction;
- `SimpleInteraction` forward Raycast and `E` interaction remain functional;
- the opening view no longer behaves like a top-down overview of the whole map;
- Unity compiles with no new red Console errors;
- the change is verified in Play Mode, not only by code inspection.

After Task 1, stop and report results before beginning spatial reconstruction.

## Protected Scope

Do not:

- modify `Assets/Scenes/Prototype_01.unity`;
- expand or redesign Pipeline V2;
- add new gameplay systems;
- add new content tables;
- build a generalized quest / objective framework;
- create dependency visualization;
- build a broad Editor GUI without a demonstrated workflow need;
- attempt to complete all remaining D10 tasks in one uncontrolled pass.

## Handoff Maintenance

After each structural D10 task, update this document with:

- the new active task;
- measured timing or Play Mode results where relevant;
- newly discovered issues;
- resolved issues;
- any remaining verification risk.
