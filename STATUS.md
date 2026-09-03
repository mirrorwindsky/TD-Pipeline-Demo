# Current Status

**Last updated:** 2026-09-03  
**Sprint stage:** Day 3 completed 
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

## Current Runtime State

The current prototype supports:

`WASD input → Player movement → Face movement direction`

and:

`E input → Forward raycast → Interactable tag check → ConfigurableInteractable.Interact()`

The current end-to-end content pipeline is:

`ConfigSource/interactables.csv → config_tool.py → Assets/Data/interactables.json → JsonUtility → Dictionary lookup → Runtime object behavior`

## Current Milestone

Day 3 objective completed:

**The first designer-facing CSV → Python → JSON → Unity gameplay pipeline is working.**

Gameplay content can now be changed from the CSV source without manually editing generated JSON or modifying C# gameplay logic.

## Next — Day 4

Main objective:

**Build Demo V0 with a small playable graybox content loop.**

Planned tasks:

- Learn basic Prefab workflow
- Learn Trigger / Event basics
- Build a small graybox level
- Implement an entry/start condition
- Implement a clear objective
- Reuse interaction or another minimal action
- Implement a completion condition
- Add visible completion feedback / door opening / ending
- Play the demo from start to finish

## Current Blockers

None.

## Important Constraints

- Do not expand gameplay scope unnecessarily
- Do not switch to UE5 or another main technology during the 14-day sprint
- Do not optimize architecture before a real need appears
- Python tooling begins from the existing real config chain rather than as an isolated script
- Core progress is judged by working artifacts rather than tutorial completion