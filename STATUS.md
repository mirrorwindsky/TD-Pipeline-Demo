# Current Status

**Last updated:** 2026-09-04  
**Sprint stage:** Day 4 completed
**Repository:** `TD-Pipeline-Demo`

## Current Direction

Primary job target: **Technical Designer**

Current project strategy:

- Unity / C# for a small playable game-content demo
- Python for batch processing, validation, and automation
- Git / GitHub for version history
- Codex / AI Coding as an accelerator, while keeping all portfolio code explainable

The project should demonstrate a small real content-production pipeline rather than only a standalone gameplay prototype.

## Completed — Day 1

### Environment

- Installed Unity 6.3 LTS
- Installed Visual Studio Community
- Created the Unity project
- Connected the project to a private GitHub repository

### Unity Project

Created project folders:

- `Assets/Scripts`
- `Assets/Prefabs`
- `Assets/Data`

Created and saved:

- `Assets/Scenes/Prototype_01.unity`

Built a minimal graybox scene containing:

- Ground
- Player
- InteractableCube

### Player Movement

Implemented `SimplePlayerController.cs`:

- WASD movement through the new Unity Input System
- `CharacterController`-based movement
- Normalized movement vector
- Player faces movement direction
- Frame-rate independent movement using `Time.deltaTime`

### Interaction

Implemented `SimpleInteraction.cs`:

- E-key interaction
- Forward `Physics.Raycast`
- `Interactable` tag check
- Console logging
- `Debug.DrawRay` visualization

The first interaction issue was debugged by inspecting the complete raycast chain and adjusting the ray origin downward so that it reliably intersects the target collider.

### Git / Documentation

- Committed and pushed project changes
- Created and pushed `README.md`

### Coding Warm-up

Completed LeetCode #1 **Two Sum** in Python:

1. Wrote brute-force O(n²) solution
2. Identified complement lookup idea
3. Replaced list search with `dict`
4. Reached average O(n) time using a hash table
5. Understood that Python `dict` key lookup is average O(1), trading additional O(n) space

## Completed — Day 2

### Config Data Model

Added serializable C# configuration classes:

- `InteractableConfig`
- `InteractableConfigCollection`

Each interactable configuration currently contains:

- `id`
- `displayName`
- `requiredInteractions`
- `deactivateOnComplete`

Multiple configuration entries are stored in:

`List<InteractableConfig>`

### External Configuration

Added external gameplay configuration:

`Assets/Data/interactables.json`

The file defines multiple interactable objects with different runtime parameters.

Current examples include:

- `cube_quick`
- `cube_sturdy`

### Config Loading

Implemented `InteractableConfigDatabase`.

At runtime:

1. Unity reads the external JSON file
2. `JsonUtility` deserializes the JSON into C# objects
3. Configuration entries are initially stored in a `List`
4. A `Dictionary<string, InteractableConfig>` is built using config IDs as keys
5. Runtime objects can request configuration by ID

The dictionary provides ID-based lookup rather than repeatedly scanning the full configuration list.

### Config-Driven Interaction

Implemented `ConfigurableInteractable`.

Each configurable object contains:

- A `configId`
- A reference to `InteractableConfigDatabase`
- Runtime interaction state

The object requests its own configuration using its ID and applies values such as `requiredInteractions` to gameplay behavior.

`SimpleInteraction` now detects an interactable target and calls its `Interact()` behavior rather than directly disabling every target itself.

### Runtime Verification

Verified:

- `cube_quick` completes after 1 interaction
- `cube_sturdy` completes after 3 interactions
- Changing `cube_sturdy.requiredInteractions` from 3 to 5 in JSON makes it require 5 interactions
- No gameplay C# code needs to be rewritten when changing this configuration value

This confirms the first real:

**external configuration → Unity gameplay**

data chain.

### Coding Warm-up

Completed the Day 2 LeetCode daily problem.

The core reasoning was independently identified through parity-case analysis, including:

- With at least two odd numbers, odd values can be transformed through odd-minus-odd operations to produce even results
- With exactly one odd number, even values can subtract that odd value to produce an all-odd result

## Completed — Day 3

### Designer-Facing Source Data

Added:

`ConfigSource/interactables.csv`

The CSV now acts as the editable source configuration for interactable content.

Current source records include:

- `cube_quick`
- `cube_sturdy`

The source data contains:

- `id`
- `displayName`
- `requiredInteractions`
- `deactivateOnComplete`

### Python Tool V0

Added:

`Tools/config_tool.py`

