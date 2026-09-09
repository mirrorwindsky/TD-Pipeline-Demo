# D10 Handoff — Game Presentation

## Current Milestone

Day 9 is complete and sealed.

D10 Task 1 and Task 2 are complete with user acceptance. Task 3 re-timing / pacing diagnosis is also complete. The current active task is **D10 Task 4 — Basic Materials + Lighting + Visual Readability**. Its first static visual pass is implemented and MCP-verified, and is awaiting user visual acceptance. Task 5 has not started.

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

## Measured D10 Timing

### Original D10 baseline — before camera / spatial restructure

- PowerCell: `0:09`
- PowerNode: `0:16`
- ControlTerminal: `0:22`
- Mission Complete: `0:27`
- Total: `0:27`

This first timing exposed presentation and spatial-structure problems: the old fixed high camera and open graybox made the whole route visible almost immediately.

### Task 3 human re-test — after Task 1 + Task 2

User timing on 2026-09-09:

- PowerCell: `0:25`
- PowerNode: `0:32`
- ControlTerminal: `0:40`
- Mission Complete: `0:46`
- Total: `0:46`

Interpretation:

- The new enclosed layout successfully increases spatial reading and traversal time without artificial padding.
- More than half of the total run is now spent reaching / locating PowerCell (`25 s`).
- The remainder of the actual dependency chain from PowerCell to Mission Complete takes only about `21 s`.
- The current core gameplay loop is inherently very small. The short duration is no longer primarily a room-layout problem.

D10 will **not** force the original 5–8 minute target by adding filler such as:

- reducing movement speed only to increase duration;
- adding long empty corridors;
- increasing `requiredInteractions` for no gameplay reason;
- hiding objectives in arbitrary corners;
- adding new gameplay systems only to satisfy a duration target.

The current priority is presentation quality and a tight, complete Technical Designer Vertical Slice. Final unfamiliar-player duration will be measured during the later user-test stage.

## Current Key State

Task 1's third-person mouse camera and natural movement are complete and have passed user acceptance.

Task 2 has replaced the previous open graybox with an enclosed indoor primitive layout featuring real room boundaries, ceilings, door openings, turns, and occlusion. The user reports that the result feels substantially better: all areas now read as indoor spaces with proper doorways, the structure is more complex, and the camera behaves normally inside the new layout.

Task 4 has now added the first static facility material / lighting pass:

- floors, walls, ceilings and entrance frames have distinct material roles;
- room identity uses restrained cool / warm tints and local indoor lighting;
- key interactables have contrasting bodies and fixed emissive surfaces;
- brightness comfort, first-glance recognition and video readiness await user review;
- completion-state feedback and HUD polish have not yet received their presentation pass.

## D10 Execution Order

Proceed in this order unless a verified blocker requires otherwise:

1. third-person mouse camera + natural movement — **Completed**;
2. restructure `VerticalSlice_01` for real indoor spatial separation — **Completed**;
3. re-time the complete flow and diagnose pacing — **Completed**;
4. add basic materials, room / area visual differentiation, lighting, and interactable readability — **First pass complete; active user acceptance**;
5. add necessary visible completion-state changes for PowerNode / ControlTerminal / ExitDoor and polish Objective / Prompt / Feedback;
6. produce a standalone Build and run the full Smoke Test while confirming Pipeline V2 still drives the real Demo;
7. improve Tool UX only for real operation problems; add Editor Integration only if it demonstrably shortens the workflow.

Do not jump directly to later presentation tasks before validating the current visual pass.

## Active Task

### D10 Task 4 — Basic Materials + Lighting + Visual Readability

Task 4 should improve the static presentation of the existing, already-functional indoor slice without changing gameplay architecture or pacing.

Primary goals:

- establish a simple facility-like material language for floors, walls, ceilings, and structural elements;
- make Storage / Maintenance / Control / Exit perceptibly different without rebuilding their geometry;
- replace the current flat graybox lighting with basic indoor lighting and readable light / dark hierarchy;
- make PowerCell, PowerNode, ControlTerminal, and ExitDoor visually stand out from environment geometry;
- preserve the complete existing gameplay chain and all serialized references.

