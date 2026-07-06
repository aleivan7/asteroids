# Asteroids Pygame Project Rules

## Project context
This is a Python/Pygame Asteroids-style game. Keep the code beginner-readable and aligned with the current architecture unless asked to refactor.

## Workflow
- Before implementing a feature, inspect the relevant files and explain the plan.
- Prefer small changes over large rewrites.
- Do not change unrelated behavior.
- After changes, summarize what changed, what files changed, and what manual tests should be run.
- If tests exist, run them before finishing.
- If a feature is visual and hard to unit test, provide a manual QA checklist.

## Code style
- Keep classes focused.
- Avoid global state unless it already exists in the project pattern.
- Use clear names.
- Prefer constants for tunable values like speed, cooldowns, lives, score values, and power-up duration.

## Git workflow
- Each sprint should happen on its own branch.
- Each feature should have a clear commit message.