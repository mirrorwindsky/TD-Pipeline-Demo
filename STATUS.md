# Current Status

**Last updated:** 2026-09-02  
**Sprint stage:** Day 2 completed  
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

## Current Runtime State

The current prototype supports:

`WASD input → Player movement → Face movement direction`

and:

`E input → Forward raycast → Interactable tag check → ConfigurableInteractable.Interact()`

The current data-driven gameplay chain is:

`interactables.json → JsonUtility → List<InteractableConfig> → Dictionary<string, InteractableConfig> → Config ID lookup → Runtime object behavior`

## Current Milestone

Day 2 objective completed:

**The first external configuration → gameplay chain is working.**

Changing gameplay configuration can now alter object behavior without rewriting the interaction implementation.

## Next — Day 3

Main objective:

**Create Python Tool V0 and start the designer-facing data conversion pipeline.**

Planned tasks:

- Learn only the Python modules needed immediately:
  - `pathlib`
  - `csv`
  - `json`
  - `dataclass`
- Create `config_tool.py`
- Read source CSV config
- Convert CSV into JSON / structured config
- Output generated config to a deterministic path
- Make Unity consume generated data
- Complete one Easy HashMap / string coding problem

Target flow:

`CSV source config → Python conversion → JSON → Unity → Runtime gameplay`

## Current Blockers

None.

## Important Constraints

- Do not expand gameplay scope unnecessarily
- Do not switch to UE5 or another main technology during the 14-day sprint
- Do not optimize architecture before a real need appears
- Python tooling begins from the existing real config chain rather than as an isolated script
- Core progress is judged by working artifacts rather than tutorial completion