Task 4 should stay deliberately small:

- use Unity-native / simple materials and basic lights;
- no external art production is required;
- no new gameplay systems;
- no HUD polish yet;
- no completion-state behavior yet unless required to fix a regression;
- no VFX / audio unless separately authorized after core D10 work is complete;
- no Pipeline / ConfigSource / Tool changes.

After the first visual pass, stop for user Play Mode review before continuing to Task 5.

### Task 4 Static Visual Pass / Verification — 2026-09-09

**Status: first static pass complete, awaiting user visual acceptance.** Unity is
out of Play Mode, the scene is saved, and this run stops here. No commit, push,
Task 5 work, Build or Build Settings change was performed.

Baseline inspection confirmed `VerticalSlice_01`, PC URP / Linear color space,
the supported `Universal Render Pipeline/Lit` shader, and one enabled white
Directional Light at intensity 2. All 60 existing mesh renderers, including the
inactive legacy objects, used the packaged default Lit material. There was no
project environment-material library; the other material assets belonged to TMP.

Fifteen new opaque URP Lit materials are in `Assets/Materials/D10Facility/`:

| Material | Responsibility |
| --- | --- |
| M_Floor_Graphite | Dark, rough industrial floor; metallic 0.05 / smoothness 0.18 |
| M_Wall_Facility | Neutral facility walls and main connector |
| M_Ceiling_Cool | Darker, cooler ceiling surface |
| M_Structure_Metal | Dark metal entrance trim, panel surrounds, cell end caps and gate seam |
| M_Wall_Storage | Muted blue-gray Storage walls |
| M_Wall_Maintenance | Warm gray / taupe Maintenance walls |
| M_Wall_Control | Lighter, cleaner cool-gray Control walls |
| M_Accent_Amber | Restrained warm Maintenance doorway accent |
| M_Accent_Cyan | Storage / Control doorway accents |
| M_Accent_Exit | Muted green Exit gate and entrance accents |
| M_Equipment_Metal | Shared metal body for PowerNode and ControlTerminal |
| M_Energy_Amber | Bright warm PowerCell body and fixed PowerNode panel |
| M_Screen_Cyan | Fixed cyan ControlTerminal screen surface |
| M_Light_Diffuser | Ceiling fixture diffuser surfaces |
| M_Player_Shell | Neutral light player shell replacing the default material |

Emission is fixed, with color multipliers 0.45 for Energy, 0.65 for Screen and
1.2 for Diffuser. No event changes these values. URP 17.3's material validation
requires an emissive GI eligibility flag to retain `_EMISSION`; these three
materials use `BakedEmissive` and have the keyword enabled. No lightmap bake or
runtime GI / emission-state system was added.

Region direction:

- Storage: cooler blue-gray walls and cooler local light; the warm bright cell
  contrasts with the surroundings and has two dark end caps.
- Maintenance: warmer walls / doorway accent and a warm work light; PowerNode's
  dark metal body surrounds a fixed warm energy panel.
- Control: lighter walls and cool-white illumination; the terminal has a cyan
  screen facing the existing interaction approach. The closed green gate is
  already identifiable before terminal completion.
- Exit: green entrance / gate accents, a central gate seam and a pale green-white
  local light establish a consistent exit direction. The existing gate behavior
  remains unchanged.

Seven local lights live under `Visual_Presentation/Indoor_Lighting`:

| Light | Type | Position | Intensity / range | Color |
| --- | --- | --- | --- | --- |
| Light_Airlock | Spot, 145 degrees | (0, 3.9, -12) | 12 / 7 m | #E1EBF2 |
| Light_Hall_Entry | Spot, 145 degrees | (-0.7, 3.9, -8.2) | 14 / 7 m | #E4EBEE |
| Light_Hall_Junction | Spot, 150 degrees | (0.7, 3.9, -2.4) | 14 / 8 m | #E4EBEE |
| Light_Storage | Point | (-7.8, 3.25, -3.6) | 4.3 / 6 m | #C5DCEF |
| Light_Maintenance | Point | (8, 3.25, -3.3) | 5.5 / 6.5 m | #F1DAB8 |
| Light_Control | Point | (0.8, 3.35, 3.1) | 6 / 7 m | #DDEDF0 |
| Light_Exit | Spot, 120 degrees | (2.2, 3.9, 9.8) | 12 / 6 m | #D6EADD |

