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

## Current Runtime Behavior

The prototype currently supports:

`WASD input → Player movement → Face movement direction`

and:

`E input → Forward raycast → Interactable tag check → ConfigurableInteractable.Interact()`

Interaction behavior is no longer fully hard-coded inside the player interaction script. Each configurable interactable reads its runtime behavior from external configuration data.

## Current Project Structure

Key project areas currently include:

- `Assets/Scenes`
  - Prototype graybox scene
- `Assets/Scripts`
  - Player movement
  - Raycast interaction
  - Configuration data classes
  - Configuration database
  - Config-driven interactable behavior
- `Assets/Data`
  - External JSON gameplay configuration

## Tech

- Unity 6.3 LTS
- C#
- JSON
- Python — pipeline tooling planned from Day 3
- Git / GitHub

## Next

### Day 3 — Python Tool V0

Next objective:

Build the first designer-facing source-data conversion step.

Planned pipeline:

`CSV source data → Python tool → JSON output → Unity runtime`

Planned tasks:

- Read CSV configuration data
- Convert CSV into structured JSON
- Write generated config to a deterministic output path
- Make Unity consume generated data
- Establish the first real automated content-production pipeline