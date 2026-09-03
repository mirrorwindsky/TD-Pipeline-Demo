# TD Pipeline Demo

Two-week Technical Designer portfolio project.

## Goal

Build a small Unity gameplay demo, identify bottlenecks in its content-production workflow, and improve the pipeline with Python tooling and automation.

The project is intended to demonstrate:

- Gameplay / content implementation
- Data-driven design
- Tooling and automation
- Content-pipeline understanding
- Debugging and iteration
- Explainable AI-assisted development

## Current Progress

### Day 1 — Minimal Unity Prototype

- Set up Unity 6.3 LTS project
- Created the initial graybox scene
- Implemented basic WASD player movement
- Used `CharacterController` for movement
- Normalized movement input to avoid faster diagonal movement
- Made the player face the movement direction
- Implemented E-key interaction using a forward `Physics.Raycast`
- Added `Interactable` tag checking
- Added Console logging and `Debug.DrawRay` for interaction debugging
- Verified the complete interaction chain:

`Input → Raycast → Tag Check → Interaction`

### Day 2 — First Config-Driven Gameplay Chain

- Added external JSON configuration for interactable objects
- Added serializable C# configuration classes
- Loaded external JSON data into Unity using `JsonUtility`
- Stored multiple configuration entries in `List<InteractableConfig>`
- Built a runtime lookup table using `Dictionary<string, InteractableConfig>`
- Added config-driven interactable behavior
- Allowed individual GameObjects to select configuration through `configId`
- Verified multiple objects can use different configuration entries
- Verified configuration changes alter runtime behavior without changing gameplay code

Current configuration flow:

`interactables.json → JsonUtility → List<InteractableConfig> → Dictionary lookup → ConfigurableInteractable → Runtime behavior`

Example:

- `cube_quick` requires 1 interaction before completion
- `cube_sturdy` requires 3 interactions before completion
- Changing `cube_sturdy.requiredInteractions` from 3 to 5 in JSON changes its runtime behavior without modifying C# gameplay logic

### Day 3 — Python Tool V0

- Added designer-facing CSV source data in `ConfigSource/interactables.csv`
- Added `Tools/config_tool.py`
- Used `pathlib` to resolve deterministic project-relative input and output paths
- Used `csv.DictReader` to read source configuration rows
- Added an `InteractableConfig` Python `dataclass` for structured config data
- Converted CSV string values into runtime data types such as `int` and `bool`
- Used `json.dump` to generate Unity-consumable JSON
- Generated `Assets/Data/interactables.json` automatically from CSV source data
- Verified Unity continues to consume the generated JSON without changing the existing C# loading path
- Verified changing `cube_sturdy.requiredInteractions` from 3 to 5 in CSV propagates through Python → JSON → Unity and changes runtime behavior to 5 interactions
- Restored the final example configuration to 3 interactions after verification

Current content pipeline:

`CSV source data → Python config tool → Generated JSON → Unity config database → Runtime gameplay`

## Current Runtime Behavior

The prototype currently supports:

`WASD input → Player movement → Face movement direction`

and:

`E input → Forward raycast → Interactable tag check → ConfigurableInteractable.Interact()`

Interaction behavior is no longer fully hard-coded inside the player interaction script. Each configurable interactable reads its runtime behavior from external configuration data.

## Current Project Structure

Key project areas currently include:

- `ConfigSource`
  - Designer-facing CSV source configuration
- `Tools`
  - Python config conversion tooling
- `Assets/Data`
  - Generated JSON gameplay configuration consumed by Unity
- `Assets/Scripts`
  - Player movement
  - Raycast interaction
  - Configuration data classes
  - Configuration database
  - Config-driven interactable behavior
- `Assets/Scenes`
  - Prototype graybox scene

## Tech

- Unity 6.3 LTS
- C#
- JSON
- Python — CSV/JSON pipeline tooling
- Git / GitHub

## Next

### Day 4 — Demo V0

Next objective:

Build a small playable graybox content loop using the existing config-driven interaction foundation.

Planned tasks:

- Learn basic Prefab workflow
- Learn Trigger / Event basics
- Build a small graybox level
- Implement a clear start → objective → interaction/action → completion loop
- Add visible completion feedback
- Play the demo from beginning to end