All seven are stationary Realtime lights with soft shadows. Storage and
Maintenance use the existing URP low shadow tier (256); the other lights use
medium (512). No render-pipeline asset or global quality setting was changed.
The original Directional Light object is retained but its Light component is
disabled. Scene ambient lighting uses Trilight fill with sky (0.48, 0.52, 0.58),
equator (0.34, 0.38, 0.42), ground (0.20, 0.23, 0.27), and reflection intensity
0.35. The existing Volume profile and post-processing settings are unchanged.

Scene scope / reference checks:

- Added 24 non-colliding Cube details: ten entrance jambs, seven ceiling fixtures
  and seven static device details. Added seven Light GameObjects and three groups.
- The new visual details have no Collider and use Ignore Raycast. Door jambs sit
  outside the existing clear openings. No doorway size or route was changed.
- Existing Gameplay Renderer materials changed intentionally. Existing gameplay
  scripts and logic components did not change; the 27 pre-existing serialized
  MonoBehaviour blocks match the pre-pass scene exactly.
- Every pre-existing Transform retains its position, rotation, scale and parent.
  Gameplay objects were not moved. Their added visual children inherit only the
  existing pickup / gate visibility behavior; no new state switching was added.
- The final Editor audit found 78 active mesh renderers, zero active default
  material users, zero missing material slots, zero unsupported / error shaders
  and zero missing scripts. Inactive legacy / Ground default materials were left
  intact, and the shared packaged Lit material was never edited.
- `Prototype_01.unity` SHA-256 is unchanged. Gameplay source, ConfigSource, Tools,
  generated JSON, Assets/Settings and ProjectSettings have no final changes.

Verification / visual iteration:

- Unity reported scripts up to date; there were no C# source edits. Final Console
  Error and Warning counts are both zero, including material / shader errors.
- The complete route was replayed through queued mouse / W / E input from the
  original spawn, with no teleports or direct calls to `Interact`. PowerCell,
  inventory consumption, PowerNode 3/3, ControlTerminal 2/2, gate opening,
  EndMarker and Mission Complete all passed with the original architecture.
- Objective, Prompt and Feedback updated normally. The final run passed all 44
  checks; 6,633 sampled frames showed no environment overlap at the camera center
  and no lost grounding. Task 1's accepted camera / movement values are unchanged.
- A separate per-key WASD probe did not reliably deliver movement while the
  Editor lacked application focus. A controlled input-routing retry also produced
  zero displacement, so neither is counted as a passing test. The temporary input
  routing was restored to `PointersAndKeyboardsRespectGameViewFocus`. The earlier
  continuous mouse/W/E walkthrough remains a passing functional route test.
- Game View captures were actually inspected for Opening/Airlock, Storage entry
  and reveal, Maintenance, Control, the closed gate, Exit and Mission Complete.
- The first visual pass was too dark and URP had cleared the emission keywords
  because of the initial GI flag. The flag was corrected, floor / frame and
  ambient visibility were lifted, and entry illumination was adjusted.
- Wide-angle shadow banding was reduced by improving local shadow resolution /
  bias and narrowing the Exit spot angle. The final images retain dark corners
  while making floors, openings and interactable surfaces readable.
- Temporary authoring / input probes, audit evidence and screenshots are under
  ignored `Temp/D10Task4`; no deliverable Editor tool or GUI was added.

Known limits / user acceptance:

- Normal hardware A/S/D/W input and control comfort after focusing Game View:
  **该项仍需要用户手动验证**. The supplementary per-key MCP probe was inconclusive;
  no gameplay code or persistent input settings were changed.
