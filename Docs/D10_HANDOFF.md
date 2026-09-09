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

### Task 1 Implementation / Verification — 2026-09-09

Task 1 is implemented. The active follow-up is **manual acceptance of Task 1**;
Task 2 has not started. Unity was left out of Play Mode. No commit or push was made.

Implementation:

- `SimpleCameraFollow` reads Input System mouse delta. Horizontal mouse motion
  updates camera yaw and player yaw together; vertical motion changes only camera
  pitch. Camera input runs before player movement and the unchanged interaction
  update, keeping `transform.forward` consistent within the frame.
- `LateUpdate` smooths the follow focus with exponential interpolation. Entering
  Play Mode initializes the camera directly at the new view, without sweeping
  down from the old high camera pose.
- A small sphere cast shortens camera distance against existing solid geometry,
  ignores the player and triggers, and eases back out when clear. This is needed
  because the initial player position is only about 2.35 m from the back wall.
- The cursor locks and hides in Play Mode. Escape / focus loss releases it;
  clicking the Game view resumes mouse control. Disabling the camera or stopping
  Play Mode releases the cursor. Player movement pauses while the cursor is free.
- `SimplePlayerController` uses player-relative W/S forward/back and A/D strafe
  in this scene, preserving normalization, speed 5, gravity -20, grounding and
  `CharacterController.Move`. Strafing/backing up does not turn the player away
  from the mouse-facing direction.
- The new movement mode is a serialized opt-in, enabled only in
  `VerticalSlice_01`. Its default is false so the shared controller retains the
  fixed-camera movement behavior used by the untouched V1 baseline scene.
- `SimpleInteraction`, `IInteractable`, Inventory, Pickup, Device, Objective,
  Gate and all Pipeline V2 files are unchanged.

Current Inspector parameters:

| Parameter | Value |
| --- | --- |
| Camera distance | 3.5 m, shortened near geometry |
| Focus height | 1 m above the player Transform / capsule center |
| Mouse sensitivity | 0.12 degrees per input pixel |
| Initial pitch | 12 degrees downward |
| Pitch limits | -15 to 40 degrees |
| Follow speed | 8 |
| Camera collision radius | 0.3 m |
| Camera near clip | 0.1 m, changed from 0.3 m |
| Player-relative movement | Enabled in `VerticalSlice_01` |

Validation performed through Unity MCP in Unity 6000.3.23f1:

- Script compilation completed successfully, with no new red Console errors.
- The active scene was `Assets/Scenes/VerticalSlice_01.unity` throughout the work.
- In actual Play Mode frames, a temporary probe queued mouse/keyboard state into
  the existing Input System. It did not call `Interact` directly or replace
  gameplay methods. Runtime-only repositioning was used to isolate test cases;
  these checks are not a complete player-driven route playthrough or new timing.
- Mouse yaw left/right and pitch up/down passed. Repeated extreme input stayed
  clamped at exactly -15 / 40 degrees; the player remained upright.
- At player yaw 90 degrees, W/S moved along +X/-X and A/D along +Z/-Z. Facing
  stayed at 90 degrees; diagonal speed remained normalized.
- Camera follow settled within 0.00003 m of the expected unobstructed position;
  subsequent idle drift was below 0.000005 m. The opening back-wall constraint
  kept the camera inside the room, around world height 2.5 m, rather than the
  previous high overview. The final opening camera render was visually inspected.
- Cursor lock/hide, Escape release, click re-lock, movement stopping while the
  cursor is free, gravity during a fall, and grounded recovery all passed.
- After mouse turning, the unchanged forward ray hit PowerCell. E picked it up,
  deactivated it and added `power_cell` to inventory.
- After mouse turning toward PowerNode, E consumed the item once and completed
  the device in three presses. Holding E for several frames counted only once.
  The objective advanced to `Activate the Control Terminal.` Console call stacks
  confirmed these interactions originated in `SimpleInteraction.Update`.
- No missing scripts were found. The saved scene diff changes only camera
  parameters, camera near clip and the player movement-mode flag; existing
  serialized object references remain intact. `Prototype_01.unity` SHA-256 was
  unchanged before/after the task.

Remaining manual acceptance / risks:

- Real mouse sensitivity, sustained turning while moving, and overall control
  comfort still need user testing: **该项仍需要用户手动验证**.
- Real application focus loss / return and camera behavior at all wall corners
  still need user testing: **该项仍需要用户手动验证**. The initial wall constraint
  was verified, but exhaustive camera collision coverage was not performed.
- The complete route through ControlTerminal, ExitDoor and EndMarker was not
  replayed during Task 1; nor was the V1 baseline opened for runtime regression.
  These remain manual regression checks. No broken serialized references were
  introduced or observed; the shared player script still carries a small
  unverified V1 regression risk despite retaining its default movement mode.
- The opening no longer presents a top-down map overview. Open sky and distant
  sightlines in the existing graybox remain; room geometry was not changed.

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
