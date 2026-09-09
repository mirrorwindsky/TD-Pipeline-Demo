# D10 Handoff — Game Presentation

## Current Milestone

Day 9 is complete and sealed.

D10 Task 1 is Completed with user acceptance. Task 2's first indoor structure
pass is complete and functionally verified; user wayfinding / camera comfort
review is the remaining acceptance step. Task 3 has not started.

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

Task 1's third-person mouse camera and natural movement are complete and have
passed user acceptance. Task 2 has now addressed the open room boundaries,
missing ceilings and long sightlines with an enclosed primitive structure pass.
The remaining review is whether an unfamiliar player can read the route and
comfortably steer the camera through its entrances and turns. Materials,
lighting and UI presentation have not been worked on in this pass.

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

### D10 Task 2 — Vertical Slice Spatial Restructure

**First structure pass complete; pending user walkthrough.** This run stops here.
The active acceptance task remains Task 2; Task 3 has not been started.

### Task 2 Structure / Verification — 2026-09-09

The compact route is now:

`Airlock offset doorway → left turn in the main connector → Storage entry return
→ back to the connector → Maintenance work bay → Control entry turn
→ unlocked Exit vestibule → EndMarker`

The six existing floor GameObjects and all existing room groups were reused.
East is +X and north is +Z. The overall footprint remains approximately the same;
there are no added long corridors, extra objectives or interaction-count changes.

| Space | First-pass structure |
| --- | --- |
| Airlock | Existing 6 × 5 m floor; enclosed front wall with a right-offset 2.2 m opening |
| Main connector | Floor narrowed from 10 to 8 m; one return wall directs a short left turn toward Storage |
| Storage | Existing 6 × 6 m room; east-side doorway and an internal return hide PowerCell until the player enters and turns |
| Maintenance | Floor deepened from 6 to 8 m; north-side approach and a structural service corner create a narrower work bay |
| Control | 8 × 5.6 m broad room; offset south entry and a short internal return conceal the terminal from the connector |
| Exit | Existing 4 × 8 m floor moved 2 m east; fitted gate opening and short internal return form a narrow final vestibule |

Walls meet ceilings at 4.2 m. The six ceiling slabs are 0.3 m thick, with edges
overlapping the enclosing walls. Door openings are 2.2–2.4 m wide and 3.3 m high.
No material, lighting, UI, camera-script or movement-parameter edits were made.

Gameplay Transform changes, preserving the original GameObjects and components:

| Object | Previous position | New position | Reason |
| --- | --- | --- | --- |
| PowerCell | (-8, 0.5, -4) | (-8, 0.5, -2.4) | Place it behind Storage's entry return |
| PowerNode | (8, 1, -4) | (8.2, 1, -5.6) | Place it inside the Maintenance work bay |
| ExitDoor | (0, 1.5, 5.6) | (2, 1.65, 5.6) | Align it with the offset Exit opening |
| EndMarker_V2 | (0, 1.5, 12.5) | (2, 1.5, 12) | Keep the completion trigger inside the relocated Exit |

ExitDoor scale changed from (4, 3, 0.3) to (2.4, 3.3, 0.3) to fit the opening.
ControlTerminal remains at (2.7, 1, 3). Player and Main Camera serialized values
are unchanged from the accepted Task 1 configuration.

Authoring / reference checks:

- All construction used Unity MCP with scene-scoped Unity Primitive, Transform
  and Undo APIs. The temporary authoring script lives under ignored
  `Temp/D10Task2`; no generic Editor tool or runtime component was added.
- Added 23 Cube primitives: 17 walls / returns / headers and six ceilings.
  Added two empty groups, `Level_Geo/Walls/Hall` and `Level_Geo/Ceilings`.
- Deleted no GameObjects. Existing twenty wall primitives were extended / fitted;
  four existing floor Transforms were adjusted.
- All existing serialized object IDs remain present. All 27 persisted
  MonoBehaviour blocks are unchanged, including config IDs, database references,
  prerequisite Device, gate source, flow-controller, HUD and camera target links.
- No missing scripts were found. `Prototype_01.unity` SHA-256 is unchanged.
- Git changes are limited to `VerticalSlice_01.unity` and this handoff document.