- Overall brightness comfort and any glare: **该项仍需要用户手动验证**.
- Whether room differences feel natural and each interactable is identifiable
  at first glance: **该项仍需要用户手动验证**.
- Shadows and wall appearance during prolonged camera rotation, especially at
  close / grazing angles: **该项仍需要用户手动验证**. The simple 256/512 shadow
  settings are not a guarantee of perfect edges from every angle.
- Whether the scene is ready for a demo-video recording:
  **该项仍需要用户手动验证**. The scene deliberately retains primitive silhouettes
  and untextured surfaces; this is a basic facility presentation pass.
- No new completion-color changes, dynamic emission, gate animation, VFX, audio,
  HUD/Prompt/Feedback polish, Tool UX or Build work has been started.

## Completed Task

### D10 Task 3 — Re-time and Pacing Diagnosis — Completed

Task 3 made no scene, gameplay, Pipeline, or configuration changes.

Human re-test result:

- PowerCell: `0:25`
- PowerNode: `0:32`
- ControlTerminal: `0:40`
- Mission Complete: `0:46`
- Total: `0:46`

Decision:

The project will not pad the current gameplay loop to force the previous 5–8 minute target. The measured result indicates that the current dependency chain is intentionally small; further D10 effort should improve quality, readability, and presentation rather than add low-value traversal or repeated interactions.

The final unfamiliar-player timing remains deferred to the later user-test milestone.

### D10 Task 2 — Vertical Slice Spatial Restructure — Completed

User acceptance passed on 2026-09-09.

User feedback:

- the scene now reads as fully indoor rather than open graybox space;
- rooms have proper door openings and real enclosure;
- the structure is more complex but still readable;
- the third-person camera behaves normally in the enclosed layout and does not visibly break during normal play;
- the complete route still works.

#### Task 2 Structure / Verification — 2026-09-09

The compact route is now:

`Airlock offset doorway → left turn in the main connector → Storage entry return → back to the connector → Maintenance work bay → Control entry turn → unlocked Exit vestibule → EndMarker`

The six existing floor GameObjects and all existing room groups were reused. East is +X and north is +Z. The overall footprint remains approximately the same; there are no added long corridors, extra objectives or interaction-count changes.

| Space | First-pass structure |
| --- | --- |
| Airlock | Existing 6 × 5 m floor; enclosed front wall with a right-offset 2.2 m opening |
| Main connector | Floor narrowed from 10 to 8 m; one return wall directs a short left turn toward Storage |
| Storage | Existing 6 × 6 m room; east-side doorway and an internal return hide PowerCell until the player enters and turns |
| Maintenance | Floor deepened from 6 to 8 m; north-side approach and a structural service corner create a narrower work bay |
| Control | 8 × 5.6 m broad room; offset south entry and a short internal return conceal the terminal from the connector |
| Exit | Existing 4 × 8 m floor moved 2 m east; fitted gate opening and short internal return form a narrow final vestibule |

Walls meet ceilings at 4.2 m. The six ceiling slabs are 0.3 m thick, with edges overlapping the enclosing walls. Door openings are 2.2–2.4 m wide and 3.3 m high. No material, lighting, UI, camera-script or movement-parameter edits were made during Task 2.

Gameplay Transform changes, preserving the original GameObjects and components:

| Object | Previous position | New position | Reason |
| --- | --- | --- | --- |
| PowerCell | (-8, 0.5, -4) | (-8, 0.5, -2.4) | Place it behind Storage's entry return |
| PowerNode | (8, 1, -4) | (8.2, 1, -5.6) | Place it inside the Maintenance work bay |
| ExitDoor | (0, 1.5, 5.6) | (2, 1.65, 5.6) | Align it with the offset Exit opening |
| EndMarker_V2 | (0, 1.5, 12.5) | (2, 1.5, 12) | Keep the completion trigger inside the relocated Exit |

ExitDoor scale changed from (4, 3, 0.3) to (2.4, 3.3, 0.3) to fit the opening. ControlTerminal remains at (2.7, 1, 3). Player and Main Camera serialized values are unchanged from the accepted Task 1 configuration.

Authoring / reference checks:

