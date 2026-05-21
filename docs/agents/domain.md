# Domain Docs

This repo uses a **single-context** layout.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root — project glossary and domain language
- **`docs/adr/`** — architectural decisions that touch the area you're working in

If either doesn't exist, proceed silently. `/grill-with-docs` creates them lazily when terms or decisions get resolved.

## File structure

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-*.md
│       └── 0002-*.md
└── app/
```

## Use the glossary's vocabulary

When naming concepts in issue titles, test names, or refactor proposals, use terms as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly:

> _Contradicts ADR-0001 (sqlite-over-postgres) — but worth reopening because…_
