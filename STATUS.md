# Current Status

**Last updated:** 2026-09-01  
**Sprint stage:** Day 1 completed  
**Repository:** `TD-Pipeline-Demo`

## Current Direction

Primary job target: **Technical Designer**

Current project strategy:
- Unity / C# for a small playable game-content demo
- Python for batch processing, validation, and automation
- Git / GitHub for version history
- Codex / AI Coding as an accelerator, while keeping all portfolio code explainable

The project should demonstrate a small real content-production pipeline rather than only a standalone gameplay prototype.

## Completed Today

### Environment
- Installed Unity 6.3 LTS
- Installed Visual Studio Community
- Created the Unity project
- Connected the project to a private GitHub repository

### Unity Project
- Created project folders:
  - `Assets/Scripts`
  - `Assets/Prefabs`
  - `Assets/Data`
- Saved `Assets/Scenes/Prototype_01.unity`
- Built a minimal graybox scene
- Added:
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
- Interaction disables `InteractableCube`
- Console logging for input / hit / interaction
- `Debug.DrawRay` visible in Scene view

A first interaction issue was debugged by inspecting the raycast chain and adjusting the ray origin downward so it reliably intersects the cube collider.

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

## Current Runtime State

The current prototype supports:

`WASD input → Player movement → face movement direction`

and:

`E input → forward raycast → Interactable tag check → disable target object`

The interaction path has been verified with both Console logs and Scene-view ray visualization.

## Next — Day 2

Main objective:

**Create the first real "configuration → Unity gameplay" data chain.**

Planned tasks:
- Learn only the C# needed immediately:
  - `class`
  - `List`
  - `Dictionary`
  - basic serialization
- Define external configuration for an enemy or interactable object
- Load configuration into Unity
- Make configuration values visibly change game behavior
- Update README
- Complete one Easy array / HashMap coding problem

## Current Blockers

None.

## Important Constraints

- Do not start Python tooling before the config chain exists.
- Do not expand the gameplay scope unnecessarily.
- Do not switch to UE5 or another main technology during the 14-day sprint.
- Do not optimize architecture before a real need appears.
- Core progress is judged by working artifacts, not tutorial completion.