- All construction used Unity MCP with scene-scoped Unity Primitive, Transform and Undo APIs. The temporary authoring script lived under ignored `Temp/D10Task2`; no generic Editor tool or runtime component was added.
- Added 23 Cube primitives: 17 walls / returns / headers and six ceilings.
- Added two empty groups, `Level_Geo/Walls/Hall` and `Level_Geo/Ceilings`.
- Deleted no GameObjects. Existing wall primitives were extended / fitted; selected floor Transforms were adjusted.
- All existing serialized object IDs remain present. Persisted MonoBehaviour references, config IDs, database references, prerequisite Device, gate source, flow-controller, HUD, and camera target links remain intact.
- No missing scripts were found. `Prototype_01.unity` was not modified.

Play Mode verification through Unity MCP:

- Unity reported scripts up to date and final Console Error count zero.
- A continuous input-driven walkthrough traversed every room, picked up PowerCell, completed PowerNode in three E presses, completed ControlTerminal in two E presses, passed the unlocked gate and entered EndMarker.
- Final HUD displayed `Mission Complete` and `Facility restored. Exit reached.`
- Start occlusion checks confirmed the later gameplay objects are blocked by `Level_Geo` from the starting view.
- PowerCell remains hidden until the player enters Storage and rounds its internal return.
- Objective progression, interaction prompts, item consumption, device feedback, gate unlocking and mission-completion feedback all worked through the unchanged gameplay chain.
- Camera collision checks detected no environment overlap on the tested route; subjective camera comfort was subsequently accepted by the user during manual play.

Remaining boundary:

- The V1 baseline was not opened for runtime testing during Task 2 and was not edited.

### D10 Task 1 — Third-Person Camera + Movement — Completed

User acceptance passed on 2026-09-09:

- mouse yaw / pitch work normally;
- the third-person camera experience is good;
- WASD controls feel natural;
- E interaction works;
- the cursor locks and hides correctly when Game View has focus;
- the user considers Task 1 successful.

Current relevant scripts include:

- `Assets/Scripts/SimpleCameraFollow.cs`
- `Assets/Scripts/SimplePlayerController.cs`
- `Assets/Scripts/SimpleInteraction.cs`

Implementation summary:

- `SimpleCameraFollow` reads Input System mouse delta. Horizontal mouse motion updates camera yaw and player yaw together; vertical motion changes only camera pitch.
- `LateUpdate` smooths the follow focus with exponential interpolation.
- A small sphere cast shortens camera distance against solid geometry and eases back out when clear.
- Cursor lock / hide is handled in Play Mode; Escape / focus loss releases it and clicking Game View resumes control.
- `SimplePlayerController` uses player-relative W/S forward/back and A/D strafe in `VerticalSlice_01`, while preserving normalization, speed, gravity, grounding and `CharacterController.Move`.
- The new movement mode is a serialized opt-in. Its default remains false so the shared controller retains the fixed-camera movement behavior used by the untouched V1 baseline scene.
- `SimpleInteraction`, `IInteractable`, Inventory, Pickup, Device, Objective, Gate and all Pipeline V2 files were unchanged.

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
| Camera near clip | 0.1 m |
| Player-relative movement | Enabled in `VerticalSlice_01` |

Task 1 compiled with no new red Console errors. Mouse / movement / interaction behavior was verified through Unity MCP and subsequently accepted through direct user play.

## Protected Scope

Do not:

- modify `Assets/Scenes/Prototype_01.unity`;
- expand or redesign Pipeline V2;
- add new gameplay systems merely to increase duration;
- add new content tables;
- build a generalized quest / objective framework;
- create dependency visualization;
- build a broad Editor GUI without a demonstrated workflow need;
- pad duration with long empty traversal, lower movement speed, or inflated interaction counts;
- attempt to complete all remaining D10 tasks in one uncontrolled pass.

## Handoff Maintenance

After each structural D10 task, update this document with:

- the new active task;
- measured timing or Play Mode results where relevant;
- newly discovered issues;
- resolved issues;
- any remaining verification risk.