The tool currently:

1. Resolves project-relative paths using `pathlib`
2. Reads CSV source data using `csv.DictReader`
3. Converts each CSV row into an `InteractableConfig` dataclass
4. Converts CSV string values into appropriate Python types
5. Converts dataclass instances into dictionaries
6. Writes the final structure using `json.dump`
7. Outputs generated data directly to:

`Assets/Data/interactables.json`

### Type Conversion

CSV values are initially read as strings.

The tool currently converts:

- `requiredInteractions` → `int`
- `deactivateOnComplete` → `bool`

This creates structured configuration data before JSON generation.

### End-to-End Verification

Verified the complete flow:

`CSV → Python → JSON → Unity → Runtime gameplay`

Test performed:

1. Changed `cube_sturdy.requiredInteractions` from 3 to 5 in the CSV source
2. Ran `config_tool.py`
3. Confirmed generated JSON changed to 5
4. Ran the Unity prototype
5. Confirmed SturdyCube required 5 interactions
6. Did not manually edit JSON
7. Did not modify C# gameplay logic

After verification, the source configuration was restored to:

`cube_sturdy.requiredInteractions = 3`

and the JSON was regenerated.

### Coding Warm-up

Completed the Day 3 LeetCode daily problem.

## Completed — Day 4

### Graybox Demo V0

Built a small playable content loop using the existing player interaction and config-driven object systems.

Current level flow:

`Player Start → StartGate → QuickCube / SturdyCube → ExitDoor → EndMarker`

### Prefab Workflow

Created:

`Assets/Prefabs/StartGate.prefab`

The StartGate was converted into a reusable Prefab.

The Prefab contains the reusable object structure and trigger behavior, including:

- Box Collider configured as a Trigger
- Disabled Mesh Renderer
- `StartTrigger` component

Prefab Overrides were applied back to the Prefab Asset after configuring the scene instance.

Scene-specific references such as the active `DemoFlowController` remain connections made by the scene instance rather than reusable Prefab data.

### Trigger-Based Mission Start

Implemented `StartTrigger`.

When the Player enters the trigger:

`OnTriggerEnter → Player tag check → DemoFlowController.StartMission()`

The flow controller prevents repeated mission initialization if the player enters the trigger multiple times.

### Objective Completion Events

Updated `ConfigurableInteractable` with a `Completed` event.

Each interactable now announces completion without directly deciding what other gameplay systems should do.

Current event flow:

`ConfigurableInteractable completed → Completed event → DemoFlowController`

This separates objective behavior from level-flow behavior.

### Demo Flow Controller

Implemented `DemoFlowController`.

It currently tracks:

- Whether the mission has started
- Number of completed objectives
- Whether the exit is unlocked
- Whether the mission has finished

The controller subscribes to completion events from:

- QuickCube
- SturdyCube

After both objectives are complete:

`2 / 2 objectives → ExitDoor disabled → Exit opened`

### End Trigger

Implemented `EndTrigger`.

After the exit has been unlocked, entering the EndMarker calls:

`DemoFlowController.TryFinishMission()`

and completes the playable loop with:

`Demo Complete!`

### Runtime Verification

Verified three cases:

1. Normal flow:
   `Start → QuickCube → SturdyCube → Exit → End`

2. Reverse objective order:
   `Start → SturdyCube → QuickCube → Exit → End`

3. Re-entering StartGate:
   the mission is not initialized a second time

All tests behaved as expected.

## Current Runtime State

The current playable loop is:

`Start Trigger → Mission Start → Config-Driven Objectives → Completed Events → Objective Count 2/2 → Exit Open → End Trigger → Demo Complete`

The content data pipeline remains:

`ConfigSource/interactables.csv → config_tool.py → interactables.json → Unity → Runtime gameplay`

## Current Milestone

Day 4 objective completed:

**Demo V0 can now be played from beginning to end as a complete graybox content loop.**

## Next — Day 5

Main objective:

**Upgrade Python Tool V0 with validation and actionable error reporting.**

Planned tasks:

- Missing-field validation
- Duplicate-ID validation
- Range validation
- Reference validation
- ERROR / WARNING separation
- Actionable error messages
- Invalid-data testing

## Current Blockers

None.

## Important Constraints

- Do not expand gameplay scope unnecessarily
- Do not switch to UE5 or another main technology during the 14-day sprint
- Do not optimize architecture before a real need appears
- Python tooling begins from the existing real config chain rather than as an isolated script
- Core progress is judged by working artifacts rather than tutorial completion