Play Mode validation through Unity MCP:

- Unity reports scripts up to date; no C# source changed. Final Console Error
  count is zero. The scene was saved and Unity was left out of Play Mode.
- A continuous input-driven walkthrough moved from the original spawn through
  every doorway and room, picked up PowerCell, completed PowerNode in three E
  presses, completed ControlTerminal in two E presses, passed the unlocked gate
  and entered EndMarker. The final HUD displayed `Mission Complete` and
  `Facility restored. Exit reached.`
- The walkthrough queued mouse / W / E input through the existing Input System;
  it did not teleport the player, call `Interact` directly, modify gameplay
  state, lower movement speed or change configuration data.
- Start occlusion checks covered the center and eight bounds corners of
  PowerCell, PowerNode, ControlTerminal, ExitDoor and EndMarker from both the
  camera and player-head positions; all were blocked by Level_Geo.
- PowerCell was also occluded from both viewpoints outside Storage's entrance.
  It became visible after entering and rounding the return, as confirmed by
  the runtime camera captures.
- Objective progression, interaction prompts, item consumption, device feedback,
  gate unlocking and mission-completion feedback all worked through the existing
  gameplay chain. The upper pitch clamp also stayed below the new ceiling.
- Across 8,044 sampled route frames, a 0.08 m camera-center overlap probe detected
  zero overlaps with environment colliders; the controller remained grounded.
  Camera follow distance ranged from approximately 0.55 to 3.5 m as obstacles
  shortened the boom. This is not exhaustive frustum / corner collision testing.
- The first automated attempt used a waypoint inside the terminal's collider.
  That test waypoint was corrected to the adjacent aisle, then the entire route
  passed from a fresh Play session. No scene change was needed for that correction.
- Runtime captures and the temporary input probe / reports are under
  `Temp/D10Task2`. These are local verification artifacts, not shipped assets.

Remaining user review:

- Whether the first-time Storage → Maintenance → Control route is understandable
  without knowing the layout: **该项仍需要用户手动验证**.
- Camera comfort during fast turns, doorway approaches and close device exits,
  especially where the boom retracts toward 0.55 m:
  **该项仍需要用户手动验证**. No camera-center penetration was detected on the
  tested route, but subjective comfort cannot be certified by the input probe.
- Check that the room-size / entry-direction differences are perceptible in the
  untextured graybox. Existing ambient lighting is unchanged; this pass deliberately
  leaves lighting and material readability for their later authorized tasks.
- The V1 baseline was not opened for runtime testing and was not edited.

The next human timing should include room entry, short turns and orientation
instead of a direct open-floor traversal. No duration is promised and the
5–8-minute target has not been validated. The functional walkthrough was not a
Task 3 pacing measurement; no Task 3 work, commit or push was performed.

## Completed Task

### D10 Task 1 — Third-Person Camera + Movement — Completed

User acceptance passed on 2026-09-09:

- mouse yaw / pitch work normally;
- the third-person camera experience is good;
- WASD controls feel natural;
- E interaction works;
- the cursor locks and hides correctly when Game View has focus;
- the user considers Task 1 successful and has authorized Task 2.

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

Task 1 was stopped and reported before spatial work. Task 2 is now separately
authorized by the user.

### Task 1 Implementation / Verification — 2026-09-09

Task 1 implementation and user acceptance are complete. The technical checks
below record the Task 1 implementation pass; the active task is now Task 2.

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

Task 1 verification history / remaining regression boundaries:

- The user subsequently accepted mouse control, third-person feel, natural WASD,
  E interaction and Game View focus / cursor behavior. These are no longer
  outstanding Task 1 acceptance items.
- Camera behavior in the new walls / ceilings will be checked again in Task 2;
  the Task 1 tests did not provide exhaustive wall-corner collision coverage.
- The Task 1 implementation probe did not replay the route through ControlTerminal,
  ExitDoor and EndMarker. Task 2 subsequently verified the complete chain in the
  new layout. The V1 baseline has not been opened for runtime regression; the
  shared player script retains its default V1 movement mode.
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
