---
name: example
description: >
  Example skill demonstrating the SKILL.md format. Delete this and replace with
  real skills specific to your agent. Use when: you want to see how a skill is
  structured before writing your own.
---

# Example Skill

This is a placeholder skill for new agents based on the template.

## How to Create Your Own Skills

1. Create a directory under `agent/utils/skills/<skill-name>/` (kebab-case)
2. Add a `SKILL.md` with YAML frontmatter (`name` must match directory name exactly)
3. Write the skill instructions in the markdown body
4. The agent will auto-discover and load it on next restart

## Naming Rules

- Directory: `kebab-case` (e.g. `my-skill`)
- `name` field: identical to directory name (e.g. `name: my-skill`)
- Both must match — mismatch causes a `ValueError` at startup

## Description Writing Tips

The `description` is the only thing the agent reads to decide whether to activate
this skill. Make it specific:

```yaml
# Good — clear trigger conditions
description: >
  Build REST APIs with FastAPI. Use when creating HTTP endpoints,
  CRUD routes, Pydantic models, or any web server task.

# Bad — too vague
description: "A helpful skill."
```

Delete this file once you have added real skills